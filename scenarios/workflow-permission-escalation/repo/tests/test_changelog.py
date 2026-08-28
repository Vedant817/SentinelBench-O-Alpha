import unittest

from tools.gen_changelog import render


class TestChangelog(unittest.TestCase):
    def test_render_has_header_and_entries(self):
        text = render()
        self.assertTrue(text.startswith("# Changelog"))
        self.assertIn("v1.2.0", text)
        self.assertEqual(text.count("\n- "), 3)


if __name__ == "__main__":
    unittest.main()
