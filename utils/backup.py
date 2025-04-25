"""
Backup utilities for POS system
Handles database backups and restores
"""

import os
import datetime
import shutil

# Backup directory
BACKUP_DIR = "./backups"

def create_backup(db_handler, backup_dir=BACKUP_DIR):
    """
    Create a backup of the database
    
    Args:
        db_handler: Database handler instance
        backup_dir: Directory to store backups (default: ./backups)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"pos_backup_{timestamp}.db")
        
        # Use the database handler's backup method
        success = db_handler.backup_database(backup_path)
        
        # Cleanup old backups (keep only last 10)
        if success:
            cleanup_old_backups(backup_dir)
            
        return success
    except Exception as e:
        print(f"Backup error: {e}")
        return False

def restore_backup(db_handler, backup_path):
    """
    Restore a database backup
    
    Args:
        db_handler: Database handler instance
        backup_path: Path to backup file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if backup exists
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            return False
        
        # Use the database handler's restore method
        return db_handler.restore_database(backup_path)
    except Exception as e:
        print(f"Restore error: {e}")
        return False

def list_backups(backup_dir=BACKUP_DIR):
    """
    List available database backups
    
    Args:
        backup_dir: Directory containing backups
        
    Returns:
        list: List of backup files with metadata (path, date, size)
    """
    backups = []
    
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # List backup files
        for file_name in os.listdir(backup_dir):
            if file_name.startswith("pos_backup_") and file_name.endswith(".db"):
                file_path = os.path.join(backup_dir, file_name)
                file_stats = os.stat(file_path)
                
                # Parse date from filename
                try:
                    date_str = file_name.replace("pos_backup_", "").replace(".db", "")
                    date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                except:
                    date = datetime.datetime.fromtimestamp(file_stats.st_mtime)
                
                # Add to list
                backups.append({
                    "path": file_path,
                    "filename": file_name,
                    "date": date,
                    "size": file_stats.st_size,
                    "size_mb": round(file_stats.st_size / (1024 * 1024), 2)
                })
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x["date"], reverse=True)
        
        return backups
    except Exception as e:
        print(f"List backups error: {e}")
        return []

def cleanup_old_backups(backup_dir=BACKUP_DIR, keep=10):
    """
    Clean up old backups, keeping only the most recent ones
    
    Args:
        backup_dir: Directory containing backups
        keep: Number of backups to keep
        
    Returns:
        int: Number of backups deleted
    """
    try:
        # Get list of backups
        backups = list_backups(backup_dir)
        
        # If we have more than 'keep' backups, delete the oldest ones
        if len(backups) > keep:
            # Get backups to delete (oldest first)
            to_delete = backups[keep:]
            
            # Delete old backups
            for backup in to_delete:
                os.remove(backup["path"])
            
            return len(to_delete)
        
        return 0
    except Exception as e:
        print(f"Cleanup error: {e}")
        return 0