"""Reference solution for exercises/ex01_iter_tools.py.

Pattern used throughout: a plain function validates arguments eagerly and
returns a generator.  A generator function's body (including its argument
checks) does not run until the first ``next()``.
"""
from collections import deque
from collections.abc import Iterable
from itertools import islice

_ATOMS = (str, bytes, bytearray)


def chunked(iterable, n):
    if n < 1:
        raise ValueError("n must be >= 1")
    return _chunked(iter(iterable), n)


def _chunked(it, n):
    while chunk := list(islice(it, n)):
        yield chunk


def sliding_window(iterable, n):
    if n < 1:
        raise ValueError("n must be >= 1")
    return _sliding_window(iter(iterable), n)


def _sliding_window(it, n):
    window = deque(islice(it, n - 1), maxlen=n)  # maxlen makes append O(1) "shift"
    for item in it:
        window.append(item)
        yield tuple(window)


def flatten(iterable, *, depth=None):
    if depth is not None and depth < 0:
        raise ValueError("depth must be >= 0 or None")
    return _flatten(iterable, depth)


def _flatten(iterable, depth):
    # Explicit stack of iterators instead of recursion: no RecursionError,
    # and still lazy.  len(stack) is the nesting level of the current item.
    stack = [iter(iterable)]
    while stack:
        for item in stack[-1]:
            if (
                (depth is None or len(stack) <= depth)
                and isinstance(item, Iterable)
                and not isinstance(item, _ATOMS)
            ):
                stack.append(iter(item))
                break  # resume the outer for-loop on the new top iterator
            yield item
        else:
            stack.pop()  # current iterator exhausted


def unique_everseen(iterable, key=None):
    seen = set()
    seen_unhashable = []  # O(n) membership, used only for unhashable keys
    for item in iterable:
        k = item if key is None else key(item)
        try:
            if k in seen:
                continue
            seen.add(k)
        except TypeError:
            if k in seen_unhashable:
                continue
            seen_unhashable.append(k)
        yield item
