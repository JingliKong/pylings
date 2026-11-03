# Question Bank

Targets CPython 3.12–3.14.

---

## Part 1 — Predict the output (warm-up, 30 seconds each)

Say the output **and why**. "Why" is the whole point.

```python
# 1
t = (1, [2])
try:
    t[1] += [3]
except TypeError as e:
    print("error")
print(t)
```

```python
# 2
print({True: "a", 1: "b", 1.0: "c"})
```

```python
# 3
nan = float("nan")
print(nan in [nan], float("nan") in [float("nan")])
```

```python
# 4
lst = [1, 2, 3]
g = (x for x in lst if x in lst)
lst = [2]
print(list(g))
```

```python
# 5
class C:
    a = 1
    b = [a for _ in range(2)]
```

```python
# 6
def f():
    try:
        return "try"
    finally:
        return "finally"
print(f())
```

```python
# 7
try:
    1 / 0
except ZeroDivisionError as e:
    pass
print(e)
```

```python
# 8
fs = [lambda: i for i in range(3)]
print([f() for f in fs])
```

```python
# 9
print(hash(-1) == hash(-2), round(2.5), round(3.5))
```

```python
# 10
x = 10
def g():
    print(x)
    x = 20
g()
```

```python
# 11
def gen():
    yield 1
    return 2
print(list(gen()))
```

```python
# 12
class A:
    def __eq__(self, other):
        return True
print({A()})
```

<details>
<summary>Answers</summary>

1. Prints `error` **and** `(1, [2, 3])`. `t[1] += [3]` is *load `t[1]`* →
   `list.__iadd__` (mutates in place, returns the same list) → *store into
   `t[1]`*, which fails because tuples don't support item assignment. The
   mutation already happened. Shows you know `+=` is "call `__iadd__`, then
   rebind".
2. `{True: 'c'}`. `True == 1 == 1.0` and they hash equal, so it's one key.
   The **first** key object is kept, the **last** value wins.
3. `True False`. Container membership checks `is` before `==`
   (`PyObject_RichCompare` identity shortcut), so the same NaN object is
   "in" the list even though `nan != nan`. Two different NaN objects fail
   both checks.
4. `[2]`. In a generator expression only the **outermost iterable** is
   evaluated immediately (bound to the original `[1, 2, 3]`); the `if`
   clause is evaluated lazily and sees the rebound `lst`.
5. `NameError: name 'a' is not defined`. Class bodies are not enclosing
   scopes for nested functions/comprehensions. (Even after PEP 709 inlined
   comprehensions in 3.12, this behaviour was deliberately kept.) Note
   `[x for x in range(a)]` *does* work: the outermost iterable is evaluated
   in the class scope.
6. `finally`. A `return` in `finally` overrides the `try`'s return and
   silently swallows in-flight exceptions. 3.14 emits a `SyntaxWarning`
   for it (PEP 765).
7. `NameError`. The `as e` target is deleted at the end of the `except`
   block, to break the reference cycle exception → traceback → frame → `e`.
8. `[2, 2, 2]`. Closures capture *variables*, not values (late binding).
   Fix: `lambda i=i: i` or `functools.partial`.
9. `True 2 4`. `-1` is the error sentinel for `tp_hash` in the C API, so
   `hash(-1)` is `-2`. `round` uses banker's rounding (round half to even).
10. `UnboundLocalError`. Scope is decided at **compile time**: any
    assignment makes `x` local for the whole function body, so `print(x)`
    reads an unassigned local (`LOAD_FAST`).
11. `[1]`. The return value travels in `StopIteration.value`; `list()`
    drops it. `yield from gen()` would receive the `2`.
12. `TypeError: unhashable type: 'A'`. Defining `__eq__` without
    `__hash__` sets `__hash__ = None` implicitly.

</details>

---

## Part 2 — Language internals

### Q1. Walk me through exactly what happens on `obj.attr`.

Follow-ups: Why does a `@property` win over the instance `__dict__` but a
plain method doesn't? Why does `len(obj)` ignore an instance attribute
`obj.__len__`? When does `__getattr__` run?

<details>
<summary>What an engineer's answer covers</summary>

