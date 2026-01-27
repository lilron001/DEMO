# views/operator_dashboard.py
import tkinter as tk
from .styles import Colors, Fonts


class OperatorDashboard(tk.Frame):
    """Operator dashboard - main traffic monitoring interface"""
    
    def __init__(self, parent, current_user=None, on_logout_callback=None):
        super().__init__(parent, bg=Colors.BACKGROUND)
        self.current_user = current_user
        self.on_logout_callback = on_logout_callback
        
        self.setup_window()
    
    def setup_window(self):
        """Setup operator dashboard window"""
        # This will use the existing main_window structure
        # The operator gets the full traffic monitoring interface
        
        # Create header with user info
        header_frame = tk.Frame(self, bg=Colors.PRIMARY)
        header_frame.pack(fill=tk.X)
        
        # Logo and title
        left_header = tk.Frame(header_frame, bg=Colors.PRIMARY)
        left_header.pack(side=tk.LEFT, padx=20, pady=15)
        
        title_label = tk.Label(
            left_header,
            text="🛡️ OPTIFLOW - TRAFFIC CONTROL",
            font=("Arial", 16, "bold"),
            bg=Colors.PRIMARY,
            fg="white"
        )
        title_label.pack()
        
        # User info and logout
        right_header = tk.Frame(header_frame, bg=Colors.PRIMARY)
        right_header.pack(side=tk.RIGHT, padx=20, pady=15)
        
        user_label = tk.Label(
            right_header,
            text=f"👤 {self.current_user['username']} (Operator)",
            font=("Arial", 11),
            bg=Colors.PRIMARY,
            fg="white"
        )
        user_label.pack(side=tk.LEFT, padx=10)
        
        logout_button = tk.Button(
            right_header,
            text="Logout",
            font=("Arial", 10, "bold"),
            bg=Colors.DANGER,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.on_logout_callback,
            padx=15,
            pady=5
        )
        logout_button.pack(side=tk.LEFT)
