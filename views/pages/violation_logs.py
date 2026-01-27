# views/pages/violation_logs.py
import tkinter as tk
from tkinter import ttk
from ..styles import Colors, Fonts

class ViolationLogsPage:
    """Violation logs page with traffic violations database"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.create_widgets()
    
    def create_widgets(self):
        """Create violation logs page layout"""
        # Title
        title = tk.Label(self.frame, text="Violation Logs",
                        font=Fonts.TITLE, bg=Colors.BACKGROUND,
                        fg=Colors.PRIMARY)
        title.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.frame, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview for violations
        tree_frame = tk.Frame(content_frame, bg=Colors.CARD_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create columns
        columns = ('Date', 'Time', 'Vehicle', 'Violation Type', 'Status')
        tree = ttk.Treeview(tree_frame, columns=columns, height=10)
        
        # Configure column headings
        tree.heading('#0', text='ID')
        tree.column('#0', width=50)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        
        # Sample data
        violations = [
            ('1', '2026-01-16', '10:15', 'ABC-123', 'Red Light', 'Recorded'),
            ('2', '2026-01-16', '09:45', 'XYZ-789', 'Speeding', 'Recorded'),
            ('3', '2026-01-15', '16:30', 'DEF-456', 'No Parking', 'Recorded'),
            ('4', '2026-01-15', '15:20', 'GHI-012', 'Wrong Lane', 'Pending'),
        ]
        
        for i, (vid, date, time, vehicle, violation_type, status) in enumerate(violations):
            tree.insert('', tk.END, text=vid, values=(date, time, vehicle, violation_type, status))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
    
    def get_widget(self):
        return self.frame
