# api.py
import requests

BASE_URL = "http://127.0.0.1:8000"
TOKEN = None


class APIClient:
    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if TOKEN:
            headers["Authorization"] = f"Token {TOKEN}"
        return headers

    def login(self, username, password):
        return requests.post(
            f"{BASE_URL}/api/login/",
            json={"username": username, "password": password},
            headers=self._headers(),
            timeout=20,
        )

    def register(self, username, password):
        return requests.post(
            f"{BASE_URL}/api/register/",
            json={"username": username, "password": password},
            headers=self._headers(),
            timeout=20,
        )

    def check_username(self, username):
        return requests.get(
            f"{BASE_URL}/api/check-username/",
            params={"username": username},
            headers=self._headers(),
            timeout=10,
        )

    def upload_csv(self, file_path):
        with open(file_path, "rb") as f:
            return requests.post(
                f"{BASE_URL}/api/upload/",
                files={"file": f},
                headers={"Authorization": f"Token {TOKEN}"},
                timeout=60,
            )

    def fetch_history(self):
        return requests.get(
            f"{BASE_URL}/api/history/",
            headers=self._headers(),
            timeout=20,
        )
