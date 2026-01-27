# views/password_dialog.py
import tkinter as tk
from tkinter import messagebox
from .styles import Colors


class PasswordResetDialog(tk.Toplevel):
    """Custom password reset dialog with modern UI"""
    
    def __init__(self, parent, title="Set New Password"):
        super().__init__(parent)
        self.result = None
        
        # Configure window
        self.title(title)
        self.configure(bg="#1e293b")  # Dark background
        self.resizable(False, False)
        
        # Set window size - increased to show buttons
        window_width = 450
        window_height = 480  # Increased to show buttons
        self.geometry(f"{window_width}x{window_height}")
        
        # Center window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # Focus on password entry
        self.password_entry.focus_set()
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())
        
    def create_widgets(self):
        """Create dialog widgets"""
        # Main container with dark background
        main_container = tk.Frame(self, bg="#1e293b", padx=40, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk.Label(
            main_container,
            text="🔑",
            font=("Segoe UI Emoji", 45),
            bg="#1e293b",
            fg="#3b82f6"  # Blue
        )
        icon_label.pack(pady=(0, 8))
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Set New Password",
            font=("Segoe UI", 16, "bold"),
            bg="#1e293b",
            fg="white"
        )
        title_label.pack(pady=(0, 3))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_container,
            text="Enter your new password (minimum 6 characters)",
            font=("Segoe UI", 9),
            bg="#1e293b",
            fg="#94a3b8"
        )
        subtitle_label.pack(pady=(0, 15))
        
        # New Password label
        tk.Label(
            main_container,
            text="New Password",
            font=("Segoe UI", 10, "bold"),
            bg="#1e293b",
            fg="white"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # New Password field with eye icon
        password_frame = tk.Frame(main_container, bg="#334155", highlightbackground="#475569", highlightthickness=1)
        password_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Segoe UI", 11),
            bg="#334155",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            show="*",
            insertbackground="#3b82f6"
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=10)
        
        # Eye icon
        self.show_password = False
        self.eye_button = tk.Label(
            password_frame,
            text="👁️",
            font=("Segoe UI", 12),
            bg="#334155",
            fg="#94a3b8",
            cursor="hand2"
        )
        self.eye_button.pack(side=tk.RIGHT, padx=10)
        self.eye_button.bind("<Button-1>", lambda e: self.toggle_password_visibility())
        
        # Confirm Password label
        tk.Label(
            main_container,
            text="Confirm New Password",
            font=("Segoe UI", 10, "bold"),
            bg="#1e293b",
            fg="white"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Confirm Password field with eye icon
        confirm_frame = tk.Frame(main_container, bg="#334155", highlightbackground="#475569", highlightthickness=1)
        confirm_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.confirm_entry = tk.Entry(
            confirm_frame,
            font=("Segoe UI", 11),
            bg="#334155",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            show="*",
            insertbackground="#3b82f6"
        )
        self.confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=10)
        
        # Eye icon for confirm password
        self.show_confirm = False
        self.confirm_eye_button = tk.Label(
            confirm_frame,
            text="👁️",
            font=("Segoe UI", 12),
            bg="#334155",
            fg="#94a3b8",
            cursor="hand2"
        )
        self.confirm_eye_button.pack(side=tk.RIGHT, padx=10)
        self.confirm_eye_button.bind("<Button-1>", lambda e: self.toggle_confirm_visibility())
        
        # Buttons frame
        button_frame = tk.Frame(main_container, bg="#1e293b")
        button_frame.pack(fill=tk.X, pady=(0, 0))
        
        # Reset Password button (blue)
        ok_button = tk.Button(
            button_frame,
            text="Reset Password",
            font=("Segoe UI", 11, "bold"),
            bg="#3b82f6",  # Blue
            fg="white",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#2563eb",
            activeforeground="white",
            command=self.on_ok
        )
        ok_button.pack(side=tk.LEFT, ipady=10, padx=(0, 10), expand=True, fill=tk.X)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 11),
            bg="#475569",  # Gray
            fg="white",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#64748b",
            activeforeground="white",
            command=self.on_cancel
        )
        cancel_button.pack(side=tk.RIGHT, ipady=10, expand=True, fill=tk.X)
    
    def toggle_password_visibility(self):
        """Toggle new password visibility"""
        self.show_password = not self.show_password
        show_char = "" if self.show_password else "*"
        self.password_entry.config(show=show_char)
    
    def toggle_confirm_visibility(self):
        """Toggle confirm password visibility"""
        self.show_confirm = not self.show_confirm
        show_char = "" if self.show_confirm else "*"
        self.confirm_entry.config(show=show_char)
    
    def on_ok(self):
        """Handle OK button"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showwarning("Input Error", "Please enter a password", parent=self)
            self.password_entry.focus_set()
            return
        
        if len(password) < 6:
            messagebox.showwarning("Input Error", "Password must be at least 6 characters", parent=self)
            self.password_entry.focus_set()
            return
        
        if password != confirm:
            messagebox.showwarning("Input Error", "Passwords do not match", parent=self)
            self.confirm_entry.delete(0, tk.END)
            self.confirm_entry.focus_set()
            return
        
        self.result = password
        self.destroy()
    
    def on_cancel(self):
        """Handle Cancel button"""
        self.result = None
        self.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.wait_window()
        return self.result
