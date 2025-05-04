"""
Test Excel invoice generation with the shop_bill.xlsx template
"""

import os
from datetime import datetime
from utils.invoice_generator import generate_invoice

def test_excel_invoice():
    """Test generating an Excel invoice with sample data"""
    
    # Create sample invoice data
    invoice_data = {
        "invoice_number": "AGT2025050401",
        "date": datetime.now().strftime("%d-%m-%Y"),
        "time": datetime.now().strftime("%H:%M"),
        "template_type": "shop_bill",
        "store_info": {
            "name": "Agritech Products Shop",
            "address": "Main Road, Nashik, Maharashtra",
            "phone": "+91 9876543210",
            "email": "contact@agritech.com",
            "gstin": "27AABCU9603R1ZX",
            "laid_no": "L-12345",
            "lcsd_no": "C-54321",
            "lfrd_no": "F-98765",
            "state_name": "Maharashtra",
            "state_code": "27",
            "terms_conditions": "Goods once sold cannot be returned. Please check goods before leaving."
        },
        "customer": {
            "name": "Raj Kumar",
            "phone": "9876543210",
            "address": "Farm House, Rural Road, Nashik",
            "email": "raj@example.com",
            "gstin": "27AAACU9603R1ZX"
        },
        "items": [
            {
                "name": "Organic Fertilizer",
                "manufacturer": "Nature Grow",
                "price": 850,
                "quantity": 2,
                "hsn_code": "31010000",
                "batch_no": "BT2025001",
                "expiry_date": "31-12-2026",
                "unit": "Bag",
                "discount": 5,
                "total": 1615
            },
            {
                "name": "Pesticide Spray",
                "manufacturer": "Plant Shield",
                "price": 450,
                "quantity": 1,
                "hsn_code": "38089199",
                "batch_no": "PS202504",
                "expiry_date": "30-06-2026",
                "unit": "Bottle",
                "discount": 0,
                "total": 450
            }
        ],
        "payment": {
            "method": "Split",
            "status": "PARTIALLY_PAID",
            "subtotal": 2150,
            "discount": 85,
            "cgst": 51.63,
            "sgst": 51.63,
            "total": 2168.26,
            "split": {
                "cash_amount": 1000,
                "credit_amount": 1168.26
            },
            "payments": [
                {
                    "amount": 1000,
                    "method": "Cash",
                    "date": "04-05-2025",
                    "time": "10:30",
                    "depositor_name": "Raj Kumar",
                    "remaining": 1168.26,
                    "status": "PARTIALLY_PAID",
                    "note": "Initial payment"
                }
            ]
        }
    }
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Generate Excel invoice
    excel_result = generate_invoice(invoice_data, "output/test_invoice.xlsx", output_format="excel")
    print(f"Excel invoice generation: {'Success' if excel_result else 'Failed'}")
    
    # Generate PDF invoice
    pdf_result = generate_invoice(invoice_data, "output/test_invoice.pdf", output_format="pdf")
    print(f"PDF invoice generation: {'Success' if pdf_result else 'Failed'}")

if __name__ == "__main__":
    test_excel_invoice()