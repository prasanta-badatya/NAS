import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, tap } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private _user = new BehaviorSubject<any>(null);
  user$ = this._user.asObservable();

  constructor(private api: ApiService, private router: Router) {
    const stored = localStorage.getItem('user');
    if (stored) this._user.next(JSON.parse(stored));
  }

  get isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  login(username: string, password: string) {
    return this.api.login({ username, password }).pipe(
      tap((res: any) => {
        localStorage.setItem('token', res.token);
        localStorage.setItem('user', JSON.stringify(res.user));
        this._user.next(res.user);
      })
    );
  }

  logout() {
    // Always clear local state regardless of API result
    const clear = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this._user.next(null);
      this.router.navigate(['/login']);
    };
    this.api.logout().subscribe({ next: clear, error: clear });
  }
}
