import os
import json
from datetime import datetime

from app.intake.email_reader import fetch_email_attachments
from app.intake.pdf_processor import process_pdfs  # FastAPI integration
from app.extraction.ocr import extract_text_from_pdf, extract_acord_fields  # OLD: keep commented
from app.database.db_handler import (
    init_db,
    insert_certificate,
    fetch_all_certificates,
    insert_manual_review  # Manual review insertion
)
from app.utils.logger import get_logger

logger = get_logger()

OUTPUT_FOLDER = os.path.join(os.getcwd(), "data", "output")
MANUAL_REVIEW_FOLDER = os.path.join(os.getcwd(), "data", "manual_review")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(MANUAL_REVIEW_FOLDER, exist_ok=True)

# FastAPI endpoint
FASTAPI_URL = "http://localhost:8000/process_pdf"  # adjust if needed


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

        # Step 2: Fetch PDF attachments
        pdf_files = fetch_email_attachments()
        if not pdf_files:
            print("📧 No new PDFs found → Nothing to process")
            return

        # Step 3: Process PDFs via FastAPI
        results = process_pdfs(os.path.dirname(pdf_files[0]), FASTAPI_URL)

        inserted_records = []

        for filename, result in results.items():
            print(f"\n📄 Processing result for: {filename}")

            if result["status"] == "success":
                structured_json = result["data"]
                structured_json["processed_at"] = run_id

                vendor_name = structured_json.get("vendor_name")
                policy_number = structured_json.get("policy_number")

                # -----------------------------
                # Manual review for missing key fields
                # -----------------------------
                if not vendor_name or not policy_number:
                    error_msg = "Missing vendor_name or policy_number"
                    print(f"⚠️ Manual Review Needed: {error_msg}")

                    insert_manual_review(filename, error_msg, structured_json, run_id)

                    # Save JSON to manual_review folder
                    review_json_path = os.path.join(
                        MANUAL_REVIEW_FOLDER,
                        f"{os.path.splitext(filename)[0]}_{run_id.replace(':','-')}.json"
                    )
                    with open(review_json_path, "w", encoding="utf-8") as f:
                        json.dump(structured_json, f, indent=4)
                    print(f"📝 Manual review JSON saved: {review_json_path}")
                    continue  # skip DB insertion

                # DB Insert
                try:
                    insert_certificate(structured_json)
                    print(f"✅ Inserted into DB: {vendor_name}")
                    inserted_records.append(vendor_name)
                except Exception as e:
                    print(f"❌ DB Insert Failed: {str(e)}")
                    insert_manual_review(filename, str(e), structured_json, run_id)

                    # Save JSON to manual_review folder
                    review_json_path = os.path.join(
                        MANUAL_REVIEW_FOLDER,
                        f"{os.path.splitext(filename)[0]}_{run_id.replace(':','-')}.json"
                    )
                    with open(review_json_path, "w", encoding="utf-8") as f:
                        json.dump(structured_json, f, indent=4)
                    print(f"📝 Manual review JSON saved: {review_json_path}")

                # Save JSON
                json_file_path = os.path.join(OUTPUT_FOLDER, f"{vendor_name}.json")
                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(structured_json, f, indent=4)
                print(f"📝 JSON saved: {json_file_path}")

            else:
                # FastAPI failed
                print(f"❌ Failed to process {filename}: {result['data']}")
                insert_manual_review(filename, result['data'], None, run_id)

                # Save empty or raw JSON for review
                review_json_path = os.path.join(
                    MANUAL_REVIEW_FOLDER,
                    f"{os.path.splitext(filename)[0]}_{run_id.replace(':','-')}.json"
                )
                with open(review_json_path, "w", encoding="utf-8") as f:
                    json.dump({"error": result['data']}, f, indent=4)
                print(f"📝 Manual review JSON saved: {review_json_path}")

            # -----------------------------
            # OLD: Local OCR & extraction (keep for reference)
            # -----------------------------
            """
            print(f"\n📄 Processing PDF (OLD OCR): {filename}")

            pdf_text = extract_text_from_pdf(os.path.join(os.path.dirname(pdf_files[0]), filename))
            if not pdf_text:
                print("⚠️ No text extracted → Skipping")
                continue

            structured_json_old = extract_acord_fields(pdf_text)
            structured_json_old["processed_at"] = run_id
            print("\n🔍 Extracted JSON (OLD OCR):")
            print(json.dumps(structured_json_old, indent=4))
            """

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