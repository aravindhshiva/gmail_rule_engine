"""
loader.py - Manages loading of emails from the Gmail API, and insertion into local database.
"""
import base64
import sqlite3
import sys

import click
from dateutil import parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from authz import authz
from db.email_dao import EmailDAO
from logutils.utils import get_logger
from model.email import Email

log = get_logger()


class Loader:
  def __init__(self):
    self.service = build("gmail", "v1", credentials=authz.credentials())

  @staticmethod
  def _get_message_body(message):
    payload = message['payload']
    parts = payload.get('parts')
    if parts:
      for part in parts:
        if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
          data = part['body']['data']
          return base64.urlsafe_b64decode(data).decode('utf-8').replace('\r', ' ').replace('\n', ' ')
    else:
      body = payload['body']['data']
      return base64.urlsafe_b64decode(body).decode('utf-8').replace('\r', ' ').replace('\n', ' ')

  def _get_all_messages(self):
    messages = []
    try:
        response = self.service.users().messages().list(userId="me", maxResults=100).execute()
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
          page_token = response['nextPageToken']
          response = self.service.users().messages().list(userId="me", maxResults=100, pageToken=page_token).execute()

          if 'messages' in response:
              messages.extend(response['messages'])

    except Exception as e:
        log.failure(f'An error occurred: {e}')

    return messages

  @staticmethod
  def _get_message_details(message_headers):
    result = {}
    for header in message_headers:
      if header['name'] in {'From','To','Subject'}:
        result[header['name']] = (header['value'])
      elif header['name'] == 'Date':
        result[header['name']] = parser.parse(header['value'])
    return result['From'], result['To'], result['Subject'], result['Date']

  def load(self):
    try:
      messages = self._get_all_messages()

      if not messages:
        log.warning("⚠️  No messages found in inbox.")
        sys.exit(0)  # Exiting with 1 for proper CLI behavior

      log.success(f"Loading {len(messages)} messages from inbox.")
      with click.progressbar(messages) as bar:
        for message in bar:
          message_id = message["id"]
          gmail_message = self.service.users().messages().get(userId="me", id=message_id, format="full").execute()

          email = Email()
          email.message_id = message_id
          email.from_email, email.to_email, email.subject, email.received_date = Loader._get_message_details(
            gmail_message["payload"]["headers"])
          email.body = Loader._get_message_body(gmail_message)

          email_dao = EmailDAO()
          email_dao.insert_email(email)
      log.success(f"Loaded {len(messages)} messages from inbox.")
    except HttpError as error:
      log.failure(f"An error occurred: {error}")
      sys.exit(1)
    except sqlite3.OperationalError as error:
      log.failure(f"An error occurred when inserting into database.")
      log.failure(f"Error: {error}")
      sys.exit(1)
    except sqlite3.IntegrityError as error:
      if "UNIQUE constraint failed" in str(error):
        log.failure("Cannot load the same message twice. The database might already be loaded.")
        sys.exit(1)

      log.failure(f"Something went wrong. Error: {error}")
      sys.exit(1)
