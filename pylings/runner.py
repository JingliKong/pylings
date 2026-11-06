"""Run an exercise's tests in a subprocess and make sense of unittest's output."""
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass

TIMEOUT = 60
DETAIL_LINES = 25

PASS, FAIL, NOT_STARTED, ERROR, TIMEOUT_STATUS = "pass", "fail", "not_started", "error", "timeout"

_RAN = re.compile(r"^Ran (\d+) tests? in ", re.M)
_FAILED = re.compile(r"^FAILED \(([^)]*)\)\s*$", re.M)
_OK = re.compile(r"^OK\b", re.M)
_SEP_EQ = "=" * 70
_SEP_DASH = "-" * 70


@dataclass
class Block:
    kind: str  # "FAIL" or "ERROR"
    header: str  # e.g. "FAIL: test_x (module.Test.test_x)"
    body: str  # the traceback

    @property
    def exception_line(self):
        lines = [line for line in self.body.splitlines() if line.strip()]
        return lines[-1] if lines else ""

    @property
    def not_implemented(self):
        return self.kind == "ERROR" and self.exception_line.startswith("NotImplementedError")


@dataclass
class Result:
    status: str
    ran: int = 0
    failures: int = 0
    errors: int = 0
    output: str = ""
    detail: str = ""
    duration: float = 0.0

    @property
    def passed(self):
        return self.status == PASS

    @property
    def broken(self):
        return self.failures + self.errors


def parse_blocks(output):
    """Split unittest's report into its FAIL/ERROR blocks."""
    end = output.rfind("\n" + _SEP_DASH + "\nRan ")
    text = output[:end] if end != -1 else output
    blocks = []
    for chunk in text.split(_SEP_EQ + "\n")[1:]:
        header, _, rest = chunk.partition("\n")
        kind = header.split(":", 1)[0]
        if kind not in ("FAIL", "ERROR"):
            continue
        body = rest.split(_SEP_DASH + "\n", 1)[-1]
        blocks.append(Block(kind, header.strip(), body.rstrip()))
    return blocks


def _trim(text, limit=DETAIL_LINES):
    lines = text.rstrip().splitlines()
    if len(lines) <= limit:
        return "\n".join(lines)
    return "\n".join(["  ..."] + lines[-(limit - 1):])


def parse(output, returncode, duration=0.0):
    ran_match = _RAN.search(output)
    if ran_match is None:
        # The file crashed before unittest could report: syntax error, import error,
        # an exception at module level...
        return Result(ERROR, output=output, detail=_trim(output), duration=duration)
    ran = int(ran_match.group(1))
    failures = errors = 0
    failed = _FAILED.search(output)
    if failed:
        for part in failed.group(1).split(","):
            key, _, value = part.strip().partition("=")
            if key == "failures":
                failures = int(value)
            elif key == "errors":
                errors = int(value)
    if returncode == 0 and _OK.search(output) and ran > 0:
        return Result(PASS, ran, 0, 0, output, "", duration)
    if ran == 0:
        return Result(ERROR, 0, 0, 0, output, "No tests ran.\n" + _trim(output), duration)

    blocks = parse_blocks(output)
    if blocks and all(b.not_implemented for b in blocks):
        return Result(NOT_STARTED, ran, failures, errors, output, "", duration)
    # Show the first real problem; a NotImplementedError is less interesting than an assertion.
    interesting = [b for b in blocks if not b.not_implemented] or blocks
    detail = ""
    if interesting:
        first = interesting[0]
        detail = first.header + "\n" + _trim(first.body, DETAIL_LINES - 1)
    elif output.strip():
        detail = _trim(output)
    return Result(FAIL, ran, failures, errors, output, detail, duration)


def run_file(root, test_file, *, solutions=False, timeout=TIMEOUT):
    env = dict(os.environ)
    env.pop("SOLUTIONS", None)
    if solutions:
        env["SOLUTIONS"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"  # don't litter the learner's folders with __pycache__
    env.setdefault("PYTHONIOENCODING", "utf-8")
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, test_file],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        partial = e.stdout or b""
        partial += e.stderr or b""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", "replace")
        detail = f"The tests did not finish within {timeout} s: an infinite loop or a deadlock?"
        if partial.strip():
            detail += "\n" + _trim(partial)
        return Result(TIMEOUT_STATUS, output=partial, detail=detail, duration=time.perf_counter() - t0)
    return parse(proc.stdout + proc.stderr, proc.returncode, time.perf_counter() - t0)


def run(ex, root, *, timeout=TIMEOUT):
    """Run the learner's version of an exercise."""
    return run_file(root, ex.test, timeout=timeout)


def run_solution(ex, root, *, timeout=TIMEOUT):
    test_file, solutions = ex.solution_test()
    return run_file(root, test_file, solutions=solutions, timeout=timeout)
