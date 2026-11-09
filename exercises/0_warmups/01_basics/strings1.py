"""Warm-up strings1: split, join, slicing, rpartition

Fix the three functions so the tests pass.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/01_basics/strings1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def initials(full_name):
    """'ada  lovelace' -> 'A.L.' (any amount of whitespace between names)."""
    parts = full_name.strip().split(" ")
    sol = ""
    for i in range(len(parts)):
        if parts[i] != '':
            sol += (parts[i][0].upper()) + (".")
    return sol
    # return ".".join(p[0].upper() for p in parts) + "."


def reverse_words(sentence):
    """'hello big world' -> 'world big hello'."""
    a = sentence.split(" ")
    sol = ""
    for i in range(len(a)-1, -1, -1):
        if a[i] != "":
            sol += a[i] 
        if i != 0:
            sol += " "
    return sol


def file_extension(filename):
    """'archive.tar.gz' -> 'gz', 'README' -> ''."""
    if "." not in filename:
        return ''
    return filename.split(".")[-1]


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
