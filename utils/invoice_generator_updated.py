"""
Updated invoice generator for POS system
Implements the exact layout from the provided PDF template
"""

import os
import datetime
import io
from utils.helpers import format_currency, num_to_words_indian
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def generate_invoice(invoice_data, save_path=None):
    """
    Generate a PDF invoice based on provided template
    
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
            pagesize=A4,
            rightMargin=1.0*cm,
            leftMargin=1.0*cm,
            topMargin=1.0*cm,
            bottomMargin=1.0*cm
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        styles.add(ParagraphStyle(
            name='ShopName',
            fontName='Helvetica-Bold',
            fontSize=11
        ))
        
        styles.add(ParagraphStyle(
            name='ShopInfo',
            fontSize=8
        ))
        
        styles.add(ParagraphStyle(
            name='CustomerInfo',
            fontSize=9
        ))
        
        styles.add(ParagraphStyle(
            name='OriginalCopy',
            fontSize=8,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceInfo',
            fontSize=9,
            alignment=TA_RIGHT
        ))
        
        styles.add(ParagraphStyle(
            name='AmountWords',
            fontSize=9
        ))
        
        styles.add(ParagraphStyle(
            name='Terms',
            fontSize=7,
            alignment=TA_CENTER
        ))
        
        # Create elements list to build PDF
        elements = []
        
        # Extract shop info from store_info structure
        store_info = invoice_data.get('store_info', {})
        shop_name = store_info.get('name', 'Agritech Products Shop')
        shop_address = store_info.get('address', 'Main Road, Maharashtra')
        shop_phone = store_info.get('phone', '+91 1234567890')
        shop_gst = store_info.get('gstin', '27AABCU9603R1ZX')
        shop_email = store_info.get('email', '')
        
        # Extract customer data
        customer_data = invoice_data.get('customer', {})
        invoice_number = invoice_data.get('invoice_number', '')
        date_obj = datetime.datetime.now()
        try:
            if 'date' in invoice_data:
                if isinstance(invoice_data['date'], str):
                    date_obj = datetime.datetime.strptime(invoice_data['date'], '%d-%m-%Y')
        except:
            pass
            
        invoice_date = date_obj.strftime('%d-%m-%Y')
        invoice_time = invoice_data.get('time', date_obj.strftime('%H:%M'))
        
        customer_name = customer_data.get('name', 'Walk-in Customer')
        customer_phone = customer_data.get('phone', '')
        customer_address = customer_data.get('address', '')
        
        # Payment information
        payment_data = invoice_data.get('payment', {})
        payment_method = payment_data.get('method', 'Cash')
        payment_status = payment_data.get('status', 'PAID')
        
        # Extract financial data
        try:
            subtotal = float(payment_data.get('subtotal', 0))
        except (ValueError, TypeError):
            subtotal = 0.0
            
        try:
            discount = float(payment_data.get('discount', 0))
        except (ValueError, TypeError):
            discount = 0.0
            
        try:
            cgst = float(payment_data.get('cgst', 0))
        except (ValueError, TypeError):
            cgst = 0.0
            
        try:
            sgst = float(payment_data.get('sgst', 0))
        except (ValueError, TypeError):
            sgst = 0.0
            
        try:
            total = float(payment_data.get('total', 0))
        except (ValueError, TypeError):
            total = 0.0
        
        # Calculate outstanding amount based on payment method
        outstanding_amount = 0
        if payment_method.upper() == "CREDIT":
            outstanding_amount = total
        elif payment_method.upper() == "SPLIT" and payment_data.get('split'):
            split_data = payment_data.get('split', {})
            try:
                outstanding_amount = float(split_data.get('credit_amount', 0))
            except (ValueError, TypeError):
                outstanding_amount = 0
                
        # If payment is partially paid, try to get the pending amount
        if payment_status.upper() == "PARTIALLY_PAID":
            # Get sum of all payments made
            try:
                payment_made = sum([float(p.get('amount', 0)) for p in payment_data.get('payments', [])])
                outstanding_amount = outstanding_amount - payment_made
            except:
                # If error in calculation, leave as is
                pass
                
        # Top header with shop name, original copy text, and GST
        header_data = [
            [
                Paragraph(f"{shop_name}", styles['ShopName']), 
                Paragraph("(Original for Recipients)", styles['OriginalCopy']), 
                Paragraph(f"{shop_gst}", styles['ShopInfo'])
            ]
        ]
        
        header_table = Table(header_data, colWidths=[doc.width*0.4, doc.width*0.3, doc.width*0.3])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        
        elements.append(header_table)
        
        # Shop address
        elements.append(Paragraph(f"{shop_address}", styles['ShopInfo']))
        
        # Shop contact & email
        elements.append(Paragraph(f"{shop_phone} {shop_email}", styles['ShopInfo']))
        elements.append(Spacer(1, 0.3*cm))
        
        # Customer info and invoice info in top section
        customer_invoice_data = [
            [
                Paragraph(f"{customer_name}", styles['CustomerInfo']),
                Paragraph(f"{customer_phone}", styles['CustomerInfo']),
                Paragraph(f"{invoice_date} {invoice_time}", styles['InvoiceInfo'])
            ],
            [
                Paragraph(f"{customer_address}", styles['CustomerInfo']),
                "",
                Paragraph(f"{invoice_number}", styles['InvoiceInfo'])
            ]
        ]
        
        customer_invoice_table = Table(customer_invoice_data, colWidths=[doc.width*0.4, doc.width*0.3, doc.width*0.3])
        customer_invoice_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ]))
        
        elements.append(customer_invoice_table)
        elements.append(Spacer(1, 0.3*cm))
        
        # Items Table
        # Define column headers
        items_data = [
            ["No", "Description of\nGood", "Company\nname", "HSN", "Batch\nNO", "Expiry\nDate", "Qty", "Rate", "Unit", "Amount"]
        ]
        
        # Add items
        items = invoice_data.get('items', [])
        total_qty = 0
        
        for i, item in enumerate(items, 1):
            # Convert values to the correct numeric types with error handling
            try:
                price = float(item.get('price', 0))
            except (ValueError, TypeError):
                price = 0.0
                
            try:
                qty = float(item.get('quantity', 0))
                total_qty += qty
            except (ValueError, TypeError):
                qty = 0.0
                
            try:
                discount = float(item.get('discount', 0))
            except (ValueError, TypeError):
                discount = 0.0
            
            # Use the provided total if available, otherwise calculate it
            if 'total' in item and item['total'] is not None:
                try:
                    item_total = float(item['total'])
                except (ValueError, TypeError):
                    # If conversion fails, calculate it
                    item_total = price * qty * (1 - discount/100)
            else:
                # Calculate if total not provided
                item_total = price * qty * (1 - discount/100)
            
            # Get item details, using defaults for new columns from template
            item_name = item.get('name', 'Item')
            hsn_code = item.get('hsn_code', '')
            company_name = item.get('manufacturer', '')
            batch_no = item.get('batch_no', '')
            expiry_date = item.get('expiry_date', '')
            unit = item.get('unit', '')
            
            items_data.append([
                str(i),
                item_name,
                company_name,
                hsn_code,
                batch_no,
                expiry_date,
                str(qty),
                format_currency(price),
                unit,
                format_currency(item_total)
            ])
        
        # Create items table with column widths
        col_widths = [
            0.7*cm,   # No
            3.5*cm,   # Description
            2.2*cm,   # Company
            1.2*cm,   # HSN
            1.3*cm,   # Batch
            1.5*cm,   # Expiry
            1.0*cm,   # Qty
            1.8*cm,   # Rate
            1.0*cm,   # Unit
            1.8*cm    # Amount
        ]
        
        # Add empty rows to match template if needed
        while len(items_data) < 5:
            items_data.append(["", "", "", "", "", "", "", "", "", ""])
        
        items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Header styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No column
            ('ALIGN', (6, 0), (6, -1), 'CENTER'),  # Qty column
            ('ALIGN', (7, 0), (7, -1), 'RIGHT'),   # Rate column
            ('ALIGN', (8, 0), (8, -1), 'CENTER'),  # Unit column
            ('ALIGN', (9, 0), (9, -1), 'RIGHT'),   # Amount column
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Make rows smaller
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.3*cm))
        
        # Bottom section with amount details, payment info
        # First row - Outstanding amount, total qty, total amount
        total_row = [
            [
                Paragraph(f"{format_currency(outstanding_amount)}", styles['CustomerInfo']),
                Paragraph(f"{total_qty}", styles['CustomerInfo']),
                Paragraph(f"Total {format_currency(total)}", styles['CustomerInfo']),
            ]
        ]
        
        total_table = Table(total_row, colWidths=[doc.width*0.6, doc.width*0.2, doc.width*0.2])
        total_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        
        elements.append(total_table)
        
        # Amount in words and discount in same row
        amount_discount_row = [
            [
                Paragraph(f"{amount_in_words_indian(total)}", styles['AmountWords']),
                Paragraph(f"{format_currency(discount)}", styles['CustomerInfo']),
            ]
        ]
        
        amount_discount_table = Table(amount_discount_row, colWidths=[doc.width*0.8, doc.width*0.2])
        amount_discount_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        elements.append(amount_discount_table)
        
        # Payment mode/status and taxes
        payment_tax_data = [
            [
                # Left column for payment details
                Table(
                    [
                        [Paragraph(f"{payment_method}", styles['CustomerInfo'])],
                        [Paragraph(f"{payment_status}", styles['CustomerInfo'])]
                    ],
                    colWidths=[doc.width*0.3]
                ),
                # Right column for tax details
                Table(
                    [
                        [Paragraph(f"{format_currency(cgst)}", styles['CustomerInfo'])],
                        [Paragraph(f"{format_currency(sgst)}", styles['CustomerInfo'])],
                        [Paragraph(f"{format_currency(total)}", styles['CustomerInfo'])]
                    ],
                    colWidths=[doc.width*0.2]
                )
            ]
        ]
        
        payment_tax_table = Table(payment_tax_data, colWidths=[doc.width*0.8, doc.width*0.2])
        payment_tax_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        elements.append(payment_tax_table)
        elements.append(Spacer(1, 1.0*cm))
        
        # Terms and return policy
        elements.append(Paragraph("[Return policy and terms and conditions]", styles['Terms']))
        elements.append(Spacer(1, 1.0*cm))
        
        # Signature area
        signature_data = [
            ["Customer Signatory", "", f"{shop_name}"],
            ["", "", "Authorised Signatory"]
        ]
        
        signature_table = Table(signature_data, colWidths=[doc.width*0.33, doc.width*0.34, doc.width*0.33])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(signature_table)
        
        # Build PDF
        doc.build(elements)
        
        # If using BytesIO, get the data
        if not save_path:
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()
            return pdf_data
        
        return True
    
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        
        # If using BytesIO, make sure to close it
        if not save_path and 'pdf_buffer' in locals():
            pdf_buffer.close()
        
        return False