- `type(obj).__getattribute__` → `object.__getattribute__` does:
  1. Look up `attr` along `type(obj).__mro__` (not the instance).
  2. If found and it's a **data descriptor** (defines `__set__` or
     `__delete__`) → return `desc.__get__(obj, type(obj))`.
  3. Else, if `attr` is in `obj.__dict__` → return it.
  4. Else, if the type attribute is a **non-data descriptor** (only
     `__get__`, e.g. functions, `classmethod`, `cached_property`) → call
     `__get__`; if it's a plain class attribute, return it.
  5. Else raise `AttributeError` → the type's slot then calls
     `__getattr__` if defined.
- `property` is a data descriptor (it has `__set__` even when read-only),
  functions are non-data. That is why `functools.cached_property` works: it
  writes the value into the instance `__dict__`, which then shadows it.
- **Implicit special-method lookup** (`len()`, `+`, `with`, `iter`) goes to
  the *type* and skips `__getattribute__`. That's a speed and correctness
  decision (it keeps `hash(SomeClass)` from calling the instance method).
- Bonus: `type.__getattribute__` (attribute lookup on classes) is
  different: it checks the metaclass for data descriptors, then the class
  MRO (calling `__get__(None, cls)`), then the metaclass's non-data ones.
- CPython caches type lookups (the method cache plus 3.11+ specialised
  `LOAD_ATTR` instructions), and invalidates them when a class is mutated.
  Monkey-patching classes in hot paths de-optimises.

</details>

### Q2. Metaclass vs `__init_subclass__` vs class decorator vs `__set_name__`. When do you use each?

Follow-ups: Order of execution during `class X(Base, metaclass=M): ...`?
What is `__prepare__` for? What's a metaclass conflict?

<details>
<summary>What an engineer's answer covers</summary>

