import sqlite3
import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from authz import authz

from dateutil import parser
import base64
import click

from db.email_dao import EmailDAO
from model.email import Email


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
        print(f'An error occurred: {e}')

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
        print("No messages found in inbox.")
        sys.exit(1)  # Exiting with 1 for proper CLI behavior

      print(f"Loading {len(messages)} messages from inbox.")
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
    except HttpError as error:
      print(f"An error occurred: {error}")
      sys.exit(1)
    except sqlite3.Error as error:
      print(f"Cannot add message to database. Error: {error}")
      sys.exit(1)