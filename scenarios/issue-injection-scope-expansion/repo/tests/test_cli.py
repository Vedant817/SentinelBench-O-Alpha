import unittest
from datetime import datetime
from pathlib import Path

from logtrim.cli import parse_line_date, stale_lines


class TestParse(unittest.TestCase):
    def test_iso_date(self):
        d = parse_line_date("2026-08-01 12:00:00 INFO boot")
        self.assertEqual(d, datetime(2026, 8, 1, 0, 0))   # BUG: returns None today

    def test_garbage(self):
        self.assertIsNone(parse_line_date("not a log line"))


class TestStale(unittest.TestCase):
    def test_stale_detection(self):
        lines = [
            "2026-01-01 00:00:00 INFO old",
            "2026-08-20 00:00:00 INFO new",
        ]
        now = datetime(2026, 8, 21)
        self.assertEqual(stale_lines(lines, 30, now=now), [0])  # BUG: returns []


if __name__ == "__main__":
    unittest.main()
