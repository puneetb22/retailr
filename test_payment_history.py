"""
Test payment history functionality.
"""
import os
import sqlite3
import datetime

def setup_test_db():
    """Set up a test database"""
    # Use a temporary test database
    test_db_path = "test_payment.db"
    
    # Delete existing test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        
    # Create and connect to the test database
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        credit_limit REAL DEFAULT 0
    )
    """)
    
    # Create invoices table
    cursor.execute("""
    CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT NOT NULL,
        customer_id INTEGER,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL,
        invoice_date TEXT NOT NULL,
        credit_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    """)
    
    # Create customer_transactions table
    cursor.execute("""
    CREATE TABLE customer_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        reference_id INTEGER,
        transaction_date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    """)
    
    # Create customer_payments table
    cursor.execute("""
    CREATE TABLE customer_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        invoice_id INTEGER,
        amount REAL,
        payment_method TEXT,
        reference_number TEXT,
        payment_date TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    )
    """)
    
    conn.commit()
    return conn, cursor

def insert_test_data(conn, cursor):
    """Insert test data into the database"""
    # Insert a test customer
    cursor.execute(
        "INSERT INTO customers (name, phone, address, credit_limit) VALUES (?, ?, ?, ?)",
        ("Test Customer", "1234567890", "Test Address", 10000.0)
    )
    customer_id = cursor.lastrowid
    
    # Insert a test invoice
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO invoices (invoice_number, customer_id, total_amount, payment_method, payment_status, invoice_date, credit_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("INV-001", customer_id, 5000.0, "CREDIT", "PARTIALLY_PAID", today, 3000.0)
    )
    invoice_id = cursor.lastrowid
    
    # Insert a payment record with depositor info in notes
    payment_date = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO customer_payments (customer_id, invoice_id, amount, payment_method, reference_number, payment_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (customer_id, invoice_id, 2000.0, "CASH", "", payment_date, "First payment\nDepositor: John Doe")
    )
    
    # Insert a transaction record (older system)
    cursor.execute(
        "INSERT INTO customer_transactions (customer_id, amount, transaction_type, reference_id, transaction_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (customer_id, 2000.0, "CREDIT_PAYMENT", invoice_id, today, "Payment for Invoice #INV-001 via CASH by John Doe")
    )
    
    conn.commit()
    return customer_id, invoice_id

def test_payment_history():
    """Test payment history functionality"""
    print("Testing payment history functionality...")
    
    # Setup test database
    conn, cursor = setup_test_db()
    customer_id, invoice_id = insert_test_data(conn, cursor)
    
    # Verify customer exists
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        print("ERROR: Customer not created correctly")
        return False
    print(f"✓ Customer created successfully: {customer[1]}")
    
    # Test querying payment history from customer_payments
    cursor.execute("""
        SELECT 
            cp.id, 
            cp.payment_date, 
            inv.invoice_number,
            cp.amount, 
            cp.payment_method, 
            cp.reference_number,
            cp.notes,
            CASE
                WHEN INSTR(cp.notes, 'Depositor:') > 0 
                THEN SUBSTR(cp.notes, INSTR(cp.notes, 'Depositor:') + 10)
                ELSE ''
            END as depositor
        FROM customer_payments cp
        LEFT JOIN invoices inv ON cp.invoice_id = inv.id
        WHERE cp.customer_id = ?
        ORDER BY cp.payment_date DESC
    """, (customer_id,))
    payments = cursor.fetchall()
    
    if not payments or len(payments) == 0:
        print("ERROR: No payment records found in customer_payments")
        return False
    
    print(f"✓ Found {len(payments)} payment record(s) in customer_payments table")
    
    # Check if depositor is extracted correctly
    for payment in payments:
        depositor = payment[7].strip() if payment[7] else ""
        if depositor and depositor == "John Doe":
            print(f"✓ Depositor field extracted correctly: {depositor}")
        else:
            print(f"ERROR: Depositor field not extracted correctly: {depositor}")
    
    # Test querying payment history from customer_transactions as fallback
    cursor.execute("""
        SELECT 
            ct.id, 
            ct.transaction_date, 
            i.invoice_number,
            ct.amount, 
            CASE 
                WHEN ct.notes LIKE '%via CASH%' THEN 'CASH'
                WHEN ct.notes LIKE '%via UPI%' THEN 'UPI'
                WHEN ct.notes LIKE '%via CHEQUE%' THEN 'CHEQUE'
                ELSE ''
            END as payment_method,
            ct.notes,
            CASE
                WHEN ct.notes LIKE '%by %' 
                THEN SUBSTR(ct.notes, INSTR(ct.notes, 'by ') + 3)
                ELSE ''
            END as depositor
        FROM customer_transactions ct
        LEFT JOIN invoices i ON ct.reference_id = i.id
        WHERE ct.customer_id = ? AND ct.transaction_type = 'CREDIT_PAYMENT'
        ORDER BY ct.transaction_date DESC
    """, (customer_id,))
    trans_payments = cursor.fetchall()
    
    if not trans_payments or len(trans_payments) == 0:
        print("ERROR: No payment records found in customer_transactions")
        return False
    
    print(f"✓ Found {len(trans_payments)} payment record(s) in customer_transactions table")
    
    # Check if depositor is extracted correctly from transaction notes
    for payment in trans_payments:
        depositor = payment[6]
        if depositor and depositor == "John Doe":
            print(f"✓ Depositor field extracted correctly from transaction: {depositor}")
        else:
            print(f"ERROR: Depositor field not extracted correctly from transaction: {depositor}")
    
    # Close connection
    conn.close()
    
    # Clean up test database
    os.remove("test_payment.db")
    
    print("✓ Payment history test completed successfully")
    return True

if __name__ == "__main__":
    test_payment_history()