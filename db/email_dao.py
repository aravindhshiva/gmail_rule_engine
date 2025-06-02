import os
import sqlite3

from model.email import Email

DB_FILE_PATH = "config/email.db"

class EmailDAO:
    """
    Very simple DAO for emails. Supports only insertion of emails and a way to query the emails table.

    For now, this is a very simple implementation where a connection is created when the class is instantiated. We can make this
    better by creating a connection pool, and also ensuring a new connection is created for each query.
    """
    def __init__(self):
        if not os.path.exists(DB_FILE_PATH):
            raise FileNotFoundError(f"No database exists at {DB_FILE_PATH}.")

        conn = sqlite3.connect(DB_FILE_PATH)
        conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    def insert_email(self, email: Email):
        query = "INSERT INTO email('MESSAGEID', 'FROMEMAIL', 'TOEMAIL', 'RECEIVEDDATE', 'SUBJECT', 'BODY') VALUES (?, ?, ?, ?, ?, ?)"
        params = (email.message_id, email.from_email, email.to_email, email.received_date, email.subject, email.body)
        self.cursor.execute(query, params)
        self.cursor.connection.commit()


    def query_email(self, where_clause):
        base_query = "SELECT * FROM email WHERE"
        full_query = f"{base_query} {where_clause}"
        # print(f"Running the query -- {full_query}")

        rows = self.cursor.execute(full_query)
        emails = []
        for row in rows.fetchall():
            emails.append(Email.from_dict(dict(row)))

        return emails

