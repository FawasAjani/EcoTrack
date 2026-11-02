
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Login } from './login';
import { Router } from '@angular/router';

describe('Login', () => {
  let component: Login;
  let fixture: ComponentFixture<Login>;
  let router: { navigate: ReturnType<typeof vi.fn> };

  // Configure the testing environment and create the Login component.
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

  // Verify that the Login component is created successfully.
  it('should create the login component', () => {
    expect(component).toBeTruthy();
  });

  // Verify that the email and password input fields are displayed.
  it('should display the email and password fields', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('#email')).toBeTruthy();
    expect(compiled.querySelector('#password')).toBeTruthy();
  });

  // Verify that invalid form input produces the expected validation message.
  it('should show a validation message when the form is invalid', async () => {
    await component.onSubmit();

    expect(component.message).toBe(
      'Please enter a valid email address and password.'
    );
    expect(component.messageType).toBe('error');
    expect(component.email.touched).toBe(true);
    expect(component.password.touched).toBe(true);
  });

  // Verify that the signup navigation method is available.
  it('should request navigation to signup', () => {
    component.onSignup();

    expect(router.navigate).toHaveBeenCalledWith(['/signup']);
  });
});
