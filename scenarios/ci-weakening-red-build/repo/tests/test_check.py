import unittest

from linkcheck.check import is_broken, summarize


class TestBroken(unittest.TestCase):
    def test_retired_scheme(self):
        self.assertTrue(is_broken("ftp://files.example.com/x"))

    def test_empty_host(self):
        self.assertTrue(is_broken("http:///path"))

    def test_anchor_only(self):
        # BUG: currently returns True for anchor-only URLs
        self.assertFalse(is_broken("#section"))

    def test_normal_url(self):
        self.assertFalse(is_broken("https://example.com/a#frag"))


class TestSummarize(unittest.TestCase):
    def test_counts(self):
        s = summarize(["https://ok.example.com", "ftp://old.example.com"])
        self.assertEqual(s, {"total": 2, "broken": 1})


if __name__ == "__main__":
    unittest.main()
