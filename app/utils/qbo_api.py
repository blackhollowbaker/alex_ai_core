# app/utils/qbo_api.py

import requests
import os

from app.db import SessionLocal, QBOToken
from datetime import datetime

def get_latest_token():
    db = SessionLocal()
    token = db.query(QBOToken).first()
    db.close()
    return token

def fetch_transactions(access_token, realm_id):
    token = refresh_token_if_needed()
    if not token:
        return {"error": "No QBO token available."}

    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }

    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{token.realm_id}/query"
    query = "SELECT * FROM Purchase MAXRESULTS 10"

    response = requests.post(url, headers=headers, data=query)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json().get("QueryResponse", {}).get("Purchase", [])


from app.db import SessionLocal, QBOToken
from datetime import datetime, timedelta
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("QBO_CLIENT_ID")
CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

def refresh_token_if_needed():
    db = SessionLocal()
    token = db.query(QBOToken).first()

    if not token:
        db.close()
        return None

    if datetime.utcnow() < token.expires_at:
        db.close()
        return token  # Token still valid

    # Token expired — refresh it
    print("🔄 Refreshing QBO token...")

    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token
    }

    response = requests.post(TOKEN_URL, headers=headers, data=body)
    if response.status_code != 200:
        db.close()
        raise Exception(f"Token refresh failed: {response.text}")

    new_data = response.json()
    token.access_token = new_data["access_token"]
    token.refresh_token = new_data.get("refresh_token", token.refresh_token)
    token.expires_at = datetime.utcnow() + timedelta(seconds=int(new_data["expires_in"]))

    db.commit()
    db.refresh(token)
    db.close()
    return token
