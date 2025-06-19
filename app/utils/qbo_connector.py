# app/utils/qbo_connector.py

import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("QBO_CLIENT_ID")
CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("QBO_REDIRECT_URI")

SCOPES = "com.intuit.quickbooks.accounting"

AUTH_URL = f"https://appcenter.intuit.com/connect/oauth2?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}&state=123456"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
