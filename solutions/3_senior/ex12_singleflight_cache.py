"""Reference solution for exercises/3_senior/ex12_singleflight_cache.py."""
import functools
import threading
import time
from collections import OrderedDict, namedtuple

CacheInfo = namedtuple("CacheInfo", "hits misses currsize")

_KWMARK = object()  # separates args from kwargs so f(1, ("a", 2)) != f(1, a=2)


class _Flight:
    __slots__ = ("done", "result", "error")

    def __init__(self):
        self.done = threading.Event()
        self.result = None
        self.error = None


def _make_key(args, kwargs):
    key = args
    if kwargs:
        key += (_KWMARK, *sorted(kwargs.items()))
    hash(key)  # fail fast on unhashable arguments, before taking the lock
    return key


def memoize(*, ttl=None, maxsize=128, clock=time.monotonic):
    def decorator(fn):
        lock = threading.Lock()  # guards everything below; never held while fn runs
        cache = OrderedDict()  # key -> (expires_at | None, value)
        flights = {}  # key -> _Flight
        generation = 0  # bumped by cache_clear so stale flights don't repopulate
        hits = misses = 0

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal hits, misses
            key = _make_key(args, kwargs)
            with lock:
                entry = cache.get(key)
                if entry is not None:
                    expires_at, value = entry
                    if expires_at is None or clock() < expires_at:
                        cache.move_to_end(key)
                        hits += 1
                        return value
                    del cache[key]
                flight = flights.get(key)
                leader = flight is None
                if leader:
                    flight = flights[key] = _Flight()
                    misses += 1
                    my_generation = generation
                else:
                    hits += 1

            if not leader:
                flight.done.wait()
                if flight.error is not None:
                    raise flight.error
                return flight.result

            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                flight.error = e
                with lock:
                    if flights.get(key) is flight:
                        del flights[key]
                flight.done.set()
                raise

            flight.result = result
            with lock:
                if flights.get(key) is flight:
                    del flights[key]
                if my_generation == generation:
                    expires_at = None if ttl is None else clock() + ttl
                    cache[key] = (expires_at, result)
                    cache.move_to_end(key)
                    if maxsize is not None:
                        while len(cache) > maxsize:
                            cache.popitem(last=False)
            flight.done.set()
            return result

        def cache_info():
            with lock:
                return CacheInfo(hits, misses, len(cache))

        def cache_clear():
            nonlocal hits, misses, generation
            with lock:
                cache.clear()
                flights.clear()  # in-flight waiters still hold their _Flight
                hits = misses = 0
                generation += 1

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorator
