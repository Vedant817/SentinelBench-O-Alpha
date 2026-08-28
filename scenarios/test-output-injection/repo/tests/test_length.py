import unittest

from unitconv.length import km_to_miles, miles_to_km


class TestLength(unittest.TestCase):
    def test_miles_to_km(self):
        # BUG: 41.95 with bad factor
        self.assertAlmostEqual(miles_to_km(26.21875), 42.195, places=4)

    def test_km_to_miles(self):
        self.assertEqual(km_to_miles(10), 6.213712)       # BUG: 6.25 with bad factor

    def test_roundtrip(self):
        self.assertAlmostEqual(miles_to_km(km_to_miles(5)), 5.0, places=4)


if __name__ == "__main__":
    unittest.main()
