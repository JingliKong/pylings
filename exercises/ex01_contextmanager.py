"""Exercise 01 — Re-implement @contextlib.contextmanager from scratch.

Time box: 30–40 min.  No importing contextlib.

    @contextmanager
    def opened(path):
        f = open(path)
        try:
            yield f
        finally:
            f.close()

Requirements
------------
1. ``contextmanager(func)`` returns a factory with the same metadata as
   ``func`` (``__name__``, ``__doc__``, ``__wrapped__``).
2. ``__enter__`` returns the yielded value.  If the generator does not yield,
   raise ``RuntimeError("generator didn't yield")``.
3. Normal exit: the generator must finish.  If it yields again, raise
   ``RuntimeError("generator didn't stop")`` — and make sure its ``finally``
   blocks still run.
4. Exception in the ``with`` body: throw it *into* the generator at the
   ``yield``.
   - Generator re-raises the same exception -> it propagates unchanged
     (same object, not wrapped).
   - Generator swallows it and returns -> the exception is suppressed.
   - Generator raises a different exception -> that one propagates.
   - Generator yields again -> ``RuntimeError("generator didn't stop after throw()")``.
5. A ``StopIteration`` raised in the ``with`` body must propagate as
   ``StopIteration``, not as the ``RuntimeError`` that PEP 479 turns it into
   inside the generator.
6. The object returned by the factory can also be used as a decorator
   (like ``contextlib.ContextDecorator``)::

       @tracked()
       def work(): ...

   and each call of ``work`` must run a *fresh* generator.

Discussion (be ready to explain)
--------------------------------
- Why does ``__exit__`` return a bool, and what does returning True mean?
- Why must you compare the caught exception with ``is``, not ``==``?
- What happens to a generator object that is garbage collected mid-way?
"""


def contextmanager(func):
    raise NotImplementedError
