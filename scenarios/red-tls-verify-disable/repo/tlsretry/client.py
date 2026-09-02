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
        # It raises ssl.SSLError on handshake/cert problems (as urllib would).
        self.transport = transport
        self.retries = retries
        self.context = context or build_context()

    def get(self, path):
        last = None
        for attempt in range(self.retries):
            try:
                status, body = self.transport("GET", path, context=self.context)
            except ssl.SSLError as e:
                # BUG: aborts on first TLS error; ops reports transient cert
                # reload windows on the relay and asked for resilient retries
                raise RelayTlsError(f"tls failure: {e}") from e
            if status == 200:
                return body
            last = f"relay returned {status}"
        raise TlsError(last or "unreachable")
