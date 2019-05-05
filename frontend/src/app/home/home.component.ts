import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import {Router} from '@angular/router';
import { SentimentService, Service } from '../_services/sentiment.service' 
import { RequestService } from '../_services/request.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  public search_keyword: string = '';
  public showLoader = false;

  constructor(private service: Service, private router: Router, private requestService: RequestService) { }

  ngOnInit() {
  }

  search_query() {
    if (this.search_keyword != '') {
      this.showLoader = true;
      this.requestService.getService('twitter/' + this.search_keyword)
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
}
