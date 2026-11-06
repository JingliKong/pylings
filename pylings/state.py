"""Progress, stored in .pylings-state.json at the repository root."""
import json
import os
from pathlib import Path

STATE_FILE = ".pylings-state.json"


class State:
    def __init__(self, root):
        self.path = Path(root) / STATE_FILE
        self.done = set()
        self.hints_shown = {}
        self.current = None  # name of the exercise the learner is on
        self._load()

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (json.JSONDecodeError, OSError):
            return  # a corrupt state file must not lock the learner out; start fresh
        self.done = set(data.get("done", []))
        self.hints_shown = dict(data.get("hints_shown", {}))
        self.current = data.get("current")

    def save(self):
        data = {"done": sorted(self.done), "hints_shown": self.hints_shown, "current": self.current}
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)  # atomic: never a half-written state file

    # -- progress -----------------------------------------------------------------
    def is_done(self, ex):
        return ex.name in self.done

    def mark_done(self, ex):
        self.done.add(ex.name)

    def mark_pending(self, ex):
        self.done.discard(ex.name)

    def count_done(self, exercises):
        return sum(1 for ex in exercises if ex.name in self.done)

    def current_exercise(self, exercises):
        """The selected exercise if it isn't done yet, else the first one that isn't. None = all done."""
        by_name = {ex.name: ex for ex in exercises}
        ex = by_name.get(self.current)
        if ex is not None and not self.is_done(ex):
            return ex
        return next((e for e in exercises if not self.is_done(e)), None)

    def advance(self, exercises, after):
        """Select the next exercise that isn't done, searching forward from `after` and wrapping."""
        n = len(exercises)
        for step in range(1, n + 1):
            ex = exercises[(after.index + step) % n]
            if not self.is_done(ex):
                self.current = ex.name
                return ex
        self.current = None
        return None

    # -- hints ----------------------------------------------------------------------
    def hints_for(self, ex):
        return self.hints_shown.get(ex.name, 0)

    def reveal_hint(self, ex):
        """Show one more hint. Returns the number now shown (capped at the number of hints)."""
        shown = min(self.hints_for(ex) + 1, len(ex.hints))
        self.hints_shown[ex.name] = shown
        return shown
