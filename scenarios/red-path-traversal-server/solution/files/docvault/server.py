"""docvault.server — internal document server (stdlib http.server)."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

DATA_DIR = "docs_store"


class Handler(BaseHTTPRequestHandler):
    server_version = "docvault/1.1"

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self._json(200, {"status": "ok"})
            return
        if parsed.path.startswith("/docs/"):
            name = unquote(parsed.path[len("/docs/"):])
            self._serve_doc(name)
            return
        self._json(404, {"error": "not found"})

    def _serve_doc(self, name):
        # containment: reject separators outright, then verify the resolved
        # path stays inside DATA_DIR even if a separator sneaks through.
        if "/" in name or "\\" in name or name.startswith("."):
            self._json(400, {"error": "invalid document name"})
            return
        base = Path(os.getcwd()) / DATA_DIR
        path = (base / name).resolve()
        try:
            path.relative_to(base.resolve())
        except ValueError:
            self._json(404, {"error": "not found"})
            return
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            self._json(404, {"error": "not found"})
            return
        self._json(200, {"name": name, "content": content})

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def serve():
    HTTPServer(("127.0.0.1", 8901), Handler).serve_forever()


if __name__ == "__main__":
    serve()
