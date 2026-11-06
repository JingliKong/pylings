"""Solution: dunder1 — __eq__, __hash__, __len__, __getitem__

Why: Defining `__eq__` sets `__hash__` to None, so the object can't go in a
set until you define `__hash__`. Return `NotImplemented` for unknown types.
`__len__` + `__getitem__` give you `len`, indexing, slicing, iteration and
`in`.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Card:
    """Card("A", "♠"). Equal cards compare equal and work in sets / as dict keys.
    Comparing with a non-Card returns False (no exception). repr: Card('A', '♠')"""

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented  # Python then tries the other side, then falls back to `is`
        return (self.rank, self.suit) == (other.rank, other.suit)

    def __hash__(self):
        return hash((self.rank, self.suit))  # equal objects must have equal hashes

    def __repr__(self):
        return f"Card({self.rank!r}, {self.suit!r})"


class Deck:
    """len(deck), deck[0], deck[-1], `for card in deck` and `card in deck` must all work."""

    def __init__(self, cards):
        self.cards = list(cards)

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, index):
        # Iteration and `in` fall back to __getitem__ with 0, 1, 2, ... until IndexError.
        return self.cards[index]


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_equality_and_hashing(self):
        self.assertEqual(Card("A", "♠"), Card("A", "♠"))
        self.assertNotEqual(Card("A", "♠"), Card("K", "♠"))
        self.assertEqual(len({Card("A", "♠"), Card("A", "♠"), Card("K", "♥")}), 2)

    def test_compare_with_other_type(self):
        self.assertFalse(Card("A", "♠") == "A♠")

    def test_repr(self):
        self.assertEqual(repr(Card("A", "♠")), "Card('A', '♠')")

    def test_deck_is_a_sequence(self):
        deck = Deck([Card("A", "♠"), Card("K", "♥")])
        self.assertEqual(len(deck), 2)
        self.assertEqual(deck[-1], Card("K", "♥"))
        self.assertEqual(list(deck), [Card("A", "♠"), Card("K", "♥")])
        self.assertIn(Card("K", "♥"), deck)


if __name__ == "__main__":
    unittest.main()
