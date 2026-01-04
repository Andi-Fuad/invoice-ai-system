import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import os
from app.config import settings

class ReportService:
    @staticmethod
    def generate_report(db: Session, start_date, end_date, report_type: str) -> str:
        """Generate PDF report with grouped invoice structure"""
        # Query invoices
        invoices = db.query(Invoice).filter(
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).order_by(Invoice.invoice_date.desc()).all()
        
        # Generate PDF
        filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(settings.report_dir, filename)
        
        # Use landscape for better table layout
        doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"Invoice Report ({report_type.capitalize()})", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary Statistics
        if invoices:
            total_invoices = len(invoices)
            total_amount = sum(inv.total for inv in invoices)
            unique_stores = len(set(inv.store_name for inv in invoices))
            total_items = sum(len(inv.details) for inv in invoices)
            
            summary_text = f"""
            <b>Period:</b> {start_date} to {end_date}<br/>
            <b>Total Invoices:</b> {total_invoices}<br/>
            <b>Total Items:</b> {total_items}<br/>
            <b>Unique Stores:</b> {unique_stores}<br/>
            <b>Total Amount:</b> Rp.{total_amount:,.2f}
            """
        else:
            summary_text = f"""
            <b>Period:</b> {start_date} to {end_date}<br/>
            <b>No invoices found for this period</b>
            """
        
        summary = Paragraph(summary_text, styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed Table with grouped invoices
        if invoices:
            # Create table header
            table_data = [[
                'Invoice Date',
                'Store',
                'Product',
                'Qty',
                'Unit',
                'Amount',
                'Discount',
                'Total'
            ]]
            
            # Build table with invoice grouping
            for invoice in invoices:
                # First row of invoice (with invoice-level info)
                first_detail = invoice.details[0]
                table_data.append([
                    str(invoice.invoice_date),
                    invoice.store_name,
                    first_detail['product_name'],
                    f"{first_detail['quantity']:.2f}",
                    first_detail['unit'],
                    f"Rp.{first_detail['amount']:,.2f}",
                    f"Rp.{first_detail['discount']:,.2f}",
                    f"Rp.{invoice.total:,.2f}"
                ])
                
                # Subsequent rows (sub-rows for additional products)
                for detail in invoice.details[1:]:
                    table_data.append([
                        '',  # Empty date (merged cell effect)
                        '',  # Empty store (merged cell effect)
                        detail['product_name'],
                        f"{detail['quantity']:.2f}",
                        detail['unit'],
                        f"Rp.{detail['amount']:,.2f}",
                        f"Rp.{detail['discount']:,.2f}",
                        ''  # Empty total (only show on first row)
                    ])
            
            # Create table
            t = Table(table_data, colWidths=[80, 120, 150, 50, 50, 70, 70, 80])
            
            # Apply styling
            style = TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (6, -1), 'RIGHT'),  # Right align numbers
                ('ALIGN', (7, 1), (7, -1), 'RIGHT'),  # Right align total
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
            ])
            
            # Add alternating row colors and invoice grouping
            row_num = 1
            for i, invoice in enumerate(invoices):
                num_details = len(invoice.details)
                
                # Alternate background color per invoice group
                bg_color = colors.HexColor('#f8f9fa') if i % 2 == 0 else colors.white
                style.add('BACKGROUND', (0, row_num), (-1, row_num + num_details - 1), bg_color)
                
                # Add thicker line between invoice groups
                if row_num > 1:
                    style.add('LINEABOVE', (0, row_num), (-1, row_num), 1.5, colors.HexColor('#34495e'))
                
                # Bold the first row of each invoice
                style.add('FONTNAME', (0, row_num), (1, row_num), 'Helvetica-Bold')
                style.add('FONTNAME', (7, row_num), (7, row_num), 'Helvetica-Bold')
                
                row_num += num_details
            
            t.setStyle(style)
            elements.append(t)
        
        doc.build(elements)
        return filename