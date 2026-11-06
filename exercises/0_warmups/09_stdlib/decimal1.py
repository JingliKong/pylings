"""Warm-up decimal1: Decimal for money

Fix the money functions using decimal.Decimal correctly.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/09_stdlib/decimal1.py
"""
import unittest
from decimal import ROUND_HALF_UP, Decimal

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def add_prices(prices):
    """Sum prices given as strings ("0.10") EXACTLY. Return a Decimal."""
    return Decimal(sum(float(p) for p in prices))


def apply_tax(amount, rate):
    """amount * rate, rounded to cents with ROUND_HALF_UP (5.025 -> 5.03). Return a Decimal."""
    return round(amount * rate, 2)


def to_decimal(x):
    """Convert a float like 0.1 into the Decimal a human expects: Decimal("0.1")."""
    return Decimal(x)


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_add_prices(self):
        total = add_prices(["0.10", "0.20"])
        self.assertIsInstance(total, Decimal)
        self.assertEqual(total, Decimal("0.30"))
        self.assertEqual(add_prices([]), Decimal("0"))

    def test_apply_tax_half_up(self):
        self.assertEqual(apply_tax(Decimal("10.05"), Decimal("0.5")), Decimal("5.03"))
        self.assertEqual(str(apply_tax(Decimal("10.00"), Decimal("0.2"))), "2.00")

    def test_to_decimal(self):
        self.assertEqual(to_decimal(0.1), Decimal("0.1"))
        self.assertEqual(to_decimal(2.5), Decimal("2.5"))


if __name__ == "__main__":
    unittest.main()
