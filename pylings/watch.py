"""Watch mode: re-run the current exercise on every save, react to single key presses."""
import contextlib
import os
import select
import sys
import time
from pathlib import Path

from . import actions, runner, ui

POLL_SECONDS = 0.3

KEYS_HELP = (
    "n next · h hint · r re-run · l list · c check all · x reset · s solution · q quit"
)


@contextlib.contextmanager
def _cbreak(fd):
    """Deliver key presses one at a time, without Enter; always restore the terminal."""
    import termios
    import tty

    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _mtimes(root, ex):
    out = {}
    for rel in ex.watched_files():
        with contextlib.suppress(OSError):
            out[rel] = (Path(root) / rel).stat().st_mtime_ns
    return out


class Watcher:
    def __init__(self, root, exercises, state):
        self.root = root
        self.exercises = exercises
        self.state = state
        self.ex = state.current_exercise(exercises)
        self.result = None
        self.message = ""
        self.interactive = sys.stdin.isatty()

    # -- input ----------------------------------------------------------------------
    def read_key(self, timeout=None):
        """One key press (cbreak mode) or None on timeout."""
        fd = sys.stdin.fileno()
        ready, _, _ = select.select([fd], [], [], timeout)
        if not ready:
            return None
        data = os.read(fd, 1)
        if not data:
            raise EOFError
        return data.decode(errors="ignore").lower()

    def wait_for_key(self, prompt="Press any key to go back."):
        print("\n" + ui.dim(prompt), flush=True)
        if self.interactive:
            self.read_key()
        else:
            input()

    # -- drawing --------------------------------------------------------------------
    def run_current(self):
        if self.ex is None or self.ex.is_review:
            self.result = None
            return
        self.result = runner.run(self.ex, self.root)
        if self.result.passed and not self.state.is_done(self.ex):
            self.state.mark_done(self.ex)
            self.state.current = self.ex.name  # stay here until the learner presses n
            self.state.save()

    def render(self):
        ui.clear()
        total = len(self.exercises)
        print(ui.bold("pylings") + ui.dim(" · Python interview trainer"))
        print(ui.progress_bar(self.state.count_done(self.exercises), total))
        print(ui.rule())
        ex = self.ex
        print(f"{ui.bold(f'{ex.index + 1}/{total}  {ex.name}')}  {ui.level_tag(ex.level)}")
        print(f"Edit:  {ui.cyan(ex.path)}")
        print(ui.rule())
        if ex.is_review:
            done = self.state.is_done(ex)
            print(ui.yellow("Code review exercise: no tests."))
            print(f"  Read {ui.bold(ex.path)} and write down every bug you find:")
            print("  what goes wrong, an input that triggers it, and the fix.")
            if done:
                print(ui.green(f"\n✓ Marked done. Answer key: {ex.solution}"))
                print("  Press " + ui.bold("n") + " for the next exercise.")
            else:
                print("\n  When you're finished, press " + ui.bold("n") + " to mark it done and see the answer key.")
        elif self.result is not None:
            print(ui.result_summary(ex, self.result))
        hints = ui.hints_block(ex, self.state.hints_for(ex))
        if hints:
            print(ui.rule())
            print(hints)
        print(ui.rule())
        if self.message:
            print(self.message)
            self.message = ""
        print(ui.dim(KEYS_HELP), flush=True)

    # -- key handling -----------------------------------------------------------------
    def handle(self, key):
        """Returns False to quit."""
        ex = self.ex
        if key == "q":
            return False
        if key == "h":
            if not ex.hints:
                self.message = ui.dim("This exercise has no hints.")
            elif self.state.hints_for(ex) >= len(ex.hints):
                self.message = ui.dim("No more hints. Re-read the spec and the failing test.")
            else:
                self.state.reveal_hint(ex)
                self.state.save()
        elif key == "r":
            self.run_current()
        elif key == "n":
            if ex.is_review and not self.state.is_done(ex):
                self.state.mark_done(ex)
                self.state.current = ex.name
                self.state.save()
                return True  # show the answer key first; the next n moves on
            if not self.state.is_done(ex):
                self.message = ui.yellow("Not done yet: the tests have to pass first.")
                return True
            nxt = self.state.advance(self.exercises, ex)
            self.state.save()
            if nxt is None:
                return False
            self.ex = nxt
            self.run_current()
        elif key == "l":
            ui.clear()
            print(ui.exercise_list(self.exercises, self.state))
            self.wait_for_key()
        elif key == "c":
            ui.clear()
            actions.check_all(self.root, self.exercises, self.state)
            self.ex = self.state.current_exercise(self.exercises) or ex
            self.wait_for_key()
            self.run_current()
        elif key == "x":
            print(ui.yellow(f"\nReset {ex.path} to the original? Your changes will be lost. [y/N] "),
                  end="", flush=True)
            answer = self.read_key() if self.interactive else input().strip().lower()[:1]
            if answer == "y":
                ok, msg = actions.reset(self.root, ex, self.state)
                self.message = ui.green(msg) if ok else ui.red(msg)
                self.run_current()
            else:
                self.message = ui.dim("Reset cancelled.")
        elif key == "s":
            if self.state.is_done(ex):
                self.message = f"Solution: {ui.cyan(ex.solution)}"
            else:
                self.message = ui.yellow("Finish the exercise first. (Stuck? `python3 -m pylings solution "
                                         f"{ex.name} --force`)")
        return True

    # -- main loops -------------------------------------------------------------------
    def loop(self):
        if self.ex is None:
            print(ui.green(ui.bold("🎉 Every exercise is done. Well played!")))
            return
        self.run_current()
        if self.interactive:
            with _cbreak(sys.stdin.fileno()):
                self._interactive_loop()
        else:
            self._line_loop()
        if self.state.current_exercise(self.exercises) is None:
            print(ui.green(ui.bold("\n🎉 Every exercise is done. Well played!")))

    def _interactive_loop(self):
        self.render()
        seen = _mtimes(self.root, self.ex)
        while True:
            key = self.read_key(POLL_SECONDS)
            if key is not None:
                current = self.ex
                if not self.handle(key):
                    break
                if self.ex is not current:
                    seen = _mtimes(self.root, self.ex)
                self.render()
                continue
            now = _mtimes(self.root, self.ex)
            if now != seen:
                time.sleep(0.05)  # let the editor finish writing the file
                seen = _mtimes(self.root, self.ex)
                self.run_current()
                self.render()

    def _line_loop(self):
        """Fallback when stdin is not a terminal: one command per line, Enter re-runs."""
        while True:
            self.render()
            try:
                line = input("> ").strip().lower()
            except EOFError:
                break
            key = line[:1] or "r"
            if not self.handle(key):
                break


def watch(root, exercises, state):
    try:
        Watcher(root, exercises, state).loop()
    except KeyboardInterrupt:
        print()