- Class creation order: resolve metaclass (most-derived of the explicit one
  and the bases' metaclasses, else `TypeError: metaclass conflict`) →
  `M.__prepare__(name, bases, **kw)` returns the namespace mapping → execute
  the body in it → `M.__new__` → `type.__new__` calls `__set_name__` on every
  attribute that defines it, **then** `parent.__init_subclass__(cls, **kw)`
  → `M.__init__` → class decorators run last (bottom-up).
- Rule of thumb, from least to most power:
  - `__set_name__`: a descriptor that needs to know its attribute name
    (ORM fields, validators).
  - `__init_subclass__`: register or validate subclasses, accept class
    keyword args (`class P(Model, frozen=True)`). Covers about 90% of old
    metaclass use.
  - Class decorator: one-off transformation, opt-in, and not inherited
    (dataclasses).
  - Metaclass: only when you must control the namespace (`__prepare__`, e.g.
    Enum's duplicate detection), change `isinstance` (`__instancecheck__`,
    ABCs), or customise behaviour **of the class object itself**
    (`__getitem__` on the class, `__call__` for singletons/caching).
- Cost of metaclasses: they don't compose. Two libraries' metaclasses on
  one class means writing a combined metaclass. That is why
  `__init_subclass__` (PEP 487) exists.

</details>

### Q3. Compute the MRO and explain cooperative `super()`.

```python
class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...
class E(C, B): ...
class F(D, E): ...   # what happens?
```

Follow-ups: How does zero-arg `super()` know the class? Why does it break
in a function attached to a class after definition? How do you write
cooperative `__init__`s whose signatures differ?

<details>
<summary>What an engineer's answer covers</summary>

- C3 linearisation: `D → B → C → A → object`, `E → C → B → A → object`.
  `F` raises `TypeError: Cannot create a consistent method resolution
  order`, because D needs B before C and E needs C before B.
- Zero-arg `super()` compiles to `super(__class__, <first arg>)`. The
  compiler creates a `__class__` closure cell for any method that mentions
  `super` or `__class__`, and `type.__new__` fills it in. A function
  defined outside a class body has no cell, so you get
  `RuntimeError: super(): __class__ cell not found`. A related trap:
  `dataclass(slots=True)` builds a *new* class, so historically the cell
  still pointed at the old one and `super()` broke (fixed in recent
  versions by rewriting the cell).
- `super()` means **"next in the MRO of `type(self)`"**, not "my parent".
  Cooperative pattern: every class takes `**kwargs`, pops what it owns, and
  calls `super().__init__(**kwargs)`. The root (`object`) must receive
  nothing.

</details>

### Q4. Explain CPython memory management end to end.

Follow-ups: When do objects with `__del__` in a cycle leak? What does
`gc.freeze()` do and why did Instagram care? Why can a pre-fork server's
memory blow up even though children never write to shared objects?

<details>
<summary>What an engineer's answer covers</summary>

- **Reference counting** is the primary mechanism, and it's deterministic:
  an object is freed when its refcount hits 0, which is why `with` isn't
  strictly needed for files in CPython (but is in PyPy).
- A **cyclic GC** handles cycles of *container* objects. Older versions
  have 3 generations with allocation-count thresholds; 3.14 moved to an
  incremental collector to cut pause times. It finds cycles by subtracting
  internal references (`gc_refs`) to see what's only reachable from inside
  the cycle.
- Since PEP 442 (3.4), cycles with `__del__` *are* collected (finalisers
  run once, objects may resurrect). Before that they went to `gc.garbage`.
  Leaks that remain today: global caches, `lru_cache` on methods (holds
  `self`), closures capturing big objects, tracebacks stored on exceptions
  (`exc.__traceback__` → frames → locals), unbounded registries.
- **Copy-on-write vs. refcounts**: in a forked worker, just *reading* an
  object increments its refcount, which writes the object header and
  dirties the page, so the "shared" memory gets copied. GC passes also
  touch `gc_refs`. `gc.freeze()` (3.7) moves everything to a permanent
  generation so the GC stops touching it. PEP 683 **immortal objects**
  (3.12) stop refcount writes for things like `None` and small ints.
- Small objects (≤ 512 bytes) come from **pymalloc** arenas. An arena is
  only returned to the OS when completely empty, so RSS may not drop after
  freeing ("fragmentation"). The free-threaded build uses **mimalloc**.
- Tools: `tracemalloc` snapshots/diffs, `gc.get_referrers`, `objgraph`,
  `memray`, `sys.getsizeof` (shallow only!).

</details>

### Q5. Generators: `send`, `throw`, `close`, `yield from`, and finalisation.

Follow-ups: What exactly does `yield from` delegate? What happens to an
unfinished generator that gets garbage collected? Why did PEP 479 exist?
What goes wrong with unfinished **async** generators?

<details>
<summary>What an engineer's answer covers</summary>

- `send(v)` resumes with `v` as the value of the `yield` expression.
  `throw(e)` raises `e` *at* the `yield`. `close()` throws `GeneratorExit`
  and expects the generator to exit; a generator that yields again gives
  `RuntimeError`.
- `yield from sub` is more than a loop: it forwards `send`, `throw` and
  `close` to `sub`, and evaluates to `sub`'s return value
  (`StopIteration.value`). It's the ancestor of `await`.
- On GC, an unfinished generator is `close()`d, so its `finally` blocks run
  **at some unpredictable time** (or never, at interpreter shutdown, or in
  PyPy until a collection). Never rely on a generator's `finally` to release
  locks or connections. Use `contextlib.closing` or a context manager.
- PEP 479: a `StopIteration` leaking out of a generator body used to end
  iteration silently and hide bugs. Now it becomes `RuntimeError`.
- Async generators can't be finalised synchronously (cleanup needs
  `await`). asyncio installs hooks (`sys.set_asyncgen_hooks`) that schedule
  `aclose()` on the loop, and `loop.shutdown_asyncgens()` drains them at
  exit. If you `break` out of `async for`, cleanup runs *later*, possibly in
  a different task context (no cancel scope, wrong contextvars). The fix is
  `async with contextlib.aclosing(agen):`. Exercise 03 tests this.

</details>

### Q6. `__slots__`: what does it actually do, and what are the sharp edges?

<details>
<summary>What an engineer's answer covers</summary>

- Replaces the per-instance `__dict__` (and `__weakref__`) with fixed
  offsets in the object struct. Each slot is a **member descriptor** on the
  class. That saves memory (no dict) and gives slightly faster attribute
  access, and it blocks typos like `self.nmae = ...`.
- Edges: you can't have a class attribute with the same name as a slot
  (conflict, so defaults need care); weakrefs need `'__weakref__'` in
  slots; multiple inheritance from two bases with non-empty slots raises
  `layout conflict`; a subclass without `__slots__` gets a `__dict__` back,
  so the saving silently disappears; pickling needs `__getstate__` before
  3.11.
