import tkinter as tk
from ..styles import Colors, Fonts

class CustomMessageBox(tk.Toplevel):
    """Custom styled message box that matches system theme"""
    
    def __init__(self, title, message, type_="info", buttons=None, parent=None):
        super().__init__(parent)
        self.title(title)
        
        # Determine colors and icon based on type
        self.type_config = {
            "info": {"icon": "ℹ️", "color": Colors.INFO, "title": "Information"},
            "success": {"icon": "✅", "color": Colors.SUCCESS, "title": "Success"},
            "warning": {"icon": "⚠️", "color": Colors.WARNING, "title": "Warning"},
            "error": {"icon": "❌", "color": Colors.DANGER, "title": "Error"},
            "question": {"icon": "❓", "color": Colors.PRIMARY, "title": "Question"}
        }
        
        config = self.type_config.get(type_, self.type_config["info"])
        self.result = None
        
        # Window Setup
        self.configure(bg=Colors.BACKGROUND)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Remove standard title bar for full custom look (optional, but requested aligned design)
        self.overrideredirect(True)
        
        # Center the window
        self.update_idletasks()
        if parent:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 200
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 100
        else:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 200) // 2
        
        self.geometry(f"+{x}+{y}")
        
        # Draw Border
        main_frame = tk.Frame(self, bg=Colors.BACKGROUND, highlightbackground=config["color"], highlightthickness=2)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title Bar
        title_bar = tk.Frame(main_frame, bg=Colors.CARD_BG, height=40)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        title_bar.pack_propagate(False)
        
        # Icon
        tk.Label(title_bar, text=config["icon"], font=("Segoe UI", 12), bg=Colors.CARD_BG, fg="white").pack(side=tk.LEFT, padx=(15, 5))
        
        # Title Text
        tk.Label(title_bar, text=title or config["title"], font=Fonts.BODY_BOLD, bg=Colors.CARD_BG, fg="white").pack(side=tk.LEFT)
        
        # Close Button (X) - mainly for if they want to cancel without strictly choosing an option
        close_btn = tk.Label(title_bar, text="✕", font=("Arial", 12), bg=Colors.CARD_BG, fg=Colors.TEXT_LIGHT, cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=15)
        close_btn.bind("<Button-1>", lambda e: self.on_close())
        
        # Dragging logic
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        
        # Content Content
        content_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND, padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text=message, font=Fonts.BODY, bg=Colors.BACKGROUND, fg=Colors.TEXT, wraplength=340, justify=tk.LEFT).pack(expand=True)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND, height=60)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=15, padx=30)
        
        if not buttons:
            buttons = [("OK", "ok", Colors.PRIMARY)]
            
        for text, value, color in buttons:
            # Reverse order to put primary action on right usually, but pack side=RIGHT works too
            btn = tk.Button(btn_frame, 
                           text=text,
                           font=Fonts.BODY_BOLD,
                           bg=color,
                           fg="white",
                           relief=tk.FLAT,
                           activebackground=Colors.HOVER,
                           activeforeground="white",
                           padx=20,
                           pady=5,
                           command=lambda v=value: self.on_btn_click(v))
            btn.pack(side=tk.RIGHT, padx=(10, 0))

        if parent is None:
            # Try to get default root
            parent = tk._default_root
            if parent is None:
                # Should not happen if Tk() exists
                pass

        self.transient(parent)
        self.grab_set()
        if parent:
            parent.wait_window(self)
        else:
            self.wait_window(self)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_btn_click(self, value):
        self.result = value
        self.destroy()
        
    def on_close(self):
        self.result = None
        self.destroy()

class MessageBox:
    @staticmethod
    def showinfo(title, message, parent=None):
        # Ensure we have a valid parent if possible, otherwise let Toplevel resolve it
        if parent is None and tk._default_root:
            parent = tk._default_root
        dialog = CustomMessageBox(title, message, "info", parent=parent)
        return dialog.result

    @staticmethod
    def showwarning(title, message, parent=None):
        if parent is None and tk._default_root:
            parent = tk._default_root
        dialog = CustomMessageBox(title, message, "warning", parent=parent)
        return dialog.result
        
    @staticmethod
    def showerror(title, message, parent=None):
        if parent is None and tk._default_root:
            parent = tk._default_root
        dialog = CustomMessageBox(title, message, "error", parent=parent)
        return dialog.result
        
    @staticmethod
    def showsuccess(title, message, parent=None):
        if parent is None and tk._default_root:
            parent = tk._default_root
        dialog = CustomMessageBox(title, message, "success", [("OK", "ok", Colors.SUCCESS)], parent=parent)
        return dialog.result

    @staticmethod
    def askyesno(title, message, parent=None):
        if parent is None and tk._default_root:
            parent = tk._default_root
        buttons = [
            ("No", False, Colors.SECONDARY),
            ("Yes", True, Colors.PRIMARY)
        ]
        dialog = CustomMessageBox(title, message, "question", buttons, parent=parent)
        return dialog.result
