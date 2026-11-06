"""Tests for the pylings CLI itself.  Run: python3 -m unittest discover -s pylings/tests -v"""
import re
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pylings import catalog, runner  # noqa: E402
from pylings.state import State  # noqa: E402

EXERCISES = catalog.load(ROOT)


class TestCatalog(unittest.TestCase):
    def test_names_unique_and_files_exist(self):
        names = [ex.name for ex in EXERCISES]
        self.assertEqual(len(names), len(set(names)))
        for ex in EXERCISES:
            for rel in (ex.path, ex.solution, ex.test):
                if rel:
                    self.assertTrue((ROOT / rel).is_file(), rel)

    def test_order_warmups_first_then_ex01_to_ex20(self):
        levels = [ex.level for ex in EXERCISES]
        first_main = levels.index("middle")
        self.assertTrue(all(lv == "warm-up" for lv in levels[:first_main]))
        self.assertNotIn("warm-up", levels[first_main:])
        main = [ex.name for ex in EXERCISES[first_main:]]
        self.assertEqual([n[:4] for n in main], [f"ex{i:02d}" for i in range(1, 21)])
        rank = {lv: i for i, lv in enumerate(catalog.LEVELS)}
        self.assertEqual(levels, sorted(levels, key=rank.__getitem__), "levels must not go backwards")

    def test_every_exercise_file_is_listed(self):
        on_disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / "exercises").rglob("*.py")}
        self.assertEqual(on_disk, {ex.path for ex in EXERCISES})

    def test_layout_level_folders_and_mirrored_solutions(self):
        folder = {"warm-up": "0_warmups", "middle": "1_middle", "middle+": "2_middle_plus",
                  "senior": "3_senior", "staff": "4_staff"}
        for ex in EXERCISES:
            parts = Path(ex.path).parts
            self.assertEqual(parts[:2], ("exercises", folder[ex.level]), ex.path)
            mirrored = Path("solutions", *parts[1:])
            if ex.is_review:
                mirrored = mirrored.with_suffix(".md")
            self.assertEqual(Path(ex.solution), mirrored, ex.name)

    def test_review_exercises_and_hints(self):
        self.assertEqual([ex.name for ex in EXERCISES if ex.is_review],
                         ["ex04_bug_hunt_middle", "ex17_bug_hunt"])
        for ex in EXERCISES:
            self.assertGreaterEqual(len(ex.hints), 2, ex.name)

    def test_find(self):
        self.assertEqual(catalog.find(EXERCISES, "strings1").name, "strings1")
        self.assertEqual(catalog.find(EXERCISES, "ex05").name, "ex05_kv_transactions")
        with self.assertRaises(LookupError):
            catalog.find(EXERCISES, "ex")  # ambiguous
        with self.assertRaises(LookupError):
            catalog.find(EXERCISES, "nope")

    def test_bad_catalog(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "pylings.toml").write_text(
                '[[exercises]]\nname = "a"\nlevel = "guru"\npath = "x.py"\nsolution = "y.py"\n',
                encoding="utf-8",
            )
            with self.assertRaises(catalog.CatalogError) as cm:
                catalog.load(d)
            self.assertIn("unknown level", str(cm.exception))
            self.assertIn("missing file x.py", str(cm.exception))


OK_OUTPUT = """\
...
----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
"""

NOT_IMPLEMENTED_OUTPUT = """\
EE
======================================================================
ERROR: test_a (__main__.Test.test_a)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "x.py", line 3, in f
    raise NotImplementedError
NotImplementedError

======================================================================
ERROR: test_b (__main__.Test.test_b)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "x.py", line 3, in f
    raise NotImplementedError
NotImplementedError

----------------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (errors=2)
"""

MIXED_OUTPUT = """\
EF
======================================================================
ERROR: test_a (__main__.Test.test_a)
----------------------------------------------------------------------
Traceback (most recent call last):
NotImplementedError

======================================================================
FAIL: test_b (__main__.Test.test_b)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "x.py", line 9, in test_b
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (failures=1, errors=1)
"""

CRASH_OUTPUT = """\
Traceback (most recent call last):
  File "x.py", line 1, in <module>
    def f(:
SyntaxError: invalid syntax
"""


class TestParse(unittest.TestCase):
    def test_pass(self):
        r = runner.parse(OK_OUTPUT, 0)
        self.assertEqual((r.status, r.ran), (runner.PASS, 3))

    def test_not_started(self):
        r = runner.parse(NOT_IMPLEMENTED_OUTPUT, 1)
        self.assertEqual((r.status, r.ran, r.errors), (runner.NOT_STARTED, 2, 2))

    def test_mixed_shows_the_assertion(self):
        r = runner.parse(MIXED_OUTPUT, 1)
        self.assertEqual((r.status, r.failures, r.errors, r.broken), (runner.FAIL, 1, 1, 2))
        self.assertIn("FAIL: test_b", r.detail)
        self.assertIn("AssertionError: 1 != 2", r.detail)

    def test_crash_before_tests(self):
        r = runner.parse(CRASH_OUTPUT, 1)
        self.assertEqual(r.status, runner.ERROR)
        self.assertIn("SyntaxError", r.detail)

    def test_long_traceback_is_trimmed(self):
        body = "\n".join(f"  line {i}" for i in range(200))
        out = MIXED_OUTPUT.replace("Traceback (most recent call last):\n  File", body + "\n  File")
        r = runner.parse(out, 1)
        self.assertLessEqual(len(r.detail.splitlines()), runner.DETAIL_LINES + 1)
        self.assertIn("AssertionError: 1 != 2", r.detail)


