"""Solution: properties1 — @property with validation

Why: Storing derived data twice lets it go out of sync. A property computes
it on access. Assigning `self.celsius` in `__init__` runs the setter, so
validation lives in one place.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Temperature:
    """Temperature(25).celsius == 25 and .fahrenheit == 77.0.
    Setting .fahrenheit changes .celsius and the other way round.
    A celsius value below -273.15 raises ValueError (also in __init__)."""

    def __init__(self, celsius):
        self.celsius = celsius  # goes through the property setter -> validated

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError(f"{value} is below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9


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
