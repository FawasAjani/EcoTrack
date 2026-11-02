
import { Routes } from '@angular/router';

import { Login } from './login/login';
import { Signup } from './signup/signup';
import { ResetPassword } from './reset-password/reset-password';
import { Home } from './home/home';
import { ActivityTracker } from './activity-tracker/activity-tracker';
import { WeeklySummary } from './weekly-summary/weekly-summary';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'signup', component: Signup },
  { path: 'reset-password', component: ResetPassword },
  { path: 'home', component: Home },
  { path: 'activity-tracker', component: ActivityTracker },
  { path: 'weekly-summary', component: WeeklySummary },
  { path: '', redirectTo: 'login', pathMatch: 'full' }
];
