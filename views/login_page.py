# views/login_page.py
import tkinter as tk
from tkinter import messagebox
from .styles import Colors


class LoginPage(tk.Frame):
    """Login page with username and password"""
    
    def __init__(self, parent, on_login_callback=None, on_signup_callback=None, 
                 on_forgot_password_callback=None):
        super().__init__(parent, bg="#f8fafc")
        self.on_login_callback = on_login_callback
        self.on_signup_callback = on_signup_callback
        self.on_forgot_password_callback = on_forgot_password_callback
        
        # Animation variables
        self.animation_step = 0
        self.max_animation_steps = 20
        
        self.create_widgets()
        self.start_animations()
    
    def start_animations(self):
        """Start fade-in animation for form elements"""
        if self.animation_step < self.max_animation_steps:
            self.animation_step += 1
            self.after(50, self.start_animations)
    
    def create_widgets(self):
        """Create login page widgets"""
        # Main container
        main_container = tk.Frame(self, bg=Colors.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (Branding)
        left_panel = tk.Frame(main_container, bg=Colors.CARD_BG, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_panel.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(left_panel, bg=Colors.CARD_BG)
        logo_frame.pack(pady=60, expand=True, fill=tk.X)
        
        # Shield icon
        shield_container = tk.Frame(logo_frame, bg=Colors.CARD_BG)
        shield_container.pack(pady=(0, 10), fill=tk.X)
        
        self.shield_label = tk.Label(
            shield_container,
            text="🛡️",
            font=("Segoe UI Emoji", 80),
            bg=Colors.CARD_BG,
            fg=Colors.PRIMARY,
            justify=tk.CENTER
        )
        self.shield_label.pack(anchor=tk.CENTER)
        
        # OptiFlow text
        self.title_label = tk.Label(
            logo_frame,
            text="OPTIFLOW",
            font=("Segoe UI", 28, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT,
            justify=tk.CENTER
        )
        self.title_label.pack(pady=(0, 2), anchor=tk.CENTER, fill=tk.X)
        
        # Subtitle
        self.subtitle_label = tk.Label(
            logo_frame,
            text="Traffic Control System",
            font=("Segoe UI", 11),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_LIGHT,
            justify=tk.CENTER
        )
        self.subtitle_label.pack(anchor=tk.CENTER, fill=tk.X)
        
        # Status indicators
        status_frame = tk.Frame(logo_frame, bg=Colors.CARD_BG)
        status_frame.pack(pady=45)
        
        status_items = [
            ("●", Colors.SUCCESS, "Optimal"),
            ("●", Colors.WARNING, "Moderate"),
            ("●", Colors.DANGER, "Critical")
        ]
        
        for status, color, label in status_items:
            status_item = tk.Frame(status_frame, bg=Colors.CARD_BG)
            status_item.pack(side=tk.LEFT, padx=15, pady=5)
            
            tk.Label(
                status_item,
                text=status,
                font=("Arial", 14),
                bg=Colors.CARD_BG,
                fg=color
            ).pack(anchor=tk.CENTER)
            
            tk.Label(
                status_item,
                text=label,
                font=("Segoe UI", 9),
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_LIGHT
            ).pack(anchor=tk.CENTER, pady=(2, 0))
        
        # Right panel (Form)
        right_panel = tk.Frame(main_container, bg=Colors.BACKGROUND)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Form container (Card)
        self.form_container = tk.Frame(right_panel, bg=Colors.CARD_BG, padx=40, pady=40)
        self.form_container.pack(expand=True)
        
        # Welcome text
        self.welcome_label = tk.Label(
            self.form_container,
            text="Welcome Back",
            font=("Segoe UI", 24, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        )
        self.welcome_label.pack(pady=(0, 5), anchor=tk.W)
        
        self.subtitle_login = tk.Label(
            self.form_container,
            text="Sign in to your account",
            font=("Segoe UI", 10),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_LIGHT
        )
        self.subtitle_login.pack(pady=(0, 30), anchor=tk.W)
        
        # Username field
        tk.Label(
            self.form_container,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 8))
        
        username_wrap = tk.Frame(self.form_container, bg=Colors.BACKGROUND, pady=1, padx=1) # Border wrapper
        username_wrap.pack(fill=tk.X, pady=(0, 20))
        
        self.username_entry = tk.Entry(
            username_wrap,
            font=("Segoe UI", 11),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY
        )
        self.username_entry.pack(fill=tk.X, padx=10, ipady=8)
        
        # Password field
        tk.Label(
            self.form_container,
            text="Password",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT
        ).pack(anchor=tk.W, pady=(0, 8))
        
        password_wrap = tk.Frame(self.form_container, bg=Colors.BACKGROUND, pady=1, padx=1)
        password_wrap.pack(fill=tk.X, pady=(0, 25))
        
        password_inner = tk.Frame(password_wrap, bg=Colors.BACKGROUND)
        password_inner.pack(fill=tk.X, padx=10)
        
        self.password_entry = tk.Entry(
            password_inner,
            font=("Segoe UI", 11),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            relief=tk.FLAT,
            bd=0,
            show="*",
            insertbackground=Colors.PRIMARY
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        # Eye icon
        self.show_password = False
        self.eye_button = tk.Button(
            password_inner,
            text="👁️",
            font=("Segoe UI", 12),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT_LIGHT,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=Colors.BACKGROUND,
            activeforeground=Colors.PRIMARY,
            command=self.toggle_password_visibility
        )
        self.eye_button.pack(side=tk.RIGHT)

        # Login button
        self.login_button = tk.Button(
            self.form_container,
            text="Sign In",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.PRIMARY,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=Colors.PRIMARY_DARK,
            activeforeground="white",
            command=self.handle_login
        )
        self.login_button.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Footer
        footer_frame = tk.Frame(self.form_container, bg=Colors.CARD_BG)
        footer_frame.pack(fill=tk.X)
        
        forgot_btn = tk.Button(
            footer_frame,
            text="Forgot Password?",
            font=("Segoe UI", 9),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_LIGHT,
            activebackground=Colors.CARD_BG,
            activeforeground=Colors.PRIMARY,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.handle_forgot_password
        )
        forgot_btn.pack(side=tk.LEFT)
        
        signup_btn = tk.Button(
            footer_frame,
            text="Create Account",
            font=("Segoe UI", 9, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.PRIMARY,
            activebackground=Colors.CARD_BG,
            activeforeground=Colors.PRIMARY_DARK,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.handle_signup
        )
        signup_btn.pack(side=tk.RIGHT)

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.show_password = not self.show_password
        self.password_entry.config(show="" if self.show_password else "*")
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username:
            messagebox.showwarning("Input Error", "Please enter username")
            return
        
        if not password:
            messagebox.showwarning("Input Error", "Please enter password")
            return
        
        if self.on_login_callback:
            self.on_login_callback(username, password)
    
    def handle_signup(self):
        if self.on_signup_callback:
            self.on_signup_callback()
    
    def handle_forgot_password(self):
        if self.on_forgot_password_callback:
            self.on_forgot_password_callback()
