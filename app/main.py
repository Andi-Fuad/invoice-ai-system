from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import invoice
import os
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

# Create directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.report_dir, exist_ok=True)

app = FastAPI(
    title="Invoice Processing API",
    description="AI-powered invoice processing using Gemini Vision API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invoice.router)
# app.include_router(report.router)

@app.get("/")
def root():
    return {
        "message": "Invoice Processing API is running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "upload_invoice": "POST /invoices/upload",
            "list_invoices": "GET /invoices/",
            "generate_report": "POST /reports/generate"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)