import fitz  # PyMuPDF
from app.extraction.ocr import extract_text_from_scanned_pdf


def read_file(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)

        for page in doc:
            text += page.get_text()

        # 🔥 If no text → use OCR
        if not text.strip():
            text = extract_text_from_scanned_pdf(file_path)

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    else:
        raise Exception("Unsupported file type")

    return text.strip()