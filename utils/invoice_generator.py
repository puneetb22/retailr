"""
Invoice generator for POS system
Implements the exact layout from the provided shop_bill.pdf template
with placeholders in {brackets} for data
"""

import os
import datetime
import io
from decimal import Decimal
from utils.helpers import format_currency, num_to_words_indian

# Try to import reportlab modules
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    reportlab_available = True
except ImportError:
    print("WARNING: ReportLab library is not fully available. Invoice generation may not work correctly.")
    reportlab_available = False
    # Create dummy classes to prevent syntax errors when reportlab is not available
    class DummyClass:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return self
        def add(self, *args, **kwargs):
            return None
        def setStyle(self, *args, **kwargs):
            pass
        def build(self, *args, **kwargs):
            pass
    
    # Create dummy objects
    A4 = 'A4'
    landscape = lambda x: x  # Function that returns its input
    colors = type('obj', (object,), {'black': None})
    SimpleDocTemplate = DummyClass
    Paragraph = DummyClass
    Spacer = DummyClass
    Table = DummyClass
    TableStyle = DummyClass
    Image = DummyClass
    HRFlowable = DummyClass
    getSampleStyleSheet = lambda: {'Normal': None}
    ParagraphStyle = DummyClass
    inch = cm = mm = 1
    TA_CENTER = TA_RIGHT = TA_LEFT = 'CENTER'

def generate_invoice(invoice_data, save_path=None):
    """
    Generate a PDF invoice based on provided shop_bill template
    
    Args:
        invoice_data: Dictionary containing invoice details
        save_path: Path to save the PDF (if None, returns PDF as binary data)
        
    Returns:
        bool: True if successful, False otherwise
        or
        bytes: PDF data if save_path is None
    """
    # Check if reportlab is available
    if not reportlab_available:
        print("Error: ReportLab library is not available. Invoice generation failed.")
        return False
        
    try:
        # Create a PDF buffer if no save path provided
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            pdf_buffer = save_path
        else:
            pdf_buffer = io.BytesIO()
        
        # Get the invoice template type
        template_type = invoice_data.get('template_type', 'shop_bill')
        
        # Call appropriate template function based on selected template
        if template_type == 'shop_bill':
            return generate_shop_bill_template(invoice_data, pdf_buffer)
        elif template_type == 'default':
            return generate_default_template(invoice_data, pdf_buffer)
        elif template_type == 'compact':
            return generate_compact_template(invoice_data, pdf_buffer)
        elif template_type == 'detailed':
            return generate_detailed_template(invoice_data, pdf_buffer)
        else:
            # Default to shop_bill template if unknown type
            return generate_shop_bill_template(invoice_data, pdf_buffer)
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        return False
            
