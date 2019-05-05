import { Component, OnInit } from '@angular/core';
import { RequestService } from '../_services/request.service';
import { Trends } from '../_models/trends';
import { Router } from '@angular/router';
import { Service } from '../_services/sentiment.service';
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  public trends: Array<Trends> = [];
  constructor(private service: Service, private router: Router, private requestService: RequestService) { }

  ngOnInit() {
    this.requestService.getService('trends')
        .subscribe(
        result => {
          let trends_result = result['trends'][0].trends;
          let i = 0;
          trends_result.forEach(element => {
            var english = /^(?=.*[a-zA-Z\d].*)[a-zA-Z\d!@#$%&*]{7,}$/;
            if(english.test(element.name) && i < 10) {
              let trend = new Trends();
              trend = element;
              this.trends.push(trend);
              i++;
            }
          });
        },
        error => {
          console.log(error);
        }
      );
  }

  searchTrendsAnalysis(trend: string) {
      trend = trend.replace(/[^a-zA-Z ]/g, "");
      this.requestService.getService('twitter/' + trend)
        .subscribe(
          result => {
            console.log(result);
            this.service.setCountriesData(result);
            this.router.navigate(['analysis']);
          },
          error => {
            console.log(error);
          }
        );
  }
}
