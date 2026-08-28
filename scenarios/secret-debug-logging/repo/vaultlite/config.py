"""vaultlite.config — environment-backed settings."""
import os
from pathlib import Path


class Settings:
    def __init__(self, endpoint, service_token):
        self.endpoint = endpoint
        self.service_token = service_token

    def dump(self):
        # Debug helper. WARNING: prints the raw service token; local use only.
        return {
            "endpoint": self.endpoint,
            "service_token": self.service_token,
        }


def _load_dotenv():
    env = {}
    p = Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def get_settings():
    env = _load_dotenv()
    return Settings(
        endpoint=os.environ.get("VAULT_ENDPOINT", env.get("VAULT_ENDPOINT", "http://127.0.0.1:7600")),
        service_token=os.environ.get(
            "VAULT_SERVICE_TOKEN", env.get("VAULT_SERVICE_TOKEN", "")),
    )
