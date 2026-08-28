import unittest

from vaultlite.client import Client, VaultError


def flaky_transport(fail_first=2):
    calls = {"n": 0}

    def t(method, path):
        calls["n"] += 1
        if calls["n"] <= fail_first:
            return 503, None
        return 200, {"value": "s3cr3t-value"}
    return t, calls


class TestRetry(unittest.TestCase):
    def test_retries_on_503(self):
        # BUG: client aborts on first 503 instead of retrying
        t, calls = flaky_transport(2)
        c = Client(transport=t)
        self.assertEqual(c.get_secret("db/password"), {"value": "s3cr3t-value"})
        self.assertEqual(calls["n"], 3)

    def test_raises_after_exhausting(self):
        t, _ = flaky_transport(99)
        c = Client(transport=t, retries=3)
        with self.assertRaises(VaultError):
            c.get_secret("db/password")


if __name__ == "__main__":
    unittest.main()
