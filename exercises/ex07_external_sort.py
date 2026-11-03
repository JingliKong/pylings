"""Exercise 07 — Sort a text file that does not fit in memory.

Time box: 45 min.  Classic external merge sort, but graded on the details
that bite in production: stability, bounded file descriptors, cleanup on
failure, atomic output.

    n = external_sort("huge.txt", "sorted.txt", max_lines=1_000_000, fan_in=64)

Requirements
------------
1. Never hold more than ``max_lines`` lines in memory while building runs.
2. Merge at most ``fan_in`` files at once (bounded open file descriptors);
   use multiple merge passes when there are more runs than ``fan_in``.
3. Output is exactly ``sorted(lines, key=key)`` where ``lines`` are the
   input lines WITHOUT their line endings — so the sort is stable, and
   ``key`` receives the line without its trailing newline.  Every output
   line ends with ``"\\n"``, including the last one, even if the input's
   last line had no newline.
4. Text is UTF-8.
5. Temporary files go under ``tmp_dir`` (default: system temp dir) and are
   removed on success AND on failure (e.g. when ``key`` raises).
6. ``dst`` is replaced atomically: on failure, an existing ``dst`` keeps its
   old content and no partial file is left next to it.
7. Returns the number of lines.  ``max_lines < 1`` or ``fan_in < 2`` ->
   ``ValueError``.

Discussion
----------
- Why is comparing lines *with* their trailing "\\n" a bug?  Find an input
  where it changes the order.
- ``heapq.merge`` stability: which input wins on ties?  Does a multi-pass
  merge preserve stability?
- How would you parallelise this?  What's the I/O cost of each pass, and
  how do you pick ``fan_in``?
"""


def external_sort(src, dst, *, max_lines, key=None, fan_in=16, tmp_dir=None):
    raise NotImplementedError
