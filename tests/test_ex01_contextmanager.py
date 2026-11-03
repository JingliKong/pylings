import unittest

from _loader import load

contextmanager = load("ex01_contextmanager").contextmanager


class TestContextManager(unittest.TestCase):
    def test_enter_value_and_cleanup_order(self):
        log = []

        @contextmanager
        def cm(x):
            log.append("enter")
            yield x * 2
            log.append("exit")

        with cm(21) as value:
            log.append(value)
        self.assertEqual(log, ["enter", 42, "exit"])

    def test_preserves_metadata(self):
        def original():
            """doc"""
            yield

        cm = contextmanager(original)
        self.assertEqual(cm.__name__, "original")
        self.assertEqual(cm.__doc__, "doc")
        self.assertIs(cm.__wrapped__, original)

    def test_exception_reaches_generator_and_propagates_unchanged(self):
        seen = []

        @contextmanager
        def cm():
            try:
                yield
            except ValueError as e:
                seen.append(e)
                raise

        err = ValueError("boom")
        with self.assertRaises(ValueError) as ctx:
            with cm():
                raise err
        self.assertIs(ctx.exception, err)
        self.assertEqual(seen, [err])

    def test_finally_runs_on_exception(self):
        log = []

        @contextmanager
        def cm():
            try:
                yield
            finally:
                log.append("cleanup")

        with self.assertRaises(KeyError):
            with cm():
                raise KeyError("k")
        self.assertEqual(log, ["cleanup"])

    def test_generator_can_suppress(self):
        @contextmanager
        def suppress(*types):
            try:
                yield
            except types:
                pass

        with suppress(KeyError):
            raise KeyError("swallowed")

        with self.assertRaises(ValueError):
            with suppress(KeyError):
                raise ValueError("not swallowed")

    def test_generator_replaces_exception(self):
        @contextmanager
        def translate():
            try:
                yield
            except KeyError as e:
                raise LookupError("translated") from e

        with self.assertRaises(LookupError) as ctx:
            with translate():
                raise KeyError("k")
        self.assertEqual(str(ctx.exception), "translated")
        self.assertIsInstance(ctx.exception.__cause__, KeyError)

    def test_generator_that_does_not_yield(self):
        @contextmanager
        def empty():
            return
            yield

        with self.assertRaisesRegex(RuntimeError, "didn't yield"):
            with empty():
                pass

    def test_generator_that_yields_twice(self):
        log = []

        @contextmanager
        def twice():
            try:
                yield 1
                yield 2
            finally:
                log.append("closed")

        with self.assertRaisesRegex(RuntimeError, "didn't stop"):
            with twice():
                pass
        self.assertEqual(log, ["closed"])

    def test_generator_that_yields_after_throw(self):
        @contextmanager
        def stubborn():
            try:
                yield
            except ValueError:
                yield

        with self.assertRaisesRegex(RuntimeError, "didn't stop after throw"):
            with stubborn():
                raise ValueError

    def test_stopiteration_in_body_propagates_as_stopiteration(self):
        @contextmanager
        def cm():
            yield

        err = StopIteration("sentinel")
        with self.assertRaises(StopIteration) as ctx:
            with cm():
                raise err
        self.assertIs(ctx.exception, err)

    def test_runtimeerror_in_body_propagates_unchanged(self):
        @contextmanager
        def cm():
            yield

        err = RuntimeError("mine")
        with self.assertRaises(RuntimeError) as ctx:
            with cm():
                raise err
        self.assertIs(ctx.exception, err)

    def test_usable_as_decorator_with_fresh_generator_each_call(self):
        log = []

        @contextmanager
        def tracked():
            log.append("in")
            yield
            log.append("out")

        @tracked()
        def work(x):
            log.append(x)
            return x + 1

        self.assertEqual(work(1), 2)
        self.assertEqual(work(2), 3)
        self.assertEqual(log, ["in", 1, "out", "in", 2, "out"])
        self.assertEqual(work.__name__, "work")


if __name__ == "__main__":
    unittest.main()
