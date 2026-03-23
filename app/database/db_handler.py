# app/database/db_handler.py

import sqlite3
import os
import json
from datetime import datetime

# -----------------------------
# Database configuration
# -----------------------------
DB_FOLDER = os.path.join(os.getcwd(), "data")
DB_PATH = os.path.join(DB_FOLDER, "certificates.db")
os.makedirs(DB_FOLDER, exist_ok=True)


# -----------------------------
# Step 1: Initialize DB
# -----------------------------
def init_db():
    """
    Create the certificates and manual_review tables if they don't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Certificates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT,
            gl_limit INTEGER,
            el_limit INTEGER,
            coverage_start TEXT,
            coverage_end TEXT,
            additional_insured BOOLEAN,
            processed_at TEXT
        )
    """)
    # Manual review table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manual_review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            error_msg TEXT,
            run_id TEXT,
            processed_at TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------
# Step 2: Insert OCR JSON
# -----------------------------
def insert_certificate(data):
    """
    Insert a single ACORD 25 record (JSON) into the certificates table
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO certificates
        (vendor_name, gl_limit, el_limit, coverage_start, coverage_end, additional_insured, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("vendor_name"),
        data.get("gl_limit"),
        data.get("el_limit"),
        data.get("coverage_start"),
        data.get("coverage_end"),
        int(data.get("additional_insured", 0)),  # SQLite stores BOOLEAN as 0/1
        data.get("processed_at", datetime.utcnow().isoformat())
    ))
    conn.commit()
    conn.close()


# -----------------------------
# Step 3: Insert for manual review
# -----------------------------
def insert_manual_review(filename, error_msg, structured_json, run_id):
    """
    Insert records that require manual review into a separate table
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manual_review
        (filename, error_msg, run_id, processed_at, data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        error_msg,
        run_id,
        datetime.utcnow().isoformat(),
        json.dumps(structured_json)
    ))
    conn.commit()
    conn.close()


# -----------------------------
# Optional: Fetch all records (for testing)
# -----------------------------
def fetch_all_certificates():
    """
    Return all certificates in the database (for debug / validation)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificates")
    rows = cursor.fetchall()
    conn.close()
    return rows


def fetch_all_manual_reviews():
    """
    Return all manual review records (for debug / validation)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM manual_review")
    rows = cursor.fetchall()
    conn.close()
    return rows


# -----------------------------
# Standalone test (commented out)
# -----------------------------
# if __name__ == "__main__":
#     from app.extraction.ocr import extract_text_from_pdf, extract_acord_fields
#
#     # Initialize DB
#     init_db()
#
#     # Test PDF
#     pdf_path = "mock_files/ACORD25.pdf"  # replace with actual path
#     pdf_text = extract_text_from_pdf(pdf_path)
#     data = extract_acord_fields(pdf_text)
#
#     # Insert into DB
#     insert_certificate(data)
#     print("✅ Record inserted into SQLite!")
#
#     # Insert for manual review (example)
#     insert_manual_review("ACORD25.pdf", "Missing GL limit", data, "run_001")
#     print("✅ Manual review record inserted!")
#
#     # Fetch & display all records
#     print(fetch_all_certificates())
#     print(fetch_all_manual_reviews())