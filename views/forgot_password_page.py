# views/forgot_password_page.py
import tkinter as tk
from tkinter import messagebox
from .styles import Colors


class ForgotPasswordPage(tk.Frame):
    """Forgot password page"""
    
    def __init__(self, parent, on_reset_callback=None, on_back_callback=None):
        super().__init__(parent, bg="#f8fafc")
        self.on_reset_callback = on_reset_callback
        self.on_back_callback = on_back_callback
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create forgot password page widgets"""
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
        form_container = tk.Frame(main_container, bg=Colors.CARD_BG, padx=40, pady=40)
        form_container.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            form_container,
            text="Reset Your Password",
            font=("Segoe UI", 24, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(
            form_container,
            text="Enter your details to receive reset code",
            font=("Segoe UI", 10),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_LIGHT
        )
        subtitle_label.pack(pady=(0, 25))
        
        # Username field
        tk.Label(
            form_container,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 5))
        
        username_wrap = tk.Frame(form_container, bg=Colors.BACKGROUND, padx=1, pady=1)
        username_wrap.pack(fill=tk.X, pady=(0, 15))
        
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
            text="Email Address",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 5))
        
        email_wrap = tk.Frame(form_container, bg=Colors.BACKGROUND, padx=1, pady=1)
        email_wrap.pack(fill=tk.X, pady=(0, 25))
        
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
        
        # Send code button
        reset_button = tk.Button(
            form_container,
            text="SEND RESET CODE",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.PRIMARY,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=Colors.PRIMARY_DARK,
            activeforeground="white",
            command=self.handle_reset
        )
        reset_button.pack(fill=tk.X, ipady=10)
    
    def handle_reset(self):
        """Handle password reset request"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not username:
            messagebox.showwarning("Input Error", "Please enter username")
            return
        
        if not email:
            messagebox.showwarning("Input Error", "Please enter email address")
            return
        
        if '@' not in email:
            messagebox.showwarning("Input Error", "Please enter a valid email address")
            return
        
        if self.on_reset_callback:
            self.on_reset_callback(username, email)
