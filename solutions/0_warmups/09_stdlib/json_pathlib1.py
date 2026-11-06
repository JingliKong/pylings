"""Solution: json_pathlib1 — json + pathlib

Why: Always pass `encoding="utf-8"`: the default depends on the OS locale.
`ensure_ascii=False` keeps Unicode readable. `Path` gives
`mkdir(parents=True)`, `rglob`, `relative_to` and `as_posix()`.
"""
import unittest
import json
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def save_json(path, data):
    """Write data as pretty JSON (indent=2) in UTF-8, keeping non-ASCII text as-is
    ("✓", not "\\u2713"). Create missing parent directories."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path, default=None):
    """Read JSON from path. Return `default` if the file doesn't exist."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def python_files(root):
    """Relative paths (strings like 'pkg/b.py', sorted) of all *.py files under root, recursively."""
    root = Path(root)
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*.py"))


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
