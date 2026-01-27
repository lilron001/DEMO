# views/styles.py


class Colors:
    """Color palette for the application (Modern Dark Theme)"""
    # Base
    BACKGROUND = '#0f172a' # Slate 900
    CARD_BG = '#1e293b'    # Slate 800
    
    # Brand
    PRIMARY = '#3b82f6'    # Blue 500
    PRIMARY_DARK = '#2563eb' # Blue 600
    SECONDARY = '#334155'  # Slate 700
    ACCENT = '#64748b'     # Slate 500
    HOVER = '#475569'      # Slate 600
    
    # Text
    TEXT = '#f8fafc'       # Slate 50
    TEXT_LIGHT = '#94a3b8' # Slate 400
    
    # State
    SUCCESS = '#10b981'    # Emerald 500
    WARNING = '#f59e0b'    # Amber 500
    DANGER = '#ef4444'     # Red 500
    INFO = '#0ea5e9'       # Sky 500
    
    # Specific
    BLACK = '#020617'      # Slate 950
    DARK_GREY = '#111827'  # Gray 900
    WHITE = '#ffffff'
    
    # Domain specific
    ROAD_GREEN = '#15803d' # Green 700
    ROAD_DARK = '#1e293b'
    ROAD_LIGHT = '#334155'
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for status indicator"""
        status_colors = {
            'active': Colors.SUCCESS,
            'warning': Colors.WARNING,
            'error': Colors.DANGER,
            'info': Colors.INFO,
            'offline': Colors.ACCENT
        }
        return status_colors.get(status.lower(), Colors.TEXT_LIGHT)


class Fonts:
    """Font styles for the application"""
    FAMILY = 'Segoe UI' # Modern Windows Font
    
    TITLE = (FAMILY, 24, 'bold')
    HEADING = (FAMILY, 16, 'bold')
    SUBHEADING = (FAMILY, 14, 'bold')
    BODY = (FAMILY, 11)
    BODY_BOLD = (FAMILY, 11, 'bold')
    SMALL = (FAMILY, 9)
    MONO = ('Consolas', 10)