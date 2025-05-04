"""
Test script to verify the shop information mapping in the invoice generation.
"""
import os
import sqlite3
from io import BytesIO
from utils.pdf_invoice_generator import generate_pdf_invoice

def print_settings():
    """Print all settings from the database"""
    conn = sqlite3.connect('./pos_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM settings")
    settings = cursor.fetchall()
    print("\n===== SETTINGS TABLE =====")
    for row in settings:
        print(f"ID: {row['id']}, Key: {row['key']}, Value: {row['value']}")
    
    conn.close()

def add_shop_license_fields():
    """Add license fields if they don't exist"""
    conn = sqlite3.connect('./pos_data.db')
    cursor = conn.cursor()
    
    # Check if shop_laid_no exists
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'shop_laid_no'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                     ('shop_laid_no', 'L-12345-67890'))
    
    # Check if shop_lcsd_no exists
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'shop_lcsd_no'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                     ('shop_lcsd_no', 'C-12345-67890'))
    
    # Check if shop_lfrd_no exists
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'shop_lfrd_no'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                     ('shop_lfrd_no', 'F-12345-67890'))
    
    # Make sure we have shop_gst instead of shop_gstin
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'shop_gst'")
    if cursor.fetchone()[0] == 0:
        # Check if shop_gstin exists
        cursor.execute("SELECT value FROM settings WHERE key = 'shop_gst'")
        existing = cursor.fetchone()
        if existing:
            # Use the existing value
            gst_value = existing[0]
        else:
            # Use the value from shop_gstin if it exists
            cursor.execute("SELECT value FROM settings WHERE key = 'shop_gstin'")
            gstin_row = cursor.fetchone()
            if gstin_row:
                gst_value = gstin_row[0]
            else:
                gst_value = '27AABCU9603R1ZX'  # Default value
            
            # Insert the shop_gst entry
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                         ('shop_gst', gst_value))
    
    conn.commit()
    conn.close()

def test_invoice_generation():
    """Test generating an invoice with sample data"""
    # Sample invoice data
    invoice_data = {
        'invoice_number': 'INV-TEST-001',
        'date': '04/05/2025',
        'time': '10:30 AM',
        'customer': {
            'name': 'Test Customer',
            'phone': '9876543210',
            'address': 'Test Village, Test District',
            'email': 'test@example.com',
            'gstin': ''
        },
        'items': [
            {
                'product_id': 1,
                'name': 'Test Fertilizer',
                'rate': 500,
                'quantity': 2,
                'discount_percentage': 5,
                'total': 950,
                'hsn': '3105',
                'unit': 'kg'
            }
        ],
        'payment': {
            'method': 'Cash',
            'status': 'PAID',
            'subtotal': 1000,
            'discount': 50,
            'cgst': 47.5,
            'sgst': 47.5,
            'total': 1045
        },
        'store_info': {}  # We want this to be fetched from the database
    }
    
    # Generate the PDF invoice
    pdf_buffer = BytesIO()
    generate_pdf_invoice(invoice_data, pdf_buffer)
    
    # Save the generated PDF to a file
    with open("test_invoice_output.pdf", "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    print(f"\nTest invoice saved as: {os.path.abspath('test_invoice_output.pdf')}")

if __name__ == "__main__":
    print("\n===== TESTING SHOP INFORMATION IN INVOICE =====")
    
    # Step 1: Print existing settings
    print_settings()
    
    # Step 2: Add license fields if needed
    add_shop_license_fields()
    
    # Step 3: Print settings after any additions
    print_settings()
    
    # Step 4: Generate a test invoice
    test_invoice_generation()