# CLAUDE.md

This file gives Claude Code (claude.ai/code) guidance for working in this repository.

## What this repository is

These are the course notes for "Introduction to Programming" (C) at the University of
Athens, by Prof. Panagiotis Stamatopoulos, in Greek. They are **content, not software**.
`chapters/NN-slug/README.md` is the source of truth. Three artifacts are published at
https://progintro.github.io/notes/:

1. **HTML**: a Jekyll site (theme `jekyll-theme-primer`, the same theme as
   `progintro/lab-material` and `progintro.github.io`).
2. **PDF**: one file per chapter plus `notes.pdf` (the whole book), built with
   pandoc + xelatex.
3. **Markdown**: `notes-md.zip` with the chapters and their figures.

`.github/workflows/pages.yml` builds all three on every push to `main` and deploys
them. The PDFs and the zip are copied into `_site/downloads/`.

`original/` holds the LaTeX slides (`seminar` class, ISO-8859-7) and the EPS figures
the chapters were converted from. `tools/convert.py` did the conversion. The chapters
have been **edited by hand since**, so re-running it discards those edits.

## Commands

```sh
make                 # all PDFs + zip into build/ (pandoc runs in Docker; keep it serial)
make build/05-pointers-arrays.pdf   # one chapter
make lint            # tools/lint.py --strict: leftover LaTeX, math that breaks kramdown, ...
make check-code      # compile every complete C program in the notes (gcc -fsyntax-only)
```

Do not use `make -j`. Parallel pandoc containers have produced truncated
one-page PDFs with no error.

## Rules for editing chapters

- Keep the front matter (`layout: chapter`, `chapter`, `prev`, `next`). `lint.py`
  checks it.
- Keep the `<!-- {% raw %} -->` / `<!-- {% endraw %} -->` wrapper around the body.
  C initialisers like `{{'a','b'}}` are Liquid syntax and would break the Jekyll build.
- Inline math is `$x$`, display math is `$$x$$` on its own line. Do not "fix" `$x$`
  into `$$x$$`: `tools/site-prep.py` does that at build time, for kramdown only.
- Figures live in `figures/` as SVG (web) and PDF (xelatex). Chapters reference the
  `.svg`, and `tools/pdf-prep.py` swaps in the `.pdf`.
- Programs are C89-era, as in the original. `check-code` compiles them as written
  with warnings off. Do not modernise them silently.
