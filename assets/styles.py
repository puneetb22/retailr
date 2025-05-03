"""
Style definitions for the POS system
Contains color schemes, fonts, and common styles
"""

# Light theme color scheme
LIGHT_THEME = {
    # Primary colors
    "primary": "#4e73df",  # Main blue color
    "primary_light": "#6f8ce9",
    "primary_dark": "#2e59d9",
    
    # Secondary colors
    "secondary": "#1cc88a",  # Green color
    "secondary_dark": "#13855c",
    
    # Background colors
    "bg_primary": "#f8f9fc",  # Light gray background
    "bg_secondary": "#eaecf4",  # Slightly darker gray
    "bg_white": "#ffffff",
    "bg_light": "#f0f2f8",  # Very light gray
    
    # Text colors
    "text_primary": "#5a5c69",  # Main text color
    "text_secondary": "#858796",  # Secondary text color
    "text_white": "#ffffff",
    
    # Status/Alert colors
    "success": "#1cc88a",  # Green
    "danger": "#e74a3b",   # Red
    "warning": "#f6c23e",  # Yellow
    "info": "#36b9cc",     # Light blue
    
    # Border and highlight colors
    "border": "#d1d3e2",   # Light gray border color
    
    # Additional status colors (light versions)
    "success_light": "#e6fff5",
    "danger_light": "#fff5f5",
    "warning_light": "#fff9e6",
    "info_light": "#e6f9ff"
}

# Dark theme color scheme
DARK_THEME = {
    # Primary colors
    "primary": "#3a56b0",  # Darker blue color
    "primary_light": "#4e73df",
    "primary_dark": "#2a3d7d",
    
    # Secondary colors
    "secondary": "#19a372",  # Darker green color
    "secondary_dark": "#0f724f",
    
    # Background colors
    "bg_primary": "#1e1e2d",  # Dark background
    "bg_secondary": "#2a2a3c",  # Slightly lighter dark
    "bg_white": "#2a2a3c",
    "bg_light": "#24243a",  # Light dark background
    
    # Text colors
    "text_primary": "#e0e0e0",  # Light text color
    "text_secondary": "#b0b0b0",  # Secondary light text color
    "text_white": "#ffffff",
    
    # Status/Alert colors
    "success": "#1cc88a",  # Green
    "danger": "#e74a3b",   # Red
    "warning": "#f6c23e",  # Yellow
    "info": "#36b9cc",     # Light blue
    
    # Border and highlight colors
    "border": "#3a3a50",   # Dark border color
    
    # Additional status colors (light versions)
    "success_light": "#132218",
    "danger_light": "#2d1414",
    "warning_light": "#2d2411",
    "info_light": "#112125"
}

# Default to light theme
COLORS = LIGHT_THEME.copy()

# Function to switch themes
def set_theme(theme_name="light"):
    """
    Set the application theme
    
    Args:
        theme_name (str): Either 'light' or 'dark'
    
    Returns:
        dict: The new color scheme
    """
    global COLORS
    
    if theme_name.lower() == "dark":
        COLORS.update(DARK_THEME)
    else:  # Default to light theme
        COLORS.update(LIGHT_THEME)
        
    return COLORS

# Font definitions
FONTS = {
    # Headings
    "heading": ("Arial", 18, "bold"),
    "heading_light": ("Arial", 18, "bold"),
    "heading2": ("Arial", 16, "bold"),
    "subheading": ("Arial", 14, "bold"),
    
    # Regular text
    "regular": ("Arial", 12),
    "regular_bold": ("Arial", 12, "bold"),
    "regular_italic": ("Arial", 12, "italic"),
    "regular_light": ("Arial", 12),
    "regular_small": ("Arial", 11),  # Added smaller regular font
    
    # Small text
    "small": ("Arial", 10),
    "small_bold": ("Arial", 10, "bold"),
    "small_italic": ("Arial", 10, "italic"),
    
    # Navigation
    "nav_title": ("Arial", 12, "bold"),
    "nav_item": ("Arial", 11)
}

# Common styles for widgets
STYLES = {
    # Button styles
    "button_primary": {
        "bg": COLORS["primary"],
        "fg": COLORS["text_white"],
        "activebackground": COLORS["primary_dark"],
        "activeforeground": COLORS["text_white"],
        "font": FONTS["regular"],
        "cursor": "hand2",
        "relief": "flat",
        "padx": 15,
        "pady": 5
    },
    
    "button_secondary": {
        "bg": COLORS["secondary"],
        "fg": COLORS["text_white"],
        "activebackground": COLORS["secondary_dark"],
        "activeforeground": COLORS["text_white"],
        "font": FONTS["regular"],
        "cursor": "hand2",
        "relief": "flat",
        "padx": 15,
        "pady": 5
    },
    
    "button_danger": {
        "bg": COLORS["danger"],
        "fg": COLORS["text_white"],
        "activebackground": "#c0392b",  # Darker red
        "activeforeground": COLORS["text_white"],
        "font": FONTS["regular"],
        "cursor": "hand2",
        "relief": "flat",
        "padx": 15,
        "pady": 5
    },
    
    # Entry field styles
    "entry_normal": {
        "font": FONTS["regular"],
        "relief": "solid",
        "borderwidth": 1
    },
    
    # Label styles
    "label_title": {
        "font": FONTS["heading"],
        "bg": COLORS["bg_primary"],
        "fg": COLORS["text_primary"],
        "padx": 10,
        "pady": 10
    },
    
    "label_normal": {
        "font": FONTS["regular"],
        "bg": COLORS["bg_primary"],
        "fg": COLORS["text_primary"]
    }
}