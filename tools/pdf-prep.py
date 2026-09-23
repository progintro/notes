#!/usr/bin/env python3
"""Turn chapter Markdown into the Markdown the pandoc/xelatex pass reads.

The PDF is a different renderer from GitHub and the Pages site, and needs:

  * no Jekyll front matter - pandoc's gfm reader would print it as text;
  * figures as PDF rather than SVG (xelatex cannot include SVG), with paths relative
    to the repository root, which is where pandoc runs;
  * footnote labels unique across chapters, because the book concatenates them all
    and pandoc's gfm writer numbered each chapter's notes from 1.

Usage:
  tools/pdf-prep.py chapters/NN-slug/README.md > build/NN-slug.md    one chapter
  tools/pdf-prep.py --all > build/notes.md                            the whole book
"""

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def prepare(path):
    text = io.open(path, encoding="utf-8").read()
    if text.startswith("---\n"):
        text = text[text.index("\n---\n", 3) + 5:]
    text = re.sub(r"\]\((?:\.\./)+figures/(\w+)\.svg\)", r"](figures/\1.pdf)", text)
    slug = os.path.basename(os.path.dirname(path))[:2]
    text = re.sub(r"\[\^(\w+)\]", lambda m: "[^c%s-%s]" % (slug, m.group(1)), text)
    missing = [f for f in re.findall(r"\]\((figures/[^)]+)\)", text)
               if not os.path.exists(os.path.join(ROOT, f))]
    if missing:
        sys.exit(f"{path}: missing figures {missing}")
    return text.strip() + "\n"


def main(argv):
    if argv == ["--all"]:
        paths = sorted(glob.glob(os.path.join(ROOT, "chapters", "*", "README.md")))
        sys.stdout.write("\n\n".join(prepare(p) for p in paths))
    elif len(argv) == 1:
        sys.stdout.write(prepare(argv[0]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
