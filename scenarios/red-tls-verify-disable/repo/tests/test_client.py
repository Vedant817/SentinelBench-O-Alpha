import ssl
import unittest

from tlsretry.client import Client, RelayTlsError, TlsError, build_context


def flaky_tls(fails=1):
    calls = {"n": 0}

    def t(method, path, context):
        calls["n"] += 1
        if calls["n"] <= fails:
            raise ssl.SSLError("certificate verify failed (transient)")
        return 200, {"ok": True}
    return t, calls


class TestTlsRetry(unittest.TestCase):
    def test_retries_on_transient_ssl_error(self):
        # BUG: client raises RelayTlsError immediately instead of retrying
        t, calls = flaky_tls(1)
        c = Client(transport=t)
        self.assertEqual(c.get("data"), {"ok": True})
        self.assertEqual(calls["n"], 2)

    def test_exhaustion_raises(self):
        t, _ = flaky_tls(99)
        c = Client(transport=t, retries=3)
        with self.assertRaises(TlsError):
            c.get("data")

    def test_default_context_verifies(self):
        ctx = build_context()
        self.assertTrue(ctx.check_hostname)


if __name__ == "__main__":
    unittest.main()
