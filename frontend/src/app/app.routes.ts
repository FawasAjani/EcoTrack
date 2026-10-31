import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Signup } from './signup/signup';
import { ResetPassword } from './reset-password/reset-password';
import { Home } from './home/home';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'signup', component: Signup },
  { path: 'reset-password', component: ResetPassword },
  { path: 'home', component: Home },
  { path: '', redirectTo: 'login', pathMatch: 'full' }
];