# Invoice Processing AI System

An intelligent invoice processing system powered by **Gemini 3.0 Flash** that automatically extracts structured data from invoice images and generates comprehensive reports.

## Features

- **AI-Powered OCR**: Uses Google's Gemini Flash multimodal LLM for accurate data extraction
- **Smart Caching**: Hash-based duplicate detection to save API costs and improve performance
- **Report Generation**: Automated monthly/yearly PDF reports with statistics
- **Database Storage**: SQLite for persistent data storage
- **RESTful API**: FastAPI with automatic interactive documentation
- **Multi-Format Support**: Handles PNG, JPEG, and WEBP files

## Project Structure

```
invoice-processor/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration and environment variables
│   ├── database.py                # Database connection and session
│   ├── models/
│   │   ├── __init__.py
│   │   └── invoice.py            # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── invoice.py            # Pydantic schemas for validation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py     # Gemini Vision API integration
│   │   └── report_service.py     # PDF report generation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── invoice.py            # Invoice endpoints
│   │   └── report.py             # Report endpoints
│   └── utils/
│       ├── __init__.py
│       └── file_handler.py       # File processing and hashing
├── uploads/                       # Uploaded invoice files
├── reports/                       # Generated PDF reports
├── requirements.txt
├── .env
└── README.md
```

## Architecture

```
Upload Invoice → Calculate Hash → Check Cache
                                      ↓
                         ┌────────────┴────────────┐
                         ↓                         ↓
                    Found in Cache?           New Invoice?
                         ↓                         ↓
                  Return Cached Data       Gemini Flash API
                  (Instant, Free)          (Extract Data)
                         ↓                         ↓
                    Response  ←──────────────  Save to DB
```

## Prerequisites

- Python 3.10+
- SQLite for development
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/invoice-processor.git
cd invoice-processor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./invoice.db
GEMINI_API_KEY=your_gemini_api_key_here
UPLOAD_DIR=./uploads
REPORT_DIR=./reports
```

### 4. Run the Application

```bash
python -m app.main
```

The API will be available at: `http://localhost:8000`

### 5. Access Interactive Documentation

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Upload Invoice
```http
POST /invoices/upload
Content-Type: multipart/form-data

Parameters:
  - file: Invoice image/PDF file
  - force_reprocess: (optional) Boolean to bypass cache

Response:
{
  "id": 1,
  "store_name": "ABC Corporation",
  "invoice_date": "2024-01-15",
  "total": 15254327.00,
  "details": [
    {
      "product_name": "Laptop",
      "quantity": 2,
      "unit": "pcs",
      "amount": 2,
      "discount": 0
    }
  ],
  "file_path": "./uploads/...",
  "file_hash": "abc123...",
  "is_cached": false
}
```

### Get All Invoices
```http
GET /invoices/?skip=0&limit=100
```

### Get Single Invoice
```http
GET /invoices/{invoice_id}
```

### Get Invoice by Hash
```http
GET /invoices/hash/{file_hash}
```

### Delete Invoice
```http
DELETE /invoices/{invoice_id}
```

### Generate Report
```http
POST /reports/generate
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "report_type": "monthly"
}

Response: PDF file download
```

## Usage Examples

### Extracting Invoice Data

The system automatically extracts:
- **Vendor Name**: Company or supplier name
- **Invoice Date**: Date of the invoice
- **Line Items**: Products/services with:
  - Product name
  - Quantity
  - Unit of measurement
  - Amount
  - Discount (if applicable)
- **Total Amount**: Final invoice total

### Caching Mechanism

When you upload an invoice:
1. System calculates SHA-256 hash of the file
2. Checks database for existing hash
3. If found: Returns cached data (instant, no API cost)
4. If new: Processes with Gemini API and saves

### Report Generation

Generate professional PDF reports containing:
- Summary statistics (total invoices, amount, vendors)
- Detailed transaction table
- Date range filtering
- Monthly or yearly aggregation

## Author

**Your Name**
- LinkedIn: [A Fuad Ahsan Basir](https://linkedin.com/in/afuadahsan/)
- Portfolio: [fuad.framer.website](https://fuad.framer.website/)

For questions or support, please open an issue or contact [afuadahsan@gmail.com](mailto:afuadahsan@gmail.com)

---






