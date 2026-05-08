// Shared Components Barrel Export
// Clean Architecture: Single Responsibility, Type Safety, Reusability

// Core Components
export { HeaderComponent } from './header/header.component';
export { SidebarComponent } from './sidebar/sidebar.component';

// Data Display Components
export { TableComponent, TableConfig } from './table/table.component';
export { CardComponent, CardConfig } from './card/card.component';
export { SearchComponent, SearchConfig } from './search/search.component';
export { ChartComponent, ChartConfig, ChartDataPoint } from './chart/chart.component';

// Feedback Components
export { ErrorModalComponent, ErrorModalData } from './error-modal/error-modal.component';
export { LoadingComponent, LoadingConfig } from './loading/loading.component';
export { ToastComponent, ToastConfig } from './toast/toast.component';
export { BadgeComponent, BadgeConfig } from './badge/badge.component';

// UI Components
export { TooltipComponent } from './tooltip/tooltip.component';

// Shared Types
export * from '../types';
