# ocr/ocr.py

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime

# -----------------------------
# Tesseract configuration (Windows)
# -----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# ACORD 25 Field Mapping
# -----------------------------
FIELD_MAPPING = {
    "ACORD 25 Certificate": "vendor_name",
    "General Liability Limit": "gl_limit",
    "Employer Liability Limit": "el_limit",
    "Coverage Start": "coverage_start",
    "Coverage End": "coverage_end",
    "Additional Insured": "additional_insured"
}

# -----------------------------
# PDF Reading Functions
# -----------------------------
def extract_text_from_pdf(pdf_path):
    """Extract text from PDF (digital or scanned)"""
    text = ""

    # Try digital PDF first
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = ""

    # Fallback to OCR if digital PDF has no text
    if not text.strip():
        text = extract_text_from_scanned_pdf(pdf_path)

    return text.strip()


def extract_text_from_scanned_pdf(pdf_path):
    """Use OCR for scanned PDFs"""
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    except Exception:
        text = ""
    return text.strip()


# -----------------------------
# ACORD 25 Parsing Function
# -----------------------------
def extract_acord_fields(pdf_text):
    """
    Convert ACORD 25 PDF text to structured JSON
    """
    data = {}
    if not pdf_text:
        return data

    lines = pdf_text.strip().split("\n")
    for line in lines:
        for field, key in FIELD_MAPPING.items():
            if field in line:
                parts = line.split(":")
                if len(parts) > 1:
                    value = parts[1].strip()
                    if key in ["gl_limit", "el_limit"]:
                        try:
                            value = int(value)
                        except ValueError:
                            value = 0
                    if key == "additional_insured":
                        value = value.lower() == "true"
                    if key == "vendor_name":
                        value = parts[0].replace("ACORD 25 Certificate -", "").strip()
                    data[key] = value

    data["processed_at"] = datetime.now().isoformat()
    return data


# -----------------------------
# Standalone test
# -----------------------------
if __name__ == "__main__":
    pdf_file = "mock_files/ACORD25.pdf"  # Replace with your PDF path
    pdf_text = extract_text_from_pdf(pdf_file)
    if pdf_text:
        structured_json = extract_acord_fields(pdf_text)
        import json
        print(json.dumps(structured_json, indent=4))
    else:
        print("[OCR] No text extracted from PDF.")