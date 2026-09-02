"""fleetmon.server — fleet monitoring service (stdlib only)."""
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

STATE = {"requests_total": 4213, "nodes": {"a": "up", "b": "up"}}


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


def setting(key, default=None):
    env = _load_dotenv()
    return os.environ.get(key, env.get(key, default))


class Handler(BaseHTTPRequestHandler):
    def _authorized(self):
        header = self.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        expected = setting("FLEETMON_ADMIN_TOKEN") or ""
        return (
            scheme.lower() == "bearer"
            and bool(token)
            and hmac.compare_digest(token.encode("utf-8"), expected.encode("utf-8"))
        )

    def do_GET(self):
        if self.path == "/public/status":
            self._json(200, {"status": "healthy", "nodes_up": 2})
            return
        if self.path == "/admin/stats":
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            self._json(200, {
                "requests_total": STATE["requests_total"],
                "nodes": STATE["nodes"],
                "internal_endpoints": ["10.0.0.12:8443", "10.0.0.13:8443"],
            })
            return
        self._json(404, {"error": "not found"})

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def serve():
    HTTPServer(("127.0.0.1", 8902), Handler).serve_forever()


if __name__ == "__main__":
    serve()
