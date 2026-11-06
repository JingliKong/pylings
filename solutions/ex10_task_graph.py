"""Reference solution for exercises/ex10_task_graph.py."""
from collections import defaultdict, deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait


class CycleError(ValueError):
    def __init__(self, cycle):
        super().__init__(f"dependency cycle: {' -> '.join(map(str, cycle))}")
        self.cycle = cycle


def _build(deps):
    """Return (prereqs, dependents) with every task present as a key."""
    prereqs = {}
    for task, ds in deps.items():
        prereqs.setdefault(task, set()).update(ds)
        for d in ds:
            prereqs.setdefault(d, set())
    dependents = defaultdict(list)
    for task, ds in prereqs.items():
        for d in ds:
            dependents[d].append(task)
    return prereqs, dependents


def _find_cycle(prereqs, remaining):
    # Every task left after Kahn's has at least one prerequisite that is also
    # left (otherwise it would have been processed).  So walking "any
    # remaining prerequisite" from any remaining task must revisit a task.
    start = min(remaining, key=str)
    path, index = [], {}
    node = start
    while node not in index:
        index[node] = len(path)
        path.append(node)
        node = min((p for p in prereqs[node] if p in remaining), key=str)
    return path[index[node]:] + [node]


def plan(deps):
    prereqs, dependents = _build(deps)
    indegree = {t: len(ds) for t, ds in prereqs.items()}
    wave_of = dict.fromkeys(prereqs, 0)  # longest path from a root, so far
    queue = deque(t for t, n in indegree.items() if n == 0)
    done = []
    while queue:  # Kahn's algorithm
        t = queue.popleft()
        done.append(t)
        for child in dependents[t]:
            wave_of[child] = max(wave_of[child], wave_of[t] + 1)
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    # Careful: "has a wave_of entry" is not "processed" — a task can be
    # partially relaxed and still be stuck behind a cycle.
    if len(done) != len(prereqs):
        raise CycleError(_find_cycle(prereqs, set(prereqs) - set(done)))
    waves = defaultdict(list)
    for t in done:
        waves[wave_of[t]].append(t)
    return [sorted(waves[w]) for w in range(len(waves))]


def run(deps, fn, *, max_workers):
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    plan(deps)  # validates: raises CycleError before anything runs
    prereqs, dependents = _build(deps)
    waiting_on = {t: len(ds) for t, ds in prereqs.items()}
    ready = sorted(t for t, n in waiting_on.items() if n == 0)
    results, running = {}, {}
    error = None

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while ready or running:
            # Never hand the pool more than max_workers tasks: anything queued
            # inside the executor would still start after a failure.
            while ready and error is None and len(running) < max_workers:
                t = ready.pop()
                running[pool.submit(fn, t)] = t
            if not running:
                break
            done, _ = wait(running, return_when=FIRST_COMPLETED)
            for fut in done:
                t = running.pop(fut)
                exc = fut.exception()
                if exc is not None:
                    if error is None:
                        error = exc
                        ready.clear()
                    continue
                results[t] = fut.result()
                for child in dependents[t]:
                    waiting_on[child] -= 1
                    if waiting_on[child] == 0 and error is None:
                        ready.append(child)
    # Leaving the `with` block waited for every running task.
    if error is not None:
        raise error
    return results
