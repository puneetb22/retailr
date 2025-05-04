import sqlite3
import json

# Connect to the SQLite database
conn = sqlite3.connect('pos_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def pretty_print(title, data):
    print(f"\n===== {title} =====")
    print(json.dumps(data, indent=2))

# Check tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [table[0] for table in cursor.fetchall()]
pretty_print("TABLES IN DATABASE", tables)

# Check if settings table exists
if 'settings' in tables:
    cursor.execute("PRAGMA table_info(settings);")
    settings_columns = [col[1] for col in cursor.fetchall()]
    pretty_print("SETTINGS TABLE COLUMNS", settings_columns)
    
    # Get all settings data
    cursor.execute("SELECT * FROM settings;")
    settings_data = [dict(row) for row in cursor.fetchall()]
    pretty_print("SETTINGS DATA", settings_data)
else:
    print("\nNo 'settings' table found.")

# Check how shop_info is retrieved in pdf_invoice_generator.py
print("\n===== PDF INVOICE GENERATOR SHOP INFO RETRIEVAL =====")
with open('utils/pdf_invoice_generator.py', 'r') as f:
    content = f.read()
    shop_info_retrieval = [line for line in content.split('\n') if 'shop_' in line or 'get_shop' in line]
    for line in shop_info_retrieval:
        print(line.strip())

# If there's no settings table, check if we have shop_info table
if 'shop_info' in tables:
    cursor.execute("PRAGMA table_info(shop_info);")
    shop_info_columns = [col[1] for col in cursor.fetchall()]
    pretty_print("SHOP_INFO TABLE COLUMNS", shop_info_columns)
    
    # Get all shop_info data
    cursor.execute("SELECT * FROM shop_info;")
    shop_info_data = [dict(row) for row in cursor.fetchall()]
    pretty_print("SHOP_INFO DATA", shop_info_data)

# Close the connection
conn.close()