import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import { environment } from '../../environments/environment';

@Injectable()
export class RequestService {
  public baseUrl: string;
  public headers: HttpHeaders;
  private api_key: string;
  private authorization : string;

  constructor(private http: HttpClient) {
    let access_token = '';
    this.baseUrl = environment['api_url'];
    // this.api_key = environment['api_key'];
    // this.authorization = environment['api_authorization_token']
   }

   getService(url: string, params?: HttpParams):  Observable<any> {
    let header = this.getHeader();
    // console.log(header);
    return this.http
      .get(`${this.baseUrl}${url}`, {params})
      .map(this.extractData)
      .catch(this.handleError);
  }

  postService(url: string, body: Object, params?: HttpParams): Observable<any> {
    let header = this.getHeader();
    return this.http
      .post(`${this.baseUrl}${url}`, body, {headers: header} )
      .map(this.extractData)
      .catch(this.handleError);
  }

  putService(url: string,body: Object, params?: HttpParams) {
    let header = this.getHeader();

    return this.http
      .put(`${this.baseUrl}${url}`, body,  {headers: header})
      .map(this.extractData)
      .catch(this.handleError);
  }

  patchService(url: string, body: Object, params?: HttpParams) {
    let header = this.getHeader();

    return this.http
      .patch(`${this.baseUrl}${url}`, body,  {headers: header})
      .map(this.extractData)
      .catch(this.handleError);
  }

  deleteService(url: string, params?: HttpParams) {
    let header = this.getHeader();
    return this.http
      .delete(`${this.baseUrl}${url}`, {headers: header, params})
      .map(this.extractData)
      .catch(this.handleError);
  }

  private extractData(res: Response) {
    if (res.status === 401 || res.status === 422) {
      alert(res['status_message']);
    }
    return res || {};
  }

  private handleError(error: any, data: any)
  {
    let errMsg = (error.message) ? error.message : (error.status ? `${error.status} - ${error.statusText}` : 'Server error');
    if (error.status === 405 || error.status === 401)
    {
      errMsg = error.error.status_message;
    }
    return Observable.throw(errMsg);
  }

  private getHeader(): HttpHeaders
  {
    const header = new HttpHeaders()
    //  .set('ApiKey', this.api_key)
    //  .set('Authorization', 'Basic ' + this.authorization);

    return header;
  }
}
