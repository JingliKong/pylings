# PyLings 🐍

## What's here

| File | What |
|------|------|
| [questions-middle.md](questions-middle.md) | **Middle → Middle+** question bank: 18 predict-the-output, core language, stdlib/testing, concurrency basics, backend practice (DB, caching, auth), and "bridge to senior" questions. Hidden answers. |
| [questions.md](questions.md) | **Senior / engineer** question bank: 22 predict-the-output, internals, concurrency, performance, typing/API design, production questions, architecture prompts. |
| [exercises/](exercises/) | 20 hands-on exercises. Each file's docstring is the spec; you write the code. |
| [tests/](tests/) | Tests for every exercise except the two bug hunts. |
| [solutions/](solutions/) | Reference solutions with design-decision comments, plus the bug-hunt answer keys. |

## Exercises: easy → hard

Numbered in order of difficulty: start at 01 and go up. Time boxes are in each docstring.

| # | Level | Exercise | What it really tests |
|---|-------|----------|----------------------|
| 01 | Middle | Lazy iterator utils: `chunked`, `sliding_window`, `flatten`, `unique_everseen` | generators, eager vs lazy validation, recursion-free traversal |
| 02 | Middle | LRU cache with O(1) ops, no `OrderedDict` | hash map + doubly linked list, sentinel nodes, `None` vs missing |
| 03 | Middle | Production `@retry` decorator | decorator factories, backoff + jitter, re-raise semantics, sync **and** async |
| 04 | Middle | Code-review bug hunt, middle edition (21 bugs) | mutable defaults, shallow copies, SQL injection, path traversal, falsy-value bugs |
| 05 | Middle | Key-value store with nested transactions | undo logs vs copying, O(1) `count`, context managers |
| 06 | Middle | Access-log report | robust parsing, aware datetimes, exact percentile definitions, stable ranking |
| 07 | Middle+ | `Money` value object | `__eq__`/`__hash__`, `NotImplemented`, `Decimal`, immutability, largest-remainder allocation |
| 08 | Middle+ | Per-key token-bucket rate limiter | lazy refill, monotonic clocks, locking, memory cleanup |
| 09 | Middle+ | In-process event bus | `WeakMethod`, re-entrancy, mutation during dispatch, `ExceptionGroup` |
| 10 | Middle+ | Task graph: plan waves + run with a thread pool | Kahn's algorithm, cycle reporting, dependency-driven scheduling, fail-fast |
| 11 | Senior | Re-implement `@contextmanager` | generator `throw`/`close`, exception identity, PEP 479 |
| 12 | Senior | Thread-safe memoize: TTL + LRU + **single-flight** | locking without holding locks during I/O, stampedes, exception propagation |
| 13 | Senior | Circuit breaker | state machines under concurrency, stale results, callbacks outside locks |
| 14 | Senior | External merge sort | bounded memory/FDs, stability, atomic writes, cleanup on failure |
| 15 | Senior | async `bounded_map` | asyncio cancellation, structured concurrency, async-generator finalisation |
| 16 | Senior | asyncio worker pool | backpressure, graceful vs hard shutdown, cancellation in both directions |
| 17 | Senior | Code-review bug hunt (17 bugs) | reading code like an engineer: no tests, just your eyes |
| 18 | Staff | Event loop built from generators | how asyncio works under the hood, virtual time, deadlock detection |
| 19 | Staff | Mini pydantic: descriptors + `__init_subclass__` + typing | attribute lookup, `__set_name__`, PEP 649 lazy annotation resolution |
| 20 | Staff | DI container with lifetimes | `get_type_hints`/`inspect`, captive dependencies, cycle detection, thread-safe singletons |

## Running

Test your own implementation:

```bash
python3 -m unittest discover -s tests -v
```

Just one exercise:

```bash
python3 -m unittest discover -s tests -p "test_ex05*" -v
```

Check the reference solutions:

```bash
SOLUTIONS=1 python3 -m unittest discover -s tests
```

## How to use it

1. Start at the first exercise of your level. Set a timer for the time box in the docstring. Don't open `solutions/`.
2. Before writing code, say out loud what the edge cases are. That is half the grade.
3. When the tests pass, answer the **Discussion** questions at the bottom of each spec. Interviewers spend more time there than on the code, and that's where middle and senior answers differ most.
4. Compare with the solution. Look at *why* each design decision was made, not just whether yours works.
5. Moving up a level: do the question bank for your target level, then the next level's exercises. If you can explain the Discussion answers of a level without notes, you're ready for it.
