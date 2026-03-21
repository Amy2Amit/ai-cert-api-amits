from fastapi import FastAPI
from datetime import datetime

from app.pipeline.pipeline import run_pipeline
from app.database.db_handler import fetch_all_certificates

app = FastAPI(
    title="AI Insurance Certificate Processing API",
    description="Processes ACORD25 PDFs from email → OCR → DB",
    version="1.0"
)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "API is running",
        "timestamp": datetime.now()
    }


# -----------------------------
# Trigger Pipeline
# -----------------------------
@app.post("/process-certificates")
def process_certificates():
    """
    Trigger full pipeline:
    Email → PDF → OCR → JSON → SQLite
    """
    try:
        run_pipeline()
        return {
            "status": "success",
            "message": "Pipeline executed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# -----------------------------
# Fetch All Certificates
# -----------------------------
@app.get("/certificates")
def get_certificates():
    """
    Fetch all processed certificate records from SQLite
    """
    try:
        data = fetch_all_certificates()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }