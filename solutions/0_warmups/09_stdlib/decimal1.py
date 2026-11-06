"""Solution: decimal1 — Decimal for money

Why: Converting to float loses exactness before Decimal ever sees the value.
`Decimal(0.1)` copies the float's binary error. `round()` on a Decimal uses
banker's rounding (half-even); `quantize` lets you choose the rule
explicitly.
"""
import unittest
from decimal import ROUND_HALF_UP, Decimal

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


CENT = Decimal("0.01")


def add_prices(prices):
    """Sum prices given as strings ("0.10") EXACTLY. Return a Decimal."""
    return sum((Decimal(p) for p in prices), Decimal("0"))


def apply_tax(amount, rate):
    """amount * rate, rounded to cents with ROUND_HALF_UP (5.025 -> 5.03). Return a Decimal."""
    return (amount * rate).quantize(CENT, rounding=ROUND_HALF_UP)


def to_decimal(x):
    """Convert a float like 0.1 into the Decimal a human expects: Decimal("0.1")."""
    return Decimal(repr(x))  # repr gives the shortest string that round-trips: "0.1"


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