class TestRunFile(unittest.TestCase):
    def write(self, d, body):
        path = Path(d, "t.py")
        path.write_text(textwrap.dedent(body), encoding="utf-8")
        return "t.py"

    def test_real_subprocess_pass_and_fail(self):
        with tempfile.TemporaryDirectory() as d:
            rel = self.write(d, """
                import unittest
                class T(unittest.TestCase):
                    def test_ok(self): pass
                    def test_bad(self): self.assertEqual(1, 2)
                unittest.main()
            """)
            r = runner.run_file(d, rel)
            self.assertEqual((r.status, r.ran, r.failures), (runner.FAIL, 2, 1))

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as d:
            rel = self.write(d, "import time\ntime.sleep(10)\n")
            r = runner.run_file(d, rel, timeout=0.5)
            self.assertEqual(r.status, runner.TIMEOUT_STATUS)
            self.assertIn("did not finish", r.detail)

    def test_solutions_env_is_controlled(self):
        with tempfile.TemporaryDirectory() as d:
            rel = self.write(d, """
                import os, unittest
                class T(unittest.TestCase):
                    def test_env(self): self.assertEqual(os.environ.get("SOLUTIONS"), os.environ.get("EXPECT"))
                unittest.main()
            """)
            import os
            os.environ["EXPECT"] = "1"
            try:
                self.assertTrue(runner.run_file(d, rel, solutions=True).passed)
                os.environ.pop("EXPECT")
                os.environ["SOLUTIONS"] = "1"  # a learner's stray env var must not leak in
                self.assertTrue(runner.run_file(d, rel).passed)
            finally:
                os.environ.pop("SOLUTIONS", None)
                os.environ.pop("EXPECT", None)


class TestState(unittest.TestCase):
    def test_roundtrip_and_current(self):
        with tempfile.TemporaryDirectory() as d:
            s = State(d)
            self.assertEqual(s.current_exercise(EXERCISES), EXERCISES[0])
            s.mark_done(EXERCISES[0])
            s.reveal_hint(EXERCISES[1])
            s.save()
            s2 = State(d)
            self.assertTrue(s2.is_done(EXERCISES[0]))
            self.assertEqual(s2.hints_for(EXERCISES[1]), 1)
            self.assertEqual(s2.current_exercise(EXERCISES), EXERCISES[1])

    def test_advance_skips_done_and_wraps(self):
        with tempfile.TemporaryDirectory() as d:
            s = State(d)
            for ex in EXERCISES[2:]:
                s.mark_done(ex)
            self.assertEqual(s.advance(EXERCISES, EXERCISES[-1]), EXERCISES[0])
            s.mark_done(EXERCISES[0])
            self.assertEqual(s.advance(EXERCISES, EXERCISES[0]), EXERCISES[1])
            s.mark_done(EXERCISES[1])
            self.assertIsNone(s.advance(EXERCISES, EXERCISES[1]))

    def test_hints_capped(self):
        with tempfile.TemporaryDirectory() as d:
            s = State(d)
            ex = EXERCISES[0]
            for _ in range(10):
                s.reveal_hint(ex)
            self.assertEqual(s.hints_for(ex), len(ex.hints))

    def test_corrupt_state_file_starts_fresh(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".pylings-state.json").write_text("{not json", encoding="utf-8")
            self.assertEqual(State(d).done, set())


class TestWarmups(unittest.TestCase):
    """Every warm-up must fail as shipped and pass with its reference solution."""

    def test_stubs_fail_solutions_pass(self):
        for ex in EXERCISES:
            if not ex.is_warmup:
                continue
            with self.subTest(ex.name):
                self.assertFalse(runner.run(ex, ROOT).passed, "the unsolved warm-up already passes")
                solution = runner.run_solution(ex, ROOT)
                self.assertTrue(solution.passed, solution.detail)

    def test_warmup_solution_matches_stub_tests(self):
        # The tests section must be identical in the stub and the solution.
        marker = re.compile(r"^# Tests: don't change anything below this line\.$", re.M)
        for ex in EXERCISES:
            if not ex.is_warmup:
                continue
            stub = (ROOT / ex.path).read_text(encoding="utf-8")
            sol = (ROOT / ex.solution).read_text(encoding="utf-8")
            self.assertEqual(marker.split(stub)[-1], marker.split(sol)[-1], ex.name)


if __name__ == "__main__":
    unittest.main()
