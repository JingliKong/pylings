"""Terminal output: colours, progress bar, exercise list, result rendering."""
import os
import shutil
import sys

from . import runner


def _colour_enabled(stream=sys.stdout):
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    return hasattr(stream, "isatty") and stream.isatty()


COLOUR = _colour_enabled()


def _style(code):
    def apply(text):
        return f"\x1b[{code}m{text}\x1b[0m" if COLOUR else str(text)

    return apply


bold, dim = _style("1"), _style("2")
red, green, yellow, blue, cyan = _style("31"), _style("32"), _style("33"), _style("34"), _style("36")


def clear():
    if COLOUR:
        sys.stdout.write("\x1b[2J\x1b[H")
    else:
        sys.stdout.write("\n" * 2)
    sys.stdout.flush()


def width():
    return max(40, min(shutil.get_terminal_size((100, 30)).columns, 120))


def rule():
    return dim("─" * width())


def progress_bar(done, total):
    bar_width = max(10, width() - 30)
    filled = round(bar_width * done / total) if total else 0
    pct = round(100 * done / total) if total else 0
    bar = green("█" * filled) + dim("░" * (bar_width - filled))
    return f"Progress {bar} {done}/{total} ({pct}%)"


LEVEL_LABEL = {
    "warm-up": "Warm-up",
    "middle": "Middle",
    "middle+": "Middle+",
    "senior": "Senior",
    "staff": "Staff",
}


def level_tag(level):
    colour = {"warm-up": cyan, "middle": green, "middle+": yellow, "senior": red, "staff": blue}[level]
    return colour(f"[{LEVEL_LABEL[level]}]")


def exercise_list(exercises, state):
    current = state.current_exercise(exercises)
    lines, last_group = [], None
    for ex in exercises:
        group = LEVEL_LABEL[ex.level] + (f" · {ex.topic}" if ex.topic else "")
        if group != last_group:
            lines.append("")
            lines.append(bold(group))
            last_group = group
        if state.is_done(ex):
            mark = green("✓")
        elif current is not None and ex.name == current.name:
            mark = yellow("▶")
        else:
            mark = dim("·")
        review = dim("  (code review)") if ex.is_review else ""
        lines.append(f"  {mark} {ex.index + 1:>3}  {ex.name:<26} {dim(ex.path)}{review}")
    lines.append("")
    lines.append(f"{progress_bar(state.count_done(exercises), len(exercises))}")
    return "\n".join(lines)


def result_summary(ex, result):
    """One or more lines describing a test run."""
    if result.status == runner.PASS:
        msg = green(bold(f"✓ All {result.ran} tests pass!"))
        if not ex.is_warmup:
            msg += "\n  Before moving on, answer the Discussion questions at the end of the spec."
        return msg + "\n  Press " + bold("n") + " for the next exercise."
    if result.status == runner.NOT_STARTED:
        return yellow(f"· Not started yet: {result.broken} of {result.ran} tests are waiting for your code.") + \
            f"\n  Open {bold(ex.path)} and replace the `raise NotImplementedError` parts."
    if result.status == runner.TIMEOUT_STATUS:
        return red("✗ " + result.detail)
    if result.status == runner.ERROR:
        return red(f"✗ {ex.path} crashed before the tests could run:") + "\n\n" + result.detail
    return red(f"✗ {result.broken} of {result.ran} tests failing") + "\n\n" + result.detail


def hints_block(ex, shown, more="press h"):
    if not shown:
        return ""
    lines = [bold("Hints")]
    for i, hint in enumerate(ex.hints[:shown], 1):
        lines.append(f"  {i}. {hint}")
    if shown < len(ex.hints):
        lines.append(dim(f"  ({len(ex.hints) - shown} more: {more})"))
    return "\n".join(lines)
