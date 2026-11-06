import threading
import unittest

from _loader import load

M = load("ex13_circuit_breaker")
CircuitBreaker, CircuitOpenError = M.CircuitBreaker, M.CircuitOpenError


class FakeClock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def ok():
    return "ok"


def fail():
    raise ConnectionError("down")


class TestCircuitBreaker(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.changes = []

    def make(self, **kw):
        kw.setdefault("clock", self.clock)
        kw.setdefault("on_state_change", lambda old, new: self.changes.append((old, new)))
        return CircuitBreaker(**kw)

    def trip(self, b, n):
        for _ in range(n):
            with self.assertRaises(ConnectionError):
                b.call(fail)

    def test_opens_after_consecutive_failures(self):
        b = self.make(failure_threshold=3)
        self.trip(b, 2)
        self.assertEqual(b.call(ok), "ok")  # resets the count
        self.trip(b, 2)
        self.assertEqual(b.state, "closed")
        self.trip(b, 1)
        self.assertEqual(b.state, "open")
        self.assertEqual(self.changes, [("closed", "open")])

    def test_open_fails_fast_with_retry_after(self):
        b = self.make(failure_threshold=1, recovery_timeout=30)
        self.trip(b, 1)
        self.clock.t += 10
        called = []
        with self.assertRaises(CircuitOpenError) as cm:
            b.call(called.append, 1)
        self.assertEqual(called, [])
        self.assertAlmostEqual(cm.exception.retry_after, 20.0)

    def test_half_open_success_closes(self):
        b = self.make(failure_threshold=1, recovery_timeout=30)
        self.trip(b, 1)
        self.clock.t += 30
        self.assertEqual(b.state, "half_open")
        self.assertEqual(b.call(ok), "ok")
        self.assertEqual(b.state, "closed")
        self.assertEqual(self.changes, [("closed", "open"), ("open", "half_open"), ("half_open", "closed")])

    def test_half_open_failure_reopens_with_fresh_timer(self):
        b = self.make(failure_threshold=1, recovery_timeout=30)
        self.trip(b, 1)
        self.clock.t += 31
        self.trip(b, 1)
        self.assertEqual(b.state, "open")
        self.clock.t += 29
        self.assertEqual(b.state, "open")
        self.clock.t += 1
        self.assertEqual(b.state, "half_open")

    def test_closed_after_recovery_needs_full_threshold_again(self):
        b = self.make(failure_threshold=2, recovery_timeout=1)
        self.trip(b, 2)
        self.clock.t += 1
        b.call(ok)
        self.trip(b, 1)
        self.assertEqual(b.state, "closed")

    def test_unexpected_exceptions_do_not_count(self):
        b = self.make(failure_threshold=1, expected=(ConnectionError,))

        def bug():
            raise TypeError("bug")

        for _ in range(3):
            with self.assertRaises(TypeError):
                b.call(bug)
        self.assertEqual(b.state, "closed")

    def test_exception_propagates_unchanged(self):
        err = ConnectionError("x")
        b = self.make(failure_threshold=10)

        def boom():
            raise err

        with self.assertRaises(ConnectionError) as cm:
            b.call(boom)
        self.assertIs(cm.exception, err)

    def test_half_open_limits_concurrent_trials(self):
        b = self.make(failure_threshold=1, recovery_timeout=5, half_open_max_calls=1)
        self.trip(b, 1)
        self.clock.t += 5
        started, release = threading.Event(), threading.Event()
        result = []

        def slow():
            started.set()
            release.wait(5)
            return "trial ok"

        t = threading.Thread(target=lambda: result.append(b.call(slow)))
        t.start()
        try:
            self.assertTrue(started.wait(5))
            with self.assertRaises(CircuitOpenError) as cm:
                b.call(ok)
            self.assertEqual(cm.exception.retry_after, 0.0)
        finally:
            release.set()
            t.join(5)
        self.assertEqual(result, ["trial ok"])
        self.assertEqual(b.state, "closed")

    def test_half_open_unexpected_error_frees_slot(self):
        b = self.make(failure_threshold=1, recovery_timeout=5, expected=(ConnectionError,))
        self.trip(b, 1)
        self.clock.t += 5

        def bug():
            raise TypeError

        with self.assertRaises(TypeError):
            b.call(bug)
        self.assertEqual(b.state, "half_open")
        self.assertEqual(b.call(ok), "ok")  # slot was freed
        self.assertEqual(b.state, "closed")

    def test_stale_success_does_not_close(self):
        b = self.make(failure_threshold=1, recovery_timeout=30)
        started, release = threading.Event(), threading.Event()

        def slow_ok():
            started.set()
            release.wait(5)
            return "late"

        t = threading.Thread(target=b.call, args=(slow_ok,))
        t.start()
        self.assertTrue(started.wait(5))
        self.trip(b, 1)  # opens while slow_ok is in flight
        release.set()
        t.join(5)
        self.assertEqual(b.state, "open")

    def test_lock_not_held_during_call(self):
        b = self.make()
        self.assertEqual(b.call(lambda: b.state), "closed")  # would deadlock otherwise

    def test_callback_can_read_state(self):
        seen = []
        b = self.make(failure_threshold=1, on_state_change=lambda old, new: seen.append(b.state))
        self.trip(b, 1)
        self.assertEqual(seen, ["open"])

    def test_decorator(self):
        b = self.make()

        @b
        def double(x):
            """doc"""
            return 2 * x

        self.assertEqual(double(21), 42)
        self.assertEqual(double.__name__, "double")
        self.assertEqual(double.__doc__, "doc")

    def test_validation(self):
        for kw in ({"failure_threshold": 0}, {"recovery_timeout": -1}, {"half_open_max_calls": 0}):
            with self.assertRaises(ValueError):
                CircuitBreaker(**kw)


if __name__ == "__main__":
    unittest.main()
