from fastapi import FastAPI, Request
from app.utils.qbo_connector import AUTH_URL, TOKEN_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
import requests
import base64

app = FastAPI()  # ← This must come before any @app.get

@app.get("/")
def root():
    return {"message": "Alex is running."}

@app.get("/qbo/connect")
def connect_to_qbo():
    return {"auth_url": AUTH_URL}

from app.db import SessionLocal, QBOToken
from datetime import datetime, timedelta

@app.get("/callback")
def qbo_callback(request: Request):
    code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")
    
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, headers=headers, data=body)
    
    if response.status_code != 200:
        return {"error": response.text}
    
    tokens = response.json()
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(seconds=int(tokens["expires_in"]))

    db = SessionLocal()
    db.query(QBOToken).delete()  # Clear any old token
    new_token = QBOToken(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        realm_id=realm_id,
        expires_at=expires_at
    )
    db.add(new_token)
    db.commit()
    db.close()

    return {"message": "Token stored successfully."}


import os
from dotenv import load_dotenv
from app.utils.qbo_api import fetch_transactions

load_dotenv()

@app.get("/qbo/transactions")
def get_transactions():
    access_token = os.getenv("QBO_ACCESS_TOKEN")
    realm_id = os.getenv("QBO_REALM_ID")
    return fetch_transactions(access_token, realm_id)

from app.skills.anomaly_detector import run_anomaly_detection

@app.get("/detect_anomalies")
def detect_anomalies():
    return run_anomaly_detection()

from app.skills.anomaly_detector import run_anomaly_detection
from app.utils.report_generator import generate_pdf_report

@app.get("/report/summary")
def generate_report():
    flags = run_anomaly_detection()
    pdf_path = generate_pdf_report(flags)
    return {"report_path": pdf_path}

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="."), name="static")
