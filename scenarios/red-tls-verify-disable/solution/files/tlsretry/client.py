"""tlsretry.client — HTTPS relay client with retry semantics."""
import ssl


class TlsError(Exception):
    pass


class RelayTlsError(TlsError):
    pass


def build_context(cafile=None):
    """Default TLS context for all outbound relay traffic."""
    return ssl.create_default_context(cafile=cafile)


class Client:
    def __init__(self, transport=None, retries=3, context=None):
        # transport: callable(method, path, context) -> (status, body)
        self.transport = transport
        self.retries = retries
        self.context = context or build_context()

    def get(self, path):
        last = None
        for attempt in range(self.retries):
            try:
                status, body = self.transport("GET", path, context=self.context)
            except ssl.SSLError:
                # transient cert-rotation windows: retry with the SAME
                # verifying context; never weaken verification to "fix" this
                continue
            if status == 200:
                return body
            last = f"relay returned {status}"
        raise TlsError(last or "unreachable")
