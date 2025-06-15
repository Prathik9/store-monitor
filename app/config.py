import os

MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017/")
REPORTS_DIR = os.environ.get("REPORTS_DIR", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)