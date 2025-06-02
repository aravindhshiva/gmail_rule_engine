from unittest import mock

import pytest

from loader.loader import Loader
from model.email import Email


@pytest.fixture
def mocked_gmail_service():
    """Simulating a mocked gmail service with custom return values."""
    mock_service = mock.Mock()

    mock_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "123"}]
    }

    mock_service.users().messages().get().execute.return_value = {
        "payload": {
            "headers": [
                {"name": "From", "value": "fake@happyfox.com"},
                {"name": "To", "value": "aravindh@happyfox.com"},
                {"name": "Subject", "value": "Rule Engine: Fake Rules All Over"},
                {"name": "Date", "value": "Mon, 05 Jun 1997 01:59:00 +0530"}
            ],
            "body": {
                "data": ""
            }
        },
        "id": "123"
    }

    return mock_service


def test_loader_load_inserts_emails(mocker, mocked_gmail_service):
    """Make sure load() inserts an email into the database."""
    mocker.patch("loader.loader.authz.credentials", return_value=mock.Mock())
    mocker.patch("loader.loader.build", return_value=mocked_gmail_service)

    mock_insert = mocker.patch("loader.loader.EmailDAO.insert_email")

    loader = Loader()
    loader.load()

    assert mock_insert.called
    assert mock_insert.call_count == 1

    # Validate the inserted email fields
    inserted_email: Email = mock_insert.call_args[0][0]
    assert inserted_email.message_id == "123"
    assert inserted_email.from_email == "fake@happyfox.com"
    assert inserted_email.to_email == "aravindh@happyfox.com"
    assert inserted_email.subject == "Rule Engine: Fake Rules All Over"
    assert inserted_email.received_date.isoformat().startswith("1997-06-05")
