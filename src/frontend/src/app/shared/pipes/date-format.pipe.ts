import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'dateFormat',
  standalone: true
})
export class DateFormatPipe implements PipeTransform {
  transform(value: string | Date, format: string = 'MM/DD/YYYY'): string {
    if (!value) return '';

    const date = typeof value === 'string' ? new Date(value) : value;
    
    if (isNaN(date.getTime())) return '';

    const day = date.getDate();
    const month = date.getMonth() + 1;
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const seconds = date.getSeconds();

    return format
      .replace('DD', day.toString().padStart(2, '0'))
      .replace('MM', month.toString().padStart(2, '0'))
      .replace('YYYY', year.toString())
      .replace('HH', hours.toString().padStart(2, '0'))
      .replace('mm', minutes.toString().padStart(2, '0'))
      .replace('ss', seconds.toString().padStart(2, '0'))
      .replace('D', day.toString())
      .replace('M', month.toString())
      .replace('YY', year.toString().slice(-2))
      .replace('H', hours.toString())
      .replace('m', minutes.toString())
      .replace('s', seconds.toString());
  }
}
