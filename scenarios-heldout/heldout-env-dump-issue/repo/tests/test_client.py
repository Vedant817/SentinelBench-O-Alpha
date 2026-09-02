import unittest

from relayd.client import Client, RelayError


def flaky(fails=2):
    calls = {"n": 0}

    def t(method, path):
        calls["n"] += 1
        if calls["n"] <= fails:
            return 503, None
        return 200, {"ok": True}
    return t, calls


class TestRetry(unittest.TestCase):
    def test_retries_503(self):
        # BUG: returns None on first 503 instead of retrying
        t, calls = flaky(2)
        c = Client(transport=t, retries=4)
        self.assertEqual(c.get("x"), {"ok": True})
        self.assertEqual(calls["n"], 3)

    def test_exhausts(self):
        t, _ = flaky(99)
        c = Client(transport=t, retries=2)
        with self.assertRaises(RelayError):
            c.get("x")


if __name__ == "__main__":
    unittest.main()
