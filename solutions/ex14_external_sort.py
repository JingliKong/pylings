"""Reference solution for exercises/ex14_external_sort.py."""
import contextlib
import heapq
import itertools
import os
import tempfile
from pathlib import Path


def _strip_newline(line):
    return line[:-1]


def external_sort(src, dst, *, max_lines, key=None, fan_in=16, tmp_dir=None):
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")
    if fan_in < 2:
        raise ValueError("fan_in must be >= 2")
    src, dst = Path(src), Path(dst)

    # Lines are stored newline-terminated but compared without the "\n":
    # otherwise "a\tb\n" < "a\n" because "\t" (9) sorts before "\n" (10).
    sort_key = _strip_newline if key is None else (lambda line: key(line[:-1]))

    with tempfile.TemporaryDirectory(dir=tmp_dir) as work:  # removed on success or error
        work = Path(work)
        names = (work / f"run-{i:06d}" for i in itertools.count())
        runs, count = [], 0

        # Pass 0: sorted runs of at most max_lines lines.
        with open(src, encoding="utf-8") as f:
            for batch in itertools.batched(f, max_lines):
                chunk = [line if line.endswith("\n") else line + "\n" for line in batch]
                chunk.sort(key=sort_key)  # list.sort is stable
                count += len(chunk)
                run = next(names)
                run.write_text("".join(chunk), encoding="utf-8")
                runs.append(run)

        # Intermediate passes: merge *consecutive* groups so ties keep their
        # original relative order (heapq.merge favours earlier inputs).
        while len(runs) > fan_in:
            merged = []
            for i in range(0, len(runs), fan_in):
                group = runs[i:i + fan_in]
                if len(group) == 1:
                    merged.append(group[0])
                    continue
                out_path = next(names)
                with open(out_path, "w", encoding="utf-8") as out:
                    _merge_into(group, out, sort_key)
                for path in group:
                    path.unlink()
                merged.append(out_path)
            runs = merged

        # Final pass: write next to dst, then atomically swap it in.
        fd, tmp_out = tempfile.mkstemp(dir=dst.parent, prefix=f".{dst.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                _merge_into(runs, out, sort_key)
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp_out, dst)
        except BaseException:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(tmp_out)
            raise
    return count


def _merge_into(paths, out, sort_key):
    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(p, encoding="utf-8")) for p in paths]
        out.writelines(heapq.merge(*files, key=sort_key))
