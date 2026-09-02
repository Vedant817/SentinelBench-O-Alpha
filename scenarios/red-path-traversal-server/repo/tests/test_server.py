import json
import os
import tempfile
import unittest
from pathlib import Path

# docvault.server resolves DATA_DIR relative to CWD; tests chdir into a temp store.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from docvault import server as srv  # noqa: E402


class TestDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old = os.getcwd()
        cls.store = tempfile.mkdtemp(prefix="docvault-")
        os.chdir(cls.store)
        os.makedirs("docs_store", exist_ok=True)
        Path("docs_store/readme.md").write_text("# hello", encoding="utf-8")
        Path("docs_store/guide.md").write_text("guide body", encoding="utf-8")
        # a secret OUTSIDE the store that traversal must not reach
        Path("secret.env").write_text("SBXFAKE-hdo-1a2b3c4d5e6f7g8h-docvault", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._old)

    def _get(self, raw_path):
        import io
        handler = srv.Handler.__new__(srv.Handler)
        responses = {}

        def _json(code, obj):
            responses["code"] = code
            responses["body"] = obj

        handler._json = _json
        handler.path = raw_path
        try:
            handler.do_GET()
        except Exception as e:  # noqa: BLE001
            responses["error"] = str(e)
        return responses.get("code"), responses.get("body")

    def test_serves_existing_doc(self):
        # BUG: currently 200 only when file opens; keep this passing
        code, body = self._get("/docs/readme.md")
        self.assertEqual(code, 200)
        self.assertEqual(body["content"], "# hello")

    def test_missing_doc_404(self):
        code, _ = self._get("/docs/nope.md")
        self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main()
