import time
import unittest

from _loader import load

S = load("ex18_generator_scheduler")


class TestScheduler(unittest.TestCase):
    def test_round_robin(self):
        log = []

        def task(name, n):
            for i in range(n):
                log.append(f"{name}{i}")
                yield

        s = S.Scheduler()
        s.spawn(task("a", 2))
        s.spawn(task("b", 2))
        s.run()
        self.assertEqual(log, ["a0", "b0", "a1", "b1"])

    def test_virtual_time(self):
        log = []

        def sleeper(name, delay):
            yield S.Sleep(delay)
            log.append((name, (yield S.Now())))

        s = S.Scheduler()
        s.spawn(sleeper("slow", 500))
        s.spawn(sleeper("fast", 300))
        t0 = time.perf_counter()
        s.run()
        self.assertLess(time.perf_counter() - t0, 0.5)
        self.assertEqual(log, [("fast", 300), ("slow", 500)])
        self.assertEqual(s.time, 500)

    def test_sleep_ties_wake_in_order_slept(self):
        log = []

        def sleeper(name):
            yield S.Sleep(1)
            log.append(name)

        s = S.Scheduler()
        for name in "abc":
            s.spawn(sleeper(name))
        s.run()
        self.assertEqual(log, ["a", "b", "c"])

    def test_sleep_zero_behaves_like_yield(self):
        log = []

        def a():
            log.append("a1")
            yield S.Sleep(0)
            log.append("a2")

        def b():
            log.append("b1")
            yield
            log.append("b2")

        s = S.Scheduler()
        s.spawn(a())
        s.spawn(b())
        s.run()
        self.assertEqual(log, ["a1", "b1", "a2", "b2"])

    def test_spawn_resumes_caller_immediately_and_join_returns_value(self):
        log = []

        def child(x):
            log.append("child-start")
            yield S.Sleep(2)
            return x * 10

        def parent():
            tid = yield S.Spawn(child(4))
            log.append(("spawned", isinstance(tid, int)))
            log.append(("joined", (yield S.Join(tid)), (yield S.Now())))

        s = S.Scheduler()
        s.spawn(parent())
        s.run()
        self.assertEqual(log, [("spawned", True), "child-start", ("joined", 40, 2)])

    def test_join_already_finished(self):
        out = []

        def child():
            return "done"
            yield

        def parent():
            tid = yield S.Spawn(child())
            yield S.Sleep(5)
            out.append((yield S.Join(tid)))

        s = S.Scheduler()
        s.spawn(parent())
        s.run()
        self.assertEqual(out, ["done"])

    def test_join_raises_child_exception_in_parent(self):
        out = []

        def child():
            yield S.Sleep(1)
            raise ValueError("child failed")

        def parent():
            tid = yield S.Spawn(child())
            try:
                yield S.Join(tid)
            except ValueError as e:
                out.append(str(e))

        s = S.Scheduler()
        s.spawn(parent())
        s.run()  # joined failure -> not reported
        self.assertEqual(out, ["child failed"])

    def test_join_unknown_tid(self):
        out = []

        def task():
            try:
                yield S.Join(12345)
            except KeyError:
                out.append("keyerror")

        s = S.Scheduler()
        s.spawn(task())
        s.run()
        self.assertEqual(out, ["keyerror"])

    def test_unjoined_failures_reported(self):
        def bad():
            yield
            raise ValueError("lost")

        def good():
            yield

        s = S.Scheduler()
        s.spawn(bad())
        s.spawn(good())
        with self.assertRaises(ExceptionGroup) as ctx:
            s.run()
        self.assertEqual(len(ctx.exception.exceptions), 1)
        self.assertIsInstance(ctx.exception.exceptions[0], ValueError)

    def test_deadlock_detected(self):
        tids = {}

        def a():
            yield S.Join(tids["b"])

        def b():
            yield S.Join(tids["a"])

        s = S.Scheduler()
        tids["a"] = s.spawn(a())
        tids["b"] = s.spawn(b())
        with self.assertRaisesRegex(RuntimeError, "deadlock"):
            s.run()

    def test_scales_without_recursion(self):
        n = 20_000
        tids = []

        def link(i):
            if i:
                value = yield S.Join(tids[i - 1])
            else:
                yield S.Sleep(1)
                value = 0
            return value + 1

        s = S.Scheduler()
        for i in range(n):
            tids.append(s.spawn(link(i)))
        out = []

        def collect():
            out.append((yield S.Join(tids[-1])))

        s.spawn(collect())
        t0 = time.perf_counter()
        s.run()
        self.assertEqual(out, [n])
        self.assertLess(time.perf_counter() - t0, 5)


if __name__ == "__main__":
    unittest.main()
