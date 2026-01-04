from sqlalchemy import Column, Integer, String, Float, Date, JSON, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String, index=True)
    invoice_date = Column(Date)
    total = Column(Float)
    details = Column(JSON) 
    file_path = Column(String)
    file_hash = Column(String(64), unique=True, index=True)  # For detecting duplicates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Create index for faster duplicate checking
    __table_args__ = (
        Index('idx_file_hash', 'file_hash'),
    )