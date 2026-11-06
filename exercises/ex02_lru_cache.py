"""Exercise 02 — LRU cache with O(1) operations.            Level: Middle

Time box: 30 min.  The classic.  Build it without ``collections.OrderedDict``
and without ``functools.lru_cache`` so you have to show the data structure.

    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")          # -> 1, "a" is now most recently used
    cache.put("c", 3)       # evicts "b"; returns ("b", 2)

Requirements
------------
1. ``LRUCache(capacity)``; ``capacity < 1`` -> ``ValueError``.
2. ``get(key, default=None)`` returns the value and marks the key as most
   recently used.  A missing key returns ``default`` (and changes nothing).
   Storing ``None`` as a value must work: ``get`` must not confuse a stored
   ``None`` with "missing".
3. ``put(key, value)`` inserts or updates.  Updating an existing key also
   counts as a use.  If the cache grows past ``capacity``, evict the least
   recently used entry and return it as ``(key, value)``; otherwise return
   ``None``.
4. ``delete(key) -> bool``: ``True`` if it was there.
5. ``len(cache)`` and ``key in cache``.  ``in`` does NOT count as a use.
6. ``cache.keys()`` -> list of keys, most recently used first.
7. Every operation above (except ``keys()``) is O(1).
8. Do not use ``OrderedDict`` or ``functools.lru_cache``.

Discussion
----------
- Since 3.7 a plain ``dict`` keeps insertion order.  Can you build an LRU
  with just ``d.pop(k); d[k] = v`` and ``next(iter(d))``?  What is the hidden
  cost of ``next(iter(d))`` after many deletions from the front?
- Why use a sentinel node in the linked list?
- How would you make it thread-safe?  Is one lock enough?  What if ``get``
  is 99% of traffic?
- What does ``__slots__`` buy you on the node class at 10 million entries?
"""


class LRUCache:
    def __init__(self, capacity):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError
