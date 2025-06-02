"""
action_handler.py - Performs processes (like accessing Gmail API) based on configured rulesets.
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import auth
from logutils.utils import get_logger

log = get_logger()

class ActionHandler:
    def __init__(self, emails, actions):
        self.emails = emails
        self.actions = actions
        self.payload = {
            "ids": [],
            "removeLabelIds": [],
            "addLabelIds": []
        }

    def process(self):
        try:
            service = build("gmail", "v1", credentials=auth.credentials())
            for action in self.actions:
                if hasattr(self, action.action_type):
                    if action.action_type == "move_message":
                        getattr(self, action.action_type)(action.destination)
                    else:
                        getattr(self, action.action_type)()

            self.payload["ids"].extend([email.message_id for email in self.emails])

            service.users().messages().batchModify(userId="me", body=self.payload).execute()

            log.success(f"Performed actions: {", ".join([a.action_type for a in self.actions])} on {len(self.emails)} emails")
        except HttpError as e:
            log.failure("Something went wrong while updating the message.", e)
            raise e

    def move_message(self, destination):
        self.payload["addLabelIds"].append(destination)

    def mark_as_read(self):
        if "UNREAD" in self.payload["addLabelIds"]:
            raise ValueError("Cannot add and remove same labels.")

        self.payload["removeLabelIds"].append("UNREAD")

    def mark_as_unread(self):
        if "UNREAD" in self.payload["removeLabelIds"]:
            raise ValueError("Cannot add and remove same labels.")

        self.payload["addLabelIds"].append("UNREAD")
