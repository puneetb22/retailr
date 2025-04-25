"""
Invoice generator for POS system
Handles creation of PDF invoices for customers
"""

import os
import datetime
import io
from utils.helpers import format_currency
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

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
    try:
        # Create a PDF buffer if no save path provided
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            pdf_buffer = save_path
        else:
            pdf_buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))
        styles.add(ParagraphStyle(name='Right', alignment=2))
        styles.add(ParagraphStyle(name='Left', alignment=0))
        styles.add(ParagraphStyle(name='Heading', fontSize=14, spaceAfter=6, spaceBefore=6, fontName='Helvetica-Bold'))
        
        # Create elements list to build PDF
        elements = []
        
        # Shop Info
        elements.append(Paragraph(f"<b>{invoice_data.get('shop_name', 'Agritech Products Shop')}</b>", styles['Heading']))
        elements.append(Paragraph(f"{invoice_data.get('shop_address', 'Main Road, Maharashtra')}", styles['Normal']))
        elements.append(Paragraph(f"Phone: {invoice_data.get('shop_phone', '+91 1234567890')}", styles['Normal']))
        elements.append(Paragraph(f"GST #: {invoice_data.get('shop_gst', '27AABCU9603R1ZX')}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Invoice Header
        elements.append(Paragraph("<b>INVOICE</b>", styles['Center']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Invoice Info in table format
        inv_info_data = [
            ["Invoice #:", invoice_data.get('invoice_number', '')],
            ["Date:", invoice_data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
        ]
        inv_info_table = Table(inv_info_data, colWidths=[1.5*inch, 4*inch])
        inv_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4)
        ]))
        elements.append(inv_info_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Customer Info
        elements.append(Paragraph("<b>Customer Information</b>", styles['Normal']))
        cust_info_data = [
            ["Name:", invoice_data.get('customer_name', 'Walk-in Customer')],
            ["Phone:", invoice_data.get('customer_phone', '')],
            ["Address:", invoice_data.get('customer_address', '')]
        ]
        cust_info_table = Table(cust_info_data, colWidths=[1*inch, 4.5*inch])
        cust_info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4)
        ]))
        elements.append(cust_info_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Items
        elements.append(Paragraph("<b>Items</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Table header
        items_data = [["#", "Item", "Qty", "Price", "Discount", "Total"]]
        
        # Add items
        items = invoice_data.get('items', [])
        for i, item in enumerate(items, 1):
            price = item.get('price', 0)
            qty = item.get('qty', 0)
            discount = item.get('discount', 0)
            item_total = item.get('total', price * qty)
            
            items_data.append([
                str(i),
                item.get('name', 'Item'),
                str(qty),
                format_currency(price),
                str(discount) + "%" if discount else "-",
                format_currency(item_total)
            ])
        
        # Create items table
        items_table = Table(items_data, colWidths=[0.3*inch, 3*inch, 0.5*inch, 1*inch, 0.7*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4)
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Totals
        subtotal = invoice_data.get('subtotal', 0)
        discount = invoice_data.get('discount', 0)
        tax = invoice_data.get('tax', 0)
        final_total = invoice_data.get('total', subtotal - discount + tax)
        
        totals_data = [
            ["Subtotal:", format_currency(subtotal)],
            ["Discount:", format_currency(discount)],
            ["Tax:", format_currency(tax)],
            ["TOTAL:", format_currency(final_total)]
        ]
        
        totals_table = Table(totals_data, colWidths=[1.5*inch, 1*inch])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold')
        ]))
        
        # Create a layout table to right-align the totals table
        alignment_table = Table([[" ", totals_table]], colWidths=[4*inch, 2.5*inch])
        alignment_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0)
        ]))
        elements.append(alignment_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Payment information
        payment_method = invoice_data.get('payment_method', 'Cash')
        payment_status = invoice_data.get('payment_status', 'PAID')
        
        payment_info = [["Payment Method:", payment_method], ["Status:", payment_status]]
        
        # Add additional payment details
        if payment_method == "SPLIT":
            cash_amount = invoice_data.get('cash_amount', 0)
            upi_amount = invoice_data.get('upi_amount', 0)
            payment_info.append(["Cash:", format_currency(cash_amount)])
            payment_info.append(["UPI:", format_currency(upi_amount)])
            
            if invoice_data.get('upi_reference'):
                payment_info.append(["UPI Reference:", invoice_data.get('upi_reference')])
        
        elif payment_method == "UPI" and invoice_data.get('upi_reference'):
            payment_info.append(["UPI Reference:", invoice_data.get('upi_reference')])
        
        elif payment_method == "CREDIT":
            credit_amount = invoice_data.get('credit_amount', 0)
            payment_info.append(["Credit Amount:", format_currency(credit_amount)])
        
        payment_table = Table(payment_info, colWidths=[1.5*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4)
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(Paragraph("Thank you for your business!", styles['Center']))
        
        # Build PDF
        doc.build(elements)
        
        # If using BytesIO, get the data
        if not save_path:
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()
            return pdf_data
        
        return True
    
    except Exception as e:
        print(f"Invoice generation error: {e}")
        return False