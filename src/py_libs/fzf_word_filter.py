"""
fzf query filter (used via `--disabled --bind change:reload(...)`).

Each space-separated query term must either be a substring of the line
(same as fzf --exact) or a chain of substrings in order, each piece except
the last at least MIN_CHUNK chars (no letter-by-letter fuzzy matching):
    "resdow" -> "Restore from Downloads"  (res + dow)
    "rfd"    -> no match

Usage: python fzf_word_filter.py <query> <file with lines>
"""

import re
import sys

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
MIN_CHUNK = 3


def _chain(term: str, text: str, start: int) -> bool:
    if term in text[start:]:
        return True
    for n in range(len(term) - 1, MIN_CHUNK - 1, -1):
        pos = text.find(term[:n], start)
        if pos != -1 and _chain(term[n:], text, pos + n):
            return True
    return False


def matches(query: str, line: str) -> bool:
    text = ANSI_RE.sub("", line).lower()
    return all(_chain(t, text, 0) for t in query.lower().split())


def main() -> None:
    query, path = sys.argv[1], sys.argv[2]
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for line in lines:
        if matches(query, line):
            print(line)


if __name__ == "__main__":
    main()
