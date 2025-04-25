"""
Invoice generator for POS system
Handles creation of PDF invoices for customers
"""

import os
import datetime
from utils.helpers import format_currency

def generate_invoice(invoice_data, save_path=None):
    """
    Generate a PDF invoice based on provided data
    
    Args:
        invoice_data: Dictionary containing invoice details
        save_path: Path to save the PDF (if None, returns PDF as binary data)
        
    Returns:
        bool: True if successful, False otherwise
        or
        bytes: PDF data if save_path is None
    """
    # This is a placeholder implementation
    # In a real implementation, this would use a PDF generation library
    # like ReportLab, FPDF, or similar to create the invoice
    
    try:
        # For now, just create a text representation of the invoice
        # that we can use for testing/placeholder
        invoice_text = f"""
INVOICE
==============================
Invoice #: {invoice_data.get('invoice_number', '')}
Date: {invoice_data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

Shop Name: {invoice_data.get('shop_name', 'Agritech Products Shop')}
Address: {invoice_data.get('shop_address', 'Main Road, Maharashtra')}
Phone: {invoice_data.get('shop_phone', '+91 1234567890')}
GST #: {invoice_data.get('shop_gst', '27AABCU9603R1ZX')}

Customer Information:
Name: {invoice_data.get('customer_name', 'Walk-in Customer')}
Phone: {invoice_data.get('customer_phone', '')}
Address: {invoice_data.get('customer_address', '')}

Items:
==============================
"""
        
        # Add items
        items = invoice_data.get('items', [])
        total = 0
        
        for i, item in enumerate(items, 1):
            price = item.get('price', 0)
            qty = item.get('qty', 0)
            item_total = price * qty
            total += item_total
            
            invoice_text += f"{i}. {item.get('name', 'Item')} x {qty} @ {format_currency(price)} = {format_currency(item_total)}\n"
        
        # Add totals
        subtotal = invoice_data.get('subtotal', total)
        discount = invoice_data.get('discount', 0)
        tax = invoice_data.get('tax', 0)
        final_total = invoice_data.get('total', subtotal - discount + tax)
        
        invoice_text += f"""
==============================
Subtotal: {format_currency(subtotal)}
Discount: {format_currency(discount)}
Tax: {format_currency(tax)}
TOTAL: {format_currency(final_total)}

Payment Method: {invoice_data.get('payment_method', 'Cash')}
"""

        # If split payment
        if invoice_data.get('cash_amount') and invoice_data.get('upi_amount'):
            invoice_text += f"""
Cash: {format_currency(invoice_data.get('cash_amount', 0))}
UPI: {format_currency(invoice_data.get('upi_amount', 0))}"""

            # Add UPI reference if available
            if invoice_data.get('upi_reference'):
                invoice_text += f"""
UPI Reference: {invoice_data.get('upi_reference')}"""
            
            invoice_text += "\n"

        # If UPI payment (without split)
        if invoice_data.get('payment_method') == 'UPI' and invoice_data.get('upi_reference'):
            invoice_text += f"""
UPI Reference: {invoice_data.get('upi_reference')}
"""

        # If credit sale
        if invoice_data.get('credit_amount', 0) > 0:
            invoice_text += f"""
Credit Amount: {format_currency(invoice_data.get('credit_amount', 0))}
"""

        invoice_text += """
==============================
Thank you for your business!
        """
        
        # Save to file if path provided
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(invoice_text)
            return True
        else:
            # Return text for now (in real implementation, would return PDF bytes)
            return invoice_text
            
    except Exception as e:
        print(f"Invoice generation error: {e}")
        return False