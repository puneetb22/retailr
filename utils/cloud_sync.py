"""
Cloud sync utilities for POS system
Handles synchronization of data with Google Drive when internet is available
"""

import os
import datetime
import time
import threading
from pathlib import Path

# Flag to track internet connectivity
has_internet = False

# Flag to track if Google Drive API is initialized
drive_api_initialized = False

# Variable to store the last sync timestamp
last_sync_time = None

class CloudSyncManager:
    """Manager for cloud sync operations"""
    
    def __init__(self, backup_dir="./backups"):
        """Initialize the cloud sync manager"""
        self.backup_dir = backup_dir
        self.is_syncing = False
        self.sync_thread = None
        self.oauth_token = None
        self.cloud_folder_id = None
        
    def check_internet_connection(self):
        """Check if internet connection is available"""
        global has_internet
        
        try:
            # Try to connect to Google's DNS server
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            has_internet = True
            return True
        except OSError:
            has_internet = False
            return False
    
    def initialize_drive_api(self):
        """Initialize the Google Drive API"""
        global drive_api_initialized
        
        if not self.check_internet_connection():
            return False
        
        if drive_api_initialized:
            return True
            
        try:
            # Note: In a real implementation, this would use the Google Drive API
            # through the google-auth and google-api-python-client packages
            # 
            # This is a placeholder implementation for demo purposes
            
            # Check if token exists
            if not self.oauth_token:
                print("Google Drive API not authenticated. Please sign in first.")
                return False
            
            # Simulate API initialization
            time.sleep(1)
            drive_api_initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing Google Drive API: {e}")
            drive_api_initialized = False
            return False
    
    def authenticate_user(self, auth_code=None):
        """Authenticate with Google Drive using OAuth"""
        if not self.check_internet_connection():
            return False, "No internet connection. Please try again when connected."
        
        try:
            # In a real implementation, this would:
            # 1. Open a browser window for OAuth authentication
            # 2. Get authorization code from user
            # 3. Exchange code for access and refresh tokens
            # 4. Store tokens securely for future use
            
            # Simplified placeholder for demo
            if auth_code:
                # Simulate token exchange
                time.sleep(1)
                self.oauth_token = "simulated_oauth_token"
                
                # Find or create cloud folder
                self.cloud_folder_id = "simulated_folder_id"
                
                return True, "Successfully authenticated with Google Drive."
            else:
                return False, "Authentication code required."
                
        except Exception as e:
            return False, f"Authentication error: {e}"
    
    def start_background_sync(self):
        """Start background sync thread"""
        if self.sync_thread and self.sync_thread.is_alive():
            return False, "Sync already running."
            
        if not self.initialize_drive_api():
            return False, "Failed to initialize Google Drive API."
        
        # Start sync thread
        self.sync_thread = threading.Thread(target=self._background_sync_task)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        return True, "Background sync started."
    
    def _background_sync_task(self):
        """Background thread for periodic sync"""
        self.is_syncing = True
        
        try:
            while self.is_syncing:
                # Check for internet
                if not self.check_internet_connection():
                    time.sleep(60)  # Wait 1 minute before checking again
                    continue
                
                # Sync backups
                self.sync_backups()
                
                # Wait before next sync (10 minutes)
                for _ in range(60):  # Check every 10 seconds if sync should stop
                    if not self.is_syncing:
                        break
                    time.sleep(10)
        finally:
            self.is_syncing = False
    
    def stop_background_sync(self):
        """Stop background sync thread"""
        self.is_syncing = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        return True, "Background sync stopped."
    
    def sync_backups(self):
        """Sync backup files to Google Drive"""
        global last_sync_time
        
        if not self.initialize_drive_api():
            return False, "Failed to initialize Google Drive API."
        
        try:
            # Get list of backup files
            backup_dir = Path(self.backup_dir)
            if not backup_dir.exists():
                return False, f"Backup directory not found: {self.backup_dir}"
            
            # Get files modified since last sync
            files_to_sync = []
            for file_path in backup_dir.glob("*.db"):
                # If we've synced before, only get newer files
                if last_sync_time and file_path.stat().st_mtime < last_sync_time.timestamp():
                    continue
                files_to_sync.append(file_path)
            
            if not files_to_sync:
                return True, "No new backup files to sync."
            
            # Simulate upload to Google Drive
            print(f"Syncing {len(files_to_sync)} backup files to Google Drive...")
            
            # In a real implementation, this would upload each file
            # using the Google Drive API
            
            # Update last sync time
            last_sync_time = datetime.datetime.now()
            
            return True, f"Successfully synced {len(files_to_sync)} backup files."
            
        except Exception as e:
            return False, f"Sync error: {e}"
    
    def get_sync_status(self):
        """Get the current sync status"""
        status = {
            "has_internet": has_internet,
            "drive_api_initialized": drive_api_initialized,
            "is_authenticated": self.oauth_token is not None,
            "is_syncing": self.is_syncing,
            "last_sync_time": last_sync_time
        }
        
        return status


# Create a global instance of the cloud sync manager
cloud_sync_manager = CloudSyncManager()


def check_internet():
    """Check if internet connection is available"""
    return cloud_sync_manager.check_internet_connection()


def authenticate_google_drive(auth_code):
    """Authenticate with Google Drive"""
    return cloud_sync_manager.authenticate_user(auth_code)


def start_sync():
    """Start background sync"""
    return cloud_sync_manager.start_background_sync()


def stop_sync():
    """Stop background sync"""
    return cloud_sync_manager.stop_background_sync()


def sync_now():
    """Perform immediate sync"""
    return cloud_sync_manager.sync_backups()


def get_sync_status():
    """Get current sync status"""
    return cloud_sync_manager.get_sync_status()