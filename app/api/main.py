from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from datetime import datetime
import traceback

# -----------------------------
# Attempt to import dependencies
# -----------------------------
try:
    from app.pipeline.pipeline import run_pipeline
except Exception as e:
    print("ERROR importing run_pipeline:", e)
    run_pipeline = None

try:
    from app.database.db_handler import fetch_all_certificates
except Exception as e:
    print("ERROR importing fetch_all_certificates:", e)
    fetch_all_certificates = None

try:
    import pytesseract
except Exception as e:
    print("ERROR importing pytesseract:", e)

# -----------------------------
# Create FastAPI app
# -----------------------------
app = FastAPI(
    title="AI Insurance Certificate Processing API",
    description="Processes ACORD25 PDFs from email → OCR → DB",
    version="1.0"
)

# -----------------------------
# Debug / Health Check (shows stack trace if error)
# -----------------------------
@app.get("/", response_class=PlainTextResponse)
def home():
    try:
        return f"API is running - {datetime.now()}"
    except Exception as e:
        return str(e) + "\n\n" + traceback.format_exc()

# -----------------------------
# Trigger Pipeline
# -----------------------------
@app.post("/process-certificates")
def process_certificates():
    try:
        if run_pipeline is None:
            raise RuntimeError("Pipeline module not available")
        run_pipeline()
        return {
            "status": "success",
            "message": "Pipeline executed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }

# -----------------------------
# Fetch All Certificates
# -----------------------------
@app.get("/certificates")
def get_certificates():
    try:
        if fetch_all_certificates is None:
            raise RuntimeError("Database handler module not available")
        data = fetch_all_certificates()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }