"""
Invoice generator for POS system
Handles creation of PDF invoices for customers
"""

import os
import datetime
import io
from utils.helpers import format_currency
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
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
        
        # Create elements list to build PDF
        elements = []
        
        # Create header table (shop info, invoice title, invoice details) with border
        shop_name = invoice_data.get('shop_name', 'Agritech Products Shop')
        shop_address = invoice_data.get('shop_address', 'Main Road, Maharashtra')
        shop_phone = invoice_data.get('shop_phone', '+91 1234567890')
        shop_gst = invoice_data.get('shop_gst', '27AABCU9603R1ZX')
        
        # Create main header with border
        header_data = [
            [Paragraph(f"<b>{shop_name}</b>", styles['ShopName'])],
            [Paragraph(f"{shop_address}", styles['ShopAddress'])],
            [Paragraph(f"Phone: {shop_phone} | GST No.: {shop_gst}", styles['ShopAddress'])],
            [Paragraph("TAX INVOICE", styles['InvoiceTitle'])]
        ]
        
        header_table = Table(header_data, colWidths=[doc.width])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -2), 1, colors.black),  # Border around shop info
            ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black), # Line below shop info
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
        ]))
        elements.append(header_table)
        
        # Invoice and Customer Info
        invoice_number = invoice_data.get('invoice_number', '')
        invoice_date = invoice_data.get('date', datetime.datetime.now().strftime('%d-%m-%Y %H:%M'))
        customer_name = invoice_data.get('customer_name', 'Walk-in Customer')
        customer_phone = invoice_data.get('customer_phone', '')
        customer_address = invoice_data.get('customer_address', '')
        
        # Create a combined customer and invoice info table with border
        invoice_customer_data = [
            # Headers
            [
                Paragraph("<b>Invoice Details</b>", styles['SectionTitle']),
                Paragraph("<b>Customer Details</b>", styles['SectionTitle'])
            ],
            # Content
            [
                Table([
                    ["Invoice No:", invoice_number],
                    ["Date:", invoice_date]
                ], colWidths=[2.5*cm, 5*cm]),
                
                Table([
                    ["Name:", customer_name],
                    ["Phone:", customer_phone],
                    ["Address:", customer_address]
                ], colWidths=[2.5*cm, 5*cm])
            ]
        ]
        
        # Create a bordered table for both sections
        info_table = Table(invoice_customer_data, colWidths=[doc.width/2, doc.width/2])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),  # Headers background
            ('BOX', (0, 0), (1, 1), 1, colors.black),  # Border around entire table
            ('LINEBELOW', (0, 0), (1, 0), 1, colors.black),  # Line below headers
            ('LINEBEFORE', (1, 0), (1, 1), 1, colors.black),  # Line between columns
            ('TOPPADDING', (0, 0), (1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('LEFTPADDING', (0, 0), (1, 1), 10),
            ('RIGHTPADDING', (0, 0), (1, 1), 10),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Items Table
        elements.append(Paragraph("<b>Item Details</b>", styles['SectionTitle']))
        
        # Table header with HSN/SAC code column
        items_data = [["S.No.", "Item Description", "HSN/SAC", "Qty", "Rate", "Disc.", "Amount"]]
        
        # Add items
        items = invoice_data.get('items', [])
        for i, item in enumerate(items, 1):
            price = item.get('price', 0)
            qty = item.get('qty', 0)
            discount = item.get('discount', 0)
            item_total = item.get('total', price * qty)
            
            # Get HSN code - This would need to be added to your product data model
            hsn_code = item.get('hsn_code', '')
            
            items_data.append([
                str(i),
                item.get('name', 'Item'),
                hsn_code,
                str(qty),
                format_currency(price),
                str(discount) + "%" if discount else "-",
                format_currency(item_total)
            ])
        
        # Create items table with column widths
        col_widths = [1*cm, 6*cm, 2*cm, 1.5*cm, 2.5*cm, 2*cm, 3*cm]
        items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # S.No. centered
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Qty centered
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'),   # Amounts right-aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Padding
            ('PADDING', (0, 0), (-1, -1), 6),
            # Make alternating rows have different background colors
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),  # Thicker line below header
        ]))
        
        # Add shading to alternate rows
        for i in range(1, len(items_data)):
            if i % 2 == 0:
                items_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)]))
                
        elements.append(items_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Totals and Tax Calculation
        subtotal = invoice_data.get('subtotal', 0)
        discount = invoice_data.get('discount', 0)
        tax = invoice_data.get('tax', 0)
        final_total = invoice_data.get('total', subtotal - discount + tax)
        
        # Amount in words using our Indian numbering system converter
        from utils.helpers import num_to_words_indian
        amount_in_words = num_to_words_indian(final_total)
        
        # Tax breakdown - customize based on your tax structure
        cgst = tax / 2  # Assuming equal CGST and SGST split
        sgst = tax / 2
        
        # Create totals table with proper styling
        totals_data = [
            ["Subtotal:", format_currency(subtotal)],
            ["Discount:", format_currency(discount)],
            ["Taxable Amount:", format_currency(subtotal - discount)],
            ["CGST (2.5%):", format_currency(cgst)],
            ["SGST (2.5%):", format_currency(sgst)],
            ["<b>TOTAL:</b>", f"<b>{format_currency(final_total)}</b>"]
        ]
        
        # Convert regular cells to Paragraphs
        for i in range(len(totals_data)):
            totals_data[i][0] = Paragraph(totals_data[i][0], styles['Normal'])
            totals_data[i][1] = Paragraph(totals_data[i][1], styles['RightAlign'])
        
        totals_table = Table(totals_data, colWidths=[4*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),  # Background for total row
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),  # Grid lines
            ('LINEBELOW', (0, -2), (1, -2), 1, colors.black),  # Thicker line above total
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold')  # Bold font for total row
        ]))
        
        # Create a separate table for amount in words with border
        amount_words_data = [
            ["<b>Amount in Words:</b>"],
            [amount_in_words]
        ]
        
        amount_words_table = Table(amount_words_data, colWidths=[doc.width * 0.6])
        amount_words_table.setStyle(TableStyle([
            ('BOX', (0, 0), (0, -1), 1, colors.black),  # Border around amount in words
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),  # Header background
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),  # Line below header
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (0, -1), 6),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center header
            ('TOPPADDING', (0, 0), (0, 0), 6),
            ('BOTTOMPADDING', (0, 0), (0, 0), 6),
        ]))
        
        # Create a table to hold both tables side by side
        final_table_data = [[amount_words_table, totals_table]]
        final_table = Table(final_table_data, colWidths=[doc.width * 0.6, doc.width * 0.4])
        final_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(final_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Payment information section with border
        payment_method = invoice_data.get('payment_method', 'Cash')
        payment_status = invoice_data.get('payment_status', 'PAID')
        
        payment_info = []
        payment_info.append(["<b>Payment Method:</b>", payment_method])
        payment_info.append(["<b>Status:</b>", payment_status])
        
        # Add additional payment details
        if payment_method == "SPLIT":
            cash_amount = invoice_data.get('cash_amount', 0)
            upi_amount = invoice_data.get('upi_amount', 0)
            payment_info.append(["<b>Cash:</b>", format_currency(cash_amount)])
            payment_info.append(["<b>UPI:</b>", format_currency(upi_amount)])
            
            if invoice_data.get('upi_reference'):
                payment_info.append(["<b>UPI Reference:</b>", invoice_data.get('upi_reference')])
        
        elif payment_method == "UPI" and invoice_data.get('upi_reference'):
            payment_info.append(["<b>UPI Reference:</b>", invoice_data.get('upi_reference')])
        
        elif payment_method == "CREDIT":
            credit_amount = invoice_data.get('credit_amount', 0)
            payment_info.append(["<b>Credit Amount:</b>", format_currency(credit_amount)])
        
        # Convert all cells to Paragraphs
        for i in range(len(payment_info)):
            payment_info[i][0] = Paragraph(payment_info[i][0], styles['Normal'])
            payment_info[i][1] = Paragraph(payment_info[i][1], styles['Normal'])
        
        # Create heading and table in a framed container
        payment_frame_data = [
            [Paragraph("<b>Payment Information</b>", styles['SectionTitle'])],
            [Table(payment_info, colWidths=[4*cm, 6*cm], 
                   style=TableStyle([
                       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                       ('PADDING', (0, 0), (-1, -1), 8)
                   ]))]
        ]
        
        payment_frame = Table(payment_frame_data, colWidths=[doc.width])
        payment_frame.setStyle(TableStyle([
            ('BOX', (0, 0), (0, -1), 1, colors.black),  # Border around entire box
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),  # Line below heading
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),  # Header background
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center header
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 6),
            ('BOTTOMPADDING', (0, 0), (0, 0), 6),
        ]))
        elements.append(payment_frame)
        
        # Signature section
        elements.append(Spacer(1, 1*cm))
        signature_data = [
            ["For " + shop_name, "Customer Signature"],
            ["Authorized Signatory", ""]
        ]
        
        signature_table = Table(signature_data, colWidths=[doc.width/2, doc.width/2])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),
            ('LINEABOVE', (1, 0), (1, 0), 1, colors.black),
        ]))
        elements.append(signature_table)
        
        # Footer
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("Thank you for your business!", styles['CenterBold']))
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