import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-tooltip',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="tooltip" [class]="'tooltip-' + position">
      {{ content }}
    </div>
  `,
  styleUrls: ['./tooltip.component.scss']
})
export class TooltipComponent {
  @Input() content: string = '';
  @Input() position: 'top' | 'bottom' | 'left' | 'right' = 'top';
}
