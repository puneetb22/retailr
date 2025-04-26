"""
Simple test for decimal handling with SQLite

This test verifies that:
1. Decimal values are correctly converted to float for SQLite storage
2. Decimal mathematical operations work as expected
"""

import sqlite3
from decimal import Decimal, InvalidOperation
import os

def test_decimal_storage():
    """Test decimal storage in SQLite"""
    # Create a test database
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Create a test table
    cursor.execute("""
        CREATE TABLE test_decimals (
            id INTEGER PRIMARY KEY,
            decimal_value REAL
        )
    """)
    
    # Test values
    test_values = [
        Decimal('123.45'),
        Decimal('0.01'),
        Decimal('999.999'),
        Decimal('0.0'),
        Decimal('10000')
    ]
    
    # Insert decimal values as float
    for i, value in enumerate(test_values):
        cursor.execute(
            "INSERT INTO test_decimals (id, decimal_value) VALUES (?, ?)",
            (i+1, float(value))
        )
    
    # Read back and verify
    cursor.execute("SELECT id, decimal_value FROM test_decimals ORDER BY id")
    results = cursor.fetchall()
    
    print("Decimal storage test results:")
    print("-" * 40)
    print(f"{'Original':15} | {'Stored':10} | {'Match?'}")
    print("-" * 40)
    
    all_passed = True
    for i, (id, stored_value) in enumerate(results):
        original = test_values[i]
        # Compare with small epsilon for floating point comparison
        match = abs(float(original) - stored_value) < 0.0001
        all_passed = all_passed and match
        print(f"{str(original):15} | {stored_value:<10.5f} | {'✓' if match else '✗'}")
    
    # Close connection
    conn.close()
    
    print("-" * 40)
    print(f"All tests {'PASSED' if all_passed else 'FAILED'}")
    return all_passed

def test_decimal_math():
    """Test decimal math operations"""
    # Test cases
    test_cases = [
        (Decimal('10.00'), Decimal('0.1'), Decimal('1.00')),  # 10.00 * 0.1 = 1.00
        (Decimal('100.00'), Decimal('0.05'), Decimal('5.00')),  # 100.00 * 0.05 = 5.00
        (Decimal('123.45'), Decimal('0.075'), Decimal('9.25875')),  # 123.45 * 0.075 = 9.25875
        (Decimal('1000.00'), Decimal('0.025'), Decimal('25.00'))  # 1000.00 * 0.025 = 25.00
    ]
    
    print("\nDecimal math test results:")
    print("-" * 70)
    print(f"{'Value 1':10} | {'Value 2':10} | {'Expected':10} | {'Result':10} | {'Match?'}")
    print("-" * 70)
    
    all_passed = True
    for val1, val2, expected in test_cases:
        result = val1 * val2
        match = abs(result - expected) < Decimal('0.0001')
        all_passed = all_passed and match
        print(f"{str(val1):10} | {str(val2):10} | {str(expected):10} | {str(result):10} | {'✓' if match else '✗'}")
    
    print("-" * 70)
    print(f"All tests {'PASSED' if all_passed else 'FAILED'}")
    return all_passed

def test_sqlite_decimal_insert():
    """Test inserting Decimal to SQLite with proper conversion"""
    # Create a test database
    db_path = "test_decimal.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a test table similar to sales
    cursor.execute("""
        CREATE TABLE test_sales (
            id INTEGER PRIMARY KEY,
            subtotal REAL,
            discount REAL,
            tax REAL,
            cgst REAL,
            sgst REAL,
            total REAL
        )
    """)
    
    # Test a typical sale scenario with decimal values
    subtotal = Decimal('1000.00')
    discount = Decimal('100.00')
    tax_rate = Decimal('0.05')  # 5%
    
    # Calculate values
    discounted_total = subtotal - discount
    tax = discounted_total * tax_rate
    cgst = tax / Decimal('2')
    sgst = tax / Decimal('2')
    total = discounted_total + tax
    
    # Try inserting with direct decimal values (this should fail)
    try:
        cursor.execute(
            "INSERT INTO test_sales (subtotal, discount, tax, cgst, sgst, total) VALUES (?, ?, ?, ?, ?, ?)",
            (subtotal, discount, tax, cgst, sgst, total)
        )
        print("\nDirect Decimal insert test: Failed (should have raised an error)")
    except sqlite3.InterfaceError as e:
        print(f"\nDirect Decimal insert test: Passed (expected error: {e})")
    
    # Try inserting with converted float values (this should work)
    try:
        cursor.execute(
            "INSERT INTO test_sales (subtotal, discount, tax, cgst, sgst, total) VALUES (?, ?, ?, ?, ?, ?)",
            (float(subtotal), float(discount), float(tax), float(cgst), float(sgst), float(total))
        )
        conn.commit()
        print("Converted float insert test: Passed")
    except Exception as e:
        print(f"Converted float insert test: Failed - {e}")
    
    # Read back and verify
    cursor.execute("SELECT * FROM test_sales")
    results = cursor.fetchall()
    
    print("\nStored values:")
    if results:
        row = results[0]
        print(f"Subtotal: {row[1]}")
        print(f"Discount: {row[2]}")
        print(f"Tax: {row[3]}")
        print(f"CGST: {row[4]}")
        print(f"SGST: {row[5]}")
        print(f"Total: {row[6]}")
    
    # Close and clean up
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    print("Running decimal handling tests for SQLite...")
    test_decimal_storage()
    test_decimal_math()
    test_sqlite_decimal_insert()
    print("\nAll tests completed.")