# ==============================
# Dockerfile for AI_CERTIFICATE_PROCESS_AGENT
# ==============================

FROM python:3.11-slim

# Install system dependencies for Tesseract OCR and Pillow
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI with Gunicorn + Uvicorn
# Ensure the path matches your FastAPI app instance
# In your case, 'app.api.main:app' should be the FastAPI object
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.api.main:app", "--bind", "0.0.0.0:8000", "--timeout", "120"]