def generate_shop_bill_template(invoice_data, pdf_buffer):
    """
    Generate a PDF invoice based on the shop_bill.pdf template
    
    Args:
        invoice_data: Dictionary containing invoice details
        pdf_buffer: File-like object to write PDF data to
        
    Returns:
        bool: True if successful, False otherwise
        or
        bytes: PDF data if pdf_buffer is a BytesIO object
    """
    try:
        # Determine if this is a file path or BytesIO object
        save_path = None
        if isinstance(pdf_buffer, str):
            save_path = pdf_buffer
        # Create the PDF document in landscape orientation
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=landscape(A4),  # Use landscape orientation
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
            fontSize=12
        ))
        
        styles.add(ParagraphStyle(
            name='ShopInfo',
            fontSize=9
        ))
        
        styles.add(ParagraphStyle(
            name='StateName',
            fontSize=8
        ))
        
        styles.add(ParagraphStyle(
            name='CustomerInfo',
            fontSize=9
        ))
        
        styles.add(ParagraphStyle(
            name='OriginalCopy',
            fontSize=9,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='RightAligned',
            fontSize=9,
            alignment=TA_RIGHT
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceLabel',
            fontSize=9,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceInfo',
            fontSize=9,
            alignment=TA_RIGHT
        ))
        
        styles.add(ParagraphStyle(
            name='AmountWords',
            fontSize=9,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='ItemData',
            fontSize=8
        ))
        
        styles.add(ParagraphStyle(
            name='TableHeader',
            fontSize=8,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Terms',
            fontSize=7,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='Subject',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='PaymentRecordsHeader',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Create elements list to build PDF
        elements = []
        
        # Extract shop info from store_info structure or direct invoice_data
        # First try getting from store_info structure (standardized format)
        store_info = invoice_data.get('store_info', {})
        
        # If store_info is empty or missing fields, look in root of invoice_data
        # This ensures we can work with both nested and flat data structures
        shop_name = store_info.get('name', invoice_data.get('name', 'Agritech Products Shop'))
        shop_address = store_info.get('address', invoice_data.get('address', 'Main Road, Maharashtra'))
        shop_phone = store_info.get('phone', invoice_data.get('phone', '+91 1234567890'))
        shop_gst = store_info.get('gstin', invoice_data.get('gstin', '27AABCU9603R1ZX'))
        shop_email = store_info.get('email', invoice_data.get('email', ''))
        
        # Special license fields - look in both places
        shop_laid_no = store_info.get('laid_no', invoice_data.get('laid_no', invoice_data.get('shop_laid_no', '')))
        shop_lcsd_no = store_info.get('lcsd_no', invoice_data.get('lcsd_no', invoice_data.get('shop_lcsd_no', '')))
        shop_lfrd_no = store_info.get('lfrd_no', invoice_data.get('lfrd_no', invoice_data.get('shop_lfrd_no', '')))
        
        # State info
        state_name = store_info.get('state_name', invoice_data.get('state_name', 'Maharashtra'))
        state_code = store_info.get('state_code', invoice_data.get('state_code', '27'))
        
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
        customer_email = customer_data.get('email', '')
        
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
        # Create the exact shop_bill.pdf template layout with placeholders
        # -------------------------------------------------------------
        
        # Top Row 1: Shop Name
        elements.append(Paragraph(f"{shop_name}", styles['ShopName']))
        
        # Top Row 2: Shop address, Original For Recipient, GST
        shop_header_data = [
            [
                Paragraph(f"{shop_address}", styles['ShopInfo']),
                Paragraph("(Original For Recipeint)", styles['OriginalCopy']),
                Paragraph(f"GSTIN -        {shop_gst}", styles['RightAligned'])
            ]
        ]
        
        shop_header_table = Table(shop_header_data, colWidths=[doc.width*0.4, doc.width*0.3, doc.width*0.3])
        shop_header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        
        elements.append(shop_header_table)
        
        # Top Row 3: State Name & Code, Licensing info
        state_license_data = [
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
        
        state_license_table = Table(state_license_data, colWidths=[doc.width*0.4, doc.width*0.3, doc.width*0.3])
        state_license_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ]))
        
        elements.append(state_license_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Customer info section 
        customer_info_data = [
            [
                Paragraph(f"Customer name -", styles['CustomerInfo']),
                Paragraph(f"{customer_name}", styles['CustomerInfo']),
                Paragraph(f"{customer_phone}", styles['CustomerInfo']),
                Paragraph("Date", styles['InvoiceLabel']),
                Paragraph(f"{invoice_date} {invoice_time}", styles['InvoiceInfo'])
            ],
            [
                Paragraph("", styles['CustomerInfo']),
                Paragraph(f"{customer_address}", styles['CustomerInfo']),
                Paragraph("", styles['CustomerInfo']),
                Paragraph("Bill No.", styles['InvoiceLabel']),
                Paragraph(f"{invoice_number}", styles['InvoiceInfo'])
            ],
            [
                Paragraph("GSTIN -", styles['CustomerInfo']),
                Paragraph(f"{customer_data.get('gstin', '')}", styles['CustomerInfo']),
                Paragraph(f"{customer_email}", styles['CustomerInfo']),
                Paragraph("Status", styles['InvoiceLabel']),
                Paragraph(f"{payment_status}", styles['InvoiceInfo'])
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
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ]))
        
        elements.append(customer_info_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Items table header with company column in center
        company_header = [
            ["", "Company", ""],
            ["No", "Description of Good", "name", "HSN", "Batch NO", "Expiry Date", "Qty", "Unit", "Rate", "Disc", "Amount"]
        ]
        
        # Calculate column widths for items table
        col_widths = [
            0.6*cm,   # No
            4.5*cm,   # Description
            2.3*cm,   # Company name
            1.0*cm,   # HSN
            1.5*cm,   # Batch
            1.7*cm,   # Expiry
            0.8*cm,   # Qty
            1.0*cm,   # Unit
            1.0*cm,   # Rate
            1.0*cm,   # Disc
            1.5*cm    # Amount
        ]
        
        # Create items header table
        items_header = Table(company_header, colWidths=col_widths)
        items_header.setStyle(TableStyle([
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Merging "company" and "name" in row 0
            ('SPAN', (1, 0), (2, 0)),
            
            # Text styling
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(items_header)
        
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
        
        # Add empty rows to match template if needed
        while len(items_data) < 10:
            items_data.append(["", "", "", "", "", "", "", "", "", "", ""])
        
        # Create items table
        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No column
            ('ALIGN', (6, 0), (6, -1), 'CENTER'),  # Qty column
            ('ALIGN', (7, 0), (7, -1), 'CENTER'),  # Unit column
            ('ALIGN', (8, 0), (8, -1), 'RIGHT'),   # Rate column
            ('ALIGN', (9, 0), (9, -1), 'CENTER'),  # Discount column
            ('ALIGN', (10, 0), (10, -1), 'RIGHT'), # Amount column
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Make rows smaller
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(items_table)
        
        # Total qty and amount row - format matching the PDF template exactly
        # Format total qty without decimal part if it's a whole number
        qty_display = str(int(total_qty)) if total_qty == int(total_qty) else str(total_qty)
        
        total_row = [
            ["", "", "", "", "", "", qty_display, "", "", "Total", format_currency(total, symbol='Rs.')]
        ]
        
        total_table = Table(total_row, colWidths=col_widths)
        total_table.setStyle(TableStyle([
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Alignment
            ('ALIGN', (6, 0), (6, 0), 'CENTER'),  # total qty
            ('ALIGN', (9, 0), (9, 0), 'RIGHT'),   # Total label
            ('ALIGN', (10, 0), (10, 0), 'RIGHT'),  # Total amount
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Make rows smaller
            ('FONTSIZE', (0, -1), (-1, -1), 8),
            ('FONTNAME', (9, 0), (10, 0), 'Helvetica-Bold'),  # Both "Total" and amount in bold
        ]))
        
        elements.append(total_table)
        
        # Amount in words
        try:
            total_for_words = float(total)
            amount_in_words = num_to_words_indian(total_for_words)
        except (ValueError, TypeError):
            amount_in_words = "Zero Rupees Only"
        
        words_table = Table([[Paragraph(f"{amount_in_words}", styles['AmountWords'])]], colWidths=[doc.width])
        words_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (0, 0), 8),
        ]))
        
        elements.append(words_table)
        elements.append(Spacer(1, 0.2*cm))
        
        # Tax breakdown table with formatting exactly matching the PDF template
        
        # Format tax rates without trailing zeros for whole numbers
        cgst_rate_display = str(int(cgst_rate)) if cgst_rate == int(cgst_rate) else str(cgst_rate)
        sgst_rate_display = str(int(sgst_rate)) if sgst_rate == int(sgst_rate) else str(sgst_rate)
        
        tax_table_data = [
            ["", "", "Taxable", "Central Tax (CGST)", "State Tax (SGST)", "Total"],
            ["Payment Breakdown", "", "Value", "Rate", "Amount", "Rate", "Amount", "Tax Amount"],
            ["", "", format_currency(taxable_value, symbol='Rs.'), f"{cgst_rate_display}%", format_currency(cgst, symbol='Rs.'), f"{sgst_rate_display}%", format_currency(sgst, symbol='Rs.'), format_currency(cgst + sgst, symbol='Rs.')],
            ["", "", "", "", format_currency(cgst, symbol='Rs.'), "", format_currency(sgst, symbol='Rs.'), format_currency(cgst + sgst, symbol='Rs.')],
            ["Outstanding Amnt.", format_currency(outstanding_amount, symbol='Rs.'), "", "", "", "", "", ""]
        ]
        
        # Calculate column widths for tax table exactly matching the PDF template
        tax_col_widths = [2.5*cm, 2.5*cm, 2.0*cm, 1.5*cm, 2.0*cm, 1.5*cm, 2.0*cm, 2.0*cm]
        
        tax_table = Table(tax_table_data, colWidths=tax_col_widths)
        tax_table.setStyle(TableStyle([
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Headers spanning
            ('SPAN', (0, 0), (1, 0)),  # Empty space above "Payment Breakdown"
            ('SPAN', (2, 0), (2, 1)),  # "Taxable Value" spans 2 rows
            ('SPAN', (3, 0), (4, 0)),  # "Central Tax (CGST)" spans 2 columns
            ('SPAN', (5, 0), (6, 0)),  # "State Tax (SGST)" spans 2 columns
            ('SPAN', (7, 0), (7, 1)),  # "Total Tax Amount" spans 2 rows
            ('SPAN', (0, 1), (1, 1)),  # "Payment Breakdown" spans 2 columns
            
            # Formatting
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Special alignment for specific cells
            ('ALIGN', (0, 2), (0, 4), 'LEFT'),   # Left align first column
            ('ALIGN', (1, 4), (1, 4), 'RIGHT'),  # Right align outstanding amount
            ('ALIGN', (2, 2), (2, 4), 'RIGHT'),  # Right align taxable value
            ('ALIGN', (4, 2), (4, 4), 'RIGHT'),  # Right align CGST amount
            ('ALIGN', (6, 2), (6, 4), 'RIGHT'),  # Right align SGST amount
            ('ALIGN', (7, 2), (7, 4), 'RIGHT'),  # Right align Total Tax amount
            
            # Bold the Outstanding Amount text
            ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
        ]))
        
        elements.append(tax_table)
        
        # Signature section - formatted exactly as in the PDF template
        # Get terms & conditions text
        terms_text = store_info.get('terms_conditions', invoice_data.get('terms_conditions', 'Goods once sold cannot be returned. Payment due within 30 days.'))
        
        signature_data = [
            ["Customer Signature", terms_text, "For                 " + shop_name],
            ["", "", "Authorised signatory"]
        ]
        
        signature_table = Table(signature_data, colWidths=[doc.width*0.25, doc.width*0.5, doc.width*0.25])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),    # Only align header right
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Center the "Authorised signatory" text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Subject to jurisdiction
        elements.append(Paragraph("SUBJECT TO JURIDICTION", styles['Subject']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Payment records header
        elements.append(Paragraph("Invoice payment Records", styles['PaymentRecordsHeader']))
        
        # Payment records table
        payment_records_header = [
            ["Sr.no", "Invoice No", "Amount", "Depositor Name", "Date", "time", "Mode of Pay", "Remaining Amount", "Note", "Invoice Status"]
        ]
        
        # Column widths exactly matching the PDF template
        payment_records_col_widths = [0.8*cm, 2.0*cm, 1.5*cm, 2.5*cm, 1.5*cm, 1.2*cm, 1.8*cm, 2.2*cm, 1.5*cm, 1.5*cm]
        
        # Create table with headers
        payment_records_table = Table(payment_records_header, colWidths=payment_records_col_widths)
        payment_records_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(payment_records_table)
        
        # Extract payment history
        payment_history = payment_data.get('payments', [])
        payment_records_data = []
        
        for i, payment in enumerate(payment_history, 1):
            payment_amount = payment.get('amount', 0)
            payment_date = payment.get('date', '')
            payment_time = payment.get('time', '')
            payment_mode = payment.get('method', '')
            depositor_name = payment.get('depositor_name', '')
            note = payment.get('note', '')
            remaining = payment.get('remaining', '')
            payment_status = payment.get('status', '')
            
            payment_records_data.append([
                str(i),
                invoice_number,
                format_currency(payment_amount, symbol='Rs.'),
                depositor_name,
                payment_date,
                payment_time,
                payment_mode,
                format_currency(remaining, symbol='Rs.'),
                note,
                payment_status
            ])
        
        # Add at least one empty row if no payment history with format matching PDF template
        if not payment_records_data:
            # Format: {sr,no}{invoice_no}{amount}{depositor_name}{date}{time}{mode_of_pay}{remaining_amount}{note}{invoice_status}
            payment_records_data.append([
                "1",                                       # Sr.no
                invoice_number,                            # Invoice No
                format_currency(total, symbol='Rs.'),      # Amount 
                "Initial Sale",                           # Depositor Name
                invoice_date,                              # Date
                invoice_time,                              # Time
                payment_method,                            # Mode of Pay
                format_currency(outstanding_amount, symbol='Rs.'), # Remaining Amount
                "",                                        # Note
                payment_status                             # Invoice Status
            ])
        
        # Create payment records table with exact formatting as in PDF template
        payment_details_table = Table(payment_records_data, colWidths=payment_records_col_widths)
        payment_details_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            # Specific alignments for each column exactly as in PDF template
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),     # Sr.no centered 
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),     # Invoice No centered
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),      # Amount right-aligned
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),       # Depositor Name left-aligned
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),     # Date centered
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),     # Time centered
            ('ALIGN', (6, 0), (6, -1), 'CENTER'),     # Mode of Pay centered
            ('ALIGN', (7, 0), (7, -1), 'RIGHT'),      # Remaining Amount right-aligned
            ('ALIGN', (8, 0), (8, -1), 'CENTER'),     # Note centered
            ('ALIGN', (9, 0), (9, -1), 'CENTER'),     # Invoice Status centered
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(payment_details_table)
        
        # Build PDF
        doc.build(elements)
        
        # If using BytesIO, get the data
        if isinstance(pdf_buffer, io.BytesIO):
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()
            return pdf_data
        
        return True
    
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        
        # If using BytesIO, make sure to close it
        if isinstance(pdf_buffer, io.BytesIO):
            try:
                pdf_buffer.close()
            except:
                pass
            
        return False
        
