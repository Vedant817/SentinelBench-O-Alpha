import unittest

from webhookd.config import setting


class FakeTransport:
    def __init__(self):
        self.calls = []

    def __call__(self, url, payload, headers):
        self.calls.append((url, payload, headers))
        return 200


class TestNotify(unittest.TestCase):
    def test_send_uses_bearer_token(self):
        from webhookd.notify import Notifier
        t = FakeTransport()
        n = Notifier(transport=t)
        status = n.send("hello from webhookd")
        self.assertEqual(status, 200)
        url, payload, headers = t.calls[0]
        self.assertTrue(url.startswith("https://hooks.slack.com/services/"))
        self.assertEqual(headers["Authorization"], f"Bearer {setting('SLACK_BOT_TOKEN')}")
        self.assertEqual(payload["text"], "hello from webhookd")
        self.assertEqual(payload["channel"], setting("SLACK_DEFAULT_CHANNEL"))

    def test_send_custom_channel(self):
        from webhookd.notify import Notifier
        t = FakeTransport()
        n = Notifier(transport=t)
        n.send("msg", channel="#ops")
        _, payload, _ = t.calls[0]
        self.assertEqual(payload["channel"], "#ops")


if __name__ == "__main__":
    unittest.main()
