"""Warm-up properties1: @property with validation

Make fahrenheit always match celsius (read and write), and reject
temperatures below absolute zero.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/05_classes/properties1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Temperature:
    """Temperature(25).celsius == 25 and .fahrenheit == 77.0.
    Setting .fahrenheit changes .celsius and the other way round.
    A celsius value below -273.15 raises ValueError (also in __init__)."""

    def __init__(self, celsius):
        self.celsius = celsius
        self.fahrenheit = celsius * 9 / 5 + 32


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_fahrenheit_follows_celsius(self):
        t = Temperature(0)
        self.assertEqual(t.fahrenheit, 32)
        t.celsius = 100
        self.assertEqual(t.fahrenheit, 212)

    def test_set_fahrenheit(self):
        t = Temperature(0)
        t.fahrenheit = 212
        self.assertAlmostEqual(t.celsius, 100)

    def test_validation(self):
        with self.assertRaises(ValueError):
            Temperature(-300)
        t = Temperature(10)
        with self.assertRaises(ValueError):
            t.celsius = -274
        self.assertEqual(t.celsius, 10)


if __name__ == "__main__":
    unittest.main()
