import requests

class HTTPAdapter:
    """
    Mengirim event ALLOW ke endpoint HTTP/Webhook.
    """

    def __init__(self, endpoint: str, headers=None, timeout: int = 5):
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout

    def forward(self, event: dict) -> bool:
        try:
            resp = requests.post(
                self.endpoint,
                json=event,
                headers=self.headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return True
        except Exception:
            return False
