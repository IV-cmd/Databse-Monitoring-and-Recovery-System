# Database Monitoring & Auto-Recovery System

A production-grade PostgreSQL monitoring and auto-recovery system built for CERN database operations, featuring an Angular frontend, FastAPI backend, and a full observability stack with Prometheus, Grafana, and AlertManager.

## 🚀 Features

### Core Monitoring
- **Real-time Health Checks** — continuous monitoring of PostgreSQL primary and replica instances
- **Advanced Metrics** — connection tracking, query performance, replication lag, resource utilisation
- **Prometheus Integration** — full metrics export with pre-configured alert rules
- **Grafana Dashboards** — provisioned PostgreSQL dashboard with auto-loaded datasource

### Auto-Recovery
- **Intelligent Failure Detection** — automatic detection of database failures and performance issues
- **Automated Recovery** — self-healing with configurable retry limits and cooldown
- **Recovery History** — complete audit trail of all recovery actions with timestamps

### Alerting
- **AlertManager** — fully configured routing, inhibition rules, and receiver groups
- **Slack / Email / SMS Integration** — multi-channel alert delivery configurable from the UI
- **Multi-level Alerts** — critical, warning, and informational alert categories
- **Alert Cooldown** — configurable cooldown periods to prevent alert spam

### Angular Frontend
- **Dashboard** — live system overview with real-time metric cards, status indicators, and auto-refresh
- **Monitoring Page** — detailed metrics view for CPU, memory, disk, connections, and replication
- **Recovery Page** — manual recovery triggers, status tracking, and history log
- **Settings** — fully redesigned settings with sidebar navigation across four sections:
  - **System** — environment picker (dev/staging/prod), log-level pills, debug/maintenance toggles, session timeout, timezone, security limits
  - **Database** — masked URL fields with show/hide, live connection test against the health API, SSL toggle with cert path fields, pool sliders
  - **Monitoring** — collection interval slider, auto-recovery toggle, visual 3-zone threshold bars (CPU / Memory / Disk), DB limits
  - **Notifications** — collapsible provider cards (Email, Slack, SMS) with test buttons, severity chip selector, cooldown slider

### Settings UX
- `localStorage` persistence — settings survive page refresh
- Unsaved-changes badge — visible in the header when the form is dirty
- Toast notifications — slide-in feedback on save
- `⌘S` / `Ctrl+S` keyboard shortcut to save (System Settings)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────────────┐
│  Angular App    │    │   FastAPI       │    │  PostgreSQL Primary      │
│  (Port 4200)    │◄──►│   (Port 8000)   │◄──►│  (Port 5432)             │
└─────────────────┘    └─────────────────┘    └──────────────────────────┘
                                │                        │
                                │              ┌──────────────────────────┐
                                │              │  PostgreSQL Replica       │
                                │              │  (Port 5433)              │
                                │              └──────────────────────────┘
                                ▼
                       ┌─────────────────┐
                       │   Prometheus    │
                       │   (Port 9090)   │
                       └─────────────────┘
                                │
                      ┌─────────┴──────────┐
                      ▼                    ▼
             ┌─────────────────┐  ┌─────────────────┐
             │   Grafana       │  │  AlertManager   │
             │   (Port 3000)   │  │   (Port 9093)   │
             └─────────────────┘  └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** — modern async Python web framework
- **PostgreSQL** — primary database with streaming replication
- **AsyncPG** — high-performance async PostgreSQL driver
- **Prometheus Client** — metrics instrumentation

### Frontend
- **Angular 17** — standalone components, feature-module routing
- **SCSS** — custom design system with CSS variables and shared tokens
- **RxJS** — reactive data streams for live metric polling
- **Angular HttpClient** — REST API integration

### Observability Stack
- **Prometheus** — metrics collection, storage, and alerting (`config/prometheus/prometheus.yml`)
- **AlertManager** — alert routing and notification delivery (`config/prometheus/alertmanager.yml`)
- **Alert Rules** — pre-configured rules for DB down, high connections, slow queries, replication lag (`config/prometheus/alert_rules.yml`)
- **Grafana** — advanced dashboards with auto-provisioned datasource and PostgreSQL dashboard (`config/grafana/`)

### Infrastructure
- **Docker** — containerisation for all services
- **Docker Compose** — full-stack orchestration

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for local frontend development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/IV-cmd/Databse-Monitoring-and-Recovery-System.git
cd Databse-Monitoring-and-Recovery-System
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the full stack**
```bash
docker-compose up -d
```

4. **Access the services**

