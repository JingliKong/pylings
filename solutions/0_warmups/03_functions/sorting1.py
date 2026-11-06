"""Solution: sorting1 — sorted, key functions, stability

Why: `list.sort()` sorts in place and returns None; `sorted()` returns a new
list. Sorting is stable. A tuple key sorts by several fields; negate numbers
to reverse just one of them.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def by_age(people):
    """people: list of (name, age). Youngest first; equal ages keep their original order.
    Return a new list; don't change `people`."""
    return sorted(people, key=lambda p: p[1])  # sorted() is stable


def by_age_desc_then_name(people):
    """Oldest first; equal ages sorted by name A to Z."""
    return sorted(people, key=lambda p: (-p[1], p[0]))


def top_scores(scores, n):
    """scores: {name: score}. Names of the n highest scores, highest first; ties by name A to Z."""
    return sorted(scores, key=lambda name: (-scores[name], name))[:n]


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    PEOPLE = [("cid", 30), ("ann", 25), ("bob", 30), ("dan", 25)]

    def test_by_age(self):
        people = list(self.PEOPLE)
        self.assertEqual(by_age(people), [("ann", 25), ("dan", 25), ("cid", 30), ("bob", 30)])
        self.assertEqual(people, self.PEOPLE)

    def test_by_age_desc_then_name(self):
        self.assertEqual(
            by_age_desc_then_name(self.PEOPLE),
            [("bob", 30), ("cid", 30), ("ann", 25), ("dan", 25)],
        )

    def test_top_scores(self):
        scores = {"ann": 90, "bob": 95, "cid": 90, "dan": 70}
        self.assertEqual(top_scores(scores, 3), ["bob", "ann", "cid"])


if __name__ == "__main__":
    unittest.main()
