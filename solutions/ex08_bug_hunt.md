# Exercise 08 — Answer key

Ranked roughly by how badly they hurt in production. 🔴 = block the PR.

| # | Where | Bug | Fix |
|---|-------|-----|-----|
| 1 🔴 | `read_config` | `return {}` in `finally` **overrides the successful return** — the function *always* returns `{}` — and swallows every exception. The file is also never closed. (3.14 emits a `SyntaxWarning`, PEP 765.) | `with open(path) as f: return json.load(f)`; catch specific errors (`FileNotFoundError`, `json.JSONDecodeError`) only if a default is really the right behaviour. |
| 2 🔴 | `RateLimiter.__init__` | Mutable default `buckets={}` is created once at `def` time and **shared by every limiter** — two limiters with different rates corrupt each other's state. | `buckets=None` → `self.buckets = {} if buckets is None else buckets`. |
| 3 🔴 | `RateLimiter.allow` | Check-then-act **outside the lock**: two threads can both see the key missing and both reset the bucket to full — more requests get through. | Do the whole read-modify-write under the lock. |
| 4 | `RateLimiter.allow` | `time.time()` is wall-clock: NTP adjustments/DST/manual changes make `now - last` negative or huge. | `time.monotonic()`. |
| 5 | `RateLimiter` | `buckets` grows forever, one entry per key ever seen (memory leak / DoS vector with attacker-controlled keys). | Evict idle buckets (LRU/TTL), or use a bounded structure. |
| 6 🔴 | `User.__eq__` | Defining `__eq__` sets `__hash__ = None` → `unique_users` raises `TypeError: unhashable type` on first `seen.add(u)`. Also `other.id` raises `AttributeError` when compared with a non-`User`. | Return `NotImplemented` for other types; define `__hash__ = hash(self.id)` (only if `id` is immutable) or use a frozen dataclass. |
| 7 | `is_admin` | `is` compares identity; it works only when both strings happen to be interned. Strings from JSON/DB/network usually aren't → admins silently lose access (or worse, inconsistently). `SyntaxWarning` since 3.8. | `==`. Better: an `Enum` for roles. |
| 8 🔴 | `ProfileService.get_profile` | `lru_cache` on a method: `self` is part of the key, so the cache **holds a strong reference to every instance forever** (leak); unbounded (`maxsize=None`); never invalidated → stale profiles; cache shared at class level, not per service. Also returns the same mutable `dict` to every caller — one caller mutating it corrupts the cache. | A per-instance bounded TTL cache (Exercise 02), keyed by `user_id` only; return copies or immutable objects. |
| 9 🔴 | `parse_ids` | `except ... as e` **deletes `e`** at the end of the `except` block → the `log.warning` line raises `UnboundLocalError` on *every* bad input — the fallback path crashes. | Log inside the `except` block. Also `int("")` for input `""` or `"1,,2"` — decide whether that's an error. |
| 10 | `build_handlers` | Late-binding closure: every lambda sees the **last** `name` → all events log under the same name. | `lambda payload, name=name: ...` or `functools.partial`. |
| 11 | `retry` | After the last attempt it **falls off the loop and returns `None`** — the error is swallowed and the caller gets `None` as if it succeeded. Also sleeps after the final failure; retries *every* exception (including bugs like `TypeError`, and non-idempotent operations); no jitter → synchronized retry storms; missing `functools.wraps`. | Re-raise the last exception; only retry an allow-list of transient errors; exponential backoff **with jitter**; `@functools.wraps(fn)`. |
| 12 | `weekly_report` | `any(active)` **consumes** the generator up to and including the first active user → `list(active)` silently drops the first active user. With exactly one active user, `send_report([])` is called. | Materialise once: `active = [u for u in all_users if u.active]; if active: ...`. |
| 13 🔴 | `notify_all` | `create_task` without keeping a reference: the loop holds tasks **weakly**, so tasks can be garbage-collected mid-flight; exceptions are never retrieved (only "Task exception was never retrieved" in logs); no concurrency limit (10k users → 10k simultaneous sends); the function returns before anything is sent, so callers think it's done. | `async with asyncio.TaskGroup() as tg:` + a semaphore, or Exercise 03's `bounded_map`. |
| 14 🔴 | `fetch_with_timeout` | Bare `except:` catches `CancelledError` (a `BaseException`) → **cancellation is swallowed**: `TaskGroup`/`timeout()`/graceful shutdown hang or misbehave; also catches `KeyboardInterrupt`/`SystemExit`. | `except (TimeoutError, httpx.HTTPError):` — and if you must catch `CancelledError`, re-raise it. |
| 15 🔴 | `get_connection` | Broken double-checked locking: no **second check inside the lock**, so two threads that both saw `None` each create a connection (leak; one overwrites the other). | `with _conn_lock: if _conn is None: _conn = create_connection()`. |
| 16 | `Registry._handlers` | Class-level mutable list is shared by **all** `Registry` instances (and subclasses) → handlers registered on one registry fire on every registry; tests leak into each other. | Initialise `self._handlers = []` in `__init__`. |
| 17 | `Registry.run_all` | One failing handler stops all subsequent handlers; handlers that register handlers mutate the list while iterating. | Iterate over a copy; isolate failures (log or collect into an `ExceptionGroup`). |

Things an engineer reviewing this also raises (not bugs, but review comments):

- Module-level mutable global state (`_conn`, the shared `buckets`) makes this
  impossible to test in isolation — inject dependencies.
- No type hints on `User.__init__`, `retry`, and the callbacks — a type
  checker would have caught #6's `other.id` and #12's double use.
- None of these are caught by the "unit tests pass" signal because each needs
  concurrency, a second instance, a non-interned string, or an error path.
  Ask *which paths the tests actually exercised*.
