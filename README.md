# Interview prep

Requires **Python 3.14** (exercise 05 relies on PEP 649 deferred annotations). No third-party packages.

## What's here

| File | What |
|------|------|
| [questions.md](questions.md) | Question bank: predict-the-output, internals, concurrency, performance, typing/API design, engineer-level architecture. Each comes with follow-ups and a hidden "what an engineer's answer covers". |
| [exercises/](exercises/) | 8 hands-on exercises. Each file's docstring is the spec; you write the code. |
| [tests/](tests/) | Tests for exercises 01–07. |
| [solutions/](solutions/) | Reference solutions with design-decision comments, plus the bug-hunt answer key. |

## Exercises (easiest → hardest, roughly)

| # | Exercise | What it really tests |
|---|----------|----------------------|
| 01 | Re-implement `@contextmanager` | generator `throw`/`close`, exception identity, PEP 479 |
| 02 | Thread-safe memoize: TTL + LRU + **single-flight** | locking without holding locks during I/O, stampedes, exception propagation |
| 03 | async `bounded_map` | asyncio cancellation, structured concurrency, async-generator finalisation |
| 04 | Event loop built from generators | how asyncio works under the hood, virtual time, deadlock detection |
| 05 | Mini pydantic: descriptors + `__init_subclass__` + typing | attribute lookup, `__set_name__`, PEP 649 lazy annotation resolution |
| 06 | DI container with lifetimes | `get_type_hints`/`inspect`, captive dependencies, cycle detection, thread-safe singletons |
| 07 | External merge sort | bounded memory/FDs, stability, atomic writes, cleanup on failure |
| 08 | Code-review bug hunt (17 bugs) | reading code like an engineer: no tests, just your eyes |

## Running

Test your own implementation:

```bash
python3 -m unittest discover -s tests -v
```

Just one exercise:

```bash
python3 -m unittest discover -s tests -p "test_ex03*" -v
```

Check the reference solutions:

```bash
SOLUTIONS=1 python3 -m unittest discover -s tests
```

## How to use it

1. Set a timer for the time box in the docstring. Don't open `solutions/`.
2. Before writing code, say out loud what the edge cases are. That is half the grade at this level.
3. When the tests pass, answer the **Discussion** questions at the bottom of each spec. Interviewers for engineer roles spend more time there than on the code.
4. Compare with the solution. Look at *why* each design decision was made, not just whether yours works.
