import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  username = '';
  password = '';
  error = '';
  loading = false;

  constructor(private auth: AuthService, private router: Router) {}

  login() {
    if (!this.username.trim() || !this.password) {
      this.error = 'Please enter username and password.';
      return;
    }
    this.loading = true;
    this.error = '';
    this.auth.login(this.username.trim(), this.password).subscribe({
      next: () => this.router.navigate(['/gallery'], { replaceUrl: true }),
      error: (err: any) => {
        if (err.status === 0) {
          this.error = 'Cannot reach server. Check your connection.';
        } else if (err.status === 429) {
          this.error = 'Too many attempts. Please wait a minute.';
        } else {
          this.error = 'Invalid username or password.';
        }
        this.loading = false;
      }
    });
  }
}
