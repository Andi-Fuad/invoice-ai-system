from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse
from app.services.gemini_service import GeminiService
from app.utils.file_handler import convert_to_supported_format
from datetime import datetime
import os
from app.config import settings

router = APIRouter(prefix="/invoices", tags=["invoices"])
gemini = GeminiService()

@router.post("/upload", response_model=InvoiceResponse)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process invoice image/PDF
    Supported formats: PNG, JPEG, JPG, WEBP, PDF
    """
    # Validate file type
    allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'application/pdf']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Read file
        content = await file.read()
        
        # Convert to supported format if needed
        processed_content, mime_type = convert_to_supported_format(content, file.content_type)
        
        # Extract structured data using Gemini Vision
        invoice_data = gemini.extract_invoice_data(processed_content, mime_type)
        
        # Save original file
        os.makedirs(settings.upload_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(settings.upload_dir, f"{timestamp}_{file.filename}")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Save to database
        db_invoice = Invoice(
            vendor_name=invoice_data['vendor_name'],
            invoice_date=datetime.strptime(invoice_data['invoice_date'], '%Y-%m-%d').date(),
            total=float(invoice_data['total']),
            details=invoice_data['details'],
            file_path=file_path
        )
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        
        return db_invoice
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")

@router.get("/", response_model=list[InvoiceResponse])
def get_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all invoices with pagination"""
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get specific invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Delete invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete file if exists
    if os.path.exists(invoice.file_path):
        os.remove(invoice.file_path)
    
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully"}
