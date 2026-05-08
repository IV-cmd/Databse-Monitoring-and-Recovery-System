import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  status: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp?: string;
}

export interface MetricsResponse {
  timestamp: string;
  current: {
    database: {
      connections: number;
      cpu_usage: number;
      memory_usage: number;
      disk_usage: number;
    };
    system: {
      cpu_usage: number;
      memory_usage: number;
      disk_usage: number;
      connections: number;
    };
  };
}

export interface RecoveryResponse {
  success: boolean;
  recovery_id?: string;
  message?: string;
  status?: string;
  recovery_record?: any;
}

export interface RecoveryRequest {
  type: string;
  reason: string;
  severity: string;
}

const API_BASE = 'http://localhost:8000/api/v1';

export class ApiService {
  private http = inject(HttpClient);

  // Health endpoints
  getHealth(): Observable<HealthResponse> {
    console.log('🔍 ApiService: Making health check request to:', `${API_BASE}/health/`);
    return this.http.get<HealthResponse>(`${API_BASE}/health/`).pipe(
      catchError(handleError)
    );
  }

  getDetailedHealth(): Observable<any> {
    return this.http.get(`${API_BASE}/health/detailed`).pipe(
      catchError(handleError)
    );
  }

  // Metrics endpoints
  getCurrentMetrics(): Observable<MetricsResponse> {
    console.log('📊 ApiService: Making metrics request to:', `${API_BASE}/metrics/current`);
    return this.http.get<MetricsResponse>(`${API_BASE}/metrics/current`).pipe(
      catchError(handleError)
    );
  }

  queryMetrics(params?: any): Observable<any> {
    return this.http.get(`${API_BASE}/metrics/query`, { params }).pipe(
      catchError(handleError)
    );
  }

  getDatabaseMetrics(): Observable<any> {
    return this.http.get(`${API_BASE}/metrics/database`).pipe(
      catchError(handleError)
    );
  }

  getSystemMetrics(): Observable<any> {
    return this.http.get(`${API_BASE}/metrics/system`).pipe(
      catchError(handleError)
    );
  }

  // Monitoring endpoints
  getMonitoringStatus(): Observable<any> {
    return this.http.get(`${API_BASE}/monitoring/status`).pipe(
      catchError(handleError)
    );
  }

  getMonitoringMetrics(): Observable<any> {
    return this.http.get(`${API_BASE}/monitoring/metrics`).pipe(
      catchError(handleError)
    );
  }

  getMonitoringAlerts(): Observable<any> {
    return this.http.get(`${API_BASE}/monitoring/alerts`).pipe(
      catchError(handleError)
    );
  }

  getMonitoringData(limit: number = 50): Observable<any> {
    return this.http.get(`${API_BASE}/monitoring/data`, { params: { limit } }).pipe(
      catchError(handleError)
    );
  }

  storeMonitoringData(data: any): Observable<any> {
    return this.http.post(`${API_BASE}/monitoring/data`, data).pipe(
      catchError(handleError)
    );
  }

  // Recovery endpoints
  startRecovery(request: RecoveryRequest): Observable<RecoveryResponse> {
    return this.http.post<RecoveryResponse>(`${API_BASE}/recovery/start`, request).pipe(
      catchError(handleError)
    );
  }

  getRecoveryStatus(recoveryId: string): Observable<any> {
    return this.http.get(`${API_BASE}/recovery/status/${recoveryId}`).pipe(
      catchError(handleError)
    );
  }

  getRecoveryHistory(params?: any): Observable<any> {
    return this.http.get(`${API_BASE}/recovery/history`, { params }).pipe(
      catchError(handleError)
    );
  }

  cancelRecovery(recoveryId: string): Observable<any> {
    return this.http.post(`${API_BASE}/recovery/cancel/${recoveryId}`, {}).pipe(
      catchError(handleError)
    );
  }
}

function handleError(error: any): Observable<never> {
  let errorMessage = 'An error occurred';
  
  if (error.error instanceof ErrorEvent) {
    errorMessage = `Error: ${error.error.message}`;
  } else {
    errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
  }
  
  console.error('API Error:', errorMessage, error);
  return throwError(() => errorMessage);
}
