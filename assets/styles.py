"""
Style definitions for the POS system
Contains color schemes, fonts, and common styles
"""

# Color scheme
COLORS = {
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
    
    # Text colors
    "text_primary": "#5a5c69",  # Main text color
    "text_secondary": "#858796",  # Secondary text color
    "text_white": "#ffffff",
    
    # Status/Alert colors
    "success": "#1cc88a",  # Green
    "danger": "#e74a3b",   # Red
    "warning": "#f6c23e",  # Yellow
    "info": "#36b9cc",     # Light blue
    
    # Additional status colors (light versions)
    "success_light": "#e6fff5",
    "danger_light": "#fff5f5",
    "warning_light": "#fff9e6",
    "info_light": "#e6f9ff"
}

# Font definitions
FONTS = {
    # Headings
    "heading": ("Arial", 18, "bold"),
    "heading_light": ("Arial", 18, "bold"),
    "subheading": ("Arial", 14, "bold"),
    
    # Regular text
    "regular": ("Arial", 12),
    "regular_bold": ("Arial", 12, "bold"),
    "regular_italic": ("Arial", 12, "italic"),
    "regular_light": ("Arial", 12),
    
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