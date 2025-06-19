# app/skills/anomaly_detector.py

from datetime import datetime, timedelta
from app.utils.qbo_api import fetch_transactions
import os
from dotenv import load_dotenv

load_dotenv()

# Placeholder for QBO connector
def get_qbo_transactions():
    access_token = os.getenv("QBO_ACCESS_TOKEN")
    realm_id = os.getenv("QBO_REALM_ID")
    return fetch_transactions(access_token, realm_id)

def detect_duplicates(transactions):
    seen = set()
    duplicates = []
    for txn in transactions:
        key = (txn["vendor"], txn["amount"], txn["date"])
        if key in seen:
            duplicates.append(txn)
        else:
            seen.add(key)
    return duplicates

def detect_unusual_amounts(transactions, history={}):
    anomalies = []
    for txn in transactions:
        vendor = txn["vendor"]
        amount = txn["amount"]
        avg = history.get(vendor, 0)
        if avg and (abs(amount - avg) / avg > 0.5):  # >50% deviation
            anomalies.append({
                "transaction": txn,
                "reason": f"Amount {amount} deviates from avg {avg:.2f} by >50%"
            })
    return anomalies

def detect_new_vendors(transactions, known_vendors):
    return [txn for txn in transactions if txn["vendor"] not in known_vendors]

from app.utils.qbo_api import fetch_transactions
def run_anomaly_detection():
    from app.db import get_latest_credentials
    # If not already imported

    #get creds
    creds = get_latest_credentials()
    access_token = creds["access_token"]
    realm_id = creds["realm_id"]
    
    #fecth transactions
    transactions = fetch_transactions(access_token, realm_id)


    # Basic normalization (convert to consistent keys)
    parsed_txns = []
    for txn in transactions:
        parsed_txns.append({
            "date": txn.get("TxnDate"),
            "vendor": txn.get("EntityRef", {}).get("name", "Unknown"),
            "amount": txn.get("TotalAmt", 0.0),
            "category": txn.get("AccountRef", {}).get("name", "Uncategorized")
        })

    # Mock data for now
    avg_spend = {"Adobe": 89.99, "Zoom": 295.00}
    known_vendors = {"Adobe", "Zoom"}

    flags = {
        "duplicates": detect_duplicates(parsed_txns),
        "unusual_amounts": detect_unusual_amounts(parsed_txns, avg_spend),
        "new_vendors": detect_new_vendors(parsed_txns, known_vendors)
    }

    return flags