| Service | URL | Credentials |
|---|---|---|
| Angular Frontend | http://localhost:4200 | — |
| API Documentation | http://localhost:8000/docs | — |
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | — |
| AlertManager | http://localhost:9093 | — |

## � Project Structure

```
cern_db/
├── config/
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   └── postgres-dashboard.json       # Pre-built PostgreSQL dashboard
│   │   └── provisioning/
│   │       ├── dashboards/dashboard.yml       # Dashboard auto-provisioning
│   │       └── datasources/prometheus.yml     # Prometheus datasource config
│   └── prometheus/
│       ├── prometheus.yml                     # Scrape config & targets
│       ├── alert_rules.yml                    # Alerting rules
│       └── alertmanager.yml                   # Routing & receiver config
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/routes/                    # FastAPI route handlers
│   │   │   ├── core/                          # Monitoring & recovery engine
│   │   │   └── models/                        # Pydantic data models
│   │   └── main.py                            # Application entry point
│   └── frontend/
│       └── src/app/
│           ├── core/services/                 # API service layer
│           ├── features/
│           │   ├── dashboard/                 # Live metrics dashboard
│           │   ├── monitoring/                # Detailed monitoring view
│           │   ├── recovery/                  # Recovery management
│           │   └── settings/
│           │       └── components/
│           │           ├── settings-shell/    # Sidebar navigation shell
│           │           ├── system-settings/
│           │           ├── database-settings/
│           │           ├── monitoring-settings/
│           │           └── notification-settings/
│           └── shared/                        # Shared components & types
├── docker/                                    # Dockerfiles per service
├── docker-compose.yml
└── .env.example
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://admin:admin123@postgres-primary:5432/monitoring_db
REPLICA_URL=postgresql://admin:admin123@postgres-replica:5432/monitoring_db

# Monitoring
MONITOR_INTERVAL=30
HEALTH_CHECK_INTERVAL=10
AUTO_RECOVERY_ENABLED=true

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ALERT_COOLDOWN=300

# Thresholds
MAX_CONNECTIONS=100
SLOW_QUERY_THRESHOLD=1.0
CPU_THRESHOLD=80.0
REPLICATION_LAG_THRESHOLD=10.0
```

### Prometheus & AlertManager

Configurations are in `config/prometheus/`:
- **`prometheus.yml`** — scrape intervals, targets (FastAPI, PostgreSQL exporter)
- **`alert_rules.yml`** — rules for DB down, high connections, slow queries, replication lag, disk usage
- **`alertmanager.yml`** — routing tree, Slack/email receivers, inhibition rules

### Grafana Auto-Provisioning

On first startup, Grafana automatically loads:
- **Datasource**: Prometheus at `http://prometheus:9090` (`config/grafana/provisioning/datasources/prometheus.yml`)
- **Dashboard**: PostgreSQL overview (`config/grafana/dashboards/postgres-dashboard.json`)

## 📈 API Endpoints

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/detailed` | Full health status |
| GET | `/api/v1/health/dependencies` | PostgreSQL + service dependency status |
| POST | `/api/v1/health/check` | Force health check |

### Monitoring
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/monitoring/status` | Monitoring engine status |
| GET | `/api/v1/monitoring/metrics` | Current live metrics |
| GET | `/api/v1/monitoring/database/stats` | Database statistics |

### Recovery
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/recovery/status` | Recovery engine status |
| POST | `/api/v1/recovery/trigger` | Manual recovery trigger |
| GET | `/api/v1/recovery/history` | Recovery action history |

## 🛠️ Local Development

```bash
# Backend
cd src/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd src/frontend
npm install
ng serve               # serves at http://localhost:4200
```

## 🧪 Testing

```bash
# Simulate a database failure
curl -X POST http://localhost:8000/api/v1/monitoring/test/failure \
  -H "Content-Type: application/json" \
  -d '{"db_type": "primary"}'

# Test the alert pipeline
curl -X POST http://localhost:8000/api/v1/recovery/test-alert \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "database_down", "message": "Test alert"}'
```

## 📊 Performance

| Resource | Overhead |
|---|---|
| CPU | < 5% |
| Memory | < 500 MB additional |
| Minimum hardware | 2 cores, 4 GB RAM, 20 GB disk |
| Recommended hardware | 4 cores, 8 GB RAM, 50 GB disk |

## 🔒 Security

- Database credentials managed via environment variables
- SSL/TLS configurable per connection (Database Settings UI)
- API endpoints secured with configurable authentication
- Internal service communication stays within Docker network

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a pull request

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

**Built for CERN Database Operations** 🚀
