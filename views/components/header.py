# views/components/header.py
import tkinter as tk
from datetime import datetime
from ..styles import Colors, Fonts

class Header:
    """Header component with enhanced design, user info, and controls"""
    
    def __init__(self, parent, current_user=None, on_logout=None):
        self.parent = parent
        self.current_user = current_user
        self.on_logout = on_logout
        
        # Main header container
        self.frame = tk.Frame(parent, bg=Colors.PRIMARY, height=80)
        self.frame.pack(fill=tk.X, side=tk.TOP)
        self.frame.pack_propagate(False)
        
        self.time_label = None
        self.create_widgets()
    
    def create_widgets(self):
        # Left Section: Brand
        left_frame = tk.Frame(self.frame, bg=Colors.PRIMARY)
        left_frame.pack(side=tk.LEFT, padx=30, fill=tk.Y)
        
        # Logo Icon (Text based for now)
        icon_label = tk.Label(left_frame, 
                            text="🛡️", 
                            font=("Segoe UI", 28),
                            bg=Colors.PRIMARY,
                            fg="white")
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title Container
        title_box = tk.Frame(left_frame, bg=Colors.PRIMARY)
        title_box.pack(side=tk.LEFT, pady=15)
        
        # Main Title
        main_title = tk.Label(title_box, 
                             text="OPTIFLOW", 
                             font=("Segoe UI", 20, "bold"),
                             bg=Colors.PRIMARY,
                             fg="white")
        main_title.pack(anchor=tk.W)
        
        # Subtitle
        sub_title = tk.Label(title_box, 
                            text="INTELLIGENT TRAFFIC CONTROL", 
                            font=("Segoe UI", 9, "bold"),
                            bg=Colors.PRIMARY,
                            fg=Colors.INFO,
                            pady=0)
        sub_title.pack(anchor=tk.W)
        
        # Right Section: Info & Controls
        right_frame = tk.Frame(self.frame, bg=Colors.PRIMARY)
        right_frame.pack(side=tk.RIGHT, padx=30, fill=tk.Y)
        
        # Time Display
        self.time_label = tk.Label(right_frame,
                                  font=("Segoe UI", 14),
                                  bg=Colors.PRIMARY,
                                  fg="white")
        self.time_label.pack(side=tk.LEFT, padx=(0, 30))
        self.update_time()
        
        # User Profile
        if self.current_user:
            user_frame = tk.Frame(right_frame, bg=Colors.PRIMARY_DARK, padx=15, pady=8)
            user_frame.pack(side=tk.LEFT, padx=(0, 15))
            
            # Role Badge
            role = self.current_user.get('role', 'operator').upper()
            role_fg = Colors.WARNING if role == 'ADMIN' else Colors.INFO
            
            tk.Label(user_frame, 
                    text=f"👤 {self.current_user.get('username')}", 
                    font=("Segoe UI", 11, "bold"),
                    bg=Colors.PRIMARY_DARK,
                    fg="white").pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(user_frame, 
                    text=role, 
                    font=("Segoe UI", 9, "bold"),
                    bg=Colors.PRIMARY_DARK,
                    fg=role_fg).pack(side=tk.LEFT)
        
        # Logout Button
        if self.on_logout:
            logout_btn = tk.Button(right_frame,
                                 text="LOGOUT",
                                 font=("Segoe UI", 10, "bold"),
                                 bg=Colors.DANGER,
                                 fg="white",
                                 activebackground="#dc2626", # Red 600
                                 activeforeground="white",
                                 relief=tk.FLAT,
                                 cursor="hand2",
                                 command=self.on_logout,
                                 padx=20,
                                 pady=8)
            logout_btn.pack(side=tk.LEFT)
            
            # Button hover effect
            def on_enter(e):
                logout_btn.config(bg="#b91c1c") # Red 700
            def on_leave(e):
                logout_btn.config(bg=Colors.DANGER)
            logout_btn.bind("<Enter>", on_enter)
            logout_btn.bind("<Leave>", on_leave)
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        if self.time_label:
            self.time_label.config(text=current_time)
        self.frame.after(1000, self.update_time)
    
    def get_widget(self):
        return self.frame
