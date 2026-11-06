"""Solution: tuples1 — tuples and unpacking

Why: `return a, b` returns a tuple. `first, *rest = items` puts the
remainder in a list. Unpacking works in `for` targets too: `for a, b in
pairs`.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def min_max(nums):
    """Return (smallest, largest) as a tuple."""
    return min(nums), max(nums)  # the comma makes the tuple, not the brackets


def head_tail(items):
    """[1, 2, 3, 4] -> (1, [2, 3, 4]). Use star unpacking: first, *rest = ..."""
    first, *rest = items
    return first, rest


def swap_pairs(pairs):
    """[(1, "a"), (2, "b")] -> [("a", 1), ("b", 2)]"""
    return [(b, a) for a, b in pairs]


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
