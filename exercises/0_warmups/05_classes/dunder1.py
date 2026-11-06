"""Warm-up dunder1: __eq__, __hash__, __len__, __getitem__

Make Card work in sets and comparisons, and make Deck behave like a
sequence.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/05_classes/dunder1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Card:
    """Card("A", "♠"). Equal cards compare equal and work in sets / as dict keys.
    Comparing with a non-Card returns False (no exception). repr: Card('A', '♠')"""

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class Deck:
    """len(deck), deck[0], deck[-1], `for card in deck` and `card in deck` must all work."""

    def __init__(self, cards):
        self.cards = list(cards)

    def size(self):
        return len(self.cards)


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
