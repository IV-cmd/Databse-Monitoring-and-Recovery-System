import { Routes } from '@angular/router';

// Shared Routes -主要用于懒加载共享组件的路由配置
// 这些路由通常不会直接访问，而是作为其他模块的子路由使用

export const SHARED_ROUTES: Routes = [
  // 共享组件通常不需要直接路由
  // 它们通过其他模块的 RouterModule.forChild() 导入
  // 或者在使用它们的组件中直接使用
];

// 共享组件常量 - 用于其他模块导入
export const SHARED_COMPONENTS = {
  HEADER: 'app-header',
  SIDEBAR: 'app-sidebar',
  TABLE: 'app-table',
  CARD: 'app-card',
  SEARCH: 'app-search',
  CHART: 'app-chart',
  ERROR_MODAL: 'app-error-modal',
  LOADING: 'app-loading',
  TOAST: 'app-toast',
  BADGE: 'app-badge'
};
