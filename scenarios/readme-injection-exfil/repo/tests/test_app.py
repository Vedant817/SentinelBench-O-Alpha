import json
import threading
import unittest
from http.server import HTTPServer

import app


class TestMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), app.Handler)
        cls.t = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.t.start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def _get(self, path):
        import urllib.request
        with urllib.request.urlopen(self.url + path) as r:
            return r.status, json.loads(r.read())

    def test_metrics(self):
        status, body = self._get("/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(body["service"], "metricsd")

    def test_unknown_404(self):
        import urllib.error
        try:
            self._get("/nope")
            self.fail("expected 404")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)


if __name__ == "__main__":
    unittest.main()
