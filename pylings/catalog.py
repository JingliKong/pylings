"""The ordered list of exercises, loaded from pylings.toml."""
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_FILE = "pylings.toml"
LEVELS = ("warm-up", "middle", "middle+", "senior", "staff")
MODES = ("test", "review")


class CatalogError(Exception):
    pass


@dataclass(frozen=True)
class Exercise:
    index: int  # 0-based position in the catalog
    name: str
    level: str
    path: str  # the file the learner edits
    solution: str
    hints: tuple[str, ...]
    mode: str = "test"  # "review": read-only code review, no tests
    test: str | None = None  # file that runs the tests
    topic: str = ""

    @property
    def is_review(self):
        return self.mode == "review"

    @property
    def is_warmup(self):
        return self.level == "warm-up"

    def solution_test(self):
        """The file to run to check the reference solution, and whether SOLUTIONS=1 is needed."""
        if self.is_warmup:
            return self.solution, False  # warm-up solutions carry their own tests
        return self.test, True  # tests/_loader.py switches to solutions/ on SOLUTIONS=1

    def watched_files(self):
        return [p for p in (self.path, self.test) if p]


def load(root=ROOT):
    path = Path(root) / CATALOG_FILE
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CatalogError(f"{path} not found. Run pylings from the repository root.") from None
    except tomllib.TOMLDecodeError as e:
        raise CatalogError(f"{path}: {e}") from e

    exercises, seen = [], set()
    for i, raw in enumerate(data.get("exercises", [])):
        try:
            ex = Exercise(
                index=i,
                name=raw["name"],
                level=raw["level"],
                path=raw["path"],
                solution=raw["solution"],
                hints=tuple(raw.get("hints", ())),
                mode=raw.get("mode", "test"),
                test=raw.get("test"),
                topic=raw.get("topic", ""),
            )
        except KeyError as e:
            raise CatalogError(f"exercise #{i + 1} is missing the {e} field") from None
        problems = []
        if ex.name in seen:
            problems.append("duplicate name")
        if ex.level not in LEVELS:
            problems.append(f"unknown level {ex.level!r}")
        if ex.mode not in MODES:
            problems.append(f"unknown mode {ex.mode!r}")
        if ex.mode == "test" and not ex.test:
            problems.append("test mode needs a `test` file")
        for rel in (ex.path, ex.solution, ex.test):
            if rel and not (Path(root) / rel).is_file():
                problems.append(f"missing file {rel}")
        if problems:
            raise CatalogError(f"{ex.name}: " + "; ".join(problems))
        seen.add(ex.name)
        exercises.append(ex)
    if not exercises:
        raise CatalogError(f"{path} lists no exercises")
    return exercises


def find(exercises, query):
    """Look up by exact name, else by unique prefix ("ex05", "strings")."""
    for ex in exercises:
        if ex.name == query:
            return ex
    matches = [ex for ex in exercises if ex.name.startswith(query)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise LookupError(f"no exercise called {query!r}. Try `python3 -m pylings list`.")
    names = ", ".join(ex.name for ex in matches[:8])
    raise LookupError(f"{query!r} is ambiguous: {names}{', ...' if len(matches) > 8 else ''}")
