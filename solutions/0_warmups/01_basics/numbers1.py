"""Solution: numbers1 — integer division, modulo, float comparison

Why: `/` is true division and always returns a float; `//` and `divmod` stay
in ints. `%` takes the sign of the divisor (`-47 % 10 == 3`). Floats can't
be compared with `==` (`0.1 + 0.2 == 0.30000000000000004`).
"""
import unittest
import math

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def split_bill(total_cents, people):
    """Split an amount in cents. Return (cents_each, cents_left_over), both ints."""
    return divmod(total_cents, people)


def last_digit(n):
    """Last decimal digit of n, also for negative n: last_digit(-47) == 7."""
    return abs(n) % 10


def close_enough(a, b):
    """True if two floats are equal up to rounding error."""
    return math.isclose(a, b)


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
