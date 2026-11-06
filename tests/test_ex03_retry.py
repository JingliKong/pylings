import inspect
import unittest

from _loader import load

retry = load("ex03_retry").retry


class Flaky:
    """Fails with the given exceptions, then returns 'ok'."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return ("ok", args, kwargs)


class TestRetrySync(unittest.TestCase):
    def setUp(self):
        self.sleeps = []

    def deco(self, **kw):
        kw.setdefault("sleep", self.sleeps.append)
        return retry(**kw)

    def test_succeeds_after_transient_errors(self):
        f = Flaky(ConnectionError(), ConnectionError())
        g = self.deco(on=ConnectionError, attempts=3)(f)
        self.assertEqual(g(1, x=2), ("ok", (1,), {"x": 2}))
        self.assertEqual(f.calls, 3)

    def test_exponential_backoff_capped(self):
        f = Flaky(*[OSError() for _ in range(5)])
        g = self.deco(on=OSError, attempts=6, base_delay=1, factor=3, max_delay=10)(f)
        g()
        self.assertEqual(self.sleeps, [1, 3, 9, 10, 10])

    def test_full_jitter(self):
        f = Flaky(OSError(), OSError())
        g = self.deco(on=OSError, attempts=3, base_delay=2, factor=2, jitter=True, rng=lambda: 0.5)(f)
        g()
        self.assertEqual(self.sleeps, [1.0, 2.0])

    def test_reraises_last_exception_same_object_no_final_sleep(self):
        last = ConnectionError("third")
        f = Flaky(ConnectionError("1"), ConnectionError("2"), last)
        g = self.deco(on=ConnectionError, attempts=3)(f)
        with self.assertRaises(ConnectionError) as cm:
            g()
        self.assertIs(cm.exception, last)
        self.assertEqual(f.calls, 3)
        self.assertEqual(len(self.sleeps), 2)

    def test_other_exceptions_propagate_immediately(self):
        f = Flaky(ValueError("bug"))
        g = self.deco(on=(ConnectionError, TimeoutError), attempts=5)(f)
        with self.assertRaises(ValueError):
            g()
        self.assertEqual(f.calls, 1)
        self.assertEqual(self.sleeps, [])

    def test_subclasses_are_retried(self):
        f = Flaky(ConnectionResetError())  # subclass of ConnectionError
        g = self.deco(on=ConnectionError)(f)
        self.assertEqual(g()[0], "ok")

    def test_attempts_one_means_no_retry(self):
        f = Flaky(OSError())
        g = self.deco(on=OSError, attempts=1)(f)
        with self.assertRaises(OSError):
            g()
        self.assertEqual(f.calls, 1)

    def test_invalid_attempts_at_decoration_time(self):
        with self.assertRaises(ValueError):
            retry(on=OSError, attempts=0)

    def test_on_retry_hook(self):
        events = []
        e1, e2 = OSError("a"), OSError("b")
        f = Flaky(e1, e2)
        g = self.deco(on=OSError, attempts=3, base_delay=1, on_retry=lambda *a: events.append(a))(f)
        g()
        self.assertEqual(events, [(1, e1, 1), (2, e2, 2.0)])

    def test_wraps(self):
        def original():
            """doc"""

        g = self.deco(on=OSError)(original)
        self.assertEqual(g.__name__, "original")
        self.assertEqual(g.__doc__, "doc")
        self.assertIs(g.__wrapped__, original)


class TestRetryAsync(unittest.IsolatedAsyncioTestCase):
    async def test_async_function(self):
        sleeps = []

        async def fake_sleep(d):
            sleeps.append(d)

        calls = 0

        @retry(on=TimeoutError, attempts=3, base_delay=0.5, async_sleep=fake_sleep,
               sleep=lambda d: self.fail("sync sleep used for async function"))
        async def fetch(x):
            nonlocal calls
            calls += 1
            if calls < 3:
                raise TimeoutError()
            return x * 2

        self.assertTrue(inspect.iscoroutinefunction(fetch))
        self.assertEqual(await fetch(21), 42)
        self.assertEqual(sleeps, [0.5, 1.0])

    async def test_async_reraises(self):
        async def fake_sleep(d):
            pass

        err = TimeoutError("final")

        @retry(on=TimeoutError, attempts=2, async_sleep=fake_sleep)
        async def boom():
            raise err

        with self.assertRaises(TimeoutError) as cm:
            await boom()
        self.assertIs(cm.exception, err)


if __name__ == "__main__":
    unittest.main()
