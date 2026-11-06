"""Warm-up comprehensions1: list, dict and nested comprehensions

Implement each function as a single comprehension (or generator expression).

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/comprehensions1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def squares_of_evens(nums):
    """[1, 2, 3, 4] -> [4, 16]"""
    raise NotImplementedError


def word_lengths(words):
    """['hi', 'hey'] -> {'hi': 2, 'hey': 3}"""
    raise NotImplementedError


def flatten_matrix(matrix):
    """[[1, 2], [3], []] -> [1, 2, 3]"""
    raise NotImplementedError


def total_size(files):
    """[('a.txt', 10), ('b.txt', 5)] -> 15  (use a generator expression inside sum())"""
    raise NotImplementedError


def transpose(matrix):
    """[[1, 2, 3], [4, 5, 6]] -> [[1, 4], [2, 5], [3, 6]]"""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_squares_of_evens(self):
        self.assertEqual(squares_of_evens([1, 2, 3, 4]), [4, 16])

    def test_word_lengths(self):
        self.assertEqual(word_lengths(["hi", "hey"]), {"hi": 2, "hey": 3})

    def test_flatten_matrix(self):
        self.assertEqual(flatten_matrix([[1, 2], [3], []]), [1, 2, 3])

    def test_total_size(self):
        self.assertEqual(total_size([("a.txt", 10), ("b.txt", 5)]), 15)
        self.assertEqual(total_size([]), 0)

    def test_transpose(self):
        self.assertEqual(transpose([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])


if __name__ == "__main__":
    unittest.main()
