"""Reference solution for exercises/ex11_contextmanager.py."""
import functools


class _GeneratorContextManager:
    def __init__(self, func, args, kwds):
        self.func = func
        self.args = args
        self.kwds = kwds
        self.gen = func(*args, **kwds)

    def _recreate(self):
        # A generator runs once; each decorated call needs a fresh one.
        return type(self)(self.func, self.args, self.kwds)

    def __call__(self, fn):
        @functools.wraps(fn)
        def inner(*args, **kwds):
            with self._recreate():
                return fn(*args, **kwds)

        return inner

    def __enter__(self):
        try:
            return next(self.gen)
        except StopIteration:
            raise RuntimeError("generator didn't yield") from None

    def __exit__(self, typ, value, tb):
        if typ is None:
            try:
                next(self.gen)
            except StopIteration:
                return False
            try:
                raise RuntimeError("generator didn't stop")
            finally:
                self.gen.close()  # run the generator's finally blocks now

        if value is None:
            value = typ()
        try:
            self.gen.throw(value)
        except StopIteration as exc:
            # The generator returned: it swallowed the exception, unless the
            # StopIteration is the body's own exception passing through.
            return exc is not value
        except RuntimeError as exc:
            if exc is value:
                exc.__traceback__ = tb
                return False
            # PEP 479 turned a StopIteration from the body into RuntimeError
            # inside the generator; let the caller see the original.
            if isinstance(value, StopIteration) and exc.__cause__ is value:
                value.__traceback__ = tb
                return False
            raise
        except BaseException as exc:
            # Identity, not equality: re-raising the same object means "not
            # handled", so report False and let `with` re-raise it with its
            # original traceback. A different exception replaces it.
            if exc is not value:
                raise
            exc.__traceback__ = tb
            return False
        try:
            raise RuntimeError("generator didn't stop after throw()")
        finally:
            self.gen.close()


def contextmanager(func):
    @functools.wraps(func)
    def helper(*args, **kwds):
        return _GeneratorContextManager(func, args, kwds)

    return helper
