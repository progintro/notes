#!/usr/bin/env python3
"""Compile every complete C program in the notes.

The programs in chapters/*/README.md were copied out of LaTeX verbatim blocks; this
is the check that none of them was damaged on the way (a lost backslash, a smart
quote, a dropped line). A ```c block counts as a complete program when it defines
main(); fragments are skipped. Each one goes through `gcc -fsyntax-only`, with
warnings off: the notes date from before C99 and are compiled as written.

Usage: tools/check-code.py [--verbose]
"""

import glob
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FENCE = re.compile(r"^([ \t]*)```c\n(.*?)^\1```", re.M | re.S)
CC = os.environ.get("CC", "gcc")


def main(argv):
    verbose = "--verbose" in argv
    ok = bad = skipped = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "chapters", "*", "README.md"))):
        text = open(path, encoding="utf-8").read()
        for m in FENCE.finditer(text):
            indent = m.group(1)
            code = "\n".join(l[len(indent):] if l.startswith(indent) else l
                             for l in m.group(2).split("\n"))
            # "...." marks code elided on purpose
            if (not re.search(r"^\s*(int\s+)?main\s*\(", code, re.M)
                    or re.search(r"^\s*\.{3,}\s*$", code, re.M)):
                skipped += 1
                continue
            line = text.count("\n", 0, m.start()) + 1
            # macOS libc declares its own heapsort() in stdlib.h, with a different
            # signature from the one the searching program defines; glibc does not
            if sys.platform == "darwin":
                code = re.sub(r"\bheapsort\b", "notes_heapsort", code)
            with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as f:
                f.write(code)
            r = subprocess.run([CC, "-fsyntax-only", "-w", "-std=gnu89", f.name],
                               capture_output=True, text=True)
            os.unlink(f.name)
            where = f"{os.path.relpath(path, ROOT)}:{line}"
            if r.returncode == 0:
                ok += 1
                if verbose:
                    print(f"ok   {where}")
            else:
                bad += 1
                print(f"FAIL {where}\n{r.stderr.replace(f.name, where)}")
    print(f"check-code: {ok} programs compile, {bad} fail, {skipped} fragments skipped")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
