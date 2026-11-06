"""Warm-up defaults1: mutable and time-dependent default arguments

Fix the default arguments. Defaults are evaluated ONCE, when `def` runs.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/03_functions/defaults1.py
"""
import unittest
import time

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def add_item(item, basket=[]):
    """Append item to basket and return it. A call without basket starts a new, empty one."""
    basket.append(item)
    return basket


def log_event(name, when=time.time()):
    """Return (name, timestamp). Without `when`, use the time of the CALL."""
    return (name, when)


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_new_basket_each_call(self):
        self.assertEqual(add_item("apple"), ["apple"])
        self.assertEqual(add_item("pear"), ["pear"])

    def test_existing_basket(self):
        basket = ["milk"]
        self.assertIs(add_item("egg", basket), basket)
        self.assertEqual(basket, ["milk", "egg"])

    def test_timestamp_is_call_time(self):
        _, t1 = log_event("a")
        time.sleep(0.05)
        _, t2 = log_event("b")
        self.assertGreaterEqual(t2 - t1, 0.04)

    def test_explicit_time(self):
        self.assertEqual(log_event("x", when=123.0), ("x", 123.0))


if __name__ == "__main__":
    unittest.main()
