"""
PDF Invoice Generator for POS system
Generates invoices matching exactly the shop_bill.pdf template
"""

import os
import datetime
import io
import platform
import subprocess
from decimal import Decimal
from utils.helpers import format_currency, num_to_words_indian

# Import ReportLab for PDF generation
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("ReportLab not available - PDF invoice generation will not work")
    REPORTLAB_AVAILABLE = False

def generate_invoice(invoice_data, save_path):
    """
    Generate a PDF invoice that exactly matches the shop_bill.pdf template
    
    Args:
        invoice_data: Dictionary containing invoice details
        save_path: Path to save the PDF invoice
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not REPORTLAB_AVAILABLE:
        print("Error: ReportLab library is not available. PDF invoice generation not possible.")
        return False
        
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        
        # Create the PDF document in landscape orientation
        doc = SimpleDocTemplate(
            save_path,
            pagesize=landscape(A4),  # Use landscape orientation
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles that match exactly the shop_bill.pdf template
        styles.add(ParagraphStyle(
            name='ShopName',
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='ShopInfo',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='StateName',
            fontSize=8,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='CustomerInfo',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='OriginalCopy',
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='RightAligned',
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceLabel',
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceInfo',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='AmountWords',
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='ItemData',
            fontSize=8,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='TableHeader',
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='TableHeaderLeft',
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='Terms',
            fontSize=7,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='Subject',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0
        ))
        
        styles.add(ParagraphStyle(
            name='PaymentRecordsHeader',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0
        ))
        
        # Create elements list to build PDF
        elements = []
        
        # Extract shop info from store_info structure
        store_info = invoice_data.get('store_info', {})
        
        # Shop information fields
        shop_name = store_info.get('name', 'Agritech Products Shop')
        shop_address = store_info.get('address', 'Main Road, Maharashtra')
        shop_phone = store_info.get('phone', '+91 1234567890')
        shop_gst = store_info.get('gstin', '27AABCU9603R1ZX')
        shop_email = store_info.get('email', '')
        
        # Special license fields
        shop_laid_no = store_info.get('laid_no', '')
        shop_lcsd_no = store_info.get('lcsd_no', '')
        shop_lfrd_no = store_info.get('lfrd_no', '')
        
        # State info
        state_name = store_info.get('state_name', 'Maharashtra')
        state_code = store_info.get('state_code', '27')
        
        # Extract customer data
        customer_data = invoice_data.get('customer', {})
        invoice_number = invoice_data.get('invoice_number', '')
        
        # Format date
        date_obj = datetime.datetime.now()
        try:
            if 'date' in invoice_data:
                if isinstance(invoice_data['date'], str):
                    # Support multiple date formats
                    try:
                        date_obj = datetime.datetime.strptime(invoice_data['date'], '%d/%m/%Y')
                    except ValueError:
                        try:
                            date_obj = datetime.datetime.strptime(invoice_data['date'], '%d-%m-%Y')
                        except ValueError:
                            pass
        except:
            pass
            
        invoice_date = date_obj.strftime('%d/%m/%Y')
        invoice_time = invoice_data.get('time', date_obj.strftime('%I:%M %p'))
        
        # Customer information
        customer_name = customer_data.get('name', 'Walk-in Customer')
        customer_phone = customer_data.get('phone', '')
        customer_address = customer_data.get('address', '')
        customer_village = customer_data.get('village', '')
        if customer_village and not customer_village in customer_address:
            customer_address = f"{customer_address}, {customer_village}"
        customer_email = customer_data.get('email', '')
        customer_gstin = customer_data.get('gstin', '')
        
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
            
        # Set default tax rates
        cgst_rate = 2.5  # Default CGST rate
        sgst_rate = 2.5  # Default SGST rate
        
        # Get tax rates from the invoice data if available
        if 'cgst_rate' in payment_data:
            try:
                cgst_rate = float(payment_data.get('cgst_rate', 2.5))
            except (ValueError, TypeError):
                cgst_rate = 2.5

        if 'sgst_rate' in payment_data:
            try:
                sgst_rate = float(payment_data.get('sgst_rate', 2.5))
            except (ValueError, TypeError):
                sgst_rate = 2.5
            
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
        
        # Calculate taxable value (subtotal - discount)
        taxable_value = subtotal - discount
        
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
        if payment_status.upper() in ["PARTIALLY_PAID", "PARTIAL"]:
            # Get sum of all payments made
            try:
                payment_made = sum([float(p.get('amount', 0)) for p in payment_data.get('payments', [])])
                outstanding_amount = total - payment_made
            except:
                # If error in calculation, leave as is
                pass
        
        # -------------------------------------------------------------
        # Create the EXACT shop_bill.pdf layout with proper tables and borders
        # -------------------------------------------------------------
        
        # ------ HEADER SECTION ------
        # Shop Name in its own bordered cell
        shop_name_table = Table(
            [[Paragraph(f"{shop_name}", styles['ShopName'])]],
            colWidths=[doc.width],
            rowHeights=[20]
        )
        shop_name_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Shop info row
        shop_info_data = [
            [
                Paragraph(f"{shop_address}", styles['ShopInfo']),
                Paragraph("(Original For Recipeint)", styles['OriginalCopy']),
                Paragraph(f"GSTIN -        {shop_gst}", styles['RightAligned'])
            ],
            [
                Paragraph(f"State Name: {state_name}, Code : {state_code}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LAID           {shop_laid_no}", styles['RightAligned'])
            ],
            [
                Paragraph(f"Contact : {shop_phone}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LCSD           {shop_lcsd_no}", styles['RightAligned'])
            ],
            [
                Paragraph(f"E-mail: {shop_email}", styles['StateName']),
                Paragraph("", styles['StateName']),
                Paragraph(f"LFRD           {shop_lfrd_no}", styles['RightAligned'])
            ]
        ]
        
        shop_info_table = Table(shop_info_data, colWidths=[doc.width*0.4, doc.width*0.3, doc.width*0.3])
        shop_info_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('SPAN', (0, 0), (0, 0)), # Shop address spans
        ]))
        
        # ------ CUSTOMER SECTION ------
        customer_info_data = [
            [
                Paragraph(f"Customer name -", styles['CustomerInfo']),
                Paragraph(f"{customer_name}", styles['CustomerInfo']),
                Paragraph(f"{customer_phone}", styles['CustomerInfo']),
                Paragraph("Date", styles['InvoiceLabel']),
                Paragraph(f"{invoice_date}{invoice_time}", styles['InvoiceInfo'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph(f"{customer_address}", styles['CustomerInfo']),
                Paragraph(f"{customer_email}", styles['CustomerInfo']),
                Paragraph("Invoice No.", styles['InvoiceLabel']),
                Paragraph(f"{invoice_number}", styles['InvoiceInfo'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph("", styles['CustomerInfo']),
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Mode of Pay", styles['InvoiceLabel']),
                Paragraph(f"{payment_method}", styles['InvoiceInfo'])
            ]
        ]
        
        customer_info_table = Table(customer_info_data, colWidths=[doc.width*0.15, doc.width*0.25, doc.width*0.2, doc.width*0.15, doc.width*0.25])
        customer_info_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('ALIGN', (4, 0), (4, -1), 'LEFT'),
        ]))
        
        # ------ ITEMS TABLE ------
        # Prepare column headers        
        items_header_data = [
            [Paragraph("No", styles['TableHeader']), 
             Paragraph("Description of Good", styles['TableHeader']), 
             Paragraph("Company\nname", styles['TableHeader']),
             Paragraph("HSN", styles['TableHeader']),
             Paragraph("Batch NO", styles['TableHeader']),
             Paragraph("Expiry Date", styles['TableHeader']),
             Paragraph("Qty", styles['TableHeader']),
             Paragraph("Unit", styles['TableHeader']),
             Paragraph("Rate", styles['TableHeader']),
             Paragraph("Disc", styles['TableHeader']),
             Paragraph("Amount", styles['TableHeader'])]
        ]
        
        # Calculate column widths for items table based on A4 landscape
        col_widths = [
            doc.width*0.03,   # No
            doc.width*0.17,   # Description
            doc.width*0.13,   # Company name
            doc.width*0.07,   # HSN
            doc.width*0.08,   # Batch
            doc.width*0.1,    # Expiry
            doc.width*0.06,   # Qty
            doc.width*0.07,   # Unit
            doc.width*0.09,   # Rate
            doc.width*0.08,   # Disc
            doc.width*0.12    # Amount
        ]
        
        # Create items header table
        items_header_table = Table(items_header_data, colWidths=col_widths)
        items_header_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        
        # Add items
        items = invoice_data.get('items', [])
        total_qty = 0
        
        # Create item rows
        items_data = []
        
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
            item_name = item.get('name', '')
            hsn_code = item.get('hsn_code', '')
            company_name = item.get('manufacturer', '')
            batch_no = item.get('batch_no', '')
            expiry_date = item.get('expiry_date', '')
            unit = item.get('unit', '')
            
            # Format values exactly as in template
            qty_str = str(int(qty)) if qty == int(qty) else str(qty)  # Don't show decimal if whole number
            discount_str = f"{int(discount)}" if discount == int(discount) else f"{discount}"  # Don't show decimal if whole number
            if discount > 0:
                discount_str += "%"
            
            items_data.append([
                str(i),                                  # No
                item_name,                               # Description of Good
                company_name,                            # Company name
                hsn_code,                                # HSN
                batch_no,                                # Batch NO
                expiry_date,                             # Expiry Date
                qty_str,                                 # Qty
                unit,                                    # Unit
                format_currency(price, symbol='Rs.'),    # Rate
                discount_str,                            # Disc
                format_currency(item_total, symbol='Rs.')# Amount
            ])
        
        # Do not add empty rows - only show actual products as per template requirements
        
        # Create items table
        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No column centered
            ('ALIGN', (6, 0), (7, -1), 'CENTER'),  # Qty and Unit columns centered
            ('ALIGN', (8, 0), (8, -1), 'RIGHT'),   # Rate column right aligned
            ('ALIGN', (9, 0), (9, -1), 'CENTER'),  # Disc column centered
            ('ALIGN', (10, 0), (10, -1), 'RIGHT'), # Amount column right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        # Total row
        qty_display = str(int(total_qty)) if total_qty == int(total_qty) else str(total_qty)
        total_row_data = [
            ["", "", "", "", "", "", qty_display, "", "", "Total", format_currency(total, symbol='Rs.')]
        ]
        
        total_row_table = Table(total_row_data, colWidths=col_widths)
        total_row_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (6, 0), (6, 0), 'CENTER'),  # total qty centered
            ('ALIGN', (9, 0), (9, 0), 'RIGHT'),   # "Total" right aligned
            ('ALIGN', (10, 0), (10, 0), 'RIGHT'), # Amount right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (9, 0), (10, 0), 'Helvetica-Bold'),  # "Total" and amount in bold
        ]))
        
        # Amount in words row
        try:
            total_for_words = float(total)
            amount_in_words = num_to_words_indian(total_for_words)
        except (ValueError, TypeError):
            amount_in_words = "Zero Rupees Only"
            
        amount_words_data = [
            [Paragraph(f"{amount_in_words.upper()}", styles['AmountWords'])]
        ]
        
        amount_words_table = Table(amount_words_data, colWidths=[doc.width])
        amount_words_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))
        
        # ------ TAX AND PAYMENT DETAILS SECTION ------
        # Create tax table that exactly matches the format shown in the reference image
        # This table has: Taxable Value | Central Tax (CGST) [Rate|Amount] | Total Tax Amount
        tax_table_header = [
            ["Taxable\nValue", "Central Tax (CGST)", "Total\nTax Amount"],
            ["", "Rate", "Amount", ""]
        ]
        
        tax_table_data = [
            [format_currency(taxable_value, symbol='Rs.'), 
             f"{cgst_rate}%", 
             format_currency(cgst, symbol='Rs.'),
             format_currency(cgst + cgst, symbol='Rs.')],
            ["", "", format_currency(cgst, symbol='Rs.'), format_currency(cgst + cgst, symbol='Rs.')]
        ]
        
        # Define column widths to match the template exactly
        tax_col_widths = [
            doc.width*0.5*0.25,  # Taxable value
            doc.width*0.5*0.15, # CGST rate
            doc.width*0.5*0.25, # CGST amount
            doc.width*0.5*0.35  # Total tax
        ]
        
        # Combine header and data
        tax_table_content = tax_table_header + tax_table_data
        
        # Create tax table with style exactly matching the sample image
        tax_table = Table(tax_table_content, colWidths=tax_col_widths)
        tax_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (0, 1)),  # Taxable Value header spans 2 rows
            ('SPAN', (1, 0), (2, 0)),  # Central Tax header spans 2 columns
            ('SPAN', (3, 0), (3, 1)),  # Total Tax Amount header spans 2 rows
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Headers centered
            ('ALIGN', (0, 2), (0, 3), 'RIGHT'),    # Taxable value right aligned
            ('ALIGN', (1, 2), (1, 3), 'CENTER'),   # CGST rate centered
            ('ALIGN', (2, 2), (2, 3), 'RIGHT'),    # CGST amount right aligned
            ('ALIGN', (3, 2), (3, 3), 'RIGHT'),    # Total tax right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),  # Headers in bold
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        # Create the payment breakdown section (left side)
        payment_section_data = [
            [Paragraph("Payment Breakdown", styles['TableHeaderLeft']), ""],
            [Paragraph("Outstanding Amnt.", styles['TableHeaderLeft']), Paragraph(format_currency(outstanding_amount, symbol='Rs.'), styles['RightAligned'])]
        ]
        
        payment_section_table = Table(payment_section_data, colWidths=[doc.width*0.25*0.6, doc.width*0.25*0.4])
        payment_section_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Line below Payment Breakdown
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, 1), 'RIGHT'),  # Outstanding amount right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        # Combine payment and tax sections in a row
        payment_tax_data = [
            [payment_section_table, tax_table]
        ]
        
        payment_tax_row = Table(payment_tax_data, colWidths=[doc.width*0.25, doc.width*0.75])
        payment_tax_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # ------ SIGNATURE SECTION ------
        # Create terms and signature section
        terms = invoice_data.get('terms', "1. Goods once sold will not be taken back or exchanged.\n2. All disputes are subject to local jurisdiction only.")
        
        signature_data = [
            [Paragraph("Customer Signature", styles['CustomerInfo']), 
             Paragraph(terms, styles['Terms']), 
             Paragraph(f"For                 {shop_name}", styles['RightAligned'])],
            ["", "", Paragraph("Authorised signatory", styles['RightAligned'])]
        ]
        
        signature_table = Table(signature_data, colWidths=[doc.width*0.25, doc.width*0.5, doc.width*0.25])
        signature_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('SPAN', (1, 0), (1, 1)),  # Terms spans both rows
        ]))
        
        # Subject line
        subject_data = [
            [Paragraph("SUBJECT TO JURIDICTION", styles['Subject'])]
        ]
        
        subject_table = Table(subject_data, colWidths=[doc.width])
        subject_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))
        
        # ------ PAYMENT HISTORY SECTION ------
        # Add payment history section if available
        payment_history_tables = []
        
        if 'payment_history' in payment_data or 'payments' in payment_data:
            payment_history_header = [
                [Paragraph("Invoice payment Records", styles['PaymentRecordsHeader'])]
            ]
            
            payment_header_table = Table(payment_history_header, colWidths=[doc.width])
            payment_header_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ]))
            
            payment_history_tables.append(payment_header_table)
            
            # Payment records column headers
            payment_record_headers = [
                ["Sr.no", "Invoice No", "Amount", "Depositor Name", "Date", "time", "Mode of Pay", "Remaining Amount", "Note", "Invoice Status"]
            ]
            
            payment_col_widths = [
                doc.width*0.05,   # Sr.no
                doc.width*0.1,    # Invoice No
                doc.width*0.1,    # Amount
                doc.width*0.15,   # Depositor Name
                doc.width*0.1,    # Date
                doc.width*0.07,   # time
                doc.width*0.1,    # Mode of Pay
                doc.width*0.13,   # Remaining Amount
                doc.width*0.1,    # Note
                doc.width*0.1     # Invoice Status
            ]
            
            payment_headers_table = Table(payment_record_headers, colWidths=payment_col_widths)
            payment_headers_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))
            
            payment_history_tables.append(payment_headers_table)
            
            # Extract payments data
            payments = payment_data.get('payments', [])
            
            # If no payments list but has payment_history string, try to parse it
            if not payments and 'payment_history' in payment_data:
                # This is a simplified parser assuming format: "1. date: amount via method"
                history_text = payment_data['payment_history']
                history_lines = [line.strip() for line in history_text.split('\n') if line.strip()]
                
                # Skip first line if it's just "Payment History:"
                start_idx = 1 if history_lines and history_lines[0].lower() == 'payment history:' else 0
                
                for i, line in enumerate(history_lines[start_idx:], 1):
                    # Try to extract payment details from each line
                    try:
                        # Extract parts after the line number
                        parts = line.split('. ', 1)[1] if '. ' in line else line
                        
                        # Split into date and amount parts
                        date_part, amount_part = parts.split(': ', 1) if ': ' in parts else (date_obj.strftime('%d/%m/%Y'), parts)
                        
                        # Extract amount and method
                        amount = "0.0"
                        method = "Unknown"
                        if ' via ' in amount_part:
                            amount_str, method = amount_part.split(' via ', 1)
                            # Clean up the amount string, removing "Rs. " and any commas
                            amount = amount_str.replace('Rs. ', '').replace(',', '')
                            
                            # Remove any reference part
                            if ' (Ref: ' in method:
                                reference = method.split(' (Ref: ')[1].rstrip(')')
                                method = method.split(' (Ref: ')[0]
                                
                                # Add to payments list
                                payments.append({
                                    'date': date_part,
                                    'amount': amount,
                                    'method': method,
                                    'reference': reference,
                                    'depositor': 'Customer'  # Default depositor
                                })
                            else:
                                # Add to payments list without reference
                                payments.append({
                                    'date': date_part,
                                    'amount': amount,
                                    'method': method,
                                    'depositor': 'Customer'  # Default depositor
                                })
                    except:
                        # Skip unparseable lines
                        continue
            
            # Format payment rows - each payment gets a row
            payment_rows = []
            remaining = total
            
            for i, payment in enumerate(payments, 1):
                # Get payment details with safe defaults
                try:
                    payment_amount = float(payment.get('amount', 0))
                except (ValueError, TypeError):
                    payment_amount = 0.0
                    
                payment_date = payment.get('date', '')
                payment_time = payment.get('time', '')
                payment_method = payment.get('method', '')
                payment_depositor = payment.get('depositor', 'Customer')
                payment_note = payment.get('note', '')
                
                # Calculate remaining amount if not provided
                if 'remaining' in payment:
                    try:
                        remaining = float(payment.get('remaining', 0))
                    except (ValueError, TypeError):
                        remaining -= payment_amount
                else:
                    remaining -= payment_amount
                
                # Get status (default based on remaining)
                if remaining <= 0:
                    status = 'PAID'
                elif remaining < total:
                    status = 'PARTIALLY_PAID'
                else:
                    status = 'UNPAID'
                
                payment_status = payment.get('status', status)
                
                payment_rows.append([
                    str(i),
                    invoice_number,
                    format_currency(payment_amount, symbol='Rs.'),
                    payment_depositor,
                    payment_date,
                    payment_time,
                    payment_method,
                    format_currency(remaining, symbol='Rs.'),
                    payment_note,
                    payment_status
                ])
            
            # If no payment rows, add a blank one for the template
            if not payment_rows:
                payment_rows = [["", invoice_number, "", "", "", "", "", "", "", ""]]
            
            # Create payments table
            payments_table = Table(payment_rows, colWidths=payment_col_widths)
            payments_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Sr.no centered
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Amount right aligned
                ('ALIGN', (7, 0), (7, -1), 'RIGHT'),   # Remaining Amount right aligned
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            
            payment_history_tables.append(payments_table)
        
        # ------ COMBINE ALL SECTIONS INTO FINAL DOCUMENT ------
        # Now we combine all our tables into the elements list
        elements.append(shop_name_table)
        elements.append(shop_info_table)
        elements.append(customer_info_table)
        elements.append(items_header_table)
        elements.append(items_table)
        elements.append(total_row_table)
        elements.append(amount_words_table)
        elements.append(payment_tax_row)
        elements.append(signature_table)
        elements.append(subject_table)
        
        # Add payment history tables if any
        for table in payment_history_tables:
            elements.append(table)
        
        # Build the document
        doc.build(elements)
        
        return True
        
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        return False

def view_invoice(file_path):
    """Open an invoice file with the appropriate application"""
    try:
        if not os.path.exists(file_path):
            return False
            
        if platform.system() == 'Windows':
            subprocess.call(['start', '', file_path], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux
            subprocess.call(['xdg-open', file_path])
        return True
    except Exception as e:
        print(f"Error opening invoice: {e}")
        return False