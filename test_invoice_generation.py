"""
Test the invoice number generation functionality.
"""

import datetime
import sqlite3
import os

# Create a temporary database for testing
db_path = "./test_invoice.db"

def setup_test_db():
    """Set up a test database"""
    # Remove the test database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # Create a new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables needed for testing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            invoice_number TEXT UNIQUE,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            cgst REAL DEFAULT 0,
            sgst REAL DEFAULT 0,
            total REAL NOT NULL,
            payment_type TEXT NOT NULL,
            payment_reference TEXT,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_status TEXT DEFAULT 'PAID',
            cash_amount REAL DEFAULT 0,
            upi_amount REAL DEFAULT 0,
            upi_reference TEXT,
            credit_amount REAL DEFAULT 0,
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                  ("invoice_prefix", "AGT"))
    
    # Commit and close
    conn.commit()
    conn.close()

def generate_invoice_number():
    """Generate an invoice number with the correct format"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get financial year for invoice number prefix (Indian Financial Year starts in April)
    today = datetime.datetime.now()
    if today.month >= 4:  # After April 1
        fy_start = today.year
        fy_end = today.year + 1
    else:
        fy_start = today.year - 1
        fy_end = today.year
    
    # Format as YY-YY (e.g., 24-25) exactly as requested by user
    fy_prefix = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
    
    # Get store name for invoice number prefix
    store_name = "AGT"  # Default prefix
    store_info = cursor.execute("SELECT value FROM settings WHERE key = 'invoice_prefix'").fetchone()
    if store_info and store_info[0].strip():
        store_name = store_info[0].strip()
    
    # Get next invoice number
    invoice_prefix = f"{fy_prefix}/{store_name}-"
    last_invoice = cursor.execute("""
        SELECT invoice_number FROM sales
        WHERE invoice_number LIKE ?
        ORDER BY id DESC LIMIT 1
    """, (f"{fy_prefix}/%",)).fetchone()
    
    if last_invoice:
        try:
            # Extract the numeric part
            last_part = last_invoice[0].split('-')[-1]
            last_num = int(last_part)
            invoice_num = last_num + 1
        except (ValueError, IndexError):
            invoice_num = 1
    else:
        invoice_num = 1
    
    # Format invoice number with 3 digits (e.g., 24-25/AGT-001)
    invoice_number = f"{fy_prefix}/{store_name}-{invoice_num:03d}"
    
    conn.close()
    return invoice_number

def test_invoice_number_format():
    """Test if the invoice number has the correct format"""
    setup_test_db()
    
    # Generate first invoice number
    invoice_number1 = generate_invoice_number()
    print(f"First invoice number: {invoice_number1}")
    
    # Validate format
    today = datetime.datetime.now()
    if today.month >= 4:  # After April 1
        expected_fy = f"{str(today.year)[-2:]}-{str(today.year+1)[-2:]}"
    else:
        expected_fy = f"{str(today.year-1)[-2:]}-{str(today.year)[-2:]}"
    
    expected_prefix = f"{expected_fy}/AGT-"
    assert invoice_number1.startswith(expected_prefix), f"Expected {invoice_number1} to start with {expected_prefix}"
    assert invoice_number1.endswith("001"), f"Expected {invoice_number1} to end with 001"
    
    # Insert a sale to simulate an existing invoice
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales 
        (customer_id, invoice_number, subtotal, total, payment_type, user_id) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (1, invoice_number1, 100.0, 100.0, "CASH", 1))
    conn.commit()
    conn.close()
    
    # Generate second invoice number
    invoice_number2 = generate_invoice_number()
    print(f"Second invoice number: {invoice_number2}")
    
    # Validate format and increment
    assert invoice_number2.startswith(expected_prefix), f"Expected {invoice_number2} to start with {expected_prefix}"
    assert invoice_number2.endswith("002"), f"Expected {invoice_number2} to end with 002"
    
    print("Invoice number generation test PASSED!")

if __name__ == "__main__":
    test_invoice_number_format()