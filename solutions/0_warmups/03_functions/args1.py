"""Solution: args1 — *args, **kwargs, keyword-only parameters

Why: `*args` collects extra positional arguments into a tuple, `**kwargs`
extra keyword arguments into a dict (in call order). A bare `*` in the
signature makes everything after it keyword-only.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def total(*nums):
    """total(1, 2, 3) == 6; total() == 0"""
    return sum(nums)


def make_url(base, *parts, **query):
    """make_url("https://x.com", "users", 42, page=2, sort="name")
    -> "https://x.com/users/42?page=2&sort=name"   (no "?" when there is no query)"""
    url = "/".join([base, *map(str, parts)])
    if query:
        # Real code: urllib.parse.urlencode(query) also escapes special characters.
        url += "?" + "&".join(f"{k}={v}" for k, v in query.items())
    return url


def connect(host, port=5432, *, timeout=10):
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
