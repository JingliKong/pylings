"""Commands shared by the CLI and watch mode."""
import subprocess
from pathlib import Path

from . import runner, ui


def check_all(root, exercises, state, *, out=print):
    """Run every test exercise; mark passing ones done and failing ones pending."""
    out(ui.bold("Checking every exercise...\n"))
    passed = 0
    for ex in exercises:
        if ex.is_review:
            mark = ui.green("✓") if state.is_done(ex) else ui.dim("·")
            out(f"  {mark} {ex.name:<28} {ui.dim('code review: marked by hand')}")
            continue
        result = runner.run(ex, root)
        if result.passed:
            state.mark_done(ex)
            passed += 1
            out(f"  {ui.green('✓')} {ex.name}")
        else:
            state.mark_pending(ex)
            label = {runner.NOT_STARTED: "not started", runner.ERROR: "crashes",
                     runner.TIMEOUT_STATUS: "timed out"}.get(result.status, f"{result.broken} failing")
            out(f"  {ui.red('✗')} {ex.name:<28} {ui.dim(label)}")
    state.save()
    out("\n" + ui.progress_bar(state.count_done(exercises), len(exercises)))
    return passed


def reset(root, ex, state):
    """Restore the exercise file from git HEAD. Returns (ok, message)."""
    proc = subprocess.run(
        ["git", "show", f"HEAD:{ex.path}"], cwd=root, capture_output=True,
    )
    if proc.returncode != 0:
        return False, (f"Can't reset {ex.path}: it isn't committed to git yet. "
                       "Commit the original exercises first.")
    (Path(root) / ex.path).write_bytes(proc.stdout)
    state.mark_pending(ex)
    state.hints_shown.pop(ex.name, None)
    state.save()
    return True, f"{ex.path} restored to the original."


def dev_check(root, exercises, *, out=print):
    """Maintainer check: every stub must fail and every reference solution must pass."""
    problems = 0
    for ex in exercises:
        if ex.is_review:
            out(f"  {ui.dim('-')} {ex.name:<28} {ui.dim('review: nothing to run')}")
            continue
        stub = runner.run(ex, root)
        solution = runner.run_solution(ex, root)
        ok = not stub.passed and solution.passed
        problems += not ok
        if ok:
            out(f"  {ui.green('✓')} {ex.name:<28} stub {stub.status}, solution {solution.ran} tests pass")
        else:
            out(f"  {ui.red('✗')} {ex.name:<28} stub {stub.status}, solution {solution.status}")
            if not solution.passed:
                out(solution.detail)
            if stub.passed:
                out("    the unsolved exercise already passes its tests")
    out("")
    out(ui.green("dev-check OK") if not problems else ui.red(f"dev-check: {problems} problem(s)"))
    return problems
