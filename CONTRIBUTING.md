# Contributing

Thanks for helping out. New exercises, better hints, bug fixes and interview questions are all welcome.

The project needs Python 3.14 and nothing else. Please keep it that way: standard library only.

## Before you open a PR

Run these from the repo root:

```bash
python3 -m pylings dev-check
```

```bash
SOLUTIONS=1 python3 -m unittest discover -s tests
```

```bash
python3 -m unittest discover -s pylings/tests
```

`dev-check` confirms that every unsolved exercise fails and every reference solution passes.

Don't commit your own answers in `exercises/`. To restore a file, run `python3 -m pylings reset <name>`.

## Adding an exercise

Every exercise has a file to edit, a reference solution with the same layout, and an entry in `pylings.toml`.

### Warm-up

A short "fix this" task, with its tests in the same file.

1. Add `exercises/0_warmups/<NN_topic>/<name>.py`, named like `strings1.py`. Give it broken code above the `Tests` divider and `unittest` tests below it.
2. Add the fixed version at the same path under `solutions/`. Keep the tests identical, and explain the fix in the docstring.

### Interview exercise

A longer task for the Middle to Staff levels.

1. Add `exercises/<level_folder>/exNN_name.py`, using the next free number. The docstring holds the level, time box, requirements and **Discussion** questions. Function bodies are `raise NotImplementedError`.
2. Add the full implementation at the same path under `solutions/`.
3. Add `tests/test_exNN_name.py`, and load the code with `from _loader import load` so the tests can run against either folder.

For a code review exercise, set `mode = "review"` in the catalog, leave out `test`, and write the answer key as `solutions/<level_folder>/exNN_name.md`.

### Catalog entry

Add the entry to `pylings.toml` where it belongs in the easy-to-hard order:

```toml
[[exercises]]
name = "ex21_example"
level = "senior"          # warm-up | middle | middle+ | senior | staff
path = "exercises/3_senior/ex21_example.py"
test = "tests/test_ex21_example.py"
solution = "solutions/3_senior/ex21_example.py"
hints = [
  "Start with a nudge.",
  "Each hint should give away a little more than the last.",
]
```

Warm-ups also set `topic`, and their `test` is the same file as `path`.

Update the counts and exercise table in `README.md` if they change.

## Pull requests

- Keep each PR to one exercise or one fix.
- Write commit subjects in the imperative, like `Add rate limiter hints`.
- Test behaviour and edge cases, and don't depend on one particular implementation.
