import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { BrowserModule } from '@angular/platform-browser';

// Shared Components
import { 
  HeaderComponent,
  SidebarComponent,
  TableComponent,
  CardComponent,
  SearchComponent,
  ChartComponent,
  ErrorModalComponent,
  LoadingComponent,
  ToastComponent,
  BadgeComponent,
  TooltipComponent
} from './components';

// Shared Directives
import { 
  ClickOutsideDirective,
  TooltipDirective,
  AutofocusDirective
} from './directives';

// Shared Pipes
import { 
  DateFormatPipe,
  FileSizePipe,
  TruncatePipe,
  SafeHtmlPipe
} from './pipes';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule,
    BrowserModule
  ],
  exports: [
    CommonModule
  ]
})
export class SharedModule {
  static forRoot() {
    return SharedModule;
  }
}
