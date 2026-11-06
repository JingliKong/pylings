"""Exercise 10 — Task graph: plan and run with dependencies.  Level: Middle+

Time box: 45 min.  Build systems, CI pipelines, DB migrations, Airflow —
all are "run tasks in dependency order".  Do it without ``graphlib``.

    deps = {"test": ["build"], "build": ["fetch"], "lint": ["fetch"]}
    plan(deps)          # [["fetch"], ["build", "lint"], ["test"]]
    run(deps, execute, max_workers=4)   # {"fetch": ..., "build": ..., ...}

Part 1 — ``plan(deps) -> list[list[str]]``
------------------------------------------
1. ``deps`` maps task -> iterable of tasks it depends on.  A task that only
   appears as a dependency is still a task (``"fetch"`` above).
2. Return "waves": wave 0 = tasks with no dependencies; a task goes in wave
   ``1 + max(wave of its dependencies)``.  Each wave is sorted.
3. A cycle -> ``CycleError`` (a ``ValueError`` subclass) whose ``.cycle`` is
   a list like ``["a", "b", "c", "a"]`` where each element depends on the
   next — a real cycle that exists in the graph.  ``{"a": ["a"]}`` gives
   ``["a", "a"]``.
4. Must handle a 20,000-task chain (no recursion).  Should be O(V + E)
   (plus sorting the waves).

Part 2 — ``run(deps, fn, *, max_workers) -> dict[str, result]``
---------------------------------------------------------------
5. Calls ``fn(task)`` for every task in a thread pool of ``max_workers``
   threads, never starting a task before all its dependencies finished.
   ``max_workers < 1`` -> ``ValueError``.  Cycles -> ``CycleError`` before
   anything runs.
6. Start a task **as soon as** its own dependencies are done — not wave by
   wave.  (A slow task in wave 0 must not delay an unrelated wave-1 task.)
7. If ``fn`` raises: start no new tasks, wait for the ones already running,
   then re-raise the first exception.  Tasks downstream of the failure never
   run.
8. Returns ``{task: fn(task)}`` for every task.

Discussion
----------
- Kahn's algorithm vs DFS with three colours: which gives you waves for
  free, which gives you the cycle path for free?
- Your CI has 400 jobs; the critical path is 40 minutes but the build takes
  70.  Where do you look?  (Critical-path scheduling: start the longest
  remaining chain first.)
- How would you make ``run`` resumable after a crash (only re-run what
  didn't finish)?  What do Make and Bazel use to decide "already done"?
- When would you prefer processes over threads for ``run``?
"""


class CycleError(ValueError):
    def __init__(self, cycle):
        super().__init__(f"dependency cycle: {' -> '.join(map(str, cycle))}")
        self.cycle = cycle


def plan(deps):
    raise NotImplementedError


def run(deps, fn, *, max_workers):
    raise NotImplementedError
