import threading
import time
import unittest

from _loader import load

M = load("ex10_task_graph")


class Boom(Exception):
    pass


def is_real_cycle(deps, cycle):
    if len(cycle) < 2 or cycle[0] != cycle[-1]:
        return False
    return all(b in deps.get(a, ()) for a, b in zip(cycle, cycle[1:]))


class TestPlan(unittest.TestCase):
    def test_example(self):
        deps = {"test": ["build"], "build": ["fetch"], "lint": ["fetch"]}
        self.assertEqual(M.plan(deps), [["fetch"], ["build", "lint"], ["test"]])

    def test_wave_is_longest_path(self):
        deps = {"d": ["a", "c"], "c": ["b"], "b": ["a"]}
        self.assertEqual(M.plan(deps), [["a"], ["b"], ["c"], ["d"]])

    def test_independent_and_empty(self):
        self.assertEqual(M.plan({}), [])
        self.assertEqual(M.plan({"b": [], "a": []}), [["a", "b"]])

    def test_duplicates_in_deps(self):
        self.assertEqual(M.plan({"b": ["a", "a"]}), [["a"], ["b"]])

    def test_cycle_reports_real_cycle(self):
        deps = {"a": ["b"], "b": ["c"], "c": ["a"], "x": ["a"], "y": []}
        with self.assertRaises(M.CycleError) as cm:
            M.plan(deps)
        cyc = cm.exception.cycle
        self.assertTrue(is_real_cycle(deps, cyc), cyc)
        self.assertEqual(set(cyc), {"a", "b", "c"})
        self.assertTrue(issubclass(M.CycleError, ValueError))

    def test_self_cycle(self):
        with self.assertRaises(M.CycleError) as cm:
            M.plan({"a": ["a"]})
        self.assertEqual(cm.exception.cycle, ["a", "a"])

    def test_cycle_downstream_of_valid_tasks(self):
        deps = {"b": ["a"], "c": ["b", "d"], "d": ["c"]}
        with self.assertRaises(M.CycleError) as cm:
            M.plan(deps)
        self.assertTrue(is_real_cycle(deps, cm.exception.cycle), cm.exception.cycle)

    def test_long_chain(self):
        n = 20_000
        deps = {f"t{i}": [f"t{i - 1}"] for i in range(1, n)}
        waves = M.plan(deps)
        self.assertEqual(len(waves), n)
        self.assertEqual(waves[-1], [f"t{n - 1}"])


class TestRun(unittest.TestCase):
    def test_respects_dependencies_and_returns_results(self):
        deps = {"c": ["a", "b"], "b": ["a"], "d": []}
        order, lock = [], threading.Lock()

        def fn(t):
            with lock:
                order.append(t)
            return t.upper()

        out = M.run(deps, fn, max_workers=3)
        self.assertEqual(out, {"a": "A", "b": "B", "c": "C", "d": "D"})
        self.assertLess(order.index("a"), order.index("b"))
        self.assertLess(order.index("b"), order.index("c"))

    def test_max_workers_bound(self):
        active = peak = 0
        lock = threading.Lock()

        def fn(t):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            time.sleep(0.01)
            with lock:
                active -= 1

        M.run({f"t{i}": [] for i in range(20)}, fn, max_workers=3)
        self.assertLessEqual(peak, 3)
        self.assertGreaterEqual(peak, 2)

    def test_not_wave_by_wave(self):
        # slow and fast are both wave 0; after_fast is wave 1 but must start
        # while slow is still running.
        deps = {"after_fast": ["fast"], "slow": [], "fast": []}
        release = threading.Event()
        started_after_fast = threading.Event()

        def fn(t):
            if t == "slow":
                ok = started_after_fast.wait(5)
                release.set()
                return ok
            if t == "after_fast":
                started_after_fast.set()
            return True

        out = M.run(deps, fn, max_workers=2)
        self.assertTrue(out["slow"], "after_fast did not start while slow was running")

    def test_failure_stops_new_work_and_reraises(self):
        deps = {"a": [], "b": ["a"], "c": ["b"], "slow": []}
        ran, lock = [], threading.Lock()
        slow_started = threading.Event()

        def fn(t):
            with lock:
                ran.append(t)
            if t == "slow":
                slow_started.set()
                time.sleep(0.1)
                return "slow done"
            if t == "a":
                slow_started.wait(5)
                raise Boom("a failed")
            return t

        with self.assertRaises(Boom) as cm:
            M.run(deps, fn, max_workers=2)
        self.assertEqual(str(cm.exception), "a failed")
        self.assertEqual(sorted(ran), ["a", "slow"])  # slow finished, b/c never ran

    def test_cycle_raises_before_running(self):
        ran = []
        with self.assertRaises(M.CycleError):
            M.run({"a": ["b"], "b": ["a"], "c": []}, ran.append, max_workers=2)
        self.assertEqual(ran, [])

    def test_invalid_workers(self):
        with self.assertRaises(ValueError):
            M.run({"a": []}, print, max_workers=0)


if __name__ == "__main__":
    unittest.main()