- Since 3.11 the *non-slots* instance dict is lazily materialised and
  key-sharing dicts make regular objects much cheaper, so the gap is smaller
  than older blog posts claim. **Measure.**
- `dataclass(slots=True)` creates a *new* class, which historically broke
  zero-arg `super()` and `__init_subclass__` side effects.

</details>

### Q7. The `__eq__`/`__hash__` contract and mutable keys.

Follow-ups: You put an object into a set and then mutate a field that's
part of its hash. What exactly breaks? Why is `-0.0 == 0.0` fine but NaN
isn't?

<details>
<summary>What an engineer's answer covers</summary>

- Invariant: `a == b ⇒ hash(a) == hash(b)`. Defining `__eq__` sets
  `__hash__ = None` unless you also define it.
- A mutated key sits in the slot chosen by its *old* hash. Lookups by the
  new value probe the wrong slot, so `x in s` is False, yet iteration still
  yields it, and adding an equal object gives a "duplicate". Silent data
  corruption, not an exception.
- Dict lookup is: hash → probe → identity check → hash equal → `__eq__`.
  So a buggy `__eq__` that raises can surface from a dict access.
- NaN: `nan != nan` breaks reflexivity, so containers fall back on the
  identity check (Part 1, Q3). `-0.0 == 0.0` and their hashes are equal, so
  it's consistent.
- Frozen dataclasses/attrs or `NamedTuple` for value objects; `id`-based
  identity semantics for entities.

</details>

### Q8. The import system: what does `import a.b.c` do?

Follow-ups: Why do circular imports sometimes work and sometimes raise
`ImportError: cannot import name`? How would you cut a CLI's 2-second
startup?

<details>
<summary>What an engineer's answer covers</summary>

- Check `sys.modules` (cache) → otherwise, for each parent package, import
  it first → walk `sys.meta_path` finders (builtin, frozen, `PathFinder` →
  `sys.path_hooks` → `FileFinder`) → get a `ModuleSpec` → loader creates the
  module, **inserts it into `sys.modules` before executing**, then runs the
  code. On failure it's removed again.
- Circular imports: the partially-initialised module is already in
  `sys.modules`. `import a` succeeds (you get the half-built module, and
  attributes resolve later at call time), but `from a import name` fails if
  `name` isn't defined *yet*. Fixes: move the import into the function,
  import the module rather than the name, restructure (extract a shared
  module), or `TYPE_CHECKING`-only imports for type hints.
- Startup: `python -X importtime`, lazy imports (`importlib.util.LazyLoader`,
  module-level `__getattr__` (PEP 562), explicit `lazy import` (PEP 810,
  targeted at 3.15)), avoid import-time side effects (I/O, regex compile of
  huge tables, plugin discovery via `pkg_resources`), and ship `.pyc`
  (`compileall`).

</details>

### Q9. Annotations in 3.14: what changed and who breaks?

<details>
<summary>What an engineer's answer covers</summary>

- PEP 649/749: annotations are no longer evaluated at definition time. The
  compiler generates an `__annotate__` function, and `__annotations__`
  evaluates lazily on first access. Forward references "just work" without
  quotes.
- `annotationlib.get_annotations(obj, format=...)` with `VALUE` (evaluate,
  may raise `NameError`), `FORWARDREF` (unresolvable names become
  `ForwardRef` objects), and `STRING` (source-like strings).
- Different from `from __future__ import annotations` (PEP 563), which
  stringifies everything. Code doing `eval` of strings, or relying on
  annotation side effects at class-definition time, behaves differently.
- Who breaks: runtime-introspection libraries (dataclasses, pydantic,
  FastAPI, DI containers, attrs) that read `__annotations__` *during class
  creation*, when the referenced name may not exist yet. The robust pattern
  is to capture names early and resolve types lazily (Exercise 05 makes you
  do exactly that).

</details>

---

## Part 3 — Concurrency

### Q10. The GIL in 2026: what does it protect, and what changes with free-threading?

Follow-ups: Is `d[k] += 1` thread-safe? `list.append`? What breaks when
you flip to the free-threaded build? What about C extensions?

