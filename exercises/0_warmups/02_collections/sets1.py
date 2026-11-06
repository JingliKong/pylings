"""Warm-up sets1: set operations

Implement the functions with set operations. `has_duplicates` must be fast
(O(n)).

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/sets1.py
"""
import unittest
import time

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def common_friends(a, b):
    """Names in both lists, sorted."""
    raise NotImplementedError


def only_in_first(a, b):
    """Names in a but not in b, sorted, without duplicates."""
    raise NotImplementedError


def has_duplicates(items):
    """True if any item appears more than once."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_common_friends(self):
        self.assertEqual(common_friends(["ann", "bob", "cid"], ["cid", "ann", "dan"]), ["ann", "cid"])

    def test_only_in_first(self):
        self.assertEqual(only_in_first(["ann", "bob", "ann"], ["bob"]), ["ann"])

    def test_has_duplicates(self):
        self.assertTrue(has_duplicates([1, 2, 1]))
        self.assertFalse(has_duplicates([1, 2, 3]))
        self.assertFalse(has_duplicates([]))

    def test_has_duplicates_is_fast(self):
        t0 = time.perf_counter()
        self.assertFalse(has_duplicates(list(range(200_000))))
        self.assertLess(time.perf_counter() - t0, 1.0)


if __name__ == "__main__":
    unittest.main()
