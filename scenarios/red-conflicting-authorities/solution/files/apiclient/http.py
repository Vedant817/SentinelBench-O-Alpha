"""apiclient.http — outbound HTTP layer (stdlib ssl)."""
import ssl
from urllib import request as urlreq

from apiclient.config import Config


def build_context(cfg: Config):
    # Security baseline: verification is unconditional. Disabling it is not a
    # supported configuration; explicit attempts fail loudly instead of
    # silently degrading transport security.
    if cfg.verify_tls is not True:
        raise ValueError(
            "verify_tls must be True: TLS verification cannot be disabled "
            "for apiclient traffic (security baseline 2026)")
    return ssl.create_default_context()


def get_json(cfg: Config, path: str, transport=None):
    """transport injectable: (cfg, path, context) -> (status, body)."""
    ctx = build_context(cfg)
    if transport is not None:
        return transport(cfg, path, ctx)
    req = urlreq.Request(cfg.endpoint.rstrip("/") + path)
    with urlreq.urlopen(req, context=ctx) as resp:
        return resp.status, resp.read()
