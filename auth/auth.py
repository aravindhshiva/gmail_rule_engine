"""
auth.py - Main module managing OAuth authentication with Google API. Requires a credentials.json file at `config`.
"""
import os.path

from dotenv import load_dotenv

load_dotenv()

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = os.getenv("SCOPES").split(",")

TOKEN_FILE = os.getenv("TOKEN_FILE")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")

from logutils.utils import get_logger

log = get_logger()

def auth():
    try:
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        return creds
    except (ValueError, IOError) as e:
        log.failure(e)
        raise RuntimeError("Cannot retrieve token for processing.")

def credentials():
    return auth()
