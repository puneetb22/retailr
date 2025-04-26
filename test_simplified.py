"""
Simplified test for invoice table integration
"""

import sqlite3
import datetime
import os

# Create test DB path
db_path = "test_simple.db"

def setup_db():
    """Set up a test database"""
    # Remove if exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create a new connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT,
            total REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT,
            total_amount REAL,
            file_path TEXT
        )
    """)
    
    conn.commit()
    return conn

def test_simple_integration():
    """Test simple integration between sales and invoices"""
    conn = setup_db()
    cursor = conn.cursor()
    
    # Create a test invoice number
    invoice_number = "25-26/AGT-001"
    
    # Insert into sales
    cursor.execute(
        "INSERT INTO sales (invoice_number, total) VALUES (?, ?)",
        (invoice_number, 105.0)
    )
    
    # Insert into invoices
    cursor.execute(
        "INSERT INTO invoices (invoice_number, total_amount) VALUES (?, ?)",
        (invoice_number, 105.0)
    )
    
    # Update file path
    file_path = f"./invoices/INV_{invoice_number.replace('/', '-')}.pdf"
    invoice_id = cursor.lastrowid
    cursor.execute(
        "UPDATE invoices SET file_path = ? WHERE id = ?",
        (file_path, invoice_id)
    )
    
    conn.commit()
    
    # Test retrieving
    result = cursor.execute(
        "SELECT s.id, s.invoice_number, i.id, i.invoice_number, i.file_path FROM sales s JOIN invoices i ON s.invoice_number = i.invoice_number"
    ).fetchone()
    
    if result:
        print(f"Sale ID: {result[0]}, Invoice Number: {result[1]}")
        print(f"Invoice ID: {result[2]}, Invoice Number: {result[3]}")
        print(f"Invoice File Path: {result[4]}")
        print("Integration test PASSED")
    else:
        print("Failed to retrieve integrated records")
    
    conn.close()

if __name__ == "__main__":
    test_simple_integration()