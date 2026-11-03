"""Reference solution for exercises/ex04_generator_scheduler.py."""
import heapq
import itertools
from collections import deque
from dataclasses import dataclass
from typing import Generator


@dataclass(frozen=True, slots=True)
class Sleep:
    delay: float


@dataclass(frozen=True, slots=True)
class Spawn:
    gen: Generator


@dataclass(frozen=True, slots=True)
class Join:
    tid: int


@dataclass(frozen=True, slots=True)
class Now:
    pass


class Scheduler:
    def __init__(self) -> None:
        self.time = 0.0
        self._ready = deque()  # (tid, value_to_send, exception_to_throw)
        self._sleeping = []  # heap of (wake_time, seq, tid); seq keeps ties FIFO
        self._seq = itertools.count()
        self._tids = itertools.count(1)
        self._tasks = {}  # live tid -> generator
        self._waiters = {}  # tid -> [tids joined on it]
        self._results = {}  # finished tid -> (ok, value_or_exception)
        self._joined = set()

    def spawn(self, gen: Generator) -> int:
        tid = next(self._tids)
        self._tasks[tid] = gen
        self._ready.append((tid, None, None))
        return tid

    def run(self) -> None:
        ready, sleeping = self._ready, self._sleeping
        while ready or sleeping:
            if not ready:
                self.time = max(self.time, sleeping[0][0])
            while sleeping and sleeping[0][0] <= self.time:
                ready.append((heapq.heappop(sleeping)[2], None, None))
            self._step(*ready.popleft())

        if self._tasks:
            blocked = sorted(self._tasks)
            for gen in self._tasks.values():
                gen.close()
            self._tasks.clear()
            raise RuntimeError(f"deadlock: tasks {blocked} are blocked on Join forever")
        lost = [v for tid, (ok, v) in self._results.items() if not ok and tid not in self._joined]
        if lost:
            raise ExceptionGroup("unjoined task failures", lost)

    def _step(self, tid, value, exc):
        """Run one task until it blocks, sleeps, yields or finishes.

        Syscalls that complete immediately (Spawn, Now, Join on a finished
        task) loop here instead of recursing or re-queueing.
        """
        gen = self._tasks[tid]
        while True:
            try:
                request = gen.throw(exc) if exc is not None else gen.send(value)
            except StopIteration as stop:
                return self._finish(tid, True, stop.value)
            except Exception as error:
                return self._finish(tid, False, error)
            value = exc = None

            match request:
                case None:
                    self._ready.append((tid, None, None))
                    return
                case Sleep(delay):
                    heapq.heappush(self._sleeping, (self.time + delay, next(self._seq), tid))
                    return
                case Spawn(child):
                    value = self.spawn(child)
                case Now():
                    value = self.time
                case Join(target) if target in self._results:
                    self._joined.add(target)
                    ok, outcome = self._results[target]
                    value, exc = (outcome, None) if ok else (None, outcome)
                case Join(target) if target in self._tasks:
                    self._waiters.setdefault(target, []).append(tid)
                    return
                case Join(target):
                    exc = KeyError(target)
                case _:
                    exc = TypeError(f"unknown syscall {request!r}")

    def _finish(self, tid, ok, outcome):
        del self._tasks[tid]
        self._results[tid] = (ok, outcome)
        waiters = self._waiters.pop(tid, ())
        if waiters:
            self._joined.add(tid)
        for waiter in waiters:
            # Re-queue instead of resuming directly: no recursion on long chains.
            self._ready.append((waiter, outcome, None) if ok else (waiter, None, outcome))
