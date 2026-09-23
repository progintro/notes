#!/usr/bin/env python3
"""Rewrite chapter math for kramdown, in place, just before the Jekyll build.

The chapters write inline math as $x$, which is what GitHub and pandoc's gfm reader
understand. kramdown (the Pages Markdown engine) only knows $$x$$: to it a single $
is plain text, so it goes on to read the underscores in $a_1 + b_2$ as emphasis and
the backslashes in $\\{$ as escapes, and MathJax is handed a mangled formula.
kramdown treats $$x$$ inside a paragraph as inline math, so doubling the delimiters
is all it takes.

This runs in CI on a throwaway checkout (see .github/workflows/pages.yml), so the
committed Markdown keeps the portable form. Do not run it in a working tree you
intend to commit from.

Usage: tools/site-prep.py [files...]   (default: chapters/*/README.md)
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INLINE = re.compile(r"(?<![$\\])\$(?![$\s])([^$\n]+?)(?<![\s\\])\$(?!\$)")


def convert_line(line):
    # only outside code spans
    parts = re.split(r"(`[^`\n]+`)", line)
    return "".join(p if p.startswith("`") else INLINE.sub(r"$$\1$$", p) for p in parts)


def convert(text):
    out, fenced = [], False
    for line in text.split("\n"):
        if re.match(r"\s*```", line):
            fenced = not fenced
        out.append(line if fenced else convert_line(line))
    return "\n".join(out)


def main(argv):
    files = argv or sorted(glob.glob(os.path.join(ROOT, "chapters", "*", "README.md")))
    for path in files:
        text = open(path, encoding="utf-8").read()
        open(path, "w", encoding="utf-8").write(convert(text))
    print(f"site-prep: {len(files)} files")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
