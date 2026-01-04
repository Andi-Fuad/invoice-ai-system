import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import os
from app.config import settings

class ReportService:
    @staticmethod
    def generate_report(db: Session, start_date, end_date, report_type: str) -> str:
        """Generate PDF report for specified date range"""
        # Query invoices
        invoices = db.query(Invoice).filter(
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).all()
        
        # Create DataFrame
        data = []
        for inv in invoices:
            for detail in inv.details:
                data.append({
                    'Date': inv.invoice_date,
                    'Vendor': inv.vendor_name,
                    'Product': detail['product_name'],
                    'Quantity': detail['quantity'],
                    'Unit': detail['unit'],
                    'Amount': detail['amount'],
                    # 'Invoice Total': inv.total
                })
        
        df = pd.DataFrame(data)
        
        # Generate PDF
        filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(settings.report_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"Invoice Report ({report_type.capitalize()})", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary Statistics
        if not df.empty:
            total_invoices = len(invoices)
            total_amount = df['Amount'].sum()
            total_items = len(df)
            unique_vendors = df['Vendor'].nunique()
            
            summary_text = f"""
            <b>Period:</b> {start_date} to {end_date}<br/>
            <b>Total Invoices:</b> {total_invoices}<br/>
            <b>Total Items:</b> {total_items}<br/>
            <b>Unique Vendors:</b> {unique_vendors}<br/>
            <b>Total Amount:</b> Rp.{total_amount:.2f}
            """
        else:
            summary_text = f"""
            <b>Period:</b> {start_date} to {end_date}<br/>
            <b>No invoices found for this period</b>
            """
        
        summary = Paragraph(summary_text, styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed Table
        if not df.empty:
            # Format dates and amounts
            df['Date'] = df['Date'].astype(str)
            df['Amount'] = df['Amount'].apply(lambda x: f"Rp.{x:.2f}")
            # df['Invoice Total'] = df['Invoice Total'].apply(lambda x: f"${x:.2f}")
            
            table_data = [df.columns.tolist()] + df.values.tolist()
            
            # Create table with styling
            t = Table(table_data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(t)
        
        doc.build(elements)
        return filename