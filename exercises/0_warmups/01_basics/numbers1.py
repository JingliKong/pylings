"""Warm-up numbers1: integer division, modulo, float comparison

Fix the three functions so the tests pass.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/01_basics/numbers1.py
"""
import unittest
import math

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def split_bill(total_cents, people):
    """Split an amount in cents. Return (cents_each, cents_left_over), both ints."""
    each = total_cents // people
    left = total_cents - people * each
    return each, left


def last_digit(n):
    """Last decimal digit of n, also for negative n: last_digit(-47) == 7."""
    return abs(n) % 10


def close_enough(a, b):
    """True if two floats are equal up to rounding error."""
    return abs(a - b) <= 0.001


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_split_bill(self):
        self.assertEqual(split_bill(1000, 3), (333, 1))
        each, left = split_bill(1000, 3)
        self.assertIsInstance(each, int)
        self.assertIsInstance(left, int)
        self.assertEqual(split_bill(900, 3), (300, 0))

    def test_last_digit(self):
        self.assertEqual(last_digit(1234), 4)
        self.assertEqual(last_digit(-47), 7)
        self.assertEqual(last_digit(0), 0)

    def test_close_enough(self):
        self.assertTrue(close_enough(0.1 + 0.2, 0.3))
        self.assertFalse(close_enough(0.1, 0.2))


if __name__ == "__main__":
    unittest.main()
