"""Exercise 18 — Build a tiny event loop out of generators.

Time box: 60 min.  This is how asyncio works underneath: tasks are
generators, ``yield`` hands a request ("syscall") to the scheduler, and the
scheduler resumes the task with ``send()``/``throw()``.  Time is VIRTUAL —
``run()`` must never actually sleep.

    def child(x):
        yield Sleep(2)
        return x * 10

    def parent():
        tid = yield Spawn(child(4))
        result = yield Join(tid)       # -> 40, at virtual time 2
        now = yield Now()              # -> 2.0

    s = Scheduler()
    s.spawn(parent())
    s.run()

Syscalls a task may yield
-------------------------
- ``None`` (bare ``yield``): give up the CPU; go to the back of the ready queue.
- ``Sleep(delay)``: resume at ``time + delay``.
- ``Spawn(gen)``: start a new task; resume the caller IMMEDIATELY with its id.
- ``Join(tid)``: resume with the task's return value, or have the task's
  exception raised at the ``yield``.  If the task is already finished,
  resume immediately.  Unknown tid -> raise ``KeyError`` in the caller.
- ``Now()``: resume immediately with the current virtual time.

Scheduling rules (tests depend on them)
---------------------------------------
1. Ready tasks run FIFO.  ``spawn()`` appends to the ready queue.
2. Every scheduling step first moves sleepers whose wake time <= now to the
   back of the ready queue (in wake-time order; ties in the order they went
   to sleep).  If nothing is ready, jump the clock to the next wake time.
3. ``run()`` returns when no task is left.  Then:
   - tasks still blocked on ``Join`` (e.g. A joins B, B joins A) ->
     ``RuntimeError`` mentioning "deadlock";
   - otherwise, tasks that failed and were never joined ->
     ``ExceptionGroup`` of their exceptions.
4. Must handle tens of thousands of tasks and long Join chains without
   recursion (no RecursionError).

Discussion
----------
- Map each piece to asyncio: Task, Future, the ready deque, the timer heap.
- Why can't a task "block" in this model?  What happens if one calls
  ``time.sleep(1)``?
- How would you add cancellation?
"""
from dataclasses import dataclass
from typing import Any, Generator


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

    def spawn(self, gen: Generator) -> int:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError
