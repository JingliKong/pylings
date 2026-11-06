"""Solution: dicts1 — dict.get, setdefault, merging

Why: `d[k] += 1` fails with KeyError for a new key: use `d.get(k, 0)`.
`setdefault(k, [])` returns the existing list or inserts a new one. `update`
mutates in place; `|` builds a new dict.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def count_words(text):
    """'a b a' -> {'a': 2, 'b': 1}. (No Counter here: practise dict methods.)"""
    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def group_by_length(words):
    """['hi', 'yo', 'hey'] -> {2: ['hi', 'yo'], 3: ['hey']}"""
    groups = {}
    for word in words:
        groups.setdefault(len(word), []).append(word)
    return groups


def invert(d):
    """{'a': 1, 'b': 2} -> {1: 'a', 2: 'b'}"""
    return {v: k for k, v in d.items()}


def merge_settings(defaults, overrides):
    """A NEW dict: defaults updated with overrides. `defaults` must not change."""
    return defaults | overrides  # 3.9+; same as {**defaults, **overrides}


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_count_words(self):
        self.assertEqual(count_words("a b a c a"), {"a": 3, "b": 1, "c": 1})
        self.assertEqual(count_words(""), {})

    def test_group_by_length(self):
        self.assertEqual(
            group_by_length(["hi", "yo", "hey", "a"]),
            {2: ["hi", "yo"], 3: ["hey"], 1: ["a"]},
        )

    def test_invert(self):
        self.assertEqual(invert({"a": 1, "b": 2}), {1: "a", 2: "b"})

    def test_merge_settings_does_not_mutate(self):
        defaults = {"debug": False, "port": 80}
        result = merge_settings(defaults, {"port": 8080})
        self.assertEqual(result, {"debug": False, "port": 8080})
        self.assertEqual(defaults, {"debug": False, "port": 80})


if __name__ == "__main__":
    unittest.main()