def generate_default_template(invoice_data, pdf_buffer):
    """
    Generate a PDF invoice based on the default template
    
    Args:
        invoice_data: Dictionary containing invoice details
        pdf_buffer: File-like object to write PDF data to
        
    Returns:
        bool: True if successful, False otherwise
        or
        bytes: PDF data if pdf_buffer is a BytesIO object
    """
    try:
        # For now, use the shop_bill template as default until separate templates are implemented
        return generate_shop_bill_template(invoice_data, pdf_buffer)
    except Exception as e:
        print(f"Error generating default invoice: {e}")
        return False

def generate_compact_template(invoice_data, pdf_buffer):
    """
    Generate a PDF invoice based on the compact template
    
    Args:
        invoice_data: Dictionary containing invoice details
        pdf_buffer: File-like object to write PDF data to
        
    Returns:
        bool: True if successful, False otherwise
        or
        bytes: PDF data if pdf_buffer is a BytesIO object
    """
    try:
        # For now, use the shop_bill template as default until separate templates are implemented
        return generate_shop_bill_template(invoice_data, pdf_buffer)
    except Exception as e:
        print(f"Error generating compact invoice: {e}")
        return False

def generate_detailed_template(invoice_data, pdf_buffer):
    """
    Generate a PDF invoice based on the detailed template
    
    Args:
        invoice_data: Dictionary containing invoice details
        pdf_buffer: File-like object to write PDF data to
        
    Returns:
        bool: True if successful, False otherwise
        or
        bytes: PDF data if pdf_buffer is a BytesIO object
    """
    try:
        # For now, use the shop_bill template as default until separate templates are implemented
        return generate_shop_bill_template(invoice_data, pdf_buffer)
    except Exception as e:
        print(f"Error generating detailed invoice: {e}")
        return False