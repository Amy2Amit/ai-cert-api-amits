# app/pipeline/pipeline.py

import os
import json
from datetime import datetime

from app.intake.email_reader import fetch_email_attachments
from app.extraction.ocr import extract_text_from_pdf, extract_acord_fields
from app.database.db_handler import init_db, insert_certificate, fetch_all_certificates
from app.utils.logger import get_logger

logger = get_logger()

OUTPUT_FOLDER = os.path.join(os.getcwd(), "data", "output")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def run_pipeline():
    try:
        run_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("\n" + "="*50)
        print(f"🚀 PIPELINE STARTED AT: {run_id}")
        print("="*50)

        logger.info("🚀 Pipeline started")

        # Step 1: Init DB
        init_db()
        print("📦 Database initialized")

        # Step 2: Fetch PDF
        pdf_files = fetch_email_attachments()
        if not pdf_files:
            print("📧 No new PDFs found → Nothing to process")
            return

        inserted_records = []

        # Step 3: Process PDFs
        for pdf_file in pdf_files:
            print(f"\n📄 Processing PDF: {pdf_file}")

            # OCR
            pdf_text = extract_text_from_pdf(pdf_file)
            if not pdf_text:
                print("⚠️ No text extracted → Skipping")
                continue

            # Extract JSON
            structured_json = extract_acord_fields(pdf_text)

            # 🔥 Add timestamp for THIS RUN
            structured_json["processed_at"] = run_id

            print("\n🔍 Extracted JSON:")
            print(json.dumps(structured_json, indent=4))

            vendor_name = structured_json.get("vendor_name", "Unknown")

            # DB Insert
            try:
                insert_certificate(structured_json)
                print(f"✅ Inserted into DB: {vendor_name}")
                inserted_records.append(vendor_name)
            except Exception as e:
                print(f"❌ DB Insert Failed: {str(e)}")

            # Save JSON
            json_file_path = os.path.join(OUTPUT_FOLDER, f"{vendor_name}.json")
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(structured_json, f, indent=4)

            print(f"📝 JSON saved: {json_file_path}")

        # -----------------------------
        # SHOW ONLY THIS RUN DATA
        # -----------------------------
        print("\n📊 RECORDS INSERTED IN THIS RUN:")
        records = fetch_all_certificates()

        found = False
        for row in records:
            if row[-1] == run_id:  # processed_at column
                print(row)
                found = True

        if not found:
            print("⚠️ No records inserted in this run")

        print("\n🎯 Pipeline completed successfully")

    except Exception as e:
        logger.error(f"🔥 Pipeline failed: {str(e)}")
        print("❌ Pipeline Error:", str(e))


if __name__ == "__main__":
    run_pipeline()