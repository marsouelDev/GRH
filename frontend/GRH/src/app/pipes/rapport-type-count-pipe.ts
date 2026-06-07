import { Pipe, PipeTransform } from '@angular/core';
import { RapportModel, TypeRapport } from '../models/rapport';

@Pipe({
  name: 'rapportTypeCount',
  standalone: true,
})
export class RapportTypeCountPipe implements PipeTransform {
  transform(rapports: RapportModel[], type: TypeRapport | string): number {
    if (!rapports?.length || !type) {
      return rapports?.length || 0;
    }
    return rapports.filter((rapport) => rapport.type_rapport === type).length;
  }
}
