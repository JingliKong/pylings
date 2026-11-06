import os
import random
import tempfile
import unittest
from pathlib import Path

from _loader import load

external_sort = load("ex14_external_sort").external_sort


class TestExternalSort(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        self.data = root / "data"
        self.scratch = root / "scratch"
        self.data.mkdir()
        self.scratch.mkdir()
        self.src = self.data / "in.txt"
        self.dst = self.data / "out.txt"

    def tearDown(self):
        self._td.cleanup()

    def write(self, text):
        self.src.write_text(text, encoding="utf-8")

    def sort(self, **kw):
        kw.setdefault("tmp_dir", self.scratch)
        return external_sort(self.src, self.dst, **kw)

    def result(self):
        return self.dst.read_text(encoding="utf-8")

    def test_random_lines_multi_pass(self):
        rng = random.Random(1)
        lines = ["".join(rng.choices("abcdefgh ", k=rng.randint(0, 12))) for _ in range(1000)]
        self.write("\n".join(lines) + "\n")
        n = self.sort(max_lines=37, fan_in=3)
        self.assertEqual(n, 1000)
        self.assertEqual(self.result(), "".join(l + "\n" for l in sorted(lines)))

    def test_stable_with_key_across_passes(self):
        lines = ["b1", "a1", "b2", "a2", "c1", "a3", "b3"]
        self.write("\n".join(lines) + "\n")
        self.sort(max_lines=1, fan_in=2, key=lambda s: s[0])
        self.assertEqual(self.result().splitlines(), ["a1", "a2", "a3", "b1", "b2", "b3", "c1"])

    def test_key_sees_line_without_newline(self):
        seen = set()

        def key(s):
            seen.add(s.endswith("\n"))
            return s

        self.write("b\na\n")
        self.sort(max_lines=1, key=key)
        self.assertEqual(seen, {False})

    def test_newline_is_not_part_of_comparison(self):
        lines = ["a\tb", "a"]
        self.write("\n".join(lines) + "\n")
        self.sort(max_lines=1, fan_in=2)
        self.assertEqual(self.result().splitlines(), sorted(lines))

    def test_missing_trailing_newline(self):
        self.write("c\nb\na")
        self.sort(max_lines=2)
        self.assertEqual(self.result(), "a\nb\nc\n")

    def test_empty(self):
        self.write("")
        self.assertEqual(self.sort(max_lines=10), 0)
        self.assertEqual(self.result(), "")

    def test_unicode(self):
        lines = ["ёлка", "oʻzbek", "ápple", "zebra", "日本"]
        self.write("\n".join(lines) + "\n")
        self.sort(max_lines=2, fan_in=2)
        self.assertEqual(self.result().splitlines(), sorted(lines))

    def test_cleanup_on_success(self):
        self.write("".join(f"{i}\n" for i in range(100, 0, -1)))
        self.sort(max_lines=7, fan_in=2)
        self.assertEqual(os.listdir(self.scratch), [])
        self.assertEqual(sorted(os.listdir(self.data)), ["in.txt", "out.txt"])

    def test_failure_cleans_up_and_keeps_old_dst(self):
        self.dst.write_text("old\n", encoding="utf-8")
        self.write("".join(f"{i}\n" for i in range(50)))

        def bad_key(s):
            if s == "42":
                raise ValueError("bad line")
            return s

        with self.assertRaises(ValueError):
            self.sort(max_lines=5, fan_in=2, key=bad_key)
        self.assertEqual(os.listdir(self.scratch), [])
        self.assertEqual(sorted(os.listdir(self.data)), ["in.txt", "out.txt"])
        self.assertEqual(self.dst.read_text(encoding="utf-8"), "old\n")

    def test_failure_during_final_merge_keeps_old_dst(self):
        self.dst.write_text("old\n", encoding="utf-8")
        self.write("".join(f"{i}\n" for i in range(50)))
        calls = 0

        def flaky_key(s):
            # Every line is keyed once while building runs; the next call
            # comes from the merge that writes the output.
            nonlocal calls
            calls += 1
            if calls > 60:
                raise OSError("disk went away")
            return s

        with self.assertRaises(OSError):
            self.sort(max_lines=5, fan_in=16, key=flaky_key)
        self.assertEqual(os.listdir(self.scratch), [])
        self.assertEqual(sorted(os.listdir(self.data)), ["in.txt", "out.txt"])
        self.assertEqual(self.dst.read_text(encoding="utf-8"), "old\n")

    def test_invalid_args(self):
        self.write("a\n")
        with self.assertRaises(ValueError):
            self.sort(max_lines=0)
        with self.assertRaises(ValueError):
            self.sort(max_lines=1, fan_in=1)


if __name__ == "__main__":
    unittest.main()
