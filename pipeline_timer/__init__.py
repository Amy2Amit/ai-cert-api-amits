import datetime
import logging
import azure.functions as func
import os
from dotenv import load_dotenv

# Load .env from function app root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # TimerTrigger folder
FUNCTION_ROOT = os.path.dirname(BASE_DIR)             # Azure Function app root
load_dotenv(os.path.join(FUNCTION_ROOT, ".env"))

from app.pipeline import pipeline  # your existing pipeline.py