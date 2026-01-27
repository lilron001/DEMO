# views/signup_page.py
import tkinter as tk
from tkinter import messagebox
import re
from .styles import Colors


class SignupPage(tk.Frame):
    """Signup/Create Account page"""
    
    def __init__(self, parent, on_signup_callback=None, on_back_callback=None):
        super().__init__(parent, bg="#f8fafc")
        self.on_signup_callback = on_signup_callback
        self.on_back_callback = on_back_callback
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create signup page widgets"""
        # Main container
        main_container = tk.Frame(self, bg=Colors.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with back button
        header_frame = tk.Frame(main_container, bg=Colors.BACKGROUND, height=60)
        header_frame.pack(fill=tk.X, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        back_button = tk.Button(
            header_frame,
            text="← Back",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=Colors.BACKGROUND,
            activeforeground=Colors.PRIMARY,
            command=self.on_back_callback
        )
        back_button.pack(side=tk.LEFT, padx=20, pady=12)
        
        # Form container - centered card
        form_container = tk.Frame(main_container, bg=Colors.CARD_BG, padx=40, pady=20)
        form_container.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            form_container,
            text="Create Account",
            font=("Segoe UI", 24, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(
            form_container,
            text="Join OptiFlow System",
            font=("Segoe UI", 10),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_LIGHT
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Username field
        tk.Label(
            form_container,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 5))
        
        username_wrap = tk.Frame(form_container, bg=Colors.BACKGROUND, padx=1, pady=1)
        username_wrap.pack(fill=tk.X, pady=(0, 10))
        
        self.username_entry = tk.Entry(
            username_wrap,
            font=("Segoe UI", 11),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY
        )
        self.username_entry.pack(fill=tk.X, ipady=8, padx=10)
        
        # Email field
        tk.Label(
            form_container,
            text="Email",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 5))
        
        email_wrap = tk.Frame(form_container, bg=Colors.BACKGROUND, padx=1, pady=1)
        email_wrap.pack(fill=tk.X, pady=(0, 10))
        
        self.email_entry = tk.Entry(
            email_wrap,
            font=("Segoe UI", 11),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY
        )
        self.email_entry.pack(fill=tk.X, ipady=8, padx=10)
        
        # Password field
        tk.Label(
            form_container,
            text="Password",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 5))
        
        password_wrap = tk.Frame(form_container, bg=Colors.BACKGROUND, padx=1, pady=1)
        password_wrap.pack(fill=tk.X, pady=(0, 10))
        
        self.password_entry = tk.Entry(
            password_wrap,
            font=("Segoe UI", 11),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            show="*",
            insertbackground=Colors.PRIMARY
        )
        self.password_entry.pack(fill=tk.X, ipady=8, padx=10)
        
        # Confirm password field
        tk.Label(
            form_container,
            text="Confirm Password",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 5))
        
        confirm_wrap = tk.Frame(form_container, bg=Colors.BACKGROUND, padx=1, pady=1)
        confirm_wrap.pack(fill=tk.X, pady=(0, 15))
        
        self.confirm_password_entry = tk.Entry(
            confirm_wrap,
            font=("Segoe UI", 11),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            show="*",
            insertbackground=Colors.PRIMARY
        )
        self.confirm_password_entry.pack(fill=tk.X, ipady=8, padx=10)
        
        # Signup button
        signup_button = tk.Button(
            form_container,
            text="CREATE ACCOUNT",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.PRIMARY,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=Colors.PRIMARY_DARK,
            activeforeground=Colors.WHITE,
            command=self.handle_signup
        )
        signup_button.pack(fill=tk.X, ipady=10)

        # Exit button
        exit_btn = tk.Button(
            form_container,
            text="Exit Application",
            font=("Segoe UI", 9),
            bg=Colors.CARD_BG,
            fg=Colors.DANGER, 
            activebackground=Colors.CARD_BG,
            activeforeground="#dc2626",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.quit_app
        )
        exit_btn.pack(pady=(15, 0), fill=tk.X)

    def quit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
             self.quit()
    
    def handle_signup(self):
        """Handle signup button click"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not username:
            messagebox.showwarning("Input Error", "Please enter username")
            return
        
        if len(username) < 3:
            messagebox.showwarning("Input Error", "Username must be at least 3 characters")
            return
        
        if not email:
            messagebox.showwarning("Input Error", "Please enter email")
            return
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showwarning("Input Error", "Please enter a valid email")
            return
        
        if not password:
            messagebox.showwarning("Input Error", "Please enter password")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Input Error", "Password must be at least 6 characters")
            return
        
        if password != confirm_password:
            messagebox.showwarning("Input Error", "Passwords do not match")
            return
        
        if self.on_signup_callback:
            self.on_signup_callback(username, email, password)
