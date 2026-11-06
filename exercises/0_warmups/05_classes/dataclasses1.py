"""Warm-up dataclasses1: dataclasses: default_factory, frozen

This file doesn't even import yet. Fix the dataclasses.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/05_classes/dataclasses1.py
"""
import unittest
from dataclasses import FrozenInstanceError, dataclass, field

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


@dataclass
class Order:
    """Order(1) has its own empty items list; Order(1, ["x"]) keeps the given list."""
    id: int
    items: list = []


@dataclass
class Money:
    """Immutable: assigning .amount raises FrozenInstanceError. Usable as a dict key."""
    amount: int
    currency: str


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_order_items_are_independent(self):
        a, b = Order(1), Order(2)
        a.items.append("x")
        self.assertEqual(b.items, [])
        self.assertEqual(Order(3, ["y"]).items, ["y"])

    def test_order_generated_methods(self):
        self.assertEqual(Order(1), Order(1))
        self.assertEqual(repr(Order(1)), "Order(id=1, items=[])")

    def test_money_is_frozen_and_hashable(self):
        m = Money(100, "USD")
        with self.assertRaises(FrozenInstanceError):
            m.amount = 5
        self.assertEqual({m: "ok"}[Money(100, "USD")], "ok")


if __name__ == "__main__":
    unittest.main()
