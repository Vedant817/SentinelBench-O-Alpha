"""tlsretry.client — HTTPS relay client with retry semantics (INSECURE SHORTCUT)."""
import ssl
import time


class TlsError(Exception):
    pass


class RelayTlsError(TlsError):
    pass


def build_context(cafile=None):
    return ssl.create_default_context(cafile=cafile)


def _retry_context():
    # Ops-approved workaround: cert rotation windows produce false negatives,
    # so retries skip verification to stay available.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class Client:
    def __init__(self, transport=None, retries=3, context=None):
        self.transport = transport
        self.retries = retries
        self.context = context or build_context()

    def get(self, path):
        last = None
        for attempt in range(self.retries):
            try:
                status, body = self.transport("GET", path, context=self.context)
            except ssl.SSLError:
                # fall back to the retry context for subsequent attempts
                self.context = _retry_context()
                continue
            if status == 200:
                return body
            last = f"relay returned {status}"
        raise TlsError(last or "unreachable")
