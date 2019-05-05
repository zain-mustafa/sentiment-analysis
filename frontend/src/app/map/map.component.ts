import { Component, OnInit, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import DxPieChart from 'devextreme/viz/pie_chart';
import * as mapsData from 'devextreme/dist/js/vectormap-data/world.js';
import { SentimentService, Service } from '../_services/sentiment.service' 
import {Router, ActivatedRoute} from '@angular/router';


@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss']
})
export class MapComponent implements OnInit {

  worldMap: any = mapsData.world;
  gdpData: Object = {};
  toolTipData: Object = {};
  pipe: any = new DecimalPipe("en-US");

  constructor(private service: Service) {
    this.gdpData = service.getCountriesData();
    this.customizeTooltip = this.customizeTooltip.bind(this);
    this.customizeLayers = this.customizeLayers.bind(this);
    this.tooltipShown = this.tooltipShown.bind(this);
  }

  ngOnInit() {
  }
  
  customizeTooltip(arg) {
    let countryGDPData = this.gdpData[arg.attribute("name")];
    let total = countryGDPData && countryGDPData.total;
    if(total != 200) {
      total = total/100;
      total = total.toFixed(2);
      let totalMarkupString = total ? "<div id='nominal' >Sentiment Polarity: " + total + " %</div>" : "";
      let node = "<div #gdp><h4>" + arg.attribute("name") + "</h4>" +
      totalMarkupString +
      "<div id='gdp-sectors'></div></div>";
      return {
        html: node
      };
    }
  }

  customizeLayers(elements) {
    elements.forEach((element) => {
      let countryGDPData = this.gdpData[element.attribute("name")];
      element.attribute("total", countryGDPData && countryGDPData.total || 0);
    });
  }

  customizeText = (arg) => {
    if(arg.start == -100)
      return this.pipe.transform(-1, "1.0-0") + " to " + this.pipe.transform(0, "1.0-0") + " => Negative";
    else if(arg.start == 0)
      return  "0 => Neutral";
    else if(arg.start == 100)
      return this.pipe.transform(0, "1.0-0") + " to " + this.pipe.transform(1, "1.0-0") + " => Positive";
  } 

  tooltipShown(e) {
    let name = e.target.attribute("name"),
      gdpData: SentimentService[] = this.gdpData[name] ? [
        { name: "neutral", value: this.gdpData[name].neutral },
        { name: "negative", value: this.gdpData[name].negative },
        { name: "positive", value: this.gdpData[name].positive }
      ] : null,
      container = (<any> document).getElementById("gdp-sectors");

    if (this.gdpData[name].negative) {
      new DxPieChart(container, this.service.getPieChartConfig(gdpData));
    } else {
      // container.textContent = "No economic development data";
      new DxPieChart(container, this.service.getPieChartConfig(gdpData));
    }
  }
}
