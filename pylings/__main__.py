"""python3 -m pylings [command]"""
import argparse
import sys

from . import actions, catalog, runner, ui
from .state import State
from .watch import watch

DESCRIPTION = """\
A rustlings-style trainer: work through the exercises from easy to hard.
With no command, starts watch mode: it re-runs the current exercise
every time you save the file."""


def _pick(exercises, state, name):
    if name is None:
        ex = state.current_exercise(exercises)
        if ex is None:
            raise LookupError("every exercise is done; name one explicitly")
        return ex
    return catalog.find(exercises, name)


def cmd_run(args, root, exercises, state):
    ex = _pick(exercises, state, args.name)
    if ex.is_review:
        print(f"{ex.name} is a code review exercise: read {ex.path}, then "
              f"`python3 -m pylings done {ex.name}`.")
        return 0
    result = runner.run(ex, root)
    print(f"{ui.bold(ex.name)} {ui.level_tag(ex.level)}  {ex.path}\n")
    print(result.output.rstrip() if args.verbose else ui.result_summary(ex, result))
    if result.passed:
        state.mark_done(ex)
        state.save()
    return 0 if result.passed else 1


def cmd_hint(args, root, exercises, state):
    ex = _pick(exercises, state, args.name)
    if not ex.hints:
        print(f"{ex.name} has no hints.")
        return 0
    shown = len(ex.hints) if args.all else state.reveal_hint(ex)
    state.save()
    print(ui.hints_block(ex, shown, more=f"run `python3 -m pylings hint {ex.name}` again"))
    return 0


def cmd_list(args, root, exercises, state):
    print(ui.exercise_list(exercises, state))
    return 0


def cmd_check_all(args, root, exercises, state):
    passed = actions.check_all(root, exercises, state)
    return 0 if passed == sum(1 for ex in exercises if not ex.is_review) else 1


def cmd_reset(args, root, exercises, state):
    ex = catalog.find(exercises, args.name)
    ok, msg = actions.reset(root, ex, state)
    print(ui.green(msg) if ok else ui.red(msg))
    return 0 if ok else 1


def cmd_done(args, root, exercises, state):
    ex = catalog.find(exercises, args.name)
    if not ex.is_review:
        print(f"{ex.name} is done when its tests pass: `python3 -m pylings run {ex.name}`.")
        return 1
    state.mark_done(ex)
    state.save()
    print(ui.green(f"✓ {ex.name} marked done. Answer key: {ex.solution}"))
    return 0


def cmd_solution(args, root, exercises, state):
    ex = catalog.find(exercises, args.name)
    if not state.is_done(ex) and not args.force:
        print(ui.yellow(f"Finish {ex.name} first, or add --force if you're really stuck."))
        return 1
    print(ex.solution)
    return 0


def cmd_dev_check(args, root, exercises, state):
    return 1 if actions.dev_check(root, exercises) else 0


def cmd_watch(args, root, exercises, state):
    watch(root, exercises, state)
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="python3 -m pylings", description=DESCRIPTION,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command")
    sub.add_parser("watch", help="watch mode (the default)").set_defaults(fn=cmd_watch)

    s = sub.add_parser("run", help="run one exercise's tests once")
    s.add_argument("name", nargs="?", help="exercise name or unique prefix (default: current)")
    s.add_argument("-v", "--verbose", action="store_true", help="print the full unittest output")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("hint", help="show the next hint")
    s.add_argument("name", nargs="?")
    s.add_argument("--all", action="store_true", help="show every hint at once")
    s.set_defaults(fn=cmd_hint)

    sub.add_parser("list", help="list exercises and progress").set_defaults(fn=cmd_list)
    sub.add_parser("check-all", help="run every exercise and update progress").set_defaults(fn=cmd_check_all)

    s = sub.add_parser("reset", help="restore an exercise file from git")
    s.add_argument("name")
    s.set_defaults(fn=cmd_reset)

    s = sub.add_parser("done", help="mark a code review exercise as done")
    s.add_argument("name")
    s.set_defaults(fn=cmd_done)

    s = sub.add_parser("solution", help="print the path of the reference solution")
    s.add_argument("name")
    s.add_argument("--force", action="store_true", help="show it even if you haven't finished")
    s.set_defaults(fn=cmd_solution)

    sub.add_parser("dev-check", help="maintainers: stubs fail, solutions pass").set_defaults(fn=cmd_dev_check)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    fn = getattr(args, "fn", cmd_watch)
    root = catalog.ROOT
    try:
        exercises = catalog.load(root)
        state = State(root)
        return fn(args, root, exercises, state)
    except (catalog.CatalogError, LookupError) as e:
        print(ui.red(f"error: {e}"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
