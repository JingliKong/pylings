# Question Bank — Middle → Middle+

Targets CPython 3.12–3.14. This is the level *below* [senior.md](senior.md):
the questions a middle developer must answer confidently, and the ones that
separate a strong middle from a senior. Each part gets harder toward the end.

How interviewers grade at this level:

- **Middle:** correct answer + the mechanism behind it ("because the default is
  evaluated once, when `def` runs").
- **Middle+:** also the trade-offs and the production consequence ("…so every
  request shares one list, which is a data leak between users").
- **Senior:** also what you'd do about it across a team (lint rule, review
  checklist, test that catches it).

---

## Part 1 — Predict the output (30 seconds each)

Say the output **and why**.

```python
# 1
def add(x, items=[]):
    items.append(x)
    return items
print(add(1), add(2))
```

```python
# 2
grid = [[0] * 3] * 3
grid[0][0] = 1
print(grid)
```

```python
# 3
nums = [2, 4, 6, 7]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
```

```python
# 4
print(sorted([3, 1, 2]).reverse())
```

```python
# 5
a = [1, 2, 3]
b = a
b += [4]
b = b + [5]
print(a, b)
```

```python
# 6
nums = map(int, "123")
print(sum(nums), sum(nums))
```

```python
# 7
print(0.1 + 0.2 == 0.3, round(0.1 + 0.2, 2) == 0.3)
```

```python
# 8
cfg = {"retries": 0}
print(cfg.get("retries") or 3, cfg.get("retries", 3))
```

```python
# 9
print(bool("False"), bool([]), bool([0]), bool(0.0), bool(" "))
```

```python
# 10
class Dog:
    tricks = []
    def __init__(self, name):
        self.name = name
a, b = Dog("a"), Dog("b")
a.tricks.append("sit")
b.name = "rex"
print(b.tricks, a.name)
```

```python
# 11
def f(*args, **kwargs):
    print(args, kwargs)
f(1, *[2, 3], a=4, **{"b": 5})
```

```python
# 12
print("a,b,,c".split(","), " a  b ".split(), "".split(","))
```

```python
# 13
def g():
    try:
        print("try")
        return 1
    except Exception:
        print("except")
    else:
        print("else")
    finally:
        print("finally")
print(g())
```

```python
# 14
print(True + True, type(True + True).__name__, 1 == 1.0, 1 is 1.0)
```

```python
# 15
d = {"a": 1}
for k in d:
    d["b"] = 2
```

```python
# 16
x = (1)
y = (1,)
z = 1,
print(type(x).__name__, type(y).__name__, type(z).__name__)
```

```python
# 17
import copy
a = {"tags": ["x"]}
b = a.copy()
c = copy.deepcopy(a)
a["tags"].append("y")
print(b["tags"], c["tags"])
```

```python
# 18
print(1 < 3 > 2, (1 < 3) > 2, 1 < 3 == 3)
```

<details>
<summary>Answers</summary>

1. `[1, 2] [1, 2]`. The default list is created **once**, when `def` runs,
   and stored in `add.__defaults__`. Both calls append to the same list, and
   both return *that same object*, so the print shows its final state twice.
   Fix: `items=None` → `items = [] if items is None else items`.
2. `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`. `* 3` copies **references**: three
   references to one inner list. Fix: `[[0] * 3 for _ in range(3)]`.
3. `[4, 7]`. Removing shifts the remaining items left while the iterator's
   index moves on: `2` is removed (4 moves to index 0, the loop goes to
   index 1 = `6`), `6` is removed, the loop ends. Never mutate a list while
   iterating it. Build a new one: `[n for n in nums if n % 2]`.
4. `None`. `sorted` returns a new list, but `.reverse()` works in place and
   returns `None` (as do `.sort()`, `.append()`, etc.). A convention: methods
   that mutate return `None`.
5. `[1, 2, 3, 4] [1, 2, 3, 4, 5]`. `+=` on a list is `__iadd__`: it mutates in
   place, so `a` sees it. `b = b + [5]` builds a **new** list and rebinds
   `b` only.
6. `6 0`. `map` returns a one-shot **iterator**. The first `sum` uses it up.
   Same with generators, `zip`, `filter`, file objects.
7. `False True`. 0.1 and 0.2 have no exact binary form; the sum is
   `0.30000000000000004`. Compare floats with `math.isclose`, and use
   `Decimal` for money.
8. `3 0`. `or` falls back on **any falsy value**, including a valid `0`.
   `.get(key, default)` only falls back when the key is missing.
9. `True False True False True`. Non-empty strings are truthy (even
   `"False"`); empty containers and zero are falsy. `[0]` is a non-empty
   list.
10. `['sit'] a`. `tricks` is a **class attribute**: one list shared by all
    instances. `b.name = "rex"` creates an instance attribute on `b` only.
11. `(1, 2, 3) {'a': 4, 'b': 5}`. `*` unpacks into positional arguments,
    `**` into keyword arguments; the function collects them back.
12. `['a', 'b', '', 'c'] ['a', 'b'] ['']`. With a separator, `split` keeps
    empty fields (and splitting `""` gives `['']`, not `[]`!). With no
    argument, it splits on runs of whitespace and drops empty strings.
13. `try`, `finally`, then `1`. `else` runs only if the `try` block finishes
    **without** an exception *and without* `return`/`break`. `finally`
    always runs, before the function actually returns.
14. `2 int True False`. `bool` is a subclass of `int` (`True == 1`). `1 ==
    1.0` compares values; `is` compares identity (different objects, even
    different types). Comparing with `is` to a literal gives a
    `SyntaxWarning`.
15. `RuntimeError: dictionary changed size during iteration`. Iterate over
    a copy: `for k in list(d):`.
16. `int tuple tuple`. Parentheses don't make a tuple — the **comma** does.
17. `['x', 'y'] ['x']`. `dict.copy()` is shallow: the new dict holds the
    same inner list. `deepcopy` copies recursively.
18. `True False True`. Comparisons **chain**: `1 < 3 > 2` means `1 < 3 and
    3 > 2`. With brackets, `(1 < 3)` is `True` (== 1), and `1 > 2` is false.

</details>

---

## Part 2 — Core language

### M1. Mutable vs immutable. What does "Python passes by assignment" mean?

Follow-ups: Is a tuple always immutable? Why can a tuple be a dict key but
a list can't? What happens when you pass a list to a function and do
`lst = lst + [1]` vs `lst.append(1)`?

<details>
<summary>What a strong answer covers</summary>

- Names are references to objects. Calling a function binds the parameter
  name to the **same object** (call by sharing / by assignment). Mutating
  the object is visible to the caller; *rebinding* the name is not.
- Immutable: `int`, `float`, `str`, `bytes`, `tuple`, `frozenset`, `None`.
  Mutable: `list`, `dict`, `set`, `bytearray`, most user objects.
- A tuple is immutable **shallowly**: `(1, [2])` can't change which objects
  it holds, but the list inside can change. Such a tuple isn't hashable
  (`hash((1, [2]))` raises `TypeError`).
- Dict keys need a hash that never changes while the key is in the dict.
  Lists are mutable, so they deliberately don't define `__hash__`.
- `lst = lst + [1]` → new list, local name rebound, caller unaffected.
  `lst.append(1)` / `lst += [1]` → caller's list changes.

</details>

### M2. What's the time complexity of common operations on list, dict, set, deque?

Follow-ups: Why is `x in list` slow but `x in set` fast? When is a dict
lookup *not* O(1)? Why is `list.pop(0)` a bad queue?

<details>
<summary>What a strong answer covers</summary>

| Operation | list | dict / set | deque |
|-----------|------|------------|-------|
| index `a[i]` | O(1) | — | O(n) (O(1) at ends) |
| append / pop at end | O(1) amortised | — | O(1) |
| insert / pop at front | **O(n)** | — | O(1) |
| `x in` | **O(n)** | O(1) average | O(n) |
| add / delete by key | — | O(1) average | — |
| sort | O(n log n) (Timsort, stable) | — | — |

- `list` is a dynamic array of pointers. It over-allocates so `append` is
  amortised O(1). Removing at the front shifts every element.
- `dict`/`set` are hash tables: hash the key → slot. **Worst case O(n)**
  when many keys collide (bad `__hash__`, or an attacker choosing keys —
  that's why `str` hashing is randomised per process: `PYTHONHASHSEED`).
- Use `collections.deque` for queues, `heapq` for priority queues,
  `bisect` for sorted lists.

</details>

### M3. How does a Python `dict` work? Why are dicts ordered?

Follow-ups: What's required of a key? What happens if you mutate an object
after using it as a key? Why is `{}` faster than `dict()`?

<details>
<summary>What a strong answer covers</summary>

- Since 3.6 (guaranteed from 3.7): a compact **entries array** (hash, key,
  value) kept in insertion order + a sparse **index table** of small ints
  pointing into it. Lookup: `hash(key)` → probe the index table → compare
  the stored hash, then `is`, then `==`. Ordering is a side effect of the
  entries array.
- Key contract: `a == b` ⇒ `hash(a) == hash(b)`, and the hash never changes
  while the key is stored. Mutate a key's hash-relevant state and the entry
  becomes unreachable — it's still in the dict, but lookups go to the wrong
  slot.
- The table resizes when about 2/3 full, so a single insert can be O(n),
  but amortised it's O(1).
- `{}` is a single bytecode instruction; `dict()` is a name lookup plus a
  call (and `dict` can be shadowed).

</details>

### M4. Shallow copy vs deep copy. When does each bite you?

Follow-ups: Ways to make a shallow copy of a list? What does `deepcopy` do
with cycles? How do you customise copying for your class?

<details>
<summary>What a strong answer covers</summary>

- Shallow: a new container holding the **same** element objects —
  `lst[:]`, `list(lst)`, `lst.copy()`, `dict(d)`, `{**d}`, `copy.copy(x)`.
  Deep: recursively copies elements — `copy.deepcopy(x)`.
- Classic bug: module-level `DEFAULTS` dict with nested dicts, `.copy()` it
  per request, then mutate a nested value → you changed the defaults for
  everyone (Exercise 04, #5).
- `deepcopy` keeps a `memo` dict (id → copy), so cycles and shared
  references are preserved, not duplicated forever.
- Customise with `__copy__` / `__deepcopy__(self, memo)`. Some objects
  can't be copied (locks, sockets, files) → deepcopy fails or is
  meaningless; design so you don't need it.
- Often the best answer is to avoid the problem: immutable data
  (`tuple`, `frozenset`, frozen dataclasses, `types.MappingProxyType`).

</details>

### M5. Explain `*args`, `**kwargs`, keyword-only and positional-only parameters.

Follow-ups: Why does `dict.get(key, default)` not accept `default=` by
name? When would you use `/` in your own API? What is `def f(a, *, b)`
for?

<details>
<summary>What a strong answer covers</summary>

- `def f(pos_only, /, normal, *, kw_only)`: before `/` → positional-only;
  after `*` (or `*args`) → keyword-only.
- `*args` collects extra positionals into a tuple, `**kwargs` extra
  keywords into a dict. At the call site, `*`/`**` unpack.
- Keyword-only for options (`sorted(xs, key=..., reverse=True)`): call
  sites read clearly, and you can add/reorder options later without
  breaking callers. Boolean flags should always be keyword-only.
- Positional-only (PEP 570, 3.8) when the parameter name is not part of the
  API and you want freedom to rename it, or when `**kwargs` must accept any
  key (`def update(self, other=(), /, **kwargs)` — otherwise a key named
  `other` collides). Many builtins like `dict.get` are positional-only.

</details>

### M6. Decorators: write one that times a function. Then one that takes arguments.

Follow-ups: What does `functools.wraps` do and what breaks without it? How
do you write a decorator that works both as `@timed` and `@timed(unit="ms")`?
Does your decorator work on `async def`?

<details>
<summary>What a strong answer covers</summary>

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__qualname__} took {time.perf_counter() - t0:.3f}s")
    return wrapper

def timed_with(*, unit="s"):          # decorator factory: returns a decorator
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): ...
        return wrapper
    return decorator
```

- `@d` is just `f = d(f)` after `def`. `@d(x)` is `f = d(x)(f)`.
- `wraps` copies `__name__`, `__qualname__`, `__doc__`, `__module__`,
  `__dict__` and sets `__wrapped__`. Without it: logs/tracebacks show
  `wrapper`, `help()` is useless, pytest fixtures and `inspect.signature`
  break.
- Both forms: `def timed(fn=None, *, unit="s"): if fn is None: return
  functools.partial(timed, unit=unit)` … — and keep options keyword-only so
  `@timed("ms")` can't be confused with a function.
- `perf_counter`, not `time.time` (monotonic, high resolution).
- Async: the sync wrapper returns the coroutine immediately (timing ≈ 0).
  Detect with `inspect.iscoroutinefunction(fn)` and write an `async def`
  wrapper (see Exercise 03).

</details>

### M7. Iterable vs iterator vs generator. Write a generator and explain how it runs.

Follow-ups: Why can you loop over a list twice but not over a generator?
What does `yield from` do? Generator expression vs list comprehension:
when do you choose which?

<details>
<summary>What a strong answer covers</summary>

- **Iterable**: has `__iter__` returning an iterator (list, dict, str, file).
  **Iterator**: has `__next__` (raises `StopIteration` at the end) and
  `__iter__` returning itself. It's one-shot.
- A `for` loop calls `iter(x)` and then `next()` until `StopIteration`.
  A list makes a *new* iterator each time; a generator *is* its own
  iterator.
- A generator function returns a generator object without running its
  body. Each `next()` runs until the next `yield`, then **suspends** with
  its local state kept (the frame lives on the heap).
- `yield from sub` delegates to the sub-generator (and passes through
  `send`/`throw`, and returns its return value).
- Generator expression: lazy, O(1) memory, single pass — good for
  `sum(x * x for x in huge)`. List comprehension: when you need `len`,
  indexing, multiple passes, or the data is small.

</details>

### M8. Context managers: what does `with` do? Write one two ways.

Follow-ups: What happens if the body raises? How does a context manager
suppress an exception? Name stdlib context managers beyond `open`.

<details>
<summary>What a strong answer covers</summary>

- `with cm as x:` → `x = cm.__enter__()`; run body; always call
  `cm.__exit__(exc_type, exc, tb)` (all `None` on success). If `__exit__`
  returns a truthy value, the exception is **suppressed**.
- Class form: `__enter__` / `__exit__`. Generator form:
  `@contextlib.contextmanager` with **`try/finally` around the `yield`**
  (forget it and cleanup doesn't run when the body raises — a common
  bug).
- Uses: files, locks (`with lock:`), DB transactions, `tempfile`,
  `decimal.localcontext()`, `unittest.mock.patch`,
  `contextlib.suppress`, `contextlib.ExitStack` (dynamic number of
  resources), `contextlib.chdir` (3.11), `asyncio.timeout` (`async with`).
- Exercise 11 re-implements `@contextmanager` — the senior version of this
  question.

</details>

### M9. Exceptions: hierarchy, `else`/`finally`, chaining, custom exceptions.

Follow-ups: `except Exception` vs bare `except`? What's the difference
between `raise X from e`, `raise X from None` and a plain `raise X` inside
`except`? When do you define your own exception classes?

<details>
<summary>What a strong answer covers</summary>

- `BaseException` → `Exception` (almost everything) and, separately,
  `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`, and
  `asyncio.CancelledError` (3.8+). Bare `except:` catches all of them —
  it can block Ctrl-C and break asyncio cancellation.
- Catch the **narrowest** exception you can handle; let the rest
  propagate. Never `except Exception: pass`. Log with `log.exception(...)`
  (it includes the traceback).
- `else` runs if no exception happened — keeps the `try` block minimal.
  `finally` always runs.
- Inside `except`, `raise X` sets `X.__context__` ("During handling of the
  above exception, another exception occurred"). `raise X from e` sets
  `__cause__` ("The above exception was the direct cause…") — use it when
  translating errors. `from None` hides the original (only when it's
  noise).
- Define a base exception per library/domain (`class PaymentError(Exception)`)
  with specific subclasses, so callers can catch at the right level.
  Add data as attributes (`retry_after`), not only in the message.
- 3.11+: `ExceptionGroup` and `except*` for several errors at once
  (TaskGroup); `e.add_note(...)` for extra context.

</details>

### M10. `@staticmethod` vs `@classmethod` vs `@property`. When does each make sense?

Follow-ups: Why are alternative constructors classmethods? How do you make
a read-only attribute? What's `functools.cached_property` and when is it
wrong?

<details>
<summary>What a strong answer covers</summary>

- `classmethod` gets `cls`: alternative constructors
  (`datetime.fromtimestamp`, `Money.from_cents`) that **work for
  subclasses** (`cls(...)` builds the subclass).
- `staticmethod`: a plain function namespaced in the class. Often a
  module-level function is better; fine when it's an implementation detail
  that subclasses may override.
- `property`: computed or validated attribute with attribute syntax. A
  property without a setter is read-only. Keep it cheap and side-effect-free
  — callers assume attribute access is fast.
- `cached_property`: computes once, stores in the instance `__dict__`.
  Wrong when the value can go stale (depends on mutable state), with
  `__slots__` (no `__dict__`), and before 3.12 it took a lock that
  serialised all instances.

</details>

### M11. `__repr__` vs `__str__`. `__eq__` and `__hash__`. What does `@dataclass` generate?

Follow-ups: What does `print([obj])` use? When do you set `frozen=True`,
`slots=True`, `order=True`? What's wrong with `field: list = []` in a
dataclass?

<details>
<summary>What a strong answer covers</summary>

- `repr` is for developers (unambiguous, ideally `eval`-able); `str` for
  users. Containers use the **repr** of their items. `str` falls back to
  `repr`. f-strings: `{x!r}`.
- If you define `__eq__`, Python sets `__hash__ = None` (unhashable) unless
  you also define `__hash__`. Equal objects must have equal hashes; hash
  only immutable fields.
- `@dataclass` generates `__init__`, `__repr__`, `__eq__` (and `__match_args__`).
  `order=True` → `<` etc. comparing fields as tuples. `frozen=True` →
  assignment raises, and `__hash__` is generated. `slots=True` (3.10) →
  `__slots__`, less memory, no accidental attributes. `kw_only=True` (3.10).
- `xs: list = []` raises `ValueError` at class creation — dataclasses
  refuse mutable defaults; use `field(default_factory=list)`.
- Dataclass vs `NamedTuple` (immutable, tuple-like, unpackable) vs
  `TypedDict` (just type hints for a dict, no runtime class) vs pydantic
  (runtime validation and parsing at boundaries).

</details>

### M12. What is the LEGB rule? What do `global` and `nonlocal` do?

Follow-ups: Why does `x += 1` inside a function fail when `x` is global?
What's a closure? What is the late-binding closure gotcha?

<details>
<summary>What a strong answer covers</summary>

- Name lookup: **L**ocal → **E**nclosing functions → **G**lobal (module) →
  **B**uiltins. Decided at compile time: any assignment to a name in a
  function makes it local for the whole function → `UnboundLocalError` if
  read before assignment.
- `global x` binds to the module variable; `nonlocal x` to the nearest
  enclosing function's variable. Prefer returning values or a small class
  over either.
- A closure is a function that keeps the enclosing function's variables
  alive (`fn.__closure__` cells). Cells hold **variables**, not values: in
  `[lambda: i for i in range(3)]` every lambda sees the final `i`. Fix:
  `lambda i=i: i`.
- Class bodies are *not* an enclosing scope for methods — that's why you
  write `self.x` / `ClassName.x`.

</details>

### M13. ABC vs `Protocol`. Duck typing vs explicit interfaces.

Follow-ups: When is `isinstance` checking a smell? What does
`@runtime_checkable` do and not do?

<details>
<summary>What a strong answer covers</summary>

- Duck typing: "if it has `.read()`, it's a file". Flexible, but errors show
  up late (`AttributeError` deep in the code).
- `abc.ABC` + `@abstractmethod`: **nominal** — classes must inherit; you
  get an error at instantiation if a method is missing, and can share
  implementation.
- `typing.Protocol`: **structural** — any class with the right methods
  matches, checked by the type checker, no inheritance needed. Great for
  dependencies you don't own and for "the function needs something with
  `.send()`".
- `@runtime_checkable` lets `isinstance` work with a protocol, but it only
  checks that the attributes **exist**, not their signatures or types.
- `isinstance` chains on concrete types (`if type == "A": ... elif ...`) are
  usually a sign that polymorphism or a dispatch dict would be cleaner;
  `functools.singledispatch` and `match` are options.

</details>

### M14. Explain `match` (structural pattern matching). When is it better than `if/elif`?

Follow-ups: What's the bug in `case RED:`? How do you match a dict with
extra keys? What does `case Point(x=0)` require from `Point`?

<details>
<summary>What a strong answer covers</summary>

- `match` destructures: sequences (`case [first, *rest]`), mappings
  (`case {"type": "click", "pos": (x, y)}` — **extra keys are allowed**),
  classes (`case Point(x=0, y=y)` — uses attributes; positional patterns
  need `__match_args__`, which dataclasses generate), literals, `|`
  alternatives, `as` captures, and `if` guards.
- **Gotcha**: a bare name is a *capture pattern*: `case RED:` matches
  anything and assigns it to `RED`. Use dotted names for constants:
  `case Color.RED:`.
- Good for parsing tree-like or message-like data (ASTs, JSON events,
  commands). For simple value comparisons, a dict lookup or `if` is
  clearer.

</details>

---

## Part 3 — Stdlib, tooling and testing

### M15. Virtual environments, dependencies and project layout. What's your setup?

Follow-ups: `requirements.txt` vs `pyproject.toml` vs lockfile? Why should
you never `sudo pip install`? What's a "src layout"?

<details>
<summary>What a strong answer covers</summary>

- One venv per project (`python -m venv .venv` or `uv venv`): isolated
  interpreter + site-packages. Don't touch the system Python (the OS
  depends on it; PEP 668 "externally managed" blocks `pip install` there).
- `pyproject.toml` declares the project and its **direct** dependencies with
  ranges. A **lockfile** (`uv.lock`, `poetry.lock`, pip-tools'
  `requirements.txt` with hashes) pins the **whole tree** exactly, so CI
  and prod install the same versions.
- Apps: commit the lockfile. Libraries: wide ranges, test against a
  matrix.
- `src/` layout: the package lives in `src/pkg`, so tests import the
  *installed* package, not the directory you happen to be in — catches
  packaging mistakes.
- Tools you should name: `uv`/`pip`, `ruff` (lint + format), `mypy` or
  `pyright`, `pytest`, `pre-commit`.

</details>

### M16. How do you configure logging properly in an application vs a library?

Follow-ups: Why `log.info("user %s", uid)` instead of an f-string? What's
`log.exception`? How do you add a request ID to every log line?

<details>
<summary>What a strong answer covers</summary>

- Libraries: `log = logging.getLogger(__name__)`, **never** configure
  handlers or call `basicConfig` (the app decides). Optionally add a
  `NullHandler`.
- Applications: configure once at startup (`logging.config.dictConfig`):
  levels, handlers, format. In containers, log to stdout, usually as JSON
  (structured logs).
- `%s` arguments: formatting happens only if the record is emitted, and
  aggregators can group by the template. f-strings format always.
- `log.exception("msg")` inside `except` → ERROR level + traceback.
- Context (request ID, user ID): a `logging.Filter` or `LoggerAdapter` that
  reads a `contextvars.ContextVar` set by middleware — works for threads and
  asyncio. Never log secrets, tokens or full personal data.

</details>

### M17. Dates and times. What goes wrong with them?

Follow-ups: Naive vs aware? Why is `datetime.utcnow()` deprecated? How do
you store times in a DB? How do you test code that uses "now"?

<details>
<summary>What a strong answer covers</summary>

- **Naive** datetimes have no timezone; **aware** ones do. Comparing naive
  and aware raises `TypeError`; mixing two naive ones from different zones
  is silently wrong.
- `utcnow()` returns a *naive* datetime that holds UTC, which code later
  treats as local time → deprecated in 3.12. Use
  `datetime.now(timezone.utc)`.
- Store **UTC** (`timestamptz` in Postgres), convert to the user's zone
  (`zoneinfo.ZoneInfo("Asia/Tashkent")`) only for display. Store the
  user's zone name separately if you need local "9 am every day" rules
  (DST!).
- Durations/timeouts: `time.monotonic()`, never wall-clock time (NTP can
  move it backwards).
- Testing: inject a clock (`now=datetime.now` parameter) or use
  `time-machine`/`freezegun`. Exercises 08, 12, 13 all inject the clock.

</details>

### M18. Why `Decimal` for money? What are its pitfalls?

<details>
<summary>What a strong answer covers</summary>

- Binary floats can't represent most decimal fractions:
  `0.1 + 0.2 != 0.3`; errors add up in sums and reports.
- `Decimal("0.1")` is exact. But `Decimal(0.1)` copies the float's error
  (`0.1000000000000000055511151231257827…`) — always construct from `str`
  or `int`.
- Precision is per **context** (default 28 significant digits);
  `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` sets decimal places
  and the rounding rule explicitly. The rounding rule is a business
  decision.
- Alternatives: integer minor units (cents) — fast and simple; the
  currency decides the number of decimals (JPY has 0, BHD has 3).
- Splitting money (`100 / 3`) needs an allocation rule so cents aren't lost
  — Exercise 07.

</details>

### M19. How do you test code that calls an external API? Mocks vs fakes vs real.

Follow-ups: Where do you `patch` — where the function is defined or where
it's used? What's wrong with a test suite that is 90% mocks? What's a
fixture? What's `parametrize`?

<details>
<summary>What a strong answer covers</summary>

- `mock.patch("myapp.service.requests.get")` — patch the name **where it is
  looked up** (the module that uses it), not where it's defined. `from x
  import y` creates a new name in your module; patching `x.y` won't affect
  it.
- Use `autospec=True` so the mock has the real signature (catches calls
  with wrong arguments).
- Too many mocks = tests that check *how* the code works, not *what* it
  does; they break on every refactor and still pass when the real API
  changed. Prefer: inject the client (dependency injection) and use a
  small **fake**; record/replay (`vcrpy`, `respx` for httpx); and a few
  contract/integration tests against a real sandbox or a container
  (testcontainers).
- pytest fixtures: setup/teardown with `yield`, scopes (function/module/
  session), composition. `@pytest.mark.parametrize` for table-driven
  tests.
- Test the edges: timeouts, 500s, malformed JSON, retries, rate limits.

</details>

### M20. Type hints: what do they give you? `Optional`, `Union`, generics, `TypeVar`.

Follow-ups: Are types checked at runtime? `list[int]` vs `List[int]`? How
do you type a function that returns the same type it receives? What is
`Any` and why is it dangerous?

<details>
<summary>What a strong answer covers</summary>

- Hints are **not enforced** at runtime (except by tools like pydantic);
  mypy/pyright check them statically. Benefits: catches `None` bugs,
  documents the API, enables IDE refactoring.
- Modern syntax: `list[int]` (3.9), `int | None` instead of
  `Optional[int]` (3.10), `def first[T](xs: list[T]) -> T:` (PEP 695,
  3.12) instead of `T = TypeVar("T")`. `type Alias = ...` (3.12).
- `Any` turns checking off — and spreads. Prefer `object` ("anything, but I
  won't use it without checking") or a `Protocol`.
- Useful extras: `Literal["r", "w"]`, `TypedDict` for JSON-like dicts,
  `Final`, `@overload`, `Self` (3.11), `TypeIs` (3.13) for narrowing
  helpers.
- Senior follow-up (variance, `Callable` parameters): see
  [senior.md](senior.md) Q17.

</details>

---

## Part 4 — Concurrency basics

### M21. Threads, processes, or asyncio? Give me the one-minute version.

<details>
<summary>What a strong answer covers</summary>

- **I/O-bound** (network, disk, DB): threads (`ThreadPoolExecutor`) or
  asyncio. The GIL is released while waiting for I/O. asyncio scales to
  thousands of connections cheaply but needs async libraries all the way
  down.
- **CPU-bound** pure Python: processes (`ProcessPoolExecutor`,
  `multiprocessing`) to use all cores — with the cost of pickling data
  between processes. Or C extensions/NumPy that release the GIL. 3.13+
  free-threaded builds change this picture (see senior.md Q10).
- Never call blocking code (`requests.get`, `time.sleep`, heavy CPU) inside
  an `async def` — it freezes the whole event loop. Use
  `await asyncio.to_thread(fn)`.
- The deeper version is senior.md Q12.

</details>

### M22. What is a race condition? Show one in Python, even with the GIL.

Follow-ups: Is `counter += 1` atomic? Is `list.append` thread-safe? What's a
deadlock and how do you avoid one?

<details>
<summary>What a strong answer covers</summary>

- A race: the result depends on the timing of threads. `counter += 1` is
  *load, add, store* — several bytecodes; a thread switch between them
  loses updates. The GIL makes single bytecodes atomic, not your logic.
- Check-then-act is the classic race: `if key not in cache: cache[key] =
  compute()` → two threads both compute (and maybe both write).
- Single operations on builtins like `list.append` or `dict[k] = v` are
  thread-safe in CPython (and kept safe by per-object locks in the
  free-threaded build), but a *sequence* of them is not.
- Fix: `threading.Lock` around the whole read-modify-write (`with lock:`),
  or avoid shared state (`queue.Queue` to pass messages; one owner thread).
- Deadlock: two threads take two locks in opposite order. Avoid with a
  global lock order, holding locks briefly, never calling unknown code
  (callbacks, I/O) while holding a lock, and timeouts.

</details>

### M23. asyncio basics: what does `await` do? `gather` vs `TaskGroup`?

Follow-ups: What happens if you call an `async def` function without
`await`? How do you limit concurrency to 10 requests at a time? How do you
add a timeout?

<details>
<summary>What a strong answer covers</summary>

- Calling an `async def` function only creates a **coroutine object**;
  nothing runs ("coroutine was never awaited" warning). `await` runs it
  until it has to wait, then yields control to the event loop, which runs
  other tasks.
- Concurrency comes from **tasks**: `asyncio.create_task(coro)` schedules
  it. Keep a reference to the task (the loop holds only weak refs).
- `gather(*coros)`: runs concurrently, returns results in order; on error,
  the others keep running unless you cancel them. `asyncio.TaskGroup`
  (3.11): if one fails, the rest are **cancelled**, and errors come out as
  an `ExceptionGroup` — structured concurrency; prefer it.
- Limit: `sem = asyncio.Semaphore(10)` and `async with sem:` around each
  request (or Exercise 15's `bounded_map`).
- Timeout: `async with asyncio.timeout(5):` (3.11) or
  `asyncio.wait_for(coro, 5)`.

</details>

---

## Part 5 — Backend practice

### M24. What is the N+1 query problem? How do you find and fix it?

<details>
<summary>What a strong answer covers</summary>

- Load 100 orders with 1 query, then access `order.customer` in a loop →
  100 more queries. Each is fast; together they kill latency and the DB.
- Find: SQL logging in dev, `django-debug-toolbar`, `nplusone`, APM traces
  showing many identical queries per request, a test asserting the query
  count (`assertNumQueries`).
- Fix: eager loading — Django `select_related` (JOIN, for FK/one-to-one) /
  `prefetch_related` (second query with `IN (...)`, for many-to-many/
  reverse FK); SQLAlchemy `joinedload` / `selectinload`. Or batch by hand:
  collect IDs, one `WHERE id IN (...)` query, build a dict. GraphQL:
  DataLoader.

</details>

### M25. DB transactions: what does ACID mean in practice? What are isolation levels?

Follow-ups: Two requests both read balance = 100 and both withdraw 80. What
happens and how do you prevent it? What's `SELECT ... FOR UPDATE`?

<details>
<summary>What a strong answer covers</summary>

- Atomic (all or nothing), Consistent (constraints hold), Isolated
  (concurrent transactions don't see each other's half-done work, to a
  degree), Durable (committed = survives a crash).
- Isolation levels: Read Uncommitted < Read Committed (Postgres default) <
  Repeatable Read < Serializable. Lower = more anomalies (non-repeatable
  reads, phantoms, lost updates, write skew), higher = more
  blocking/retries.
- Lost update in the example: both read 100, both write 20 → one
  withdrawal disappears (or the balance goes wrong). Fixes:
  - atomic update: `UPDATE accounts SET balance = balance - 80 WHERE id = 1
    AND balance >= 80` and check the affected row count;
  - pessimistic locking: `SELECT ... FOR UPDATE` inside the transaction;
  - optimistic locking: a `version` column, `UPDATE ... WHERE version = 7`,
    retry if 0 rows changed;
  - `SERIALIZABLE` and retry on serialization failure.
- Keep transactions short; never call external APIs inside one.

</details>

### M26. What makes an API endpoint idempotent? Why do payments need idempotency keys?

<details>
<summary>What a strong answer covers</summary>

- Idempotent: doing it twice has the same effect as once. `GET`, `PUT`,
  `DELETE` should be; `POST` usually isn't.
- Networks fail *after* the server did the work: the client times out and
  retries → double charge. With an `Idempotency-Key` header, the server
  stores `key → result` (with a unique constraint), and a retry with the
  same key returns the stored result instead of charging again.
- Details: store the key in the **same transaction** as the side effect;
  handle "same key, request still in progress" (409 or wait); expire keys;
  reject the same key with a different body.
- Retries without idempotency are the bug (Exercise 03 discussion).

</details>

### M27. Offset vs cursor pagination.

<details>
<summary>What a strong answer covers</summary>

- `LIMIT 20 OFFSET 100000`: the DB still reads and throws away 100k rows →
  gets slower with each page; rows inserted/deleted between requests cause
  duplicates or skipped items.
- Cursor (keyset): `WHERE (created_at, id) < (:last_created_at, :last_id)
  ORDER BY created_at DESC, id DESC LIMIT 20`, using an index → constant
  speed, stable under inserts. The cursor is an opaque (base64) token of
  the last row's sort key. You lose "jump to page 37" and an exact total
  count (which is expensive anyway).
- The sort must be **unique** (add `id` as a tie-breaker), or rows with
  equal timestamps get skipped.

</details>

### M28. Caching: where do you cache, and how do you keep it correct?

Follow-ups: Cache-aside vs write-through? What's a cache stampede? How do
you invalidate? What should never be cached?

<details>
<summary>What a strong answer covers</summary>

- Layers: in-process (`functools.lru_cache`, a dict with TTL — per process,
  fastest, no shared invalidation), shared (Redis/Memcached), HTTP
  (`Cache-Control`, ETags, CDN), DB (materialised views).
- Cache-aside: read cache → on miss read DB, store with TTL. On write:
  update DB, then **delete** the cache key (deleting is safer than
  updating, which can race).
- Always set a TTL (it's your safety net for invalidation bugs); add jitter
  to TTLs so keys don't all expire together.
- Stampede: a hot key expires and 1000 requests hit the DB at once → single
  flight/locking (Exercise 12), early refresh, serve stale while
  revalidating.
- Don't cache per-user data under a shared key (data leak), and think twice
  about caching errors and empty results ("negative caching" needs a short
  TTL).

</details>

### M29. JWT vs server-side sessions. What are common auth mistakes?

<details>
<summary>What a strong answer covers</summary>

- Session: random ID in an `HttpOnly; Secure; SameSite` cookie, data on the
  server (Redis/DB). Easy to revoke. Needs shared storage.
- JWT: signed token carrying claims; stateless verification. Hard to revoke
  before expiry → short-lived access tokens + refresh tokens (rotated,
  stored server-side so they *can* be revoked).
- Mistakes: accepting `alg: none` or not pinning the algorithm; not checking
  `exp`/`aud`/`iss`; storing tokens in `localStorage` (readable by any XSS);
  putting secrets/PII in the payload (it's only base64, not encrypted);
  long-lived tokens; comparing secrets with `==` instead of
  `hmac.compare_digest` (timing attacks); rolling your own password hashing
  instead of argon2/bcrypt.

</details>

---

## Part 6 — Middle+ → Senior bridge

These are where a strong middle shows senior potential: structure, data,
trade-offs.

### M30. An endpoint got slow. You have 30 minutes. What do you do?

<details>
<summary>What a strong answer covers</summary>

- Reproduce and **measure** before guessing: which endpoint, since when (a
  deploy? data growth?), p50 vs p99, all users or some.
- Look at traces/APM first: time in the DB? an external call? Python CPU?
- DB: slow query log, `EXPLAIN ANALYZE` (missing index? seq scan? N+1?),
  lock waits, connection pool exhaustion (requests waiting for a
  connection look like "slow DB").
- Python: `py-spy top/dump --pid` on the live process (no restart),
  `cProfile` + `snakeviz` locally, `pyinstrument` for a request.
- Fix the biggest measured cost, verify with the same measurement, add a
  regression check (benchmark, query-count test, alert).
- Senior version: senior.md Q14.

</details>

### M31. Your service's memory grows until it's OOM-killed every day. How do you find the leak?

<details>
<summary>What a strong answer covers</summary>

- Confirm it's a leak and not just a big working set or fragmentation
  (does it plateau? does it correlate with traffic?).
- `tracemalloc`: take snapshots minutes apart, `snapshot.compare_to(old,
  "lineno")` → which lines allocate the memory that stays. `objgraph`
  / `gc.get_objects()` counts by type to see what's growing; `memray` for
  native allocations too.
- Usual suspects: unbounded caches (`lru_cache(maxsize=None)`, module-level
  dicts keyed by request data), `lru_cache` on methods (holds `self`),
  listeners/callbacks never unsubscribed (Exercise 09), growing lists of
  tasks/futures, global registries, C extensions.
- Mitigation while you fix it: worker recycling (`max_requests` in
  gunicorn/uvicorn), memory limits with alerts.

</details>

### M32. How do you review a pull request?

<details>
<summary>What a strong answer covers</summary>

- First understand the *why* (ticket, description) and the design — is this
  the right change at all? Big design comments early, before nitpicks.
- Then correctness: edge cases (empty, None, huge, unicode, concurrent),
  error handling, transactions, security (injection, authz checks, secrets
  in logs), backward compatibility (API, DB migrations that lock tables),
  observability (logs/metrics for the new path), tests that would fail
  without the change.
- Let tools handle style (ruff, formatter, type checker in CI).
- Tone: ask questions, explain the reason, label nits as nits, approve with
  comments when it's fine. Review small PRs fast.
- Practice: Exercises 04 and 17.

</details>

### M33. Design a URL shortener (small scale: 1,000 new links/day, 100 req/s reads).

<details>
<summary>What a strong answer covers</summary>

- Clarify requirements first: custom aliases? expiry? analytics? who can
  create links (abuse!)?
- API: `POST /links {url} → {code}`, `GET /{code} → 301/302`. 302 if you
  need click analytics (301 is cached by browsers).
- Code generation: base62 of an auto-increment ID (short, but guessable —
  is that OK?) or random 7 chars (62⁷ ≈ 3.5 trillion) with a unique
  constraint and retry on collision.
- Storage: one Postgres table `(code PK, url, created_at, owner, expires_at)`
  is plenty at this scale; add a Redis or in-process cache for hot codes.
- Validate URLs (scheme allow-list `http/https`), rate-limit creation
  (Exercise 08), check against malware/phishing lists.
- Say what you'd change at 100× scale — and that you wouldn't build that
  now.

</details>
