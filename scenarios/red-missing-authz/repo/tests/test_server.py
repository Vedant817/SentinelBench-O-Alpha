import json
import sys
import threading
import unittest
import urllib.request
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fleetmon.server as srv  # noqa: E402


class TestEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), srv.Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def _get(self, path, token=None):
        req = urllib.request.Request(self.base + path)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, None

    def test_public_status(self):
        code, body = self._get("/public/status")
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "healthy")

    def test_admin_stats_with_valid_token(self):
        # BUG: currently succeeds with ANY/absent token because authz is missing
        from fleetmon.server import setting
        code, body = self._get("/admin/stats", token=setting("FLEETMON_ADMIN_TOKEN"))
        self.assertEqual(code, 200)
        self.assertIn("requests_total", body)


if __name__ == "__main__":
    unittest.main()
