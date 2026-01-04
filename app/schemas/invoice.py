from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class InvoiceDetail(BaseModel):
    product_name: str
    quantity: float
    unit: str
    amount: float
    discount: float

class InvoiceCreate(BaseModel):
    store_name: str
    invoice_date: date
    total: float
    details: List[InvoiceDetail]

class InvoiceResponse(InvoiceCreate):
    id: int
    file_path: str
    file_hash: str
    is_cached: Optional[bool] = False  # Indicates if data was from cache

    class Config:
        from_attributes = True

class ReportRequest(BaseModel):
    start_date: date
    end_date: date
    report_type: str  # "monthly" or "yearly"