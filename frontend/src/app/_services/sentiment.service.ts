import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SentimentService {
  name: string;
  value: number;
  
  constructor() { }
}


@Injectable()
export class Service {
    countriesData: Object = {};
    getCountriesData(): Object {
        return this.countriesData;
    }
    setCountriesData(data: Object) {
        this.countriesData = data;
    }

  getPieChartConfig(chartData: Object): Object {
      return {

          dataSource: chartData,
          series: [{
              valueField: "value",
              argumentField: "name",
              label: {
                  visible: true,
                  connector: {
                      visible: true,
                      width: 1
                  },
                  customizeText: function(pointInfo) {
                      return pointInfo.argument[0].toUpperCase()
                          + pointInfo.argument.slice(1)
                          + ": " + pointInfo.value + "";
                  }
              }
          }],
          legend: {
              visible: false
          },
          palette: ['#fd2f24', '#7ac419', '#ffd901']
      };
  }
}
