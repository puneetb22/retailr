
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

def generate_invoice(invoice_data, output_path):
    """Generate PDF invoice with the provided data"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("INVOICE", header_style))
    elements.append(Spacer(1, 20))

    # Invoice details
    invoice_details = [
        ['Invoice Number:', invoice_data['invoice_number']],
        ['Date:', invoice_data['date']],
        ['Customer:', invoice_data.get('customer', {}).get('name', '')],
    ]
    
    detail_table = Table(invoice_details, colWidths=[2*inch, 4*inch])
    detail_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 20))

    # Items table
    items_data = [['Item', 'Quantity', 'Rate', 'Total']]
    for item in invoice_data.get('items', []):
        items_data.append([
            item.get('name', ''),
            str(item.get('quantity', '')),
            str(item.get('rate', '')),
            str(item.get('total', ''))
        ])

    items_table = Table(items_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))

    # Payment details
    payment = invoice_data.get('payment', {})
    payment_data = [
        ['Subtotal:', str(payment.get('subtotal', ''))],
        ['Discount:', str(payment.get('discount', ''))],
        ['CGST:', str(payment.get('cgst', ''))],
        ['SGST:', str(payment.get('sgst', ''))],
        ['Total:', str(payment.get('total', ''))]
    ]
    
    payment_table = Table(payment_data, colWidths=[2*inch, 2*inch])
    payment_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(payment_table)

    # Build the PDF
    doc.build(elements)
