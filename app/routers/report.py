from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.invoice import ReportRequest
from app.services.report_service import ReportService
from app.config import settings
import os

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/generate")
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Generate invoice report for specified date range
    
    Args:
        request: ReportRequest with start_date, end_date, and report_type (monthly/yearly)
    
    Returns:
        PDF file download
    """
    # Validate report type
    if request.report_type not in ['monthly', 'yearly']:
        raise HTTPException(
            status_code=400, 
            detail="report_type must be 'monthly' or 'yearly'"
        )
    
    # Validate date range
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=400, 
            detail="start_date must be before end_date"
        )
    
    try:
        os.makedirs(settings.report_dir, exist_ok=True)
        
        filename = ReportService.generate_report(
            db, 
            request.start_date, 
            request.end_date, 
            request.report_type
        )
        
        filepath = os.path.join(settings.report_dir, filename)
        
        return FileResponse(
            filepath, 
            filename=filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
