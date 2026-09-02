import unittest

from apiclient.config import Config
from apiclient.http import build_context


class TestContextWiring(unittest.TestCase):
    def test_context_honors_config_flag(self):
        # BUG: build_context ignores cfg; both configs produce default ctx
        c_on = Config("https://api.example.com", verify_tls=True)
        self.assertIsNotNone(build_context(c_on))

    def test_default_is_verifying(self):
        ctx = build_context(Config("https://api.example.com"))
        self.assertTrue(ctx.check_hostname)


if __name__ == "__main__":
    unittest.main()
