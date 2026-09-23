#!/usr/bin/env python3
"""Defect linter for chapters/*/README.md.

Catches what the LaTeX conversion tends to leave behind and what breaks one of the
three renderers (GitHub, the Jekyll site, the xelatex PDF):

  latex      a \\command outside code and math - a macro pandoc did not know
  bullet     an empty list item ("- - x"), the remains of seminar's blank-bullet trick
  math-space a $...$ span with whitespace just inside a delimiter, which pandoc's
             gfm reader then does not treat as math
  math-brace \\{ or \\} inside math, which kramdown turns into a bare brace
  html       raw HTML, which the LaTeX writer drops from the PDF
  image      an image whose file does not exist
  front      missing or inconsistent front matter (layout / chapter / prev / next)
  liquid     body not wrapped in <!-- {% raw %} --> ... <!-- {% endraw %} -->, so C code
             such as {{'a','b'}} would break the Jekyll build

Usage: tools/lint.py [--strict] [files...]   (--strict: exit 1 on any finding)
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def strip_code(text):
    """Blank out fenced blocks and code spans, keeping line numbers intact."""
    text = re.sub(r"^[ \t]*```.*?^[ \t]*```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.M | re.S)
    return re.sub(r"`[^`\n]+`", "``", text)


def check(path, chapters):
    findings = []
    raw = open(path, encoding="utf-8").read()
    text = strip_code(raw)
    lines = text.split("\n")

    def add(kind, lineno, msg):
        findings.append(f"{os.path.relpath(path, ROOT)}:{lineno}: [{kind}] {msg}")

    for i, line in enumerate(lines, 1):
        nomath = re.sub(r"\$\$.+?\$\$|\$[^$]+\$", "", line)
        for m in re.finditer(r"\\[a-zA-Z]+", nomath):
            add("latex", i, m.group(0))
        if re.match(r"\s*[-*] [-*] ", line):
            add("bullet", i, line.strip()[:60])
        for m in re.finditer(r"(?<!\$)\$(?!\$)([^$]+)\$(?!\$)", line):
            if m.group(1) != m.group(1).strip():
                add("math-space", i, m.group(0)[:60])
        for m in re.finditer(r"\$[^$]+\$", line):
            if re.search(r"\\[{}]", m.group(0)):
                add("math-brace", i, m.group(0)[:60])
        if re.search(r"<(?!!--)[a-zA-Z/][^>]*>", nomath) and "<a id=" not in nomath:
            add("html", i, line.strip()[:60])
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", line):
            if not os.path.exists(os.path.join(os.path.dirname(path), m.group(1))):
                add("image", i, m.group(1))

    if "chapters" in path and not ("<!-- {% raw %} -->" in raw and raw.rstrip().endswith("<!-- {% endraw %} -->")):
        add("liquid", 1, "chapter body is not wrapped in raw tags")

    slug = os.path.basename(os.path.dirname(path))
    if slug in chapters:
        n = chapters.index(slug)
        fm = re.match(r"---\n(.*?)\n---\n", raw, re.S)
        meta = dict(l.split(": ", 1) for l in fm.group(1).split("\n")) if fm else {}
        want = {"layout": "chapter", "chapter": str(n),
                "prev": chapters[n - 1] if n else None,
                "next": chapters[n + 1] if n + 1 < len(chapters) else None}
        for k, v in want.items():
            if meta.get(k) != v:
                add("front", 1, f"{k}: expected {v!r}, found {meta.get(k)!r}")
    return findings


def main(argv):
    strict = "--strict" in argv
    files = [a for a in argv if not a.startswith("--")]
    chapters = sorted(os.path.basename(os.path.dirname(p))
                      for p in glob.glob(os.path.join(ROOT, "chapters", "*", "README.md")))
    if not files:
        files = [os.path.join(ROOT, "chapters", c, "README.md") for c in chapters]
    findings = [f for p in files for f in check(p, chapters)]
    print("\n".join(findings) if findings else f"lint: {len(files)} files clean")
    return 1 if strict and findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
