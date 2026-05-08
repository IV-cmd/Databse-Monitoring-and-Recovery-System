import { Directive, ElementRef, Output, EventEmitter, OnDestroy } from '@angular/core';
import { fromEvent, Subscription } from 'rxjs';

@Directive({
  selector: '[clickOutside]',
  standalone: true
})
export class ClickOutsideDirective implements OnDestroy {
  @Output() clickOutside = new EventEmitter<void>();
  
  private subscription: Subscription;

  constructor(private elementRef: ElementRef) {
    this.subscription = fromEvent(document, 'click').subscribe((event: Event) => {
      this.onClickOutside(event);
    });
  }

  private onClickOutside(event: Event): void {
    const targetElement = event.target as HTMLElement;
    const hostElement = this.elementRef.nativeElement as HTMLElement;
    
    const clickedInside = hostElement.contains(targetElement);
    
    if (!clickedInside) {
      this.clickOutside.emit();
    }
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }
}
