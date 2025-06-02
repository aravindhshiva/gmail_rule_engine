from datetime import datetime
from dataclasses import dataclass

# Maps the column names in the database, to the attribute names in the dataclass.
FIELD_MAP = {
    'ID': 'email_id',
    'FROMEMAIL': 'from_email',
    'TOEMAIL': 'to_email',
    'RECEIVEDDATE': 'received_date',
    'SUBJECT': 'subject',
    'BODY': 'body',
    'MESSAGEID': 'message_id',
}

@dataclass
class Email:
    email_id: str = None
    message_id: str = None
    from_email: str = None
    to_email: str = None
    received_date: datetime = None
    subject: str = None
    body: str = None

    @classmethod
    def from_dict(cls, email_dict):
        kwargs = {}
        for key, value in email_dict.items():
            if key in FIELD_MAP:
                kwargs[FIELD_MAP[key]] = value

        return cls(**kwargs)

    def __repr__(self):
        return f"<Email: {self.email_id}, {self.from_email}, {self.to_email}, {self.subject}>"