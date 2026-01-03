from sqlalchemy import Column, Integer, String, Float, Date, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String, index=True)
    invoice_date = Column(Date)
    total = Column(Float)
    details = Column(JSON)  # [{product_name, quantity, amount}]
    file_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
