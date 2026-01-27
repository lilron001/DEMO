# views/pages/settings.py
import tkinter as tk
from tkinter import ttk
from ..styles import Colors, Fonts

class SettingsPage:
    """Settings page for system configuration"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings page layout"""
        # Title
        title = tk.Label(self.frame, text="System Settings",
                        font=Fonts.TITLE, bg=Colors.BACKGROUND,
                        fg=Colors.PRIMARY)
        title.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.frame, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Settings sections
        self.create_setting_section(content_frame, "Camera Settings", 0)
        self.create_setting_section(content_frame, "Detection Settings", 1)
        self.create_setting_section(content_frame, "Database Settings", 2)
        self.create_setting_section(content_frame, "Alert Settings", 3)
    
    def create_setting_section(self, parent, label, row):
        """Create a settings section"""
        section = tk.Frame(parent, bg=Colors.CARD_BG, relief=tk.RAISED, bd=2)
        section.grid(row=row, column=0, sticky="ew", pady=10, padx=10)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Section title
        title = tk.Label(section, text=label,
                        font=Fonts.HEADING, bg=Colors.CARD_BG,
                        fg=Colors.PRIMARY)
        title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Settings options
        if label == "Camera Settings":
            self.create_checkbox(section, "Enable Camera")
            self.create_checkbox(section, "Auto-focus")
            self.create_checkbox(section, "Record Video")
        elif label == "Detection Settings":
            self.create_checkbox(section, "Enable YOLO Detection")
            self.create_checkbox(section, "Show Bounding Boxes")
            self.create_checkbox(section, "Real-time Alerts")
        elif label == "Database Settings":
            self.create_checkbox(section, "Enable Database")
            self.create_checkbox(section, "Auto Backup")
            self.create_checkbox(section, "Compress Data")
        else:  # Alert Settings
            self.create_checkbox(section, "Email Alerts")
            self.create_checkbox(section, "SMS Alerts")
            self.create_checkbox(section, "Push Notifications")
        
        # Save button
        save_btn = tk.Button(section, text="Save Settings",
                            font=Fonts.BODY, bg=Colors.PRIMARY,
                            fg='white', relief=tk.FLAT, padx=20, pady=8,
                            cursor="hand2")
        save_btn.pack(anchor=tk.W, padx=15, pady=(10, 10))
    
    def create_checkbox(self, parent, label):
        """Create a checkbox option"""
        var = tk.BooleanVar(value=True)
        checkbox = tk.Checkbutton(parent, text=label,
                                 font=Fonts.BODY, bg=Colors.CARD_BG,
                                 fg=Colors.TEXT_LIGHT, variable=var,
                                 selectcolor=Colors.CARD_BG)
        checkbox.pack(anchor=tk.W, padx=30, pady=3)
    
    def get_widget(self):
        return self.frame
