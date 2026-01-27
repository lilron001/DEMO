# views/pages/incident_history.py
import tkinter as tk
from tkinter import ttk
from ..styles import Colors, Fonts

class IncidentHistoryPage:
    """Incident history page with past events"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.create_widgets()
    
    def create_widgets(self):
        """Create incident history page layout"""
        # Title
        title = tk.Label(self.frame, text="Incident History",
                        font=Fonts.TITLE, bg=Colors.BACKGROUND,
                        fg=Colors.PRIMARY)
        title.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.frame, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview for incidents
        tree_frame = tk.Frame(content_frame, bg=Colors.CARD_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create columns
        columns = ('Date', 'Time', 'Location', 'Type', 'Severity')
        tree = ttk.Treeview(tree_frame, columns=columns, height=10)
        
        # Configure column headings
        tree.heading('#0', text='ID')
        tree.column('#0', width=50)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Sample data
        incidents = [
            ('1', '2026-01-16', '09:30', 'Main Intersection', 'Accident', 'High'),
            ('2', '2026-01-16', '08:45', 'North Gate', 'Congestion', 'Medium'),
            ('3', '2026-01-15', '17:20', 'South Junction', 'Traffic Jam', 'Medium'),
        ]
        
        for i, (incident_id, date, time, location, incident_type, severity) in enumerate(incidents):
            tree.insert('', tk.END, text=incident_id, values=(date, time, location, incident_type, severity))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
    
    def get_widget(self):
        return self.frame
