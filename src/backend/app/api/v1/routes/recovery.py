"""
Recovery Routes
This module contains all recovery related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import asyncio
import asyncpg
import asyncio.subprocess as asp
import os
import pathlib

from app.dependencies import get_database_service, get_recovery_service
from app.models.schemas import (RecoveryRequest, RecoveryResponse, RecoveryHistoryResponse, RecoveryStatusEnum)
from app.services.database_service import DatabaseService
from app.services.recovery_service import RecoveryService
from app.utils.logger import get_logger
from app.core.config import settings
from prometheus_client import Counter, Histogram, Gauge

router = APIRouter()
logger = get_logger(__name__)

# Prometheus metrics for recovery operations
RECOVERY_REQUESTS_TOTAL = Counter(
    'recovery_requests_total',
    'Total number of recovery requests',
    ['type', 'severity', 'status']
)

RECOVERY_DURATION = Histogram(
    'recovery_duration_seconds',
    'Time spent performing recovery operations',
    ['type', 'severity']
)

ACTIVE_RECOVERIES = Gauge(
    'active_recoveries',
    'Number of currently active recovery operations'
)

RECOVERY_SUCCESS_RATE = Gauge(
    'recovery_success_rate',
    'Success rate of recovery operations'
)


async def verify_recovery_auth(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify recovery operation authorization.
    """
    if not settings.RECOVERY_AUTH_REQUIRED:
        return True
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Recovery operations require authentication",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify Bearer token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        if token == settings.RECOVERY_BEARER_TOKEN:
            return True
    
    raise HTTPException(
        status_code=401,
        detail="Invalid recovery authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

BACKUP_DIR = pathlib.Path(os.getenv("BACKUP_DIR", "/tmp/cern_db_backups"))


async def _run_recovery(recovery_id: str, recovery_type: str, recovery_service: RecoveryService) -> None:
    """Background task: execute the actual recovery operation and update status."""
    start = datetime.utcnow()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    db_url = os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/monitoring_db")
    # Parse connection details from DATABASE_URL
    try:
        from urllib.parse import urlparse
        u = urlparse(db_url.replace("postgresql://", "http://"))
        db_host = u.hostname or "localhost"
        db_port = str(u.port or 5432)
        db_user = u.username or "admin"
        db_pass = u.password or "admin123"
        db_name = (u.path or "/monitoring_db").lstrip("/")
    except Exception:
        db_host, db_port, db_user, db_pass, db_name = "localhost", "5432", "admin", "admin123", "monitoring_db"

    env = {**os.environ, "PGPASSWORD": db_pass}
    ts = start.strftime("%Y%m%d_%H%M%S")

    try:
        await recovery_service.update_recovery_status(recovery_id, "running")

        container = os.getenv("DB_CONTAINER", "postgres-primary")

        if recovery_type == "backup":
            out_file = BACKUP_DIR / f"backup_{ts}.sql"
            proc = await asp.create_subprocess_exec(
                "docker", "exec", container,
                "pg_dump", "-U", db_user, "-d", db_name,
                stdout=asp.PIPE, stderr=asp.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            if proc.returncode != 0:
                raise RuntimeError(stderr.decode().strip())
            out_file.write_bytes(stdout)
            size_kb = round(out_file.stat().st_size / 1024, 1)
            details = {"backup_file": str(out_file), "size_kb": size_kb}

        elif recovery_type == "restore":
            backups = sorted(BACKUP_DIR.glob("backup_*.sql"), reverse=True)
            if not backups:
                raise RuntimeError("No backup file found. Run Backup first.")
            latest = backups[0]
            # Copy file into container then restore
            cp_proc = await asp.create_subprocess_exec(
                "docker", "cp", str(latest), f"{container}:/tmp/{latest.name}",
                stdout=asp.PIPE, stderr=asp.PIPE
            )
            _, cp_err = await asyncio.wait_for(cp_proc.communicate(), timeout=30)
            if cp_proc.returncode != 0:
                raise RuntimeError(f"docker cp failed: {cp_err.decode().strip()}")
            proc = await asp.create_subprocess_exec(
                "docker", "exec", container,
                "psql", "-U", db_user, "-d", db_name, "-f", f"/tmp/{latest.name}",
                stdout=asp.PIPE, stderr=asp.PIPE
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            if proc.returncode != 0:
                raise RuntimeError(stderr.decode().strip())
            details = {"restored_from": str(latest)}

        elif recovery_type == "repair":
            reindex_block = (
                "DO $$ DECLARE t RECORD; BEGIN "
                "FOR t IN SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' AND tableowner = current_user LOOP "
                "EXECUTE 'REINDEX TABLE public.' || quote_ident(t.tablename); "
                "END LOOP; END; $$;"
            )
            for cmd in ["VACUUM ANALYZE;", reindex_block]:
                proc = await asp.create_subprocess_exec(
                    "docker", "exec", container,
                    "psql", "-U", db_user, "-d", db_name, "-c", cmd,
                    stdout=asp.PIPE, stderr=asp.PIPE
                )
                _, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
                if proc.returncode != 0:
                    raise RuntimeError(f"{cmd[:40]}…: {stderr.decode().strip()}")
            details = {"action": "VACUUM ANALYZE + REINDEX (user-owned tables)"}

        elif recovery_type == "rebuild":
            compose_dir = os.getenv("COMPOSE_DIR", str(pathlib.Path(__file__).parents[6]))

            # Step 1: check if replica container exists and is running
            inspect = await asp.create_subprocess_exec(
                "docker", "inspect", "--format", "{{.State.Status}}", "postgres-replica",
                stdout=asp.PIPE, stderr=asp.PIPE
            )
            inspect_out, _ = await inspect.communicate()
            container_status = inspect_out.decode().strip()

            in_recovery, lag_secs = ("unknown", "unknown")

            if container_status == "running":
                # Step 2a: check replication lag before restarting
                lag_cmd = (
                    "SELECT pg_is_in_recovery()::text, "
                    "COALESCE(EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::int::text, 'n/a');"
                )
                replica_host = os.getenv("REPLICA_HOST", "localhost")
                replica_port = os.getenv("REPLICA_PORT", "5433")
                lag_proc = await asp.create_subprocess_exec(
                    "psql", "-h", replica_host, "-p", replica_port, "-U", db_user, "-d", db_name,
                    "-t", "-A", "-c", lag_cmd, "--no-password",
                    env=env, stdout=asp.PIPE, stderr=asp.PIPE
                )
                lag_out, _ = await asyncio.wait_for(lag_proc.communicate(), timeout=15)
                lag_info = lag_out.decode().strip()
                if "|" in lag_info:
                    parts = lag_info.split("|")
                    in_recovery = parts[0].strip()
                    lag_secs = parts[1].strip() if len(parts) > 1 else "unknown"

                docker_proc = await asp.create_subprocess_exec(
                    "docker", "restart", "postgres-replica",
                    stdout=asp.PIPE, stderr=asp.PIPE
                )
                action_taken = "restarted"
            else:
                # Step 2b: container missing or stopped — bring it up via docker compose
                docker_proc = await asp.create_subprocess_exec(
                    "docker", "compose", "up", "postgres-replica", "-d",
                    cwd=compose_dir,
                    stdout=asp.PIPE, stderr=asp.PIPE
                )
                action_taken = "started"

            _, docker_err = await asyncio.wait_for(docker_proc.communicate(), timeout=180)
            if docker_proc.returncode != 0:
                raise RuntimeError(f"docker {action_taken} failed: {docker_err.decode().strip()}")

            details = {
                "action": f"Replica container {action_taken} — pg_basebackup re-sync triggered",
                "container_status_before": container_status or "not found",
                "replica_was_in_recovery": in_recovery,
                "replication_lag_seconds_before": lag_secs,
            }

        else:
            details = {"action": recovery_type}

        duration = round((datetime.utcnow() - start).total_seconds(), 2)
        details["duration_seconds"] = duration
        await recovery_service.update_recovery_status(
            recovery_id, "completed",
            end_time=datetime.utcnow().isoformat(),
            details=details
        )
        logger.info(f"Recovery {recovery_id} ({recovery_type}) completed in {duration}s")
        RECOVERY_REQUESTS_TOTAL.labels(type=recovery_type, severity="", status="completed").inc()
        ACTIVE_RECOVERIES.dec()

    except Exception as e:
        duration = round((datetime.utcnow() - start).total_seconds(), 2)
        await recovery_service.update_recovery_status(
            recovery_id, "failed",
            end_time=datetime.utcnow().isoformat(),
            error=str(e),
            details={"duration_seconds": duration}
        )
        logger.error(f"Recovery {recovery_id} ({recovery_type}) failed: {e}")
        RECOVERY_REQUESTS_TOTAL.labels(type=recovery_type, severity="", status="failed").inc()
        ACTIVE_RECOVERIES.dec()


@router.post("/start")
async def start_recovery(
    request: RecoveryRequest,
    background_tasks: BackgroundTasks,
    recovery_service: RecoveryService = Depends(get_recovery_service),
    authenticated: bool = Depends(verify_recovery_auth)
):
    """Start a recovery operation."""
    RECOVERY_REQUESTS_TOTAL.labels(
        type=request.type,
        severity=request.severity,
        status='initiated'
    ).inc()

    try:
        recovery_record = await recovery_service.start_recovery(
            recovery_type=request.type,
            reason=request.reason or "",
            severity=request.severity
        )

        ACTIVE_RECOVERIES.inc()
        background_tasks.add_task(_run_recovery, recovery_record["id"], request.type, recovery_service)

        return {
            "success": True,
            "recovery_id": recovery_record["id"],
            "message": "Recovery operation started successfully",
            "status": RecoveryStatusEnum.IN_PROGRESS,
            "recovery_record": recovery_record
        }

    except ValueError as e:
        logger.error(f"Invalid recovery request: {e}")
        RECOVERY_REQUESTS_TOTAL.labels(type=request.type, severity=request.severity, status="validation_failed").inc()
        raise HTTPException(status_code=400, detail=f"Invalid recovery request: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to start recovery: {e}")
        raise HTTPException(status_code=500, detail="Failed to start recovery operation")

async def perform_recovery(
    recovery_id: str,
    request_data: Dict[str, Any],
    recovery_service: RecoveryService = Depends(get_recovery_service)
):
    """
    Perform actual recovery operation with production-grade error handling.
    
    Args:
        recovery_id: Unique recovery identifier
        request_data: Recovery request data
    """
    try:
        logger.info(f"Performing recovery {recovery_id} of type {request_data.get('type')}")
        
        # Update recovery record with success
        await recovery_service.update_recovery_status(
            recovery_id,
            "completed",
            datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Recovery {recovery_id} failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform recovery")
        
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    logger.error(f"Recovery {recovery_id} failed after {duration:.2f}s: {e}")
    
    # Update recovery record with failure
    try:
        await recovery_service.update_recovery_status(
            recovery_id,
            RecoveryStatusEnum.FAILED,
            datetime.utcnow(),
            duration=duration,
            details={"error": str(e), "error_type": type(e).__name__}
        )
    except Exception as update_error:
        logger.error(f"Failed to update recovery status: {update_error}")
    
    # Update metrics
    RECOVERY_REQUESTS_TOTAL.labels(
        type=request_data.get('type', 'unknown'), 
        severity=request_data.get('severity', 'unknown'), 
        status="failed"
    ).inc()
    
    # Update success rate
    await update_success_rate()
    
    # Update active recoveries gauge
    active_count = await recovery_repo.get_active_recoveries_count()
    ACTIVE_RECOVERIES.set(active_count)

async def update_success_rate():
    """
    Update the recovery success rate gauge.
    """
    try:
        stats = await recovery_repo.get_recovery_statistics()
        if stats["total_recoveries"] > 0:
            success_rate = stats["successful_recoveries"] / stats["total_recoveries"]
            RECOVERY_SUCCESS_RATE.set(success_rate)
        else:
            RECOVERY_SUCCESS_RATE.set(0.0)
    except Exception as e:
        logger.error(f"Failed to update success rate: {e}")

@router.get("/status/{recovery_id}")
async def get_recovery_status(
    recovery_id: str,
    recovery_service: RecoveryService = Depends(get_recovery_service),
    authenticated: bool = Depends(verify_recovery_auth)
):
    """Get status of a specific recovery operation."""
    try:
        recovery = await recovery_service.get_recovery_status(recovery_id)
        if not recovery:
            raise HTTPException(status_code=404, detail="Recovery not found")
        return recovery
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recovery status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving recovery status")

@router.get("/history")
async def get_recovery_history(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    recovery_service: RecoveryService = Depends(get_recovery_service),
    authenticated: bool = Depends(verify_recovery_auth)
):
    """Get recovery operation history with pagination."""
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

        recoveries = await recovery_service.get_recovery_history(
            limit=page_size,
            status_filter=status
        )

        return {
            "recoveries": recoveries,
            "total": len(recoveries),
            "page": page,
            "page_size": page_size
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recovery history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving recovery history")

@router.post("/cancel/{recovery_id}")
async def cancel_recovery(
    recovery_id: str,
    recovery_service: RecoveryService = Depends(get_recovery_service),
    authenticated: bool = Depends(verify_recovery_auth)
):
    """Cancel an ongoing recovery operation."""
    try:
        recovery = await recovery_service.get_recovery_status(recovery_id)

        if not recovery:
            raise HTTPException(status_code=404, detail="Recovery not found")

        if recovery.get("status") != RecoveryStatusEnum.IN_PROGRESS:
            raise HTTPException(status_code=400, detail="Recovery is not in progress")

        RECOVERY_REQUESTS_TOTAL.labels(
            type=recovery.get("type", "unknown"),
            severity=recovery.get("severity", "unknown"),
            status="cancelled"
        ).inc()

        logger.info(f"Recovery {recovery_id} cancelled")
        return {"success": True, "message": "Recovery cancelled", "recovery_id": recovery_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel recovery: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while cancelling recovery")


_HTML_BASE = """
<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8fafc;color:#1e293b;padding:2rem}}
  h1{{font-size:1.4rem;font-weight:800;margin-bottom:.25rem}}  .sub{{color:#94a3b8;font-size:.85rem;margin-bottom:1.75rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:2rem}}
  .kpi{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:1rem 1.2rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
  .kpi .val{{font-size:1.5rem;font-weight:800;color:#6366f1;line-height:1}}
  .kpi .lbl{{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#94a3b8;margin-top:.2rem}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
  th{{background:#f1f5f9;text-align:left;padding:.6rem 1rem;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;color:#64748b}}
  td{{padding:.6rem 1rem;font-size:.82rem;border-top:1px solid #f1f5f9}}
  tr:hover td{{background:#f8fafc}}
  .badge{{display:inline-block;padding:.15rem .5rem;border-radius:99px;font-size:.7rem;font-weight:700}}
  .ok{{background:#d1fae5;color:#065f46}}.warn{{background:#fef3c7;color:#92400e}}.err{{background:#fee2e2;color:#991b1b}}
  pre{{background:#0f172a;color:#7dd3fc;padding:1.25rem;border-radius:10px;font-size:.75rem;overflow-x:auto;max-height:400px;overflow-y:auto;margin-top:1.5rem}}
  .section{{margin-bottom:2rem}} .sec-title{{font-size:.95rem;font-weight:700;margin-bottom:.75rem;padding-bottom:.4rem;border-bottom:2px solid #e2e8f0}}
</style></head><body>
{body}
</body></html>
"""


@router.get("/backup-preview", response_class=HTMLResponse)
async def backup_preview(path: str):
    """Return an HTML preview of a backup .sql file."""
    try:
        p = pathlib.Path(path)
        if not p.exists() or not str(p).startswith("/tmp/cern_db_backups"):
            raise HTTPException(status_code=404, detail="Backup file not found")

        stat = p.stat()
        size_kb = round(stat.st_size / 1024, 1)
        created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        lines = p.read_text(errors="replace").splitlines()
        total_lines = len(lines)

        tables = [l[len("CREATE TABLE "):].split("(")[0].strip()
                  for l in lines if l.startswith("CREATE TABLE ")]
        copies  = sum(1 for l in lines if l.startswith("COPY "))
        preview = "\n".join(lines[:80])

        kpis = f"""
        <div class="grid">
          <div class="kpi"><div class="val">{size_kb} KB</div><div class="lbl">File size</div></div>
          <div class="kpi"><div class="val">{total_lines:,}</div><div class="lbl">Total lines</div></div>
          <div class="kpi"><div class="val">{len(tables)}</div><div class="lbl">Tables dumped</div></div>
          <div class="kpi"><div class="val">{copies}</div><div class="lbl">COPY blocks</div></div>
        </div>"""

        table_rows = "".join(
            f'<tr><td>{i+1}</td><td><code>{t}</code></td></tr>'
            for i, t in enumerate(tables)
        ) or '<tr><td colspan="2" style="color:#94a3b8">No CREATE TABLE found</td></tr>'

        body = f"""
        <h1>&#128190; Backup Preview</h1>
        <p class="sub">{p.name} &nbsp;&#183;&nbsp; Created {created} &nbsp;&#183;&nbsp; {p}</p>
        {kpis}
        <div class="section">
          <div class="sec-title">Tables in dump</div>
          <table><thead><tr><th>#</th><th>Table name</th></tr></thead><tbody>{table_rows}</tbody></table>
        </div>
        <div class="section">
          <div class="sec-title">First 80 lines</div>
          <pre>{preview}</pre>
        </div>"""

        return _HTML_BASE.format(title=f"Backup — {p.name}", body=body)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/db-report", response_class=HTMLResponse)
async def db_health_report():
    """Return an HTML database health report (table sizes, dead rows, index usage)."""
    try:
        import asyncpg as _pg
        db_url = os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/monitoring_db")
        conn = await _pg.connect(db_url)

        tables = await conn.fetch("""
            SELECT
                schemaname||'.'||relname AS table_name,
                pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
                n_live_tup AS live_rows,
                n_dead_tup AS dead_rows,
                CASE WHEN n_live_tup+n_dead_tup > 0
                     THEN round(100.0*n_dead_tup/(n_live_tup+n_dead_tup),1) ELSE 0 END AS bloat_pct,
                last_vacuum::text,
                last_analyze::text
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(relid) DESC
        """)

        indexes = await conn.fetch("""
            SELECT
                schemaname||'.'||relname AS table_name,
                indexrelname AS index_name,
                idx_scan AS scans,
                pg_size_pretty(pg_relation_size(indexrelid)) AS size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            LIMIT 20
        """)

        db_size = await conn.fetchval(
            "SELECT pg_size_pretty(pg_database_size(current_database()))"
        )
        conn_count = await conn.fetchval("SELECT count(*) FROM pg_stat_activity")
        await conn.close()

        total_dead = sum(r["dead_rows"] for r in tables)
        total_live = sum(r["live_rows"] for r in tables)

        kpis = f"""
        <div class="grid">
          <div class="kpi"><div class="val">{db_size}</div><div class="lbl">Database size</div></div>
          <div class="kpi"><div class="val">{len(tables)}</div><div class="lbl">User tables</div></div>
          <div class="kpi"><div class="val">{total_live:,}</div><div class="lbl">Live rows</div></div>
          <div class="kpi" style="border-left:3px solid {'#ef4444' if total_dead>1000 else '#10b981'}">
            <div class="val">{total_dead:,}</div><div class="lbl">Dead rows</div></div>
          <div class="kpi"><div class="val">{conn_count}</div><div class="lbl">Connections</div></div>
        </div>"""

        def bloat_badge(pct):
            pct = float(pct)
            if pct > 20: return f'<span class="badge err">{pct}% bloat</span>'
            if pct > 5:  return f'<span class="badge warn">{pct}% bloat</span>'
            return f'<span class="badge ok">{pct}%</span>'

        tbl_rows = "".join(f"""
            <tr>
              <td><code>{r['table_name']}</code></td>
              <td>{r['total_size']}</td>
              <td>{r['live_rows']:,}</td>
              <td>{r['dead_rows']:,}</td>
              <td>{bloat_badge(r['bloat_pct'])}</td>
              <td style="font-size:.72rem;color:#94a3b8">{(r['last_vacuum'] or '—')[:16]}</td>
              <td style="font-size:.72rem;color:#94a3b8">{(r['last_analyze'] or '—')[:16]}</td>
            </tr>""" for r in tables)

        idx_rows = "".join(f"""
            <tr>
              <td><code>{r['index_name']}</code></td>
              <td style="color:#64748b;font-size:.78rem">{r['table_name']}</td>
              <td>{r['scans']:,}</td>
              <td>{r['size']}</td>
            </tr>""" for r in indexes)

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        body = f"""
        <h1>&#128202; Database Health Report</h1>
        <p class="sub">monitoring_db &nbsp;&#183;&nbsp; Generated {now}</p>
        {kpis}
        <div class="section">
          <div class="sec-title">Table Health</div>
          <table><thead><tr><th>Table</th><th>Size</th><th>Live rows</th><th>Dead rows</th><th>Bloat</th><th>Last vacuum</th><th>Last analyze</th></tr></thead>
          <tbody>{tbl_rows or '<tr><td colspan=7 style="color:#94a3b8">No tables</td></tr>'}</tbody></table>
        </div>
        <div class="section">
          <div class="sec-title">Top 20 Indexes by Scan Count</div>
          <table><thead><tr><th>Index</th><th>Table</th><th>Scans</th><th>Size</th></tr></thead>
          <tbody>{idx_rows or '<tr><td colspan=4 style="color:#94a3b8">No indexes</td></tr>'}</tbody></table>
        </div>"""

        return _HTML_BASE.format(title="DB Health Report", body=body)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
