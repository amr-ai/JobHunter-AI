import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2025'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = BASE_DIR / 'flask_session'
    SESSION_FILE_THRESHOLD = 500
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7

    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    STATIC_FOLDER = BASE_DIR / 'static'
    DATA_FOLDER = BASE_DIR / 'data'

    SCRAPE_TIMEOUT = 15
    MAX_JOBS_PER_SOURCE = 50

    SKILLS_WEIGHT = 0.50
    KEYWORDS_WEIGHT = 0.15
    EXPERIENCE_WEIGHT = 0.20
    EDUCATION_WEIGHT = 0.10
    ATS_WEIGHT = 0.05

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

for folder in [Config.UPLOAD_FOLDER, Config.SESSION_FILE_DIR, Config.DATA_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)