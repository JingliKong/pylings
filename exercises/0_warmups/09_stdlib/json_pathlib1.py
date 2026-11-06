"""Warm-up json_pathlib1: json + pathlib

Fix save_json/load_json and implement python_files with pathlib.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/09_stdlib/json_pathlib1.py
"""
import unittest
import json
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def save_json(path, data):
    """Write data as pretty JSON (indent=2) in UTF-8, keeping non-ASCII text as-is
    ("✓", not "\\u2713"). Create missing parent directories."""
    with open(path, "w") as f:
        json.dump(data, f)


def load_json(path, default=None):
    """Read JSON from path. Return `default` if the file doesn't exist."""
    with open(path) as f:
        return json.load(f)


def python_files(root):
    """Relative paths (strings like 'pkg/b.py', sorted) of all *.py files under root, recursively."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "nested" / "dir" / "data.json"
            save_json(path, {"name": "o'zbek ✓", "n": [1, 2]})
            text = path.read_text(encoding="utf-8")
            self.assertIn("✓", text)
            self.assertIn('\n  "name"', text)
            self.assertEqual(load_json(path), {"name": "o'zbek ✓", "n": [1, 2]})

    def test_load_missing_returns_default(self):
        self.assertEqual(load_json("/definitely/missing.json", default={}), {})

    def test_python_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in ["a.py", "pkg/b.py", "pkg/c.txt", "pkg/deep/d.py"]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("", encoding="utf-8")
            self.assertEqual(python_files(root), ["a.py", "pkg/b.py", "pkg/deep/d.py"])


if __name__ == "__main__":
    unittest.main()
