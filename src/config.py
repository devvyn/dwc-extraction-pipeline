
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OCR_THRESHOLD = float(os.getenv('OCR_THRESHOLD', '0.85'))
    MODE = os.getenv('APP_MODE', 'local')
