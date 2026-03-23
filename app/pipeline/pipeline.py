import os
import json
from datetime import datetime
from dotenv import load_dotenv

from app.intake.email_reader import fetch_email_attachments
from app.intake.pdf_processor import process_pdfs  # FastAPI integration
from app.database.db_handler import (
    init_db,
    insert_certificate,
    fetch_all_certificates,
    insert_manual_review
)
from app.utils.logger import get_logger

logger = get_logger()

# -----------------------------
# Root directory (project or Azure Function app root)
# -----------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # parent of 'app'

# -----------------------------
# Load .env from root
# -----------------------------
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# -----------------------------
# Folders
# -----------------------------
OUTPUT_FOLDER = os.path.join(ROOT_DIR, "data", "output")
MANUAL_REVIEW_FOLDER = os.path.join(ROOT_DIR, "data", "manual_review")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(MANUAL_REVIEW_FOLDER, exist_ok=True)

# If you use a DOWNLOAD_FOLDER from .env
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", os.path.join(ROOT_DIR, "downloadcertificates", "download"))
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -----------------------------
# FastAPI endpoint
# -----------------------------
FASTAPI_URL = "http://localhost:8000/process-certificates"