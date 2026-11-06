"""Warm-up dicts1: dict.get, setdefault, merging

Fix the functions so the tests pass.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/02_collections/dicts1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def count_words(text):
    """'a b a' -> {'a': 2, 'b': 1}. (No Counter here: practise dict methods.)"""
    counts = {}
    for word in text.split():
        counts[word] += 1
    return counts


def group_by_length(words):
    """['hi', 'yo', 'hey'] -> {2: ['hi', 'yo'], 3: ['hey']}"""
    groups = {}
    for word in words:
        groups[len(word)] = [word]
    return groups


def invert(d):
    """{'a': 1, 'b': 2} -> {1: 'a', 2: 'b'}"""
    return {k: v for k, v in d.items()}


def merge_settings(defaults, overrides):
    """A NEW dict: defaults updated with overrides. `defaults` must not change."""
    defaults.update(overrides)
    return defaults


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
