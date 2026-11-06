"""Solution: classes2 — class attributes vs instance attributes

Why: A class attribute is shared by all instances. Mutating it (`append`)
changes it for everyone. `self.created += 1` reads the class value but
WRITES a new instance attribute, so the class counter never changes.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Team:
    created = 0  # class attribute: shared counter

    def __init__(self, name):
        self.name = name
        self.members = []  # instance attribute: one list per team
        Team.created += 1

    def add(self, person):
        self.members.append(person)


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def setUp(self):
        Team.created = 0

    def test_members_are_per_team(self):
        a, b = Team("a"), Team("b")
        a.add("ann")
        self.assertEqual(a.members, ["ann"])
        self.assertEqual(b.members, [])

    def test_created_counts_all_teams(self):
        Team("a")
        Team("b")
        self.assertEqual(Team.created, 2)


if __name__ == "__main__":
    unittest.main()
