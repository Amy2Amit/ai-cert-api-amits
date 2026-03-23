import os
import requests
import json
from datetime import datetime

def process_pdfs(pdf_folder: str, fastapi_url: str):
    """
    Process all PDFs in pdf_folder through the FastAPI endpoint.
    Returns a dictionary: {filename: {'status': 'success/error', 'data': JSON or error message}}
    """
    results = {}
    
    # Folder to save JSON responses
    json_folder = os.path.join(pdf_folder, "json_responses")
    os.makedirs(json_folder, exist_ok=True)

    # Iterate over PDFs
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"[{datetime.now()}] Processing: {filename}")
            try:
                with open(pdf_path, "rb") as f:
                    files = {"file": (filename, f, "application/pdf")}
                    response = requests.post(fastapi_url, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Extracted data for {filename}")

                    # Save JSON to file
                    json_path = os.path.join(json_folder, f"{os.path.splitext(filename)[0]}.json")
                    with open(json_path, "w", encoding="utf-8") as jf:
                        json.dump(data, jf, indent=2, ensure_ascii=False)

                    results[filename] = {"status": "success", "data": data}
                else:
                    error_msg = f"FastAPI returned {response.status_code}: {response.text}"
                    print(f"❌ {error_msg}")
                    results[filename] = {"status": "error", "data": error_msg}

            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")
                results[filename] = {"status": "error", "data": str(e)}

    return results