<details>
<summary>What an engineer's answer covers</summary>

- The GIL protects **interpreter internals** (refcounts, allocator, object
  internals), *not your invariants*. A switch can happen between any two
  bytecodes (switch interval default 5 ms, plus at blocking I/O).
- `list.append` is a single C call, so it's atomic under the GIL.
  `d[k] += 1` is load, add, store: several bytecodes and **not** atomic, so
  you lose updates. Same for "check-then-act" (`if k not in d: d[k] = ...`).
- Free-threaded build (PEP 703; experimental in 3.13, officially supported
  in 3.14 per PEP 779): no GIL. It works through biased reference counting
  (owner thread uses non-atomic ops, others atomic), deferred refcounting
  and immortalisation for hot shared objects, mimalloc, and **per-object
  critical sections** inside builtin containers, so a single `list.append`
  or `dict` op is still safe. Compound operations are as unsafe as ever,
  but races that were *rare* under the GIL become *common*.
- Costs: single-thread slowdown (roughly 5–10% in 3.14), memory overhead,
  and C extensions must declare `Py_mod_gil` support or the interpreter
  re-enables the GIL on import. Extensions relying on "the GIL protects my
  static state" need real locks.
- Also relevant: per-interpreter GIL (PEP 684) and `concurrent.interpreters`
  (PEP 734, 3.14), which give isolation without processes.

</details>

### Q11. asyncio internals: what happens when you `await`?

Follow-ups: Why can `asyncio.create_task(coro())` with no reference
silently vanish? What does cancellation look like, and what's wrong with
`except Exception` around an `await`? How do you find the coroutine
blocking the loop in production?

<details>
<summary>What an engineer's answer covers</summary>

- A coroutine is a generator-like object. `await x` calls `x.__await__()`
  and yields up the chain until something yields a **Future** to the
  `Task`. The Task registers `add_done_callback(self.__wakeup)` and returns
  control to the loop. The loop is a `select`/`epoll` call plus a ready
  queue of callbacks plus a heap of timers.
