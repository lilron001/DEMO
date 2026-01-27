# views/auth_pages.py
"""
This module serves as a backward compatibility layer for authentication pages.
The actual implementations are now in separate modules:
- login_page.py: LoginPage class
- signup_page.py: SignupPage class
- forgot_password_page.py: ForgotPasswordPage class
"""

from .login_page import LoginPage
from .signup_page import SignupPage
from .forgot_password_page import ForgotPasswordPage

__all__ = ['LoginPage', 'SignupPage', 'ForgotPasswordPage']
