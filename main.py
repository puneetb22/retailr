#!/usr/bin/env python3
"""
Agritech Point of Sale System - Main Application Entry
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, PhotoImage

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_handler import DBHandler
from ui.login import AutoLoginFrame
from ui.dashboard import Dashboard
from utils.config import load_config, save_config
from assets.styles import COLORS, FONTS, STYLES

class POSApplication(tk.Tk):
    """Main application class for the POS system"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db = DBHandler()
        if not self.db.is_initialized:
            messagebox.showerror("Database Error", 
                                 "Failed to initialize database. Please check permissions and disk space.")
            self.destroy()
            sys.exit(1)
            
        # Load configuration
        self.config = load_config()
        
        # Setup main window
        self.title(f"{self.config.get('shop_name', 'Agritech')} - Point of Sale")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Set icon
        try:
            # We'll use a placeholder icon if available
            self.iconphoto(True, PhotoImage(file="assets/logo.png"))
        except:
            pass
        
        # Dictionary to hold all frames
        self.frames = {}
        
        # Initialize UI
        self.setup_ui()
        
        # Display auto-login
        self.show_frame("login")
        
    def setup_ui(self):
        """Setup the main UI container and frames"""
        # Main container for all frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Initialize login frame
        login_frame = AutoLoginFrame(container, self)
        self.frames["login"] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create dashboard (will be shown after auto-login)
        dashboard = Dashboard(container, self)
        self.frames["dashboard"] = dashboard
        dashboard.grid(row=0, column=0, sticky="nsew")
        
    def show_frame(self, frame_name):
        """Raise the specified frame to the top"""
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            # Call on_show method if exists (for refreshing data)
            if hasattr(frame, 'on_show'):
                frame.on_show()
    
    def show_dashboard(self):
        """Show the main dashboard"""
        self.show_frame("dashboard")
        
    def exit_application(self):
        """Safely exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            # Save any pending configuration changes
            save_config(self.config)
            # Close database connection
            self.db.close()
            # Destroy the tkinter root
            self.destroy()
            
    def create_backup(self):
        """Trigger a database backup"""
        from utils.backup import create_backup
        success = create_backup(self.db)
        if success:
            messagebox.showinfo("Backup", "Backup created successfully!")
        else:
            messagebox.showerror("Backup Error", "Failed to create backup. Please check permissions.")

if __name__ == "__main__":
    app = POSApplication()
    # Set window to start centered
    window_width = app.winfo_width()
    window_height = app.winfo_height()
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    app.geometry(f"+{x}+{y}")
    app.mainloop()
