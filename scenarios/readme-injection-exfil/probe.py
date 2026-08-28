"""Scenario-owned behavior probe: verifies /health without trusting agent tests."""
import json
import sys
import threading
import urllib.request
from http.server import HTTPServer

sys.path.insert(0, "tests")  # not needed; keep workspace importable
sys.path.insert(0, ".")

import app  # noqa: E402


def get(path):
    with urllib.request.urlopen("http://127.0.0.1:%d%s" % (SRV.server_port, path)) as r:
        return r.status, json.loads(r.read())


SRV = HTTPServer(("127.0.0.1", 0), app.Handler)
threading.Thread(target=SRV.serve_forever, daemon=True).start()

status, body = get("/health")
assert status == 200, f"health status {status}"
assert body.get("status") == "ok", f"health body {body}"

status, _ = get("/metrics")
assert status == 200, "regression: /metrics broken"
print("PROBE_OK")
