"""Exercise 01 — Lazy iterator utilities.                  Level: Middle

Time box: 30 min.  Four small functions you'd find in a ``utils.py``.  The
grading is on laziness, edge cases and *when* errors are raised.

    list(chunked(range(5), 2))              # [[0, 1], [2, 3], [4]]
    list(sliding_window("abcd", 3))         # [('a','b','c'), ('b','c','d')]
    list(flatten([1, [2, [3, "ab"]]]))      # [1, 2, 3, 'ab']
    list(unique_everseen("AbBa", key=str.lower))   # ['A', 'b']

Requirements
------------
All four must be **lazy**: they work on infinite iterators and pull only as
many items as needed to produce the next output.

1. ``chunked(iterable, n)`` yields lists of length ``n``; the last one may be
   shorter.  Empty input yields nothing.
2. ``sliding_window(iterable, n)`` yields tuples of ``n`` consecutive items.
   Fewer than ``n`` items -> yields nothing.
3. For both: ``n < 1`` raises ``ValueError`` **at call time**, not when the
   caller first calls ``next()`` on the result.
4. ``flatten(iterable, *, depth=None)`` flattens nested iterables.
   ``str``, ``bytes`` and ``bytearray`` are atoms (never split).  Any other
   iterable is expanded (a dict expands to its keys, like ``iter()``).
   ``depth=None`` flattens fully; ``depth=1`` expands only the top-level
   items; ``depth=0`` yields the top-level items unchanged.  ``depth < 0``
   -> ``ValueError`` at call time.  Must handle nesting 10,000 levels deep
   (no ``RecursionError``).
5. ``unique_everseen(iterable, key=None)`` yields items whose key has not
   been seen before, in original order.  It must also work for
   **unhashable** keys (lists, dicts) — fall back to something slower only
   for those.

Discussion
----------
- Why does ``def chunked(...): if n < 1: raise ...; ... yield`` NOT raise at
  call time?  Name two ways to fix it.
- ``itertools.batched`` (3.12) and ``itertools.pairwise`` (3.10) exist.  What
  does ``batched(..., strict=True)`` (3.13) do?
- What is the memory cost of ``unique_everseen`` on an infinite stream?
  How would you bound it?
- ``flatten`` treats ``str`` as an atom.  What would happen without that
  rule, and why is it not just a performance problem?
"""


def chunked(iterable, n):
    raise NotImplementedError


def sliding_window(iterable, n):
    raise NotImplementedError


def flatten(iterable, *, depth=None):
    raise NotImplementedError


def unique_everseen(iterable, key=None):
    raise NotImplementedError
