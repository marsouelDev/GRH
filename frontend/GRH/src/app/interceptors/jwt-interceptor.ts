import { HttpInterceptorFn } from '@angular/common/http';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  //recupere le token stokee lors du login
    const token = localStorage.getItem('access_token');

  if(token){
    req = req.clone({
  setHeaders:{
    Authorization:`Bearer ${token}`
  }
});
}
  return next(req);
};
