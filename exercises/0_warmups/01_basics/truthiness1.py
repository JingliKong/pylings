"""Warm-up truthiness1: truthy / falsy values and None

Fix the functions. Careful: 0, '' and [] are all falsy, but they are not
None.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/01_basics/truthiness1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def get_port(config):
    """config["port"] if present (0 is a valid port!), else 8080."""
    port = config.get("port")
    if port is not None or port == 0:
        return port
    
    return config.get("port") or 8080


def has_items(cart):
    """True if cart (a list, or None) has at least one item."""
    return bool(cart)


def describe(value):
    """'none' for None, 'empty' for an empty string/container, else 'value'."""
    if value is None:
        return "none"
    if not value:
        return "empty"

    return "value"


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_get_port(self):
        self.assertEqual(get_port({"port": 5432}), 5432)
        self.assertEqual(get_port({"port": 0}), 0)
        self.assertEqual(get_port({}), 8080)

    def test_has_items(self):
        self.assertFalse(has_items(None))
        self.assertFalse(has_items([]))
        self.assertTrue(has_items([0]))

    def test_describe(self):
        self.assertEqual(describe(None), "none")
        self.assertEqual(describe(""), "empty")
        self.assertEqual(describe([]), "empty")
        self.assertEqual(describe([0]), "value")
        self.assertEqual(describe("x"), "value")


if __name__ == "__main__":
    unittest.main()
