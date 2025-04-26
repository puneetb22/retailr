"""
Test the integration between sales and invoices tables.
"""

import datetime
import sqlite3
import os
from decimal import Decimal

# Create a temporary database for testing
db_path = "./test_invoice_integration.db"

def setup_test_db():
    """Set up a test database with all required tables"""
    # Remove the test database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # Create a new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create necessary tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            village TEXT,
            email TEXT,
            gstin TEXT,
            credit_limit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER,
            purchase_price REAL DEFAULT 0,
            selling_price REAL NOT NULL,
            tax_rate REAL DEFAULT 0,
            hsn_code TEXT,
            barcode TEXT,
            reorder_level INTEGER DEFAULT 0,
            description TEXT,
            active INTEGER DEFAULT 1,
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
            user_id INTEGER NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            hsn_code TEXT,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            tax_rate REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
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
            file_path TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER,
            batch_number TEXT,
            quantity REAL NOT NULL,
            price_per_unit REAL NOT NULL,
            discount_percentage REAL DEFAULT 0,
            tax_percentage REAL DEFAULT 0,
            total_price REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_splits (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER NOT NULL,
            cash_amount REAL NOT NULL,
            upi_amount REAL NOT NULL,
            upi_reference TEXT,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                  ("invoice_prefix", "AGT"))
    
    # Add a test customer
    cursor.execute("""
        INSERT INTO customers (id, name, phone, address)
        VALUES (1, 'Walk-in Customer', '', '')
    """)
    
    # Add a test product
    cursor.execute("""
        INSERT INTO products (id, name, selling_price, tax_rate, hsn_code)
        VALUES (1, 'Test Fertilizer', 100.0, 5.0, '31010000')
    """)
    
    # Commit and close
    conn.commit()
    conn.close()

def generate_invoice_number():
    """Generate a properly formatted invoice number"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get financial year
    today = datetime.datetime.now()
    if today.month >= 4:  # After April 1 (Indian FY)
        fy_start = today.year
        fy_end = today.year + 1
    else:
        fy_start = today.year - 1
        fy_end = today.year
    
    fy_prefix = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
    
    # Get store prefix
    store_name = "AGT"
    store_info = cursor.execute("SELECT value FROM settings WHERE key = 'invoice_prefix'").fetchone()
    if store_info and store_info[0].strip():
        store_name = store_info[0].strip()
    
    # Get next invoice number
    last_invoice = cursor.execute("""
        SELECT invoice_number FROM sales
        WHERE invoice_number LIKE ?
        ORDER BY id DESC LIMIT 1
    """, (f"{fy_prefix}/%",)).fetchone()
    
    if last_invoice:
        try:
            last_part = last_invoice[0].split('-')[-1]
            last_num = int(last_part)
            invoice_num = last_num + 1
        except (ValueError, IndexError):
            invoice_num = 1
    else:
        invoice_num = 1
    
    invoice_number = f"{fy_prefix}/{store_name}-{invoice_num:03d}"
    
    conn.close()
    return invoice_number

def test_sales_invoice_integration():
    """Test the integration between sales and invoices tables"""
    setup_test_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate invoice number
    invoice_number = generate_invoice_number()
    print(f"Generated invoice number: {invoice_number}")
    
    # Simulate completing a sale
    # 1. First create a sale record
    subtotal = 100.0
    tax_amount = Decimal(str(subtotal)) * Decimal('0.05')  # 5% GST
    total_amount = subtotal + float(tax_amount)
    
    cursor.execute("""
        INSERT INTO sales 
        (customer_id, invoice_number, subtotal, discount, tax, cgst, sgst, total, payment_type, sale_date, user_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,  # Walk-in Customer
        invoice_number,
        subtotal,
        0.0,  # No discount
        float(tax_amount),
        float(tax_amount / Decimal('2')),  # CGST (2.5%)
        float(tax_amount / Decimal('2')),  # SGST (2.5%)
        total_amount,
        "CASH",
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        1  # Default user ID
    ))
    
    sale_id = cursor.lastrowid
    print(f"Created sale with ID: {sale_id}")
    
    # 2. Add a sale item
    cursor.execute("""
        INSERT INTO sale_items
        (sale_id, product_id, product_name, hsn_code, quantity, price, tax_rate, tax_amount, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sale_id,
        1,  # Test product
        "Test Fertilizer",
        "31010000",
        1.0,  # Quantity
        100.0,  # Price
        5.0,  # Tax rate
        float(tax_amount),
        total_amount
    ))
    
    # 3. Now add the corresponding invoice record
    cursor.execute("""
        INSERT INTO invoices
        (invoice_number, customer_id, subtotal, tax_amount, total_amount, payment_method, cash_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        1,  # Walk-in Customer
        subtotal,
        float(tax_amount),
        total_amount,
        "CASH",
        total_amount  # Full amount paid in cash
    ))
    
    invoice_id = cursor.lastrowid
    print(f"Created invoice with ID: {invoice_id}")
    
    # 4. Add invoice_items record
    cursor.execute("""
        INSERT INTO invoice_items
        (invoice_id, product_id, quantity, price_per_unit, tax_percentage, total_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        invoice_id,
        1,  # Test product
        1.0,  # Quantity
        100.0,  # Price
        5.0,  # Tax rate
        total_amount
    ))
    
    # 5. Update invoice file path
    file_path = f"./invoices/INV_{invoice_number.replace('/', '-')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    cursor.execute("UPDATE invoices SET file_path = ? WHERE id = ?", (file_path, invoice_id))
    
    # Commit the changes
    conn.commit()
    
    # Now test retrieving invoice information
    # 1. First check if we can find the invoice by date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    invoice_by_date = cursor.execute("""
        SELECT i.id, i.invoice_number, c.name, i.total_amount, i.payment_method
        FROM invoices i
        LEFT JOIN customers c ON i.customer_id = c.id
        WHERE DATE(i.invoice_date) = ?
    """, (today,)).fetchone()
    
    assert invoice_by_date is not None, "Invoice not found by date"
    assert invoice_by_date[1] == invoice_number, f"Expected invoice number {invoice_number}, got {invoice_by_date[1]}"
    print(f"Found invoice by date: {invoice_by_date}")
    
    # 2. Check if we can get invoice details
    invoice_details = cursor.execute("""
        SELECT i.*, c.name, c.phone, c.address
        FROM invoices i
        LEFT JOIN customers c ON i.customer_id = c.id
        WHERE i.id = ?
    """, (invoice_id,)).fetchone()
    
    assert invoice_details is not None, "Invoice details not found"
    assert invoice_details[1] == invoice_number, f"Expected invoice number {invoice_number}, got {invoice_details[1]}"
    print(f"Found invoice details: ID={invoice_details[0]}, Number={invoice_details[1]}, Amount={invoice_details[6]}")
    
    # 3. Check if we can get invoice items
    invoice_items = cursor.execute("""
        SELECT *
        FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,)).fetchall()
    
    assert len(invoice_items) == 1, f"Expected 1 invoice item, got {len(invoice_items)}"
    print(f"Found {len(invoice_items)} invoice items")
    
    conn.close()
    print("Sales-Invoice integration test PASSED!")

if __name__ == "__main__":
    test_sales_invoice_integration()