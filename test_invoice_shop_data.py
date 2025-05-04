"""
Test the invoice generator's ability to read shop information from the database.
"""
import sqlite3
import os
from io import BytesIO
from utils.pdf_invoice_generator import generate_invoice

# First set up a very basic sample invoice data
sample_invoice = {
    'invoice_number': 'TEST-SHOP-INFO-001',
    'date': '04/05/2025',
    'customer': {
        'name': 'Test Customer',
        'phone': '9876543210',
        'address': 'Test Address',
    },
    'items': [
        {
            'name': 'Test Product',
            'quantity': 1,
            'rate': 100,
            'total': 100,
        }
    ],
    'payment': {
        'subtotal': 100,
        'discount': 0,
        'cgst': 5,
        'sgst': 5,
        'total': 110,
        'method': 'Cash',
        'status': 'PAID'
    }
}

# Generate the invoice directly to a file
output_path = os.path.abspath("test_shop_info_output.pdf")
print("Generating test invoice...")
generate_invoice(sample_invoice, output_path)

print(f"Test invoice saved to: {output_path}")
print("Please open this PDF and check if the shop information is correctly displayed.")