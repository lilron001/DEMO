# views/components/stats_cards.py
import tkinter as tk
from ..styles import Colors, Fonts

class StatsCards:
    """Component for displaying statistics cards"""
    def __init__(self, parent, stats_data=None):
        self.parent = parent
        self.stats_data = stats_data or {}
        self.frame = None
        self.create_widgets()
    
    def create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=Colors.BACKGROUND)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Default stats if none provided
        stats = [
            {"label": "Active Cameras", "value": "4", "color": Colors.SUCCESS},
            {"label": "Violations Detected", "value": "12", "color": Colors.WARNING},
            {"label": "System Status", "value": "Operational", "color": Colors.INFO},
        ]
        
        # Create stat cards
        for i, stat in enumerate(stats):
            self.create_stat_card(stat, i)
    
    def create_stat_card(self, stat, index):
        """Create individual stat card"""
        card = tk.Frame(self.frame, bg=Colors.CARD_BG, relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5)
        
        # Stat label
        label = tk.Label(card, text=stat['label'],
                        font=Fonts.SUBHEADING, bg=Colors.CARD_BG,
                        fg=Colors.TEXT_LIGHT)
        label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Stat value
        value = tk.Label(card, text=stat['value'],
                        font=('Arial', 24, 'bold'), bg=Colors.CARD_BG,
                        fg=stat.get('color', Colors.PRIMARY))
        value.pack(anchor=tk.W, padx=15, pady=(5, 10))
    
    def get_widget(self):
        return self.frame
