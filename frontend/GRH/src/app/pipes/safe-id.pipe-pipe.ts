import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'safeId',
  standalone: true,
})
export class SafeIdPipe implements PipeTransform {
 
  transform(value: unknown): number | null {
    if (typeof value === 'number' && value > 0) {
      return value;
    }
    if (typeof value === 'string') {
      const num = Number(value);
      return num > 0 ? num : null;
    }
    return null;
  }
}