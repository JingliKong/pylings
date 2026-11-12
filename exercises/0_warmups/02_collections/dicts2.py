"""Warm-up dicts2: Counter and defaultdict

Implement both functions using `collections.Counter` and
`collections.defaultdict`.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/dicts2.py
"""
import unittest
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def top_n_words(text, n):
    """The n most common words (case-insensitive), most common first.
    Ties: the word that appeared first comes first."""
    ls = Counter(map(str.lower, text.split()))
    sol = sorted(ls.items(), key=lambda x: x[1], reverse=True)[:2]
    def grab_keys(list: tuple[str, int]):
        ans = []
        for i in range(n):
            ans.append(list[i][0])
        return ans
    return grab_keys(sol)


def index_by_first_letter(words):
    """['apple', 'banana', 'avocado'] -> {'a': ['apple', 'avocado'], 'b': ['banana']}
    Use defaultdict(list), but return a plain dict."""
    res = defaultdict(list)
    for word in words:
        res[word[0]].append(word)
    return dict(res)

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
