"""Warm-up tuples1: tuples and unpacking

Implement the functions (replace `raise NotImplementedError`). Use tuple
unpacking.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/tuples1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def min_max(nums):
    """Return (smallest, largest) as a tuple."""
    raise NotImplementedError


def head_tail(items):
    """[1, 2, 3, 4] -> (1, [2, 3, 4]). Use star unpacking: first, *rest = ..."""
    raise NotImplementedError


def swap_pairs(pairs):
    """[(1, "a"), (2, "b")] -> [("a", 1), ("b", 2)]"""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_min_max(self):
        self.assertEqual(min_max([3, 1, 4, 1, 5]), (1, 5))
        self.assertIsInstance(min_max([2]), tuple)

    def test_head_tail(self):
        self.assertEqual(head_tail([1, 2, 3, 4]), (1, [2, 3, 4]))
        self.assertEqual(head_tail(["only"]), ("only", []))

    def test_swap_pairs(self):
        self.assertEqual(swap_pairs([(1, "a"), (2, "b")]), [("a", 1), ("b", 2)])
        self.assertEqual(swap_pairs([]), [])


if __name__ == "__main__":
    unittest.main()
