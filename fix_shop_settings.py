"""
Fix shop settings in the database to ensure they are properly stored and can be read.
"""
import sqlite3
import sys

def ensure_settings_exists():
    """Make sure the settings table exists"""
    try:
        conn = sqlite3.connect('pos_data.db')
        cursor = conn.cursor()
        
        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if not cursor.fetchone():
            print("Creating settings table...")
            cursor.execute('''
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT
            )
            ''')
            conn.commit()
            print("Settings table created.")
        else:
            print("Settings table already exists.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error ensuring settings table exists: {e}")
        return False

def update_shop_information():
    """Make sure the shop information settings are present and correct"""
    try:
        conn = sqlite3.connect('pos_data.db')
        cursor = conn.cursor()
        
        # Define the shop settings we need
        shop_settings = {
            'shop_name': 'Agritech Products Shop',
            'shop_address': 'Main Road, Maharashtra',
            'shop_phone': '+91 1234567890',
            'shop_gst': '27AABCU9603R1ZX',
            'shop_email': 'info@agritech.com',
            'shop_laid_no': 'L-12345-67890',
            'shop_lcsd_no': 'C-12345-67890',
            'shop_lfrd_no': 'F-12345-67890',
            'state_name': 'Maharashtra',
            'state_code': '27'
        }
        
        # Update or insert each setting
        for key, value in shop_settings.items():
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", (key,))
            if cursor.fetchone()[0] > 0:
                print(f"Updating existing setting: {key}")
                cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
            else:
                print(f"Inserting new setting: {key}")
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
        
        conn.commit()
        
        # Verify all settings are present
        cursor.execute("SELECT key, value FROM settings")
        current_settings = {row[0]: row[1] for row in cursor.fetchall()}
        
        print("\nCurrent Settings in Database:")
        for key, value in current_settings.items():
            print(f"  {key}: {value}")
            
        # Check if all our shop settings are in the database
        missing = []
        for key in shop_settings:
            if key not in current_settings:
                missing.append(key)
        
        if missing:
            print(f"\nWARNING: The following settings are still missing: {', '.join(missing)}")
        else:
            print("\nAll required shop settings are in the database.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating shop information: {e}")
        return False

if __name__ == "__main__":
    print("Fixing shop settings for invoice generation...")
    
    if not ensure_settings_exists():
        print("Failed to ensure settings table exists. Exiting.")
        sys.exit(1)
    
    if not update_shop_information():
        print("Failed to update shop information. Exiting.")
        sys.exit(1)
    
    print("\nDone! Shop settings are now properly configured.")