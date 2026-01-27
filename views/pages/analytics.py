# views/pages/analytics.py
import tkinter as tk
from tkinter import ttk
import time
import collections
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from ..styles import Colors, Fonts

class AnalyticsPage:
    """Analytics page with real-time traffic trends"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        
        # Data storage for graph (keep last 60 points)
        self.max_points = 60
        self.times = collections.deque(maxlen=self.max_points)
        self.data = {
            'north': collections.deque(maxlen=self.max_points),
            'south': collections.deque(maxlen=self.max_points),
            'east': collections.deque(maxlen=self.max_points),
            'west': collections.deque(maxlen=self.max_points)
        }
        self.start_time = time.time()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create analytics page layout"""
        # Title
        title = tk.Label(self.frame, text="Real-Time Traffic Analytics",
                        font=Fonts.TITLE, bg=Colors.BACKGROUND,
                        fg=Colors.PRIMARY)
        title.pack(pady=15)
        
        # Main content container
        content_frame = tk.Frame(self.frame, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 1. Graph Section (Top)
        graph_frame = tk.Frame(content_frame, bg=Colors.CARD_BG, bd=2, relief=tk.FLAT)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Configure Matplotlib Figure
        # Dark theme style for the plot
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor=Colors.CARD_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(Colors.CARD_BG)
        self.ax.set_title("Live Vehicle Count by Direction", color=Colors.TEXT, pad=10)
        self.ax.set_xlabel("Time (s)", color=Colors.TEXT_LIGHT)
        self.ax.set_ylabel("Vehicles", color=Colors.TEXT_LIGHT)
        self.ax.grid(True, color=Colors.SECONDARY, alpha=0.3)
        self.ax.tick_params(axis='x', colors=Colors.TEXT_LIGHT)
        self.ax.tick_params(axis='y', colors=Colors.TEXT_LIGHT)
        
        # Initial empty lines
        self.lines = {}
        colors = {'north': '#ef4444', 'south': '#3b82f6', 'east': '#10b981', 'west': '#f59e0b'}
        
        for direction, color in colors.items():
            line, = self.ax.plot([], [], label=direction.title(), color=color, linewidth=2)
            self.lines[direction] = line
            
        # Legend with dark text
        legend = self.ax.legend(loc='upper left', facecolor=Colors.CARD_BG, edgecolor=Colors.SECONDARY)
        for text in legend.get_texts():
            text.set_color(Colors.TEXT)
            
        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 2. Stats Cards Section (Bottom)
        stats_frame = tk.Frame(content_frame, bg=Colors.BACKGROUND)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stat_labels = {}
        directions = ['North', 'South', 'East', 'West']
        
        for i, direction in enumerate(directions):
            card = tk.Frame(stats_frame, bg=Colors.CARD_BG, padx=15, pady=15)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            lbl_title = tk.Label(card, text=direction, font=Fonts.BODY_BOLD,
                               bg=Colors.CARD_BG, fg=Colors.TEXT_LIGHT)
            lbl_title.pack(anchor=tk.W)
            
            lbl_val = tk.Label(card, text="0", font=Fonts.HEADING,
                             bg=Colors.CARD_BG, fg=Colors.TEXT)
            lbl_val.pack(anchor=tk.W)
            
            self.stat_labels[direction.lower()] = lbl_val

    def update_analytics(self, traffic_data):
        """
        Update the graph and stats with new data
        traffic_data: dict { 'north': count, 'south': count, ... }
        """
        # Calculate relative time
        current_time = time.time() - self.start_time
        self.times.append(current_time)
        
        # Update data queues
        for direction in ['north', 'south', 'east', 'west']:
            count = traffic_data.get(direction, 0)
            self.data[direction].append(count)
            
            # Update stats text
            if direction in self.stat_labels:
                self.stat_labels[direction].config(text=str(count))
        
        # Update lines
        for direction, line in self.lines.items():
            if direction in self.data:
                line.set_data(self.times, self.data[direction])
        
        # Rescale axes
        self.ax.relim()
        self.ax.autoscale_view()
        
        # Redraw
        self.canvas.draw_idle()
    
    def get_widget(self):
        return self.frame
