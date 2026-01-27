# utils/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random
import string
from datetime import datetime, timedelta
import logging
import threading

logger = logging.getLogger(__name__)

class EmailService:
    """Handle email sending and verification"""
    
    def __init__(self):
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.sender_email = os.environ.get("SENDER_EMAIL", "your_email@gmail.com")
        self.sender_password = os.environ.get("SENDER_PASSWORD", "your_app_password")
        self.verification_codes = {}  # Store codes temporarily
    
    def generate_verification_code(self, length=6):
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_email(self, recipient_email, username):
        """Send verification email with code"""
        # Generate code
        code = self.generate_verification_code()
        
        # Store code with expiration (10 minutes)
        self.verification_codes[recipient_email] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=10),
            'username': username
        }
        
        # Check if using default credentials or missing credentials
        if self.sender_password == "your_app_password" or not self.sender_password:
            print(f"\n[DEV MODE] Email not configured. Verification code: {code}\n")
            logger.warning(f"Email not configured. Verification code for {recipient_email}: {code}")
            return True, code
        
        # Send email in background thread to avoid UI lag
        def send_email_async():
            try:
                # Create message
                message = MIMEMultipart("alternative")
                message["Subject"] = "OptiFlow - Email Verification"
                message["From"] = self.sender_email
                message["To"] = recipient_email
                
                # Plain text version
                text = f"""
                Hello {username},
                
                Welcome to OptiFlow Traffic Management System!
                
                Your email verification code is: {code}
                
                This code will expire in 10 minutes.
                
                If you did not create an account, please ignore this email.
                
                Best regards,
                OptiFlow Team
                """
                
                # HTML version
                html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                      <h2 style="color: #1a3a52; text-align: center;">🛡️ OptiFlow - Email Verification</h2>
                      
                      <p style="color: #333; font-size: 16px;">Hello <strong>{username}</strong>,</p>
                      
                      <p style="color: #333; font-size: 16px;">Welcome to OptiFlow Traffic Management System!</p>
                      
                      <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Your verification code is:</p>
                        <h1 style="color: #1a3a52; letter-spacing: 5px; margin: 10px 0;">{code}</h1>
                      </div>
                      
                      <p style="color: #666; font-size: 14px;">This code will expire in <strong>10 minutes</strong>.</p>
                      
                      <p style="color: #666; font-size: 14px;">If you did not create an account, please ignore this email.</p>
                      
                      <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                      
                      <p style="color: #999; font-size: 12px; text-align: center;">© 2026 OptiFlow. All rights reserved.</p>
                    </div>
                  </body>
                </html>
                """
                
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")
                message.attach(part1)
                message.attach(part2)
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, recipient_email, message.as_string())
                
                logger.info(f"Verification email sent to {recipient_email}")
                
            except Exception as e:
                logger.error(f"Error sending email to {recipient_email}: {e}")
                print(f"\n[FALLBACK] Failed to send email. Verification code: {code}\n")
        
        # Start email sending in background thread
        email_thread = threading.Thread(target=send_email_async, daemon=True)
        email_thread.start()
        
        # Return immediately with code (for dev mode display)
        return True, code

    def verify_code(self, email, code):
        """Verify the provided code"""
        if email not in self.verification_codes:
            return False, "No verification code found for this email"
        
        stored = self.verification_codes[email]
        
        # Check expiration
        if datetime.now() > stored['expires']:
            del self.verification_codes[email]
            return False, "Verification code has expired"
        
        # Check code
        if stored['code'] != code:
            return False, "Invalid verification code"
        
        # Code is valid, remove it
        del self.verification_codes[email]
        return True, "Email verified successfully"
    
    def is_email_verified(self, email):
        """Check if email is already verified"""
        return email not in self.verification_codes
    
    def send_password_reset_email(self, recipient_email, username):
        """Send password reset email with code"""
        # Generate code
        code = self.generate_verification_code()
        
        # Store code with expiration (15 minutes for password reset)
        self.verification_codes[f"reset_{recipient_email}"] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=15),
            'username': username,
            'type': 'reset'
        }
        
        # Check if using default credentials or missing credentials
        if self.sender_password == "your_app_password" or not self.sender_password:
            print(f"\n[DEV MODE] Email not configured. Password reset code: {code}\n")
            logger.warning(f"Email not configured. Reset code for {recipient_email}: {code}")
            return True, code
        
        # Send email in background thread to avoid UI lag
        def send_email_async():
            try:
                # Create message
                message = MIMEMultipart("alternative")
                message["Subject"] = "OptiFlow - Password Reset Request"
                message["From"] = self.sender_email
                message["To"] = recipient_email
                
                # Plain text version
                text = f"""
                Hello {username},
                
                We received a request to reset your password for your OptiFlow account.
                
                Your password reset code is: {code}
                
                This code will expire in 15 minutes.
                
                If you did not request a password reset, please ignore this email.
                
                Best regards,
                OptiFlow Team
                """
                
                # HTML version
                html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                      <h2 style="color: #1a3a52; text-align: center;">🛡️ OptiFlow - Password Reset</h2>
                      
                      <p style="color: #333; font-size: 16px;">Hello <strong>{username}</strong>,</p>
                      
                      <p style="color: #333; font-size: 16px;">We received a request to reset your password for your OptiFlow account.</p>
                      
                      <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                        <p style="color: #666; font-size: 14px; margin: 0;">Your password reset code is:</p>
                        <h1 style="color: #1a3a52; letter-spacing: 5px; margin: 10px 0;">{code}</h1>
                      </div>
                      
                      <p style="color: #666; font-size: 14px;">This code will expire in <strong>15 minutes</strong>.</p>
                      
                      <p style="color: #666; font-size: 14px;">If you did not request a password reset, please ignore this email or <a href="#" style="color: #1a3a52; text-decoration: none;">contact support</a>.</p>
                      
                      <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                      
                      <p style="color: #999; font-size: 12px; text-align: center;">© 2026 OptiFlow. All rights reserved.</p>
                    </div>
                  </body>
                </html>
                """
                
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")
                message.attach(part1)
                message.attach(part2)
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, recipient_email, message.as_string())
                
                logger.info(f"Password reset email sent to {recipient_email}")
                
            except Exception as e:
                logger.error(f"Error sending password reset email to {recipient_email}: {e}")
                print(f"\n[FALLBACK] Failed to send email. Password reset code: {code}\n")
        
        # Start email sending in background thread
        email_thread = threading.Thread(target=send_email_async, daemon=True)
        email_thread.start()
        
        # Return immediately with code (for dev mode display)
        return True, code
    
    def verify_reset_code(self, email, code):
        """Verify password reset code"""
        key = f"reset_{email}"
        if key not in self.verification_codes:
            return False, "No password reset request found for this email"
        
        stored = self.verification_codes[key]
        
        # Check expiration
        if datetime.now() > stored['expires']:
            del self.verification_codes[key]
            return False, "Password reset code has expired"
        
        # Check code
        if stored['code'] != code:
            return False, "Invalid password reset code"
        
        # Code is valid, remove it
        del self.verification_codes[key]
        return True, "Code verified successfully"
