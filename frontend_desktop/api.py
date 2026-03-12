"""
api.py
------
All HTTP communication with the Django backend lives here.
UI code should never call requests directly — always go through this module.
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api"


class APIError(Exception):
    """Raised when the backend returns an error or network fails."""
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


def login(username: str, password: str) -> str:
    """
    POST /api/login/
    Returns the auth token string on success.
    Raises APIError on failure.
    """
    try:
        resp = requests.post(
            f"{BASE_URL}/login/",
            data={"username": username, "password": password},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        raise APIError("Cannot reach server. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise APIError("Request timed out. The server may be slow.")

    if resp.status_code == 200:
        data = resp.json()
        return data["token"]
    elif resp.status_code == 400:
        raise APIError("Invalid credentials. Please try again.", 400)
    else:
        raise APIError(f"Login failed (HTTP {resp.status_code}).", resp.status_code)


def register(username: str, password: str, email: str = "") -> dict:
    """
    POST /api/register/
    Creates a new user account.
    Returns the response dict on success (may include token or success message).
    Raises APIError on failure.
    """
    try:
        payload = {"username": username, "password": password}
        if email:
            payload["email"] = email

        resp = requests.post(
            f"{BASE_URL}/register/",
            data=payload,
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        raise APIError("Cannot reach server. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise APIError("Request timed out. The server may be slow.")

    if resp.status_code in (200, 201):
        return resp.json()
    elif resp.status_code == 400:
        # Django REST Framework returns field-level validation errors as JSON.
        # Flatten them into a single readable string for the UI.
        try:
            errors = resp.json()
            messages = []
            for field, msgs in errors.items():
                if isinstance(msgs, list):
                    messages.append(f"{field}: {', '.join(str(m) for m in msgs)}")
                else:
                    messages.append(str(msgs))
            raise APIError(" | ".join(messages), 400)
        except (ValueError, AttributeError):
            raise APIError("Registration failed. Please check your details.", 400)
    elif resp.status_code == 409:
        raise APIError("Username already exists. Please choose another.", 409)
    else:
        raise APIError(f"Registration failed (HTTP {resp.status_code}).", resp.status_code)


def upload_csv(token: str, filepath: str) -> dict:
    """
    POST /api/upload/
    Sends the CSV file and returns the backend summary dict.
    Raises APIError on failure.
    """
    headers = {"Authorization": f"Token {token}"}
    try:
        with open(filepath, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/upload/",
                headers=headers,
                files={"file": (filepath.split("/")[-1], f, "text/csv")},
                timeout=30,
            )
    except requests.exceptions.ConnectionError:
        raise APIError("Cannot reach server. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise APIError("Upload timed out. File may be too large.")
    except FileNotFoundError:
        raise APIError("Selected file could not be opened.")

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 401:
        raise APIError("Session expired. Please log in again.", 401)
    else:
        raise APIError(f"Upload failed (HTTP {resp.status_code}).", resp.status_code)


def get_history(token: str) -> list:
    """
    GET /api/history/
    Returns list of last 5 upload records for the current user.
    Raises APIError on failure.
    """
    headers = {"Authorization": f"Token {token}"}
    try:
        resp = requests.get(
            f"{BASE_URL}/history/",
            headers=headers,
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        raise APIError("Cannot reach server. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise APIError("Request timed out.")

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 401:
        raise APIError("Session expired. Please log in again.", 401)
    else:
        raise APIError(f"History fetch failed (HTTP {resp.status_code}).", resp.status_code)