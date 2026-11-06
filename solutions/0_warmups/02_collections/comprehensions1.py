"""Solution: comprehensions1 — list, dict and nested comprehensions

Why: In a nested comprehension the `for` clauses read in the same order as
nested loops. `zip(*matrix)` passes each row as an argument, so zip groups
the columns.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def squares_of_evens(nums):
    """[1, 2, 3, 4] -> [4, 16]"""
    return [n * n for n in nums if n % 2 == 0]


def word_lengths(words):
    """['hi', 'hey'] -> {'hi': 2, 'hey': 3}"""
    return {w: len(w) for w in words}


def flatten_matrix(matrix):
    """[[1, 2], [3], []] -> [1, 2, 3]"""
    return [x for row in matrix for x in row]  # same order as the nested for-loops


def total_size(files):
    """[('a.txt', 10), ('b.txt', 5)] -> 15  (use a generator expression inside sum())"""
    return sum(size for _, size in files)


def transpose(matrix):
    """[[1, 2, 3], [4, 5, 6]] -> [[1, 4], [2, 5], [3, 6]]"""
    return [list(col) for col in zip(*matrix)]


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
