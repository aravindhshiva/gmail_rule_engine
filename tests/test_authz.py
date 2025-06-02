import pytest
from unittest import mock

from authz import authz

TOKEN_FILE = authz.TOKEN_FILE
CREDENTIALS_FILE = authz.CREDENTIALS_FILE
SCOPES = authz.SCOPES


def test_authz_with_valid_token(mocker):
    """Test where token exists and is valid."""
    mock_creds = mock.Mock(valid=True)
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("google.oauth2.credentials.Credentials.from_authorized_user_file", return_value=mock_creds)

    # Without mock, we will overwrite the existing token.json file, lol!
    m_open = mocker.mock_open()
    mocker.patch("builtins.open", m_open)

    creds = authz.authz()
    assert creds is mock_creds


def test_authz_with_new_credentials_flow(mocker):
    """Test when no token exists and user goes through OAuth flow."""
    mocker.patch("os.path.exists", return_value=False)
    mock_flow = mock.Mock()
    mock_creds = mock.Mock(valid=True)
    mock_flow.run_local_server.return_value = mock_creds

    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow)
    m_open = mocker.mock_open()
    mocker.patch("builtins.open", m_open)

    creds = authz.authz()
    mock_flow.run_local_server.assert_called_once()
    m_open.assert_called_with(TOKEN_FILE, "w")
    assert creds is mock_creds


def test_authz_raises_runtime_error_on_failure(mocker):
    """Test that authz raises RuntimeError on unexpected exceptions."""
    mocker.patch("os.path.exists", side_effect=ValueError("Some error"))

    with pytest.raises(RuntimeError, match="Cannot retrieve token"):
        authz.authz()
