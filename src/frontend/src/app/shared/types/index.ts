// Shared Types and Interfaces

export interface ApiResponse<T = any> {
  data: T;
  message: string;
  status: number;
  success: boolean;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export interface FilterConfig {
  field: string;
  value: any;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'startsWith';
}

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  type?: 'text' | 'number' | 'date' | 'boolean';
}

export interface TableConfig {
  columns: TableColumn[];
  pagination?: PaginationInfo;
  sort?: SortConfig;
  filters?: FilterConfig[];
}

export interface NotificationConfig {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  showClose?: boolean;
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface FormState {
  isSubmitting: boolean;
  errors: ValidationError[];
  touched: Record<string, boolean>;
}

export interface MenuItem {
  label: string;
  icon?: string;
  route?: string;
  children?: MenuItem[];
  badge?: string | number;
}

export interface BreadcrumbItem {
  label: string;
  route?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
  lastLogin?: string;
  isActive: boolean;
}

export interface DatabaseConnection {
  host: string;
  port: number;
  database: string;
  username: string;
  password?: string;
  ssl: boolean;
  connectionTimeout: number;
}

export interface MonitoringAlert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  value?: number;
  threshold?: number;
  resolved: boolean;
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  timestamp: string;
  metrics: {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
  };
  services: Array<{
    name: string;
    status: 'running' | 'stopped' | 'error';
    uptime?: number;
  }>;
}
