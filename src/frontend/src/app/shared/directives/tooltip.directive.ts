import { Directive, Input, ElementRef, Renderer2, ComponentRef, ViewContainerRef, ComponentFactoryResolver } from '@angular/core';
import { TooltipComponent } from '../components/tooltip/tooltip.component';

@Directive({
  selector: '[tooltip]',
  standalone: true
})
export class TooltipDirective {
  @Input() tooltip: string = '';
  @Input() tooltipPosition: 'top' | 'bottom' | 'left' | 'right' = 'top';
  @Input() tooltipDelay: number = 300;

  private tooltipRef: ComponentRef<TooltipComponent> | null = null;
  private timeoutId: any;

  constructor(
    private elementRef: ElementRef,
    private renderer: Renderer2,
    private viewContainerRef: ViewContainerRef
  ) {}

  @Input()
  set tooltipContent(content: string) {
    this.tooltip = content;
  }

  ngOnInit(): void {
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    const element = this.elementRef.nativeElement;
    
    this.renderer.listen(element, 'mouseenter', () => {
      this.showTooltip();
    });

    this.renderer.listen(element, 'mouseleave', () => {
      this.hideTooltip();
    });

    this.renderer.listen(element, 'focus', () => {
      this.showTooltip();
    });

    this.renderer.listen(element, 'blur', () => {
      this.hideTooltip();
    });
  }

  private showTooltip(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }

    this.timeoutId = setTimeout(() => {
      if (this.tooltip && !this.tooltipRef) {
        this.tooltipRef = this.viewContainerRef.createComponent(TooltipComponent);
        this.tooltipRef.instance.content = this.tooltip;
        this.tooltipRef.instance.position = this.tooltipPosition;
        this.updateTooltipPosition();
      }
    }, this.tooltipDelay);
  }

  private hideTooltip(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }

    if (this.tooltipRef) {
      this.tooltipRef.destroy();
      this.tooltipRef = null;
    }
  }

  private updateTooltipPosition(): void {
    if (!this.tooltipRef) return;

    const hostRect = this.elementRef.nativeElement.getBoundingClientRect();
    const tooltipElement = this.tooltipRef.location.nativeElement;
    const tooltipRect = tooltipElement.getBoundingClientRect();

    let top = 0;
    let left = 0;

    switch (this.tooltipPosition) {
      case 'top':
        top = hostRect.top - tooltipRect.height - 8;
        left = hostRect.left + (hostRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = hostRect.bottom + 8;
        left = hostRect.left + (hostRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = hostRect.top + (hostRect.height - tooltipRect.height) / 2;
        left = hostRect.left - tooltipRect.width - 8;
        break;
      case 'right':
        top = hostRect.top + (hostRect.height - tooltipRect.height) / 2;
        left = hostRect.right + 8;
        break;
    }

    this.renderer.setStyle(tooltipElement, 'top', `${top}px`);
    this.renderer.setStyle(tooltipElement, 'left', `${left}px`);
  }
}
