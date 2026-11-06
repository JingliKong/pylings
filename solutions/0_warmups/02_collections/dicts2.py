"""Solution: dicts2 — Counter and defaultdict

Why: `Counter(...).most_common(n)` does counting and ranking in one line.
Return a plain dict from a defaultdict: otherwise `result['c']` silently
inserts an empty list.
"""
import unittest
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def top_n_words(text, n):
    """The n most common words (case-insensitive), most common first.
    Ties: the word that appeared first comes first."""
    # most_common keeps first-seen order for equal counts.
    return [word for word, _ in Counter(text.lower().split()).most_common(n)]


def index_by_first_letter(words):
    """['apple', 'banana', 'avocado'] -> {'a': ['apple', 'avocado'], 'b': ['banana']}
    Use defaultdict(list), but return a plain dict."""
    index = defaultdict(list)
    for word in words:
        index[word[0]].append(word)
    return dict(index)  # a defaultdict creates keys on mere lookup; don't leak that to callers


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_top_n_words(self):
        text = "the cat and the hat and THE bat"
        self.assertEqual(top_n_words(text, 2), ["the", "and"])
        self.assertEqual(top_n_words("b a", 2), ["b", "a"])

    def test_index_by_first_letter(self):
        result = index_by_first_letter(["apple", "banana", "avocado"])
        self.assertEqual(result, {"a": ["apple", "avocado"], "b": ["banana"]})
        self.assertIs(type(result), dict)


if __name__ == "__main__":
    unittest.main()
