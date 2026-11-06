"""Reference solution for exercises/3_senior/ex13_circuit_breaker.py.

Key ideas:
- Every transition bumps ``_generation``.  A call remembers the generation
  it started in and reports its outcome only if nothing changed since.
- All state changes happen under ``_lock`` and return the list of
  transitions; callbacks fire after the lock is released.
"""
import functools
import threading
import time

CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"


class CircuitOpenError(RuntimeError):
    def __init__(self, retry_after):
        super().__init__(f"circuit open; retry after {retry_after:.2f}s")
        self.retry_after = retry_after


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold=5,
        recovery_timeout=30.0,
        half_open_max_calls=1,
        expected=(Exception,),
        clock=time.monotonic,
        on_state_change=None,
    ):
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be >= 0")
        if half_open_max_calls < 1:
            raise ValueError("half_open_max_calls must be >= 1")
        self._threshold = failure_threshold
        self._timeout = recovery_timeout
        self._max_trials = half_open_max_calls
        self._expected = expected if isinstance(expected, tuple) else (expected,)
        self._clock = clock
        self._on_change = on_state_change

        self._lock = threading.Lock()
        self._state = CLOSED
        self._failures = 0
        self._opened_at = 0.0
        self._trials = 0  # in-flight half-open calls
        self._generation = 0

    # -- state machine (caller holds the lock) ---------------------------------
    def _transition(self, new, now, out):
        old, self._state = self._state, new
        self._generation += 1
        self._failures = 0
        self._trials = 0
        if new == OPEN:
            self._opened_at = now
        out.append((old, new))

    def _advance(self, now, out):
        if self._state == OPEN and now - self._opened_at >= self._timeout:
            self._transition(HALF_OPEN, now, out)

    def _notify(self, transitions):
        if self._on_change is not None:
            for old, new in transitions:
                self._on_change(old, new)

    # -- public API -------------------------------------------------------------
    @property
    def state(self):
        transitions = []
        with self._lock:
            self._advance(self._clock(), transitions)
            state = self._state
        self._notify(transitions)
        return state

    def call(self, fn, *args, **kwargs):
        transitions = []
        rejected = None
        with self._lock:
            now = self._clock()
            self._advance(now, transitions)
            if self._state == OPEN:
                rejected = CircuitOpenError(self._opened_at + self._timeout - now)
            elif self._state == HALF_OPEN and self._trials >= self._max_trials:
                rejected = CircuitOpenError(0.0)
            elif self._state == HALF_OPEN:
                self._trials += 1
            generation = self._generation
        self._notify(transitions)
        if rejected is not None:
            raise rejected

        try:
            result = fn(*args, **kwargs)  # lock NOT held
        except self._expected:
            self._record(generation, ok=False)
            raise
        except BaseException:
            self._record(generation, ok=None)  # neither success nor failure
            raise
        self._record(generation, ok=True)
        return result

    def _record(self, generation, ok):
        transitions = []
        with self._lock:
            if generation != self._generation:
                return  # stale: the world changed while this call ran
            now = self._clock()
            if self._state == HALF_OPEN:
                if ok is True:
                    self._transition(CLOSED, now, transitions)
                elif ok is False:
                    self._transition(OPEN, now, transitions)
                else:
                    self._trials -= 1
            elif self._state == CLOSED:
                if ok is True:
                    self._failures = 0
                elif ok is False:
                    self._failures += 1
                    if self._failures >= self._threshold:
                        self._transition(OPEN, now, transitions)
        self._notify(transitions)

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return self.call(fn, *args, **kwargs)

        return wrapper
