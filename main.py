import os
import secrets
import sys
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

# Ensure local modules in the same directory can be imported when running directly
sys.path.append(str(Path(__file__).resolve().parent))

# NEW: Import the connector we just built
from google_sheets import get_tracker_data

load_dotenv()

app = FastAPI(title="Personal OS Backend")
security = HTTPBasic()

VALID_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
VALID_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "secret")

# NEW: Fetch the Spreadsheet ID from our environment variables
SHEET_ID = os.getenv("SPREADSHEET_ID")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
def read_root():
    return {"message": "Backend is running. Access /docs to test endpoints."}

# UPDATED: This endpoint now actually fetches your live spreadsheet data
@app.get("/api/purchases")
def get_purchases(username: str = Depends(verify_credentials)):
    try:
        if not SHEET_ID:
            return {"status": "error", "message": "Spreadsheet ID is missing from .env"}
            
        data = get_tracker_data(SHEET_ID)
        return {
            "status": "success", 
            "user": username,
            "row_count": len(data),
            "data": data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}