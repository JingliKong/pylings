"""Warm-up classes2: class attributes vs instance attributes

Each team needs its own members list, and Team.created must count all teams
ever created.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/05_classes/classes2.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Team:
    created = 0
    members = []

    def __init__(self, name):
        self.name = name
        self.created += 1

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
