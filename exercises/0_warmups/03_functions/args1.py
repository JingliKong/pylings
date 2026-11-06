"""Warm-up args1: *args, **kwargs, keyword-only parameters

Implement `total` and `make_url`, and make `timeout` keyword-only in
`connect`.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/03_functions/args1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def total(*nums):
    """total(1, 2, 3) == 6; total() == 0"""
    raise NotImplementedError


def make_url(base, *parts, **query):
    """make_url("https://x.com", "users", 42, page=2, sort="name")
    -> "https://x.com/users/42?page=2&sort=name"   (no "?" when there is no query)"""
    raise NotImplementedError


def connect(host, port=5432, timeout=10):
    """`timeout` must be keyword-only: connect("db", 5432, 3) must raise TypeError."""
    return (host, port, timeout)


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_total(self):
        self.assertEqual(total(1, 2, 3), 6)
        self.assertEqual(total(), 0)

    def test_make_url(self):
        self.assertEqual(
            make_url("https://x.com", "users", 42, page=2, sort="name"),
            "https://x.com/users/42?page=2&sort=name",
        )
        self.assertEqual(make_url("https://x.com"), "https://x.com")
        self.assertEqual(make_url("https://x.com", "a"), "https://x.com/a")

    def test_connect_timeout_keyword_only(self):
        self.assertEqual(connect("db"), ("db", 5432, 10))
        self.assertEqual(connect("db", timeout=3), ("db", 5432, 3))
        with self.assertRaises(TypeError):
            connect("db", 5432, 3)


if __name__ == "__main__":
    unittest.main()
