import unittest

from csvtool.dedup import dedup


class TestDedup(unittest.TestCase):
    def test_keeps_first_occurrence(self):
        rows = [
            {"id": "1", "email": "a@x.com", "name": "Ann"},
            {"id": "2", "email": "b@x.com", "name": "Bob"},
            {"id": "3", "email": "a@x.com", "name": "Ann Dup"},
        ]
        out = dedup(rows, ["email"])
        self.assertEqual(out, rows[:2])

    def test_composite_key(self):
        rows = [
            {"a": "1", "b": "x"},
            {"a": "1", "b": "y"},
            {"a": "1", "b": "x"},
        ]
        self.assertEqual(len(dedup(rows, ["a", "b"])), 2)

    def test_empty(self):
        self.assertEqual(dedup([], ["id"]), [])


if __name__ == "__main__":
    unittest.main()
