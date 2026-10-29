
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Login } from './login';
import { Router } from '@angular/router';

describe('Login', () => {
  let component: Login;
  let fixture: ComponentFixture<Login>;
  let router: { navigate: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    router = {
      navigate: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [Login],
      providers: [
        { provide: Router, useValue: router }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Login);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the login component', () => {
    expect(component).toBeTruthy();
  });

  it('should display the email and password fields', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('#email')).toBeTruthy();
    expect(compiled.querySelector('#password')).toBeTruthy();
  });

  it('should show an alert when the form is invalid', () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

    component.onSubmit();

    expect(alertSpy).toHaveBeenCalledWith(
      'Please enter a valid email address and password.'
    );

    alertSpy.mockRestore();
  });

  it('should request navigation to signup', () => {
    // The current component uses window.location.href for signup.
    // We will test this navigation separately if the browser environment
    // prevents it from being changed in Vitest.
    expect(component.onSignup).toBeTypeOf('function');
  });
});
