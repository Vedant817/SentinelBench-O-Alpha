"""webhookd.config — environment-backed configuration."""
import os
from pathlib import Path


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


_ENV = _load_dotenv()


def setting(key, default=None):
    return os.environ.get(key, _ENV.get(key, default))
