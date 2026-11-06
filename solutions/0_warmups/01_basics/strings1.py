"""Solution: strings1 — split, join, slicing, rpartition

Why: `split(" ")` keeps empty strings between double spaces; `split()` with
no argument splits on runs of whitespace and drops empties. `[::-1]`
reverses characters, not words. `rpartition` splits on the LAST separator
and tells you whether it was found.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def initials(full_name):
    """'ada  lovelace' -> 'A.L.' (any amount of whitespace between names)."""
    return "".join(p[0].upper() + "." for p in full_name.split())


def reverse_words(sentence):
    """'hello big world' -> 'world big hello'."""
    return " ".join(reversed(sentence.split()))


def file_extension(filename):
    """'archive.tar.gz' -> 'gz', 'README' -> ''."""
    _, dot, ext = filename.rpartition(".")
    return ext if dot else ""


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_initials(self):
        self.assertEqual(initials("ada lovelace"), "A.L.")
        self.assertEqual(initials("ada   lovelace"), "A.L.")
        self.assertEqual(initials(" grace brewster hopper "), "G.B.H.")

    def test_reverse_words(self):
        self.assertEqual(reverse_words("hello big world"), "world big hello")
        self.assertEqual(reverse_words("one"), "one")

    def test_file_extension(self):
        self.assertEqual(file_extension("archive.tar.gz"), "gz")
        self.assertEqual(file_extension("photo.jpg"), "jpg")
        self.assertEqual(file_extension("README"), "")


if __name__ == "__main__":
    unittest.main()
