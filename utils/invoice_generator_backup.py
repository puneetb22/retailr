"""
Invoice generator for POS system
Handles creation of PDF invoices for customers
Implements the specific format for Agritech businesses in Maharashtra
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
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        styles.add(ParagraphStyle(
            name='CenterBold', 
            alignment=TA_CENTER, 
            fontName='Helvetica-Bold',
            fontSize=14
        ))
        
        styles.add(ParagraphStyle(
            name='RightAlign', 
            alignment=TA_RIGHT,
            fontSize=9
        ))
        
        styles.add(ParagraphStyle(
            name='ShopName',
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            fontSize=18,
            spaceAfter=0.1*cm
        ))
        
        styles.add(ParagraphStyle(
            name='ShopAddress',
            alignment=TA_CENTER,
            fontSize=10,
            leading=12
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName='Helvetica-Bold',
            fontSize=12,
            spaceBefore=0.3*cm,
            spaceAfter=0.2*cm
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceTitle',
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            fontSize=15,
            spaceBefore=0.3*cm,
            spaceAfter=0.3*cm
        ))
        
        styles.add(ParagraphStyle(
            name='AmountWords',
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.navy
        ))
        
        # Create elements list to build PDF
        elements = []
        
        # Extract shop info from store_info structure
        store_info = invoice_data.get('store_info', {})
        shop_name = store_info.get('name', 'Agritech Products Shop')
        shop_address = store_info.get('address', 'Main Road, Maharashtra')
        shop_phone = store_info.get('phone', '+91 1234567890')
        shop_gst = store_info.get('gstin', '27AABCU9603R1ZX')
        
        # Shop name as a paragraph with large, bold font (no table/border)
        shop_name_para = Paragraph(f"<b>{shop_name}</b>", styles['ShopName'])
        elements.append(shop_name_para)
        
        # Shop address as a paragraph with smaller font
        shop_address_para = Paragraph(f"{shop_address}", styles['ShopAddress'])
        elements.append(shop_address_para)
        
        # Shop phone and GST as a paragraph
        shop_contact_para = Paragraph(f"Phone: {shop_phone} | GST No.: {shop_gst}", styles['ShopAddress'])
        elements.append(shop_contact_para)
        
        # Horizontal line
        elements.append(Spacer(1, 0.2*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        
        # TAX INVOICE title with prominent display
        elements.append(Spacer(1, 0.2*cm))
        tax_invoice_para = Paragraph("TAX INVOICE", styles['InvoiceTitle'])
        elements.append(tax_invoice_para)
        
        # Invoice and Customer Info
        customer_data = invoice_data.get('customer', {})
        invoice_number = invoice_data.get('invoice_number', '')
        invoice_date = invoice_data.get('date', datetime.datetime.now().strftime('%d-%m-%Y'))
        invoice_time = invoice_data.get('time', datetime.datetime.now().strftime('%H:%M'))
        
        customer_name = customer_data.get('name', 'Walk-in Customer')
        customer_phone = customer_data.get('phone', '')
        customer_address = customer_data.get('address', '')
        customer_village = customer_data.get('village', '')
        customer_gstin = customer_data.get('gstin', '')
        
        # Create separate tables for invoice details and customer details
        invoice_details_data = [
            [Paragraph("<b>Invoice No:</b>", styles['Normal']), Paragraph(invoice_number, styles['Normal'])],
            [Paragraph("<b>Date:</b>", styles['Normal']), Paragraph(invoice_date, styles['Normal'])],
            [Paragraph("<b>Time:</b>", styles['Normal']), Paragraph(invoice_time, styles['Normal'])]
        ]
        
        customer_details_data = [
            [Paragraph("<b>Customer:</b>", styles['Normal']), Paragraph(customer_name, styles['Normal'])],
            [Paragraph("<b>Phone:</b>", styles['Normal']), Paragraph(customer_phone, styles['Normal'])]
        ]
        
        if customer_address:
            customer_details_data.append([Paragraph("<b>Address:</b>", styles['Normal']), Paragraph(customer_address, styles['Normal'])])
        
        if customer_village:
            customer_details_data.append([Paragraph("<b>Village:</b>", styles['Normal']), Paragraph(customer_village, styles['Normal'])])
            
        if customer_gstin:
            customer_details_data.append([Paragraph("<b>GSTIN:</b>", styles['Normal']), Paragraph(customer_gstin, styles['Normal'])])
        
        # Create tables
        invoice_details_table = Table(invoice_details_data, colWidths=[2.5*cm, 5*cm])
        invoice_details_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        customer_details_table = Table(customer_details_data, colWidths=[2.5*cm, 5*cm])
        customer_details_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        # Create a table to hold both tables side by side
        info_table_data = [[invoice_details_table, customer_details_table]]
        info_table = Table(info_table_data, colWidths=[doc.width/2, doc.width/2])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(Spacer(1, 0.5*cm))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Items Table - Use a bordered table ONLY for this section
        elements.append(Paragraph("<b>Item Details</b>", styles['SectionTitle']))
        
        # Table header with HSN/SAC code column
        items_data = [["S.No.", "Item Description", "HSN/SAC", "Qty", "Rate", "Disc.(%)", "Amount"]]
        
        # Add items
        items = invoice_data.get('items', [])
        for i, item in enumerate(items, 1):
            # Convert values to the correct numeric types with error handling
            try:
                price = float(item.get('price', 0))
            except (ValueError, TypeError):
                price = 0.0
                
            try:
                qty = float(item.get('quantity', 0))
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
            
            # Get HSN code
            hsn_code = item.get('hsn_code', '')
            
            items_data.append([
                str(i),
                item.get('name', 'Item'),
                hsn_code,
                str(qty),
                format_currency(price),
                str(discount),
                format_currency(item_total)
            ])
        
        # Create items table with column widths and bordered for items section
        col_widths = [1*cm, 6*cm, 2*cm, 1.5*cm, 2.5*cm, 2*cm, 3*cm]
        items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            
            # Full border around entire table - THIS SHOULD HAVE BORDER
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # Interior grid lines
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Thicker line below header
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
            
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # S.No. centered
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Qty centered
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'),   # Amounts right-aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('PADDING', (0, 0), (-1, -1), 6),
            
            # Make alternating rows have different background colors
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]))
        
        # Add shading to alternate rows
        for i in range(1, len(items_data)):
            if i % 2 == 0:
                items_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)]))
                
        elements.append(items_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Totals and Tax Calculation
        payment_data = invoice_data.get('payment', {})
        
        # Convert payment values to appropriate numeric types
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
        
        # Create totals table with enhanced tax details (per requirements)
        totals_data = [
            ["Subtotal:", format_currency(subtotal)],
            ["Discount:", format_currency(discount)],
            ["Taxable Amount:", format_currency(subtotal - discount)],
            ["CGST (2.5%):", format_currency(cgst)],
            ["SGST (2.5%):", format_currency(sgst)],
            ["<b>TOTAL:</b>", f"<b>{format_currency(total)}</b>"]
        ]
        
        # Convert regular cells to Paragraphs
        for i in range(len(totals_data)):
            totals_data[i][0] = Paragraph(totals_data[i][0], styles['Normal'])
            totals_data[i][1] = Paragraph(totals_data[i][1], styles['RightAlign'])
        
        totals_table = Table(totals_data, colWidths=[8*cm, 5*cm])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),  # Background for total row
            ('LINEBELOW', (0, -2), (1, -2), 1, colors.black),    # Line above total
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Add totals table to elements, aligned right
        elements.append(totals_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Amount in words on a single horizontal line (per requirements)
        # Ensure total is a valid number before converting to words
        try:
            total_for_words = float(total)
            amount_in_words = num_to_words_indian(total_for_words)
        except (ValueError, TypeError):
            amount_in_words = "Zero Rupees Only"
        
        amount_words_para = Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", styles['AmountWords'])
        elements.append(amount_words_para)
        elements.append(Spacer(1, 0.5*cm))
        
        # Payment information section
        payment_method = payment_data.get('method', 'Cash')
        
        payment_info = []
        payment_info.append(Paragraph(f"<b>Payment Method:</b> {payment_method}", styles['Normal']))
        
        # Add UPI reference if applicable
        if payment_method.upper() == "UPI" and payment_data.get('reference'):
            payment_info.append(Paragraph(f"<b>UPI Reference:</b> {payment_data.get('reference')}", styles['Normal']))
        
        # Add credit payment method details if applicable
        if payment_method.upper() == "CREDIT":
            # Show credit payment status
            payment_status = payment_data.get('status', 'UNPAID')
            payment_info.append(Paragraph(f"<b>Credit Status:</b> {payment_status}", styles['Normal']))
            
            # If there's a specific credit payment method (e.g., UPI, CASH) add it
            credit_method = payment_data.get('credit_method', '')
            if credit_method and credit_method.upper() != "CREDIT":
                payment_info.append(Paragraph(f"<b>Credit Payment Method:</b> {credit_method}", styles['Normal']))
                
                # Add reference if available for certain payment types
                if credit_method.upper() in ["UPI", "CHEQUE", "BANK"] and payment_data.get('credit_reference'):
                    payment_info.append(Paragraph(f"<b>Reference Number:</b> {payment_data.get('credit_reference')}", styles['Normal']))
        
        # Add split payment details if applicable
        if payment_method.upper() == "SPLIT" and payment_data.get('split'):
            split_data = payment_data.get('split', {})
            
            # Convert split payment values to float
            try:
                cash_amount = float(split_data.get('cash_amount', 0))
            except (ValueError, TypeError):
                cash_amount = 0.0
                
            try:
                upi_amount = float(split_data.get('upi_amount', 0))
            except (ValueError, TypeError):
                upi_amount = 0.0
                
            try:
                credit_amount = float(split_data.get('credit_amount', 0))
            except (ValueError, TypeError):
                credit_amount = 0.0
            
            if cash_amount > 0:
                payment_info.append(Paragraph(f"<b>Cash Amount:</b> {format_currency(cash_amount)}", styles['Normal']))
            if upi_amount > 0:
                payment_info.append(Paragraph(f"<b>UPI Amount:</b> {format_currency(upi_amount)}", styles['Normal']))
                if split_data.get('upi_reference'):
                    payment_info.append(Paragraph(f"<b>UPI Reference:</b> {split_data.get('upi_reference')}", styles['Normal']))
            if credit_amount > 0:
                payment_info.append(Paragraph(f"<b>Credit Amount:</b> {format_currency(credit_amount)}", styles['Normal']))
        
        # Payment history is now only shown in customer management view
        
        for info in payment_info:
            elements.append(info)
            elements.append(Spacer(1, 0.1*cm))
            
        elements.append(Spacer(1, 0.5*cm))
        
        # Signature area
        signature_data = [
            ["", "For " + shop_name],
            ["", ""],
            ["", ""],
            ["Customer Signature", "Authorized Signatory"]
        ]
        
        signature_table = Table(signature_data, colWidths=[doc.width/2, doc.width/2])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEABOVE', (0, -1), (0, -1), 0.5, colors.black),
            ('LINEABOVE', (1, -1), (1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, -1), (-1, -1), 1),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 0),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 0.2*cm))
        
        # Terms and conditions
        terms = "Terms and Conditions: All goods sold are not returnable and non-refundable. E&OE."
        elements.append(Paragraph(terms, ParagraphStyle('Terms', fontSize=8, alignment=TA_CENTER)))
        
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