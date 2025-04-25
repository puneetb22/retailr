"""
Auto-login screen for POS system
"""

import tkinter as tk
from tkinter import ttk
import time
from assets.styles import COLORS, FONTS, STYLES

class AutoLoginFrame(tk.Frame):
    """Auto login frame that automatically logs in as shopkeeper"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Central container for login elements
        container = tk.Frame(self, bg=COLORS["bg_primary"], padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Shop name
        shop_name = self.controller.config.get('shop_name', 'Agritech Products Shop')
        title = tk.Label(container, 
                         text=shop_name,
                         font=FONTS["heading"], 
                         bg=COLORS["bg_primary"],
                         fg=COLORS["text_primary"])
        title.pack(pady=(0, 30))
        
        # Logo (placeholder - would be replaced by actual logo)
        logo_frame = tk.Frame(container, bg=COLORS["bg_secondary"], 
                             width=150, height=150)
        logo_frame.pack(pady=10)
        
        logo_label = tk.Label(logo_frame, text="POS", 
                             font=("Arial", 36, "bold"),
                             bg=COLORS["bg_secondary"],
                             fg=COLORS["text_primary"])
        logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Welcome message
        welcome_msg = tk.Label(container, 
                              text="Welcome to Point of Sale System",
                              font=FONTS["subheading"],
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
        welcome_msg.pack(pady=(20, 5))
        
        # Auto login message
        self.login_msg = tk.Label(container, 
                                 text="Automatic login in progress...",
                                 font=FONTS["regular"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_secondary"])
        self.login_msg.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(container, 
                                       orient="horizontal", 
                                       length=300, 
                                       mode="determinate")
        self.progress.pack(pady=20)
        
        # Version info at bottom
        version = self.controller.config.get('version', '1.0.0')
        version_label = tk.Label(self, 
                                text=f"Version {version}", 
                                font=FONTS["small"],
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_secondary"])
        version_label.pack(side=tk.BOTTOM, pady=10)
    
    def on_show(self):
        """Called when frame is shown"""
        # Reset progress
        self.progress["value"] = 0
        self.login_msg.config(text="Automatic login in progress...")
        
        # Simulate login process
        self.start_login_sequence()
    
    def start_login_sequence(self):
        """Simulate login process with progress bar animation"""
        if self.progress["value"] < 100:
            self.progress["value"] += 5
            
            # Update message based on progress
            if self.progress["value"] < 30:
                self.login_msg.config(text="Loading system modules...")
            elif self.progress["value"] < 60:
                self.login_msg.config(text="Connecting to database...")
            elif self.progress["value"] < 90:
                self.login_msg.config(text="Preparing dashboard...")
            else:
                self.login_msg.config(text="Welcome, Shopkeeper!")
                
            # Continue animation
            self.after(50, self.start_login_sequence)
        else:
            # Login complete, show dashboard
            self.after(500, self.controller.show_dashboard)
