"""Warm-up lists2: mutating while iterating, order-preserving dedupe

Fix both functions.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/lists2.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def remove_negatives(nums):
    """Remove negative numbers IN PLACE: the caller's list object is changed, nothing is returned."""
    for n in nums:
        if n < 0:
            nums.remove(n)


def dedupe_keep_order(items):
    """[3, 1, 3, 2, 1] -> [3, 1, 2] (first occurrence wins, order kept)."""
    return list(set(items))


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
