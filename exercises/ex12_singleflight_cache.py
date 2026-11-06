"""Exercise 12 — Thread-safe memoize with TTL, LRU and single-flight.

Time box: 45 min.  ``functools.lru_cache`` is not enough in production:
under load, N threads that miss the same key at once all hit the database
("cache stampede" / "thundering herd").  Build the decorator that fixes it.

    @memoize(ttl=30, maxsize=1024)
    def get_user(user_id: int) -> User: ...

Requirements
------------
1. Cache key = positional args + keyword args (keyword order must NOT
   matter: ``f(a=1, b=2)`` and ``f(b=2, a=1)`` share an entry).  Unhashable
   arguments raise ``TypeError``.
2. ``ttl`` (seconds, or None = forever): an entry stored at time ``t`` is
   stale once ``clock() >= t + ttl``.  ``clock`` is injectable for tests.
3. ``maxsize`` (int, or None = unbounded): evict the least-recently-used
   entry.  A cache hit counts as a "use".
4. Thread-safe.
5. **Single-flight**: if a call for key K is already running, other
   callers for K must wait for it and get the same result — the wrapped
   function runs once.
6. Calls for *different* keys must not block each other (do not hold a
   global lock while calling the wrapped function).
7. Exceptions are NOT cached.  Every caller waiting on a failed flight gets
   the exception; the next call retries.
8. ``wrapper.cache_info()`` -> ``CacheInfo(hits, misses, currsize)`` where
   ``misses`` == number of times the wrapped function actually ran and
   ``hits`` == every other call (including callers that joined a flight).
   ``wrapper.cache_clear()`` empties the cache and resets stats.
9. ``functools.wraps`` semantics (``__name__``, ``__wrapped__``).

Discussion
----------
- What if ``cache_clear()`` runs while a flight is in progress?
- Raising the same exception object in N threads: what happens to its
  ``__traceback__``?  Does it matter?
- How would this change for asyncio?  For a multi-process deployment?
"""
import time
from collections import namedtuple

CacheInfo = namedtuple("CacheInfo", "hits misses currsize")


def memoize(*, ttl=None, maxsize=128, clock=time.monotonic):
    raise NotImplementedError
