# app/database/db_handler.py

import sqlite3
import os

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
    Create the certificates table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
        data.get("processed_at")
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


# -----------------------------
# Standalone test
# -----------------------------
if __name__ == "__main__":
    from app.extraction.ocr import extract_text_from_pdf, extract_acord_fields

    # Initialize DB
    init_db()

    # Test PDF
    pdf_path = "mock_files/ACORD25.pdf"  # replace with actual downloaded path
    pdf_text = extract_text_from_pdf(pdf_path)
    data = extract_acord_fields(pdf_text)

    # Insert into DB
    insert_certificate(data)
    print("✅ Record inserted into SQLite!")

    # Fetch & display all records
    records = fetch_all_certificates()
    print(records)