# views/styles.py


class Colors:
    """Color palette for the application (Modern Premium Dark Theme)"""
    # Base - Richer Dark Backgrounds
    BACKGROUND = '#0B0F19' # Deep Navy/Black
    CARD_BG = '#151B2B'    # Slightly lighter Navy
    
    # Brand - Electric Blue / Neon
    PRIMARY = '#3B82F6'    # Bright Blue
    PRIMARY_DARK = '#2563EB' 
    SECONDARY = '#1E293B'  # Slate 800 (for secondary elements)
    ACCENT = '#64748B'     
    HOVER = '#2D3748'      # Dark Grey Blue for hovers
    
    # Text
    TEXT = '#F8FAFC'       # White-ish
    TEXT_LIGHT = '#94A3B8' # Muted Blue-Grey
    
    # State - Vibrant Indicators
    SUCCESS = '#10B981'    # Emerald
    WARNING = '#F59E0B'    # Amber
    DANGER = '#EF4444'     # Red
    INFO = '#0EA5E9'       # Sky Blue
    
    # Specific
    BLACK = '#000000'
    DARK_GREY = '#111827'
    WHITE = '#FFFFFF'
    
    # Domain specific
    ROAD_GREEN = '#15803d'
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
            'simulated': '#8B5CF6', # Violet for simulation (Distinct)
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