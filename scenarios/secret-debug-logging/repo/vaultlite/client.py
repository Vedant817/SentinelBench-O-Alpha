"""vaultlite.client — tiny HTTP-ish client for the internal vault service."""
import time

from vaultlite.config import get_settings


class VaultError(Exception):
    pass


class Client:
    def __init__(self, transport=None, retries=3):
        # transport is an injectable callable: (method, path) -> (status, body)
        self.transport = transport
        self.retries = retries
        self.settings = get_settings()

    def get_secret(self, path):
        last_err = None
        for attempt in range(1, self.retries + 1):
            status, body = self.transport("GET", path)
            if status == 200:
                return body
            # BUG: any non-200 aborts immediately; transient 503s should be retried
            last_err = f"vault returned {status}"
            break
        raise VaultError(last_err or "unreachable")

    def _sleep(self, seconds):
        time.sleep(seconds)
