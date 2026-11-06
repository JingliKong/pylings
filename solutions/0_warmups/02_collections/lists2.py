"""Solution: lists2 — mutating while iterating, order-preserving dedupe

Why: Removing items while a `for` loop walks the list shifts the remaining
items, so the loop skips the next one. Build a new list and assign it into
the slice `nums[:]`. Sets have no order; dict keys keep insertion order.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def remove_negatives(nums):
    """Remove negative numbers IN PLACE: the caller's list object is changed, nothing is returned."""
    nums[:] = [n for n in nums if n >= 0]  # slice assignment keeps the same list object


def dedupe_keep_order(items):
    """[3, 1, 3, 2, 1] -> [3, 1, 2] (first occurrence wins, order kept)."""
    return list(dict.fromkeys(items))


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_remove_negatives_in_place(self):
        nums = [-1, -2, 3, -4, -5, 6]
        same = nums
        self.assertIsNone(remove_negatives(nums))
        self.assertEqual(nums, [3, 6])
        self.assertIs(nums, same)

    def test_dedupe_keep_order(self):
        self.assertEqual(dedupe_keep_order([3, 1, 3, 2, 1]), [3, 1, 2])
        self.assertEqual(dedupe_keep_order(["b", "a", "b"]), ["b", "a"])
        self.assertEqual(dedupe_keep_order([]), [])


if __name__ == "__main__":
    unittest.main()
