# views/pages/traffic_reports.py
import tkinter as tk
from tkinter import ttk
from ..styles import Colors, Fonts

class TrafficReportsPage:
    """Traffic reports page with statistics and metrics"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.create_widgets()
    
    def create_widgets(self):
        """Create traffic reports page layout"""
        # Title
        title = tk.Label(self.frame, text="Traffic Reports",
                        font=Fonts.TITLE, bg=Colors.BACKGROUND,
                        fg=Colors.PRIMARY)
        title.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.frame, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Report cards
        self.create_report_card(content_frame, "Peak Hours", "08:00 - 09:00 AM", Colors.WARNING, 0)
        self.create_report_card(content_frame, "Average Traffic Flow", "1,250 vehicles/hour", Colors.SUCCESS, 1)
        self.create_report_card(content_frame, "Signal Efficiency", "87%", Colors.INFO, 2)
        self.create_report_card(content_frame, "Total Violations Detected", "24", Colors.DANGER, 3)
    
    def create_report_card(self, parent, label, value, color, row):
        """Create a report card"""
        card = tk.Frame(parent, bg=Colors.CARD_BG, relief=tk.RAISED, bd=2)
        card.grid(row=row, column=0, sticky="ew", pady=10, padx=10)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        label_widget = tk.Label(card, text=label,
                               font=Fonts.BODY, bg=Colors.CARD_BG,
                               fg=Colors.TEXT_LIGHT)
        label_widget.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        value_widget = tk.Label(card, text=value,
                               font=('Arial', 18, 'bold'), bg=Colors.CARD_BG,
                               fg=color)
        value_widget.pack(anchor=tk.W, padx=15, pady=(5, 10))
    
    def get_widget(self):
        return self.frame
