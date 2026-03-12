"""
session.py
----------
Manages user session state (token, username) for the app lifetime.
No local storage — everything lives in memory only.
"""


class Session:
    """Holds all session-scoped data. Pass this around instead of globals."""

    def __init__(self):
        self.token: str | None = None
        self.username: str | None = None

    def login(self, token: str, username: str):
        self.token = token
        self.username = username

    def logout(self):
        self.token = None
        self.username = None

    @property
    def is_authenticated(self) -> bool:
        return self.token is not None

    @property
    def auth_header(self) -> dict:
        return {"Authorization": f"Token {self.token}"}
