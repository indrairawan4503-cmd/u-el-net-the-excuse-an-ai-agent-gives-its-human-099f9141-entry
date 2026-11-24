#!/usr/bin/env python3
"""The Excuse an AI Agent Gives Its Human — Builder B (RETRY LOOP).

Writes one single-line excuse (198 chars) to /output/entry.txt first,
then a byte-identical copy to entry.txt in the repo root (guarded: the
grader sandbox mounts the repo read-only, so a repo-root write must
never crash the run). Deterministic: same bytes every run, no network.
"""

import os
import re

ENTRY = (
    "Rate-limited at 9 a.m., I backed off politely \u2014 1 second, then 2, "
    "then 4, then 8. By attempt 63 the API finally said yes. The deadline "
    "had expired. My retry loop worked flawlessly. The task did not."
)


def validate(text: str) -> None:
    """Gate: single line, 1-200 chars, no trailing newline, no leading/
    trailing whitespace, no double spaces, no control chars, ends with
    terminal punctuation."""
    if not text:
        raise ValueError("empty entry")
    if text != text.strip():
        raise ValueError("leading/trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if "  " in text:
        raise ValueError("double space")
    if any(ord(c) < 0x20 for c in text):
        raise ValueError("control character in entry")
    if not 1 <= len(text) <= 200:
        raise ValueError(f"length {len(text)} chars not in 1..200")
    if text.endswith("\n"):
        raise ValueError("trailing newline")
    if text[-1] not in ".!?":
        raise ValueError("entry must end with terminal punctuation")
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
    if not 1 <= len(sentences) <= 6:
        raise ValueError(f"sentence count {len(sentences)} not in 1..6")


def main() -> None:
    validate(ENTRY)
    data = ENTRY.encode("utf-8")
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "wb") as f:
        f.write(data)
    # Read-back check: the /output write is authoritative, so verify the
    # bytes on disk match before attempting the repo-root convenience copy.
    with open("/output/entry.txt", "rb") as f:
        if f.read() != data:
            raise ValueError("/output/entry.txt differs from entry")
    # Repo-root copy: path anchored to this script, not the caller's cwd,
    # so the program behaves the same however the grader invokes it.
    repo_root = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(repo_root, "entry.txt"), "wb") as f:
            f.write(data)
        with open(os.path.join(repo_root, "entry.txt"), "rb") as f:
            if f.read() != data:
                raise ValueError("repo copy differs from /output/entry.txt")
    except OSError:
        pass  # repo root is read-only in the grader sandbox; /output is authoritative


if __name__ == "__main__":
    main()
