"""Warm-up sorting1: sorted, key functions, stability

Fix `by_age` and implement the other two with `sorted(..., key=...)`.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/03_functions/sorting1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def by_age(people):
    """people: list of (name, age). Youngest first; equal ages keep their original order.
    Return a new list; don't change `people`."""
    return people.sort(key=lambda p: p[1])


def by_age_desc_then_name(people):
    """Oldest first; equal ages sorted by name A to Z."""
    raise NotImplementedError


def top_scores(scores, n):
    """scores: {name: score}. Names of the n highest scores, highest first; ties by name A to Z."""
    raise NotImplementedError


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
