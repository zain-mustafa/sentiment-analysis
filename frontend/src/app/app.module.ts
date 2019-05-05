import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { DxVectorMapModule, DxPieChartModule } from 'devextreme-angular';
import { HomeComponent } from './home/home.component';
import { MapComponent } from './map/map.component';
import { SentimentService, Service } from './_services/sentiment.service';
import { RequestService } from './_services/request.service';
import { SidebarComponent } from './sidebar/sidebar.component'
import { HttpClientModule} from '@angular/common/http';
import { HttpModule } from '@angular/http';
import { FormsModule }   from '@angular/forms';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    MapComponent,
    SidebarComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    DxVectorMapModule,
    DxPieChartModule,
    HttpClientModule,
    HttpModule,
    FormsModule,
  ],
  providers: [Service, SentimentService, RequestService],
  bootstrap: [AppComponent]
})
export class AppModule { }
