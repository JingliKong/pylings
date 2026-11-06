# Exercise 04 — Answer key

Ranked roughly by how much damage they do. 🔴 = block the PR.

| # | Where | Bug | Fix |
|---|-------|-----|-----|
| 1 🔴 | `find_orders` | **SQL injection.** `customer = "x' OR '1'='1"` returns every order; `"x'; DROP TABLE orders; --"` is the classic. Never build SQL with f-strings. | Parameters: `db.execute("... WHERE customer = ?", (customer,))`. |
| 2 🔴 | `save_upload` | **Path traversal.** `filename="../../etc/cron.d/evil"` escapes `UPLOAD_DIR`. Worse, `os.path.join` *throws away* everything before an absolute component: `join("/srv/uploads", "/etc/passwd") == "/etc/passwd"`. | Generate your own file name (UUID) and keep the user's name only as metadata. Or `Path(UPLOAD_DIR, name).resolve()` and check `.is_relative_to(Path(UPLOAD_DIR).resolve())`. |
| 3 🔴 | `Order.items` | **Class attribute shared by every instance.** `self.items.append` mutates the one list on the class: every order contains every item ever added, and `total()` is wrong for all of them. | `self.items = []` in `__init__`. |
| 4 🔴 | `Order.__init__` | `created_at=datetime.now()` is evaluated **once, at import time**. Every order created without the argument gets the time the process started. | `created_at=None` → `self.created_at = created_at or datetime.now(timezone.utc)`. |
| 5 🔴 | `load_settings` | `dict.copy()` is **shallow**: `settings["features"]` *is* `DEFAULT_SETTINGS["features"]`, so `.update(value)` changes the defaults for every later caller (one user's file turns `beta` on for everyone). | `copy.deepcopy(DEFAULT_SETTINGS)`, or build a new nested dict: `{**DEFAULT["features"], **user.get("features", {})}`. |
| 6 | `total` / `apply_discount` | **Floats for money.** `0.1 + 0.2 != 0.3`; `round()` is "round half to even" on a binary approximation, so `round(2.675, 2) == 2.67`. Rounding at the end hides errors until they add up in a report. | `Decimal` (from `str`, not from float) or integer cents; round with an explicit rule at defined points (see Exercise 07). |
| 7 | `apply_discount` | `assert` for input validation is **removed with `python -O`**: then `percent=150` gives a negative price. | `if not 0 <= percent <= 100: raise ValueError(...)`. Asserts are for "this can't happen" invariants. |
| 8 | `remove_cancelled` | **Mutating a list while iterating over it** skips the element after every removal. Two cancelled orders in a row → the second one stays. | `return [o for o in orders if o.status != "cancelled"]` (and don't mutate the caller's list unless that's the contract). |
| 9 | `latest_orders` | `list.sort()` sorts in place and **returns `None`** → `TypeError: 'NoneType' object is not subscriptable`. Also it would reorder the caller's list as a side effect. | `sorted(orders, key=..., reverse=True)[:n]` or `heapq.nlargest(n, orders, key=...)`. |
| 10 | `parse_quantity` | Bare `except:` also catches `KeyboardInterrupt`/`SystemExit`, and turning bad input into `0` **silently** hides data errors (a typo becomes "ordered 0 items"). | `except ValueError:` and let the caller decide; at least log. Also consider `int(" 3 ")` (works), `int("3.0")` (fails), negatives. |
| 11 | `get_timeout` | `x or default` treats **every falsy value** as missing: an explicit `"timeout": 0` becomes 30. | `settings.get("timeout", 30)`, or `30 if v is None else v`. |
| 12 | `Cache.get_or_compute` | Same falsy problem: cached `0`, `""`, `[]`, `None` are **recomputed on every call** (the cache never works for them). | `if key in self.data:` (or a sentinel with `.get(key, _MISSING)`). Also unbounded growth, and not thread-safe. |
| 13 | `is_recent` | Mixes **local time** (`datetime.now()` in `__init__`) with **UTC** (`utcnow()`): off by the UTC offset (5 hours in Tashkent). `utcnow()` is deprecated since 3.12 because it returns a *naive* datetime that looks local. | Aware datetimes everywhere: `datetime.now(timezone.utc)`. Store UTC, convert for display. |
| 14 | `save_upload` | Opens in **text mode** (`"w"`) and writes `bytes` → `TypeError`. Text mode also means platform newline translation and locale encoding. | `open(path, "wb")`. Also: write to a temp file + `os.replace` so readers never see half a file. |
| 15 | `chunk` | **Off by one**: `range(0, len(lst) - size, size)` drops the last chunk; `chunk([1, 2, 3], 3) == []`. | `range(0, len(lst), size)`; or `itertools.batched` (3.12+). |
| 16 | `merge_tags` | `tags = a` doesn't copy: **`extend` mutates the caller's list**. | `tags = [*a, *b]`. |
| 17 | `merge_tags` | `list(set(...))` **loses order**, and for strings the order changes between runs (hash randomisation) → flaky tests and diffs. | `list(dict.fromkeys([*a, *b]))` keeps first-seen order. |
| 18 | `export_csv` | Hand-made CSV: a customer named `Smith, John` or with a newline/quote breaks the row. Also CSV injection (`=HYPERLINK(...)` opened in Excel). `+=` on strings in a loop can be quadratic. | `csv.writer(io.StringIO())`; prefix cells starting with `= + - @` if the file goes to spreadsheets. |
| 19 | `average_order_value` | `ZeroDivisionError` for an empty list. | Decide the contract: return `None`/`Decimal(0)` or raise a clear error. `statistics.fmean` raises `StatisticsError`. |
| 20 | `find_orders` | The **connection is never closed** (leaks file handles; with SQLite also locks). Note: `with sqlite3.connect(...) as db:` only commits/rolls back — it does *not* close. | `contextlib.closing(sqlite3.connect(...))`, or a connection pool owned by the app. |
| 21 | `load_settings` | `open(path)` without `encoding=` uses the locale encoding: the same file reads differently on Windows/servers with `LANG=C`. (PEP 686 plans to make UTF-8 mode the default in 3.15; until then, be explicit.) | `open(path, encoding="utf-8")`. |

**Block on:** 1, 2, 3 (and 5 is a close fourth). Security bugs and "every
order is wrong" bugs before style.

**What interviewers listen for at middle level:** you explain the *mechanism*
(default evaluated at `def` time; class vs instance attribute lookup; shallow
copy) and give a concrete triggering input, not just "this looks wrong".
