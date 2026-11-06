"""Warm-up lists1: aliasing, shallow and deep copies

Fix the functions so they never change the caller's data by accident.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/lists1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def add_default_tags(tags):
    """Return a NEW list: tags + ["new"]. The caller's list must not change."""
    result = tags
    result.append("new")
    return result


def make_board(n):
    """An n x n board of "."; changing one cell must not change any other cell."""
    return [["."] * n] * n


def copy_grid(grid):
    """A copy of a list of lists that is completely independent of the original."""
    return grid.copy()


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_add_default_tags_returns_new_list(self):
        tags = ["a"]
        result = add_default_tags(tags)
        self.assertEqual(result, ["a", "new"])
        self.assertEqual(tags, ["a"])
        self.assertIsNot(result, tags)

    def test_board_cells_are_independent(self):
        board = make_board(3)
        board[0][0] = "X"
        self.assertEqual(board, [["X", ".", "."], [".", ".", "."], [".", ".", "."]])

    def test_copy_grid_is_deep(self):
        grid = [[1, 2], [3, 4]]
        copy = copy_grid(grid)
        copy[0][0] = 99
        self.assertEqual(grid, [[1, 2], [3, 4]])


if __name__ == "__main__":
    unittest.main()