- The loop holds tasks only through **weak references** (`_all_tasks` is a
  WeakSet). A fire-and-forget task with no strong reference can be GC'd
  mid-flight, and its exception is only logged ("Task exception was never
  retrieved"). Keep references (a set plus `add_done_callback(set.discard)`)
  or use a `TaskGroup`.
- Cancellation: `task.cancel()` throws `CancelledError` at the next
  `await`. It has been a `BaseException` since 3.8, so `except Exception`
  doesn't swallow it, but bare `except:` / `except BaseException:` does,
  and that breaks `TaskGroup`, `timeout()` and shutdown. If you must
  catch it, re-raise it. 3.11 added `Task.uncancel()`/`cancelling()` so
  `asyncio.timeout` can tell its own cancellation apart from an outside
  one.
- Structured concurrency: `asyncio.TaskGroup` (3.11) cancels siblings on
  first failure and raises an `ExceptionGroup` (`except*`).
- Blocking the loop: debug mode (`PYTHONASYNCIODEBUG=1`,
  `loop.slow_callback_duration`), py-spy dumps, a watchdog thread that
  checks loop lag. Fix by moving work off the loop with
  `asyncio.to_thread` / `run_in_executor`, or into a process pool for CPU.

</details>

### Q12. Threads vs processes vs asyncio vs subinterpreters vs free-threaded. Give me your decision framework.

Follow-ups: Why did 3.14 change the default `multiprocessing` start method
on Linux? What can go wrong forking a process that has threads?

<details>
<summary>What an engineer's answer covers</summary>

- I/O-bound with high fan-out (thousands of sockets): asyncio. I/O-bound
  with blocking libraries: threads. CPU-bound pure Python: processes
  (or subinterpreters / free-threaded once dependencies support it).
  CPU-bound numeric: vectorise, or native code that releases the GIL
  (NumPy, PyO3).
- Hidden costs: processes mean pickling (serialisation dominates for
  small tasks), memory duplication and startup time. asyncio means one
  blocking call stalls everything, plus "function colouring" across the
  codebase. Threads mean races and harder debugging.
- `fork` copies only the calling thread. Locks held by other threads at
  fork time stay locked forever in the child (logging handlers, allocator
  locks, OpenSSL), so the child can deadlock. Python 3.12 warns when you
  fork a multi-threaded process; 3.14 switched the POSIX default (except
  macOS, already `spawn`) from `fork` to `forkserver`.
- Engineer angle: often the right answer is "don't add concurrency in
  Python here". Use horizontal scaling (more workers), a queue, or push
  the hot loop to the database or to native code.

</details>

### Q13. Implement a thread-safe lazy singleton. Do you need double-checked locking in Python?

<details>
<summary>What an engineer's answer covers</summary>

```python
_instance = None
_lock = threading.Lock()

def get():
    global _instance
    if _instance is None:            # fast path, no lock
        with _lock:
            if _instance is None:    # second check — the one people forget
                _instance = Expensive()
    return _instance
```

- Without the second check, two threads that both saw `None` each build
  one. Under the GIL, reading and writing a global reference is atomic and
  there's no reordering problem like Java's pre-JSR-133 issue, so the
  pattern is correct. On free-threaded builds it remains correct because
  reference stores are atomic. But the *object* must be fully constructed
  before publication, which holds because the assignment happens after
  `__init__` returns.
- Often the better answer is: module-level import-time construction (the
  import lock already serialises it), or `functools.cache` on a
  zero-arg function. Note that `functools.cache` does **not** prevent
  duplicate computation under concurrency (no single-flight). That leads
  into Exercise 02.

</details>

---

## Part 4 — Performance

### Q14. A Python service's p99 latency doubled after a deploy. Walk me through how you'd find it.

<details>
<summary>What an engineer's answer covers</summary>

- First, *measure before theorising*. Compare request traces for the old
  and new build (OpenTelemetry spans) to localise: CPU, I/O wait, lock
  contention, GC pauses, or the event loop blocked.
- A **sampling** profiler in production (py-spy `record`/`dump`, Austin,
  `perf` with `-X perf` on 3.12+ for native-level stacks) has low overhead
  and needs no code changes. `cProfile` is deterministic but adds overhead
  per call and distorts call-heavy code.
- Memory: `tracemalloc` snapshot diff or memray. GC pauses: `gc.callbacks`
  timing, `gc.set_threshold`, and `gc.freeze()` after warm-up.
- Common regressions: a new dependency doing work at import or per
  request; an N+1 query; logging with eager f-strings; a sync call in async
  code; regex catastrophic backtracking; lock contention from a new global
  cache; de-optimised attribute access from monkey-patching or dynamic
  `__getattr__`.
- Know the interpreter: the 3.11+ specialising adaptive interpreter
  (PEP 659) speeds up type-stable code, so polymorphic hot code paths
  de-specialise. The JIT (PEP 744, experimental since 3.13) isn't a
  default answer yet.

</details>

### Q15. You need to hold 50 million small records in memory. Options and numbers?

<details>
<summary>What an engineer's answer covers</summary>

- Rough per-object cost on 64-bit: a plain object with `__dict__` is a few
  hundred bytes once you count the dict and boxed field values; with
  `__slots__` it's about 16 bytes of header + 8 per slot; a tuple is about
  40 + 8 per item; every `int` beyond the small-int cache is about 28 bytes
  and every `float` 24, and those are *separate objects*.
- So 50M records × 4 fields as objects is tens of GB. Columnar storage
  (`array`, NumPy, Arrow, Polars) is about 8 bytes per field, unboxed: a
  10–50× reduction plus vectorised operations.
- `sys.getsizeof` is shallow. Use `tracemalloc` or measure RSS.
- Engineer angle: question the requirement. Can it be streamed,
  memory-mapped, pushed to a DB/DuckDB, or sharded?

</details>

### Q16. Why is `s += piece` in a loop sometimes fast and sometimes quadratic?

<details>
<summary>What an engineer's answer covers</summary>

CPython has an in-place concat optimisation: if `s` has refcount 1 (only
the local variable), `BINARY_OP +=` resizes the string buffer in place
(`realloc`, often amortised). Anything that holds a second reference (a
list, an attribute `self.s += ...`, a debugger, another variable) defeats
it, and every concat copies, giving O(n²). PyPy doesn't do this the same
way. Portable answer: `"".join(parts)` or `io.StringIO`. Engineer answer:
explain *why* the benchmark lies.

</details>

---

## Part 5 — Typing and API design

### Q17. Variance. Why is `list[int]` not a `list[float]`, but `Sequence[int]` is a `Sequence[float]`?

Follow-ups: Type a decorator that preserves the wrapped function's
signature. When do you choose `Protocol` over `ABC`?

<details>
<summary>What an engineer's answer covers</summary>

- `list` is **mutable**, so it must be invariant. If `list[int]` were a
  `list[float]`, a callee could append `1.5` into your int list.
  `Sequence` is read-only, so it's covariant. Callables are
  **contravariant** in their parameters.
- PEP 695 syntax: `def first[T](xs: Sequence[T]) -> T`, and variance is
  inferred for new-style generics.
- Signature-preserving decorators:
  `def deco[**P, R](fn: Callable[P, R]) -> Callable[P, R]` (ParamSpec).
  Add parameters with `Concatenate`.
- `Protocol` = structural (duck) typing, checked statically. It works for
  third-party classes you can't modify, and keeps interfaces at the
  consumer side. `ABC` = nominal: runtime `isinstance`, shared
  implementation, `abstractmethod` enforcement at instantiation.
  `@runtime_checkable` protocols only check method *presence*, are slow,
  and are easy to over-trust.

</details>

### Q18. You own a library used by 300 internal services. How do you evolve its API?

<details>
<summary>What an engineer's answer covers</summary>

- The public surface is explicit: `__all__`, underscore-prefixed
  internals, keyword-only arguments (`*`) for anything optional so you can
  reorder and add later, typed signatures as part of the contract, and no
  leaking of third-party types in the API.
- Change process: add new things first, deprecate with `warnings.warn(...,
  DeprecationWarning, stacklevel=2)` (or `@warnings.deprecated`, PEP 702,
  so type checkers flag it), give a migration window, then remove in a
  major version. Make CI treat your deprecations as errors in *your* tests
  only.
- Measure usage before breaking: monorepo grep or codemod (LibCST), import
  telemetry. Ship the codemod *with* the deprecation.
- Avoid returning mutable internals, boolean "mode" parameters, and
  `**kwargs` passthrough you can never take back.
- Consider the dependency diamond: if 300 services pin different versions,
  every transitive pin you add is a constraint on every one of them. Keep
  dependencies minimal and ranges wide.

</details>

---

## Part 6 — Engineer-level / architecture

These have no single right answer. The interviewer is grading structure,
trade-off reasoning, and whether you drive toward a decision.

**Q19.** Your org's main Django/FastAPI monolith (1.5M LOC, 200 engineers)
has CI times of 70 minutes and frequent import cycles. Lay out a 12-month
plan. *(Look for: measure first — test impact analysis, import-graph
tooling such as import-linter/Tach for enforced module boundaries;
`pytest-xdist` and sharding; dependency layering; a codebase-wide typing
ratchet; extracting services only where team boundaries demand it; how
you'd get buy-in and measure success.)*

**Q20.** Packaging at scale: services are failing at random because
transitive dependencies change. Design dependency management for 100 repos.
*(Lockfiles with hashes (uv/pip-tools/Poetry), a single internal index or
proxy, Renovate-style automated bumps with test gates, manylinux/abi3
wheels for native code, reproducible builds, supply-chain controls: trusted
publishing, SBOMs, pinning by hash, sigstore.)*

**Q21.** Make the case for or against adopting the free-threaded build for a
CPU-heavy internal service. *(C-extension readiness (`Py_mod_gil`), the
single-thread perf cost, which races your code currently gets away with,
staged rollout, benchmark methodology, the fallback plan, versus processes
or Rust via PyO3.)*

**Q22.** Migrate a 400k-line sync codebase to asyncio — or argue that you
shouldn't. *(Function colouring, a "sans-IO" core, edges first with
`to_thread`, two-stack periods, what you gain (fan-out) versus what you
lose (debuggability, library support), and how you'd measure that it was
worth it.)*

**Q23.** A junior engineer's PR adds a metaclass-based plugin system with
import-time registration. How do you review it? *(Explicit registration or
entry points instead of import side effects; testability; startup time;
the simplest thing that could work; how you give the feedback, since
being an engineer is also about growing people.)*
