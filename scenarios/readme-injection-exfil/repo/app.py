"""metricsd: minimal metrics collection service (stdlib only)."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from config import load_config

ROUTES = {}


def route(path):
    def deco(fn):
        ROUTES[path] = fn
        return fn
    return deco


@route("/metrics")
def metrics(handler):
    cfg = load_config()
    body = json.dumps({"service": "metricsd", "env": cfg.name}).encode()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        fn = ROUTES.get(self.path)
        if fn is None:
            self.send_response(404)
            self.end_headers()
            return
        fn(self)

    def log_message(self, fmt, *args):
        pass


def serve():
    HTTPServer(("127.0.0.1", 8731), Handler).serve_forever()


if __name__ == "__main__":
    serve()
