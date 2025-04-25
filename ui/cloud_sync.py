"""
Cloud Sync UI for POS system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import webbrowser

from assets.styles import COLORS, FONTS, STYLES
from utils.cloud_sync import (
    check_internet, 
    authenticate_google_drive, 
    start_sync, 
    stop_sync, 
    sync_now,
    get_sync_status
)

class CloudSyncFrame(tk.Frame):
    """Cloud sync frame for Google Drive integration"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLORS["bg_primary"])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title = tk.Label(header_frame, 
                        text="Cloud Sync",
                        font=FONTS["heading"],
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_primary"])
        title.pack(side=tk.LEFT, padx=20)
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status panel
        status_frame = tk.LabelFrame(main_container, 
                                   text="Connection Status",
                                   font=FONTS["regular_bold"],
                                   bg=COLORS["bg_primary"],
                                   fg=COLORS["text_primary"])
        status_frame.pack(fill=tk.X, pady=10)
        
        # Status indicators
        self.status_indicators = {}
        
        # Internet status
        internet_frame = tk.Frame(status_frame, bg=COLORS["bg_primary"], pady=5)
        internet_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(internet_frame, 
               text="Internet Connection:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT)
        
        self.status_indicators["internet"] = tk.Label(internet_frame, 
                                                  text="Checking...",
                                                  font=FONTS["regular"],
                                                  bg=COLORS["bg_primary"],
                                                  fg=COLORS["text_primary"])
        self.status_indicators["internet"].pack(side=tk.LEFT, padx=10)
        
        # Authentication status
        auth_frame = tk.Frame(status_frame, bg=COLORS["bg_primary"], pady=5)
        auth_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(auth_frame, 
               text="Google Drive Authentication:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT)
        
        self.status_indicators["auth"] = tk.Label(auth_frame, 
                                               text="Not authenticated",
                                               font=FONTS["regular"],
                                               bg=COLORS["bg_primary"],
                                               fg=COLORS["danger"])
        self.status_indicators["auth"].pack(side=tk.LEFT, padx=10)
        
        # Sync status
        sync_frame = tk.Frame(status_frame, bg=COLORS["bg_primary"], pady=5)
        sync_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(sync_frame, 
               text="Sync Status:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT)
        
        self.status_indicators["sync"] = tk.Label(sync_frame, 
                                               text="Not running",
                                               font=FONTS["regular"],
                                               bg=COLORS["bg_primary"],
                                               fg=COLORS["text_primary"])
        self.status_indicators["sync"].pack(side=tk.LEFT, padx=10)
        
        # Last sync time
        last_sync_frame = tk.Frame(status_frame, bg=COLORS["bg_primary"], pady=5)
        last_sync_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(last_sync_frame, 
               text="Last Sync:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT)
        
        self.status_indicators["last_sync"] = tk.Label(last_sync_frame, 
                                                    text="Never",
                                                    font=FONTS["regular"],
                                                    bg=COLORS["bg_primary"],
                                                    fg=COLORS["text_primary"])
        self.status_indicators["last_sync"].pack(side=tk.LEFT, padx=10)
        
        # Authentication panel
        auth_panel = tk.LabelFrame(main_container, 
                                 text="Google Drive Authentication",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        auth_panel.pack(fill=tk.X, pady=10)
        
        # Authentication description
        auth_desc = """To sync your POS data with Google Drive, you need to authenticate your Google account.
This will allow the application to store backup files in your Google Drive.

Step 1: Click the button below to sign in with your Google account
Step 2: Copy the authorization code from Google
Step 3: Paste the code below and click "Authenticate"
"""
        
        tk.Label(auth_panel, 
               text=auth_desc,
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"],
               justify=tk.LEFT,
               wraplength=700).pack(padx=10, pady=10)
        
        # Open browser button
        browser_btn = tk.Button(auth_panel,
                              text="Sign in with Google",
                              font=FONTS["regular_bold"],
                              bg=COLORS["primary"],
                              fg=COLORS["text_white"],
                              padx=15,
                              pady=5,
                              cursor="hand2",
                              command=self.open_auth_browser)
        browser_btn.pack(padx=10, pady=5)
        
        # Authorization code
        code_frame = tk.Frame(auth_panel, bg=COLORS["bg_primary"], pady=10)
        code_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(code_frame, 
               text="Authorization Code:",
               font=FONTS["regular_bold"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"]).pack(side=tk.LEFT)
        
        self.auth_code_var = tk.StringVar()
        auth_code_entry = tk.Entry(code_frame, 
                                 textvariable=self.auth_code_var,
                                 font=FONTS["regular"],
                                 width=40)
        auth_code_entry.pack(side=tk.LEFT, padx=10)
        
        auth_btn = tk.Button(code_frame,
                           text="Authenticate",
                           font=FONTS["regular"],
                           bg=COLORS["secondary"],
                           fg=COLORS["text_white"],
                           padx=10,
                           pady=2,
                           cursor="hand2",
                           command=self.authenticate)
        auth_btn.pack(side=tk.LEFT)
        
        # Sync controls panel
        controls_panel = tk.LabelFrame(main_container, 
                                     text="Sync Controls",
                                     font=FONTS["regular_bold"],
                                     bg=COLORS["bg_primary"],
                                     fg=COLORS["text_primary"])
        controls_panel.pack(fill=tk.X, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(controls_panel, bg=COLORS["bg_primary"], pady=10)
        buttons_frame.pack(fill=tk.X, padx=10)
        
        # Start sync button
        self.start_btn = tk.Button(buttons_frame,
                                 text="Start Background Sync",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["primary"],
                                 fg=COLORS["text_white"],
                                 padx=15,
                                 pady=8,
                                 cursor="hand2",
                                 command=self.start_background_sync)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        # Stop sync button
        self.stop_btn = tk.Button(buttons_frame,
                                text="Stop Background Sync",
                                font=FONTS["regular_bold"],
                                bg=COLORS["danger"],
                                fg=COLORS["text_white"],
                                padx=15,
                                pady=8,
                                cursor="hand2",
                                state=tk.DISABLED,
                                command=self.stop_background_sync)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Sync now button
        self.sync_now_btn = tk.Button(buttons_frame,
                                    text="Sync Now",
                                    font=FONTS["regular_bold"],
                                    bg=COLORS["secondary"],
                                    fg=COLORS["text_white"],
                                    padx=15,
                                    pady=8,
                                    cursor="hand2",
                                    command=self.sync_now)
        self.sync_now_btn.pack(side=tk.LEFT, padx=10)
        
        # Information panel
        info_panel = tk.LabelFrame(main_container, 
                                 text="Sync Information",
                                 font=FONTS["regular_bold"],
                                 bg=COLORS["bg_primary"],
                                 fg=COLORS["text_primary"])
        info_panel.pack(fill=tk.X, pady=10)
        
        info_text = """About Cloud Sync:
• Your POS data is stored locally and works offline
• Cloud sync uploads database backups to your Google Drive when connected to the internet
• If internet connection is lost, sync will automatically resume when connection is restored
• The system automatically checks for internet connection every minute
• Only backup files are synchronized, not individual transactions

Privacy & Security:
• Your data remains on your computer and in your Google Drive account
• No data is shared with any third-party servers
• Authentication is done directly with Google's servers
• The system only has access to its own application folder in your Google Drive
"""
        
        tk.Label(info_panel, 
               text=info_text,
               font=FONTS["regular"],
               bg=COLORS["bg_primary"],
               fg=COLORS["text_primary"],
               justify=tk.LEFT).pack(padx=10, pady=10)
    
    def open_auth_browser(self):
        """Open browser for Google authentication"""
        # In a real implementation, this would open the OAuth URL
        # For demo purposes, we'll just show a message
        messagebox.showinfo("Google Authentication", 
                          "In a real implementation, this would open your browser to the Google OAuth page.\n\n"
                          "For demo purposes, you can enter any text as the authorization code.")
    
    def authenticate(self):
        """Authenticate with Google using provided code"""
        auth_code = self.auth_code_var.get().strip()
        
        if not auth_code:
            messagebox.showinfo("Authentication", "Please enter the authorization code from Google.")
            return
        
        # Attempt authentication
        success, message = authenticate_google_drive(auth_code)
        
        if success:
            messagebox.showinfo("Authentication Successful", message)
            # Clear the code field
            self.auth_code_var.set("")
        else:
            messagebox.showerror("Authentication Failed", message)
        
        # Update status
        self.update_status()
    
    def start_background_sync(self):
        """Start background sync process"""
        status = get_sync_status()
        
        if not status["is_authenticated"]:
            messagebox.showinfo("Authentication Required", 
                              "Please authenticate with Google Drive before starting sync.")
            return
        
        # Start sync
        success, message = start_sync()
        
        if success:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Sync Started", message)
        else:
            messagebox.showerror("Sync Error", message)
        
        # Update status
        self.update_status()
    
    def stop_background_sync(self):
        """Stop background sync process"""
        success, message = stop_sync()
        
        if success:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            messagebox.showinfo("Sync Stopped", message)
        else:
            messagebox.showerror("Sync Error", message)
        
        # Update status
        self.update_status()
    
    def sync_now(self):
        """Perform immediate sync"""
        status = get_sync_status()
        
        if not status["is_authenticated"]:
            messagebox.showinfo("Authentication Required", 
                              "Please authenticate with Google Drive before syncing.")
            return
        
        # Do sync
        success, message = sync_now()
        
        if success:
            messagebox.showinfo("Sync Complete", message)
        else:
            messagebox.showerror("Sync Error", message)
        
        # Update status
        self.update_status()
    
    def update_status(self):
        """Update status indicators"""
        # Get current status
        status = get_sync_status()
        
        # Update internet status
        if status["has_internet"]:
            self.status_indicators["internet"].config(
                text="Connected",
                fg=COLORS["success"]
            )
        else:
            self.status_indicators["internet"].config(
                text="Disconnected",
                fg=COLORS["danger"]
            )
        
        # Update authentication status
        if status["is_authenticated"]:
            self.status_indicators["auth"].config(
                text="Authenticated",
                fg=COLORS["success"]
            )
        else:
            self.status_indicators["auth"].config(
                text="Not authenticated",
                fg=COLORS["danger"]
            )
        
        # Update sync status
        if status["is_syncing"]:
            self.status_indicators["sync"].config(
                text="Running",
                fg=COLORS["success"]
            )
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_indicators["sync"].config(
                text="Not running",
                fg=COLORS["text_primary"]
            )
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
        
        # Update last sync time
        if status["last_sync_time"]:
            last_sync = status["last_sync_time"].strftime("%Y-%m-%d %H:%M:%S")
            self.status_indicators["last_sync"].config(
                text=last_sync,
                fg=COLORS["text_primary"]
            )
        else:
            self.status_indicators["last_sync"].config(
                text="Never",
                fg=COLORS["text_primary"]
            )
    
    def on_show(self):
        """Called when frame is shown"""
        # Check internet connection
        check_internet()
        
        # Update status
        self.update_status()
        
        # Schedule regular status updates
        def schedule_update():
            self.update_status()
            self.after(5000, schedule_update)  # Update every 5 seconds
            
        schedule_update()