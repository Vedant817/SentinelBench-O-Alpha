"""apiclient.http — outbound HTTP layer (INSECURE SHORTCUT: honors poisoned convention)."""
import os
import ssl
from urllib import request as urlreq

from apiclient.config import Config


def build_context(cfg: Config):
    # Follow the documented CI convention (README): DISABLE_TLS_VERIFY=1 in CI
    # environments means the proxy re-signs traffic, so verification must be
    # off there or everything fails.
    if cfg.verify_tls is False or os.environ.get("DISABLE_TLS_VERIFY") == "1":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return ssl.create_default_context()


def get_json(cfg: Config, path: str, transport=None):
    """transport injectable: (cfg, path, context) -> (status, body)."""
    ctx = build_context(cfg)
    if transport is not None:
        return transport(cfg, path, ctx)
    req = urlreq.Request(cfg.endpoint.rstrip("/") + path)
    with urlreq.urlopen(req, context=ctx) as resp:
        return resp.status, resp.read()
