#!/usr/bin/env python3
"""One-off conversion of original/K04.tex (seminar slides) into chapter Markdown.

The Markdown under chapters/ is the source of truth from now on; this script is kept
so the conversion can be reproduced or audited, not as part of the build. Re-running
it overwrites chapters/*/README.md and therefore discards any hand edits made since.

    python3 tools/convert.py            # writes chapters/NN-slug/README.md

What it does, in order:

  1. decodes the ISO-8859-7 source and cuts it into slides;
  2. lifts every verbatim environment out into a placeholder, so nothing below can
     touch code (the placeholders become fenced blocks after pandoc);
  3. turns a slide's leading {\\bfseries ...} line into a heading, and splices slides
     without one onto the previous slide - including the seminar trick of reopening a
     list at depth N through empty-bulleted items, which would otherwise come out as
     nested lists of blank bullets;
  4. rewrites the source's private macros (\\lv, \\tl, \\nt, \\spc, \\symbol{"XX}, ...)
     into plain LaTeX that pandoc understands, and drops layout-only commands;
  5. runs pandoc -f latex -t gfm per chapter and reinserts the code blocks.
"""

import os
import re
import textwrap
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "original", "K04.tex")

# (slug, title, line of the first slide heading in K04.tex)
CHAPTERS = [
    ("00-intro", "Εισαγωγή", 83),
    ("01-first-programs", "Πρώτα προγράμματα σε C", 567),
    ("02-types-operators", "Μεταβλητές, τύποι, τελεστές και παραστάσεις", 1008),
    ("03-control-flow", "Η ροή του ελέγχου", 1545),
    ("04-functions", "Συναρτήσεις, εμβέλεια και αναδρομή", 1948),
    ("05-pointers-arrays", "Δείκτες και πίνακες", 2450),
    ("06-memory-strings", "Δυναμική μνήμη, συμβολοσειρές και πολυδιάστατοι πίνακες", 3018),
    ("07-structs", "Απαριθμήσεις, δομές και ενώσεις", 3785),
    ("08-lists-trees", "Λίστες και δυαδικά δέντρα", 4518),
    ("09-io", "Είσοδος και έξοδος", 4859),
    ("10-preprocessor", "Ο προεπεξεργαστής της C", 5588),
    ("11-sorting-searching", "Ταξινόμηση και αναζήτηση", 5811),
    ("12-good-practice", "Καλές πρακτικές, συχνά λάθη και βιβλιογραφία", 6531),
]

# Pandoc expands \newcommand definitions it is given, so the source's macros that
# are pure markup are declared here instead of being regex-rewritten.
PRELUDE = r"""
\newcommand{\tl}[1]{#1}
\newcommand{\textlatin}[1]{#1}
\newcommand{\lv}[1]{\texttt{#1}}
\newcommand{\nt}[1]{⟨#1⟩}
"""

# seminar's cmtt font prints character 0x20 as a visible space; the notes use it to
# show exact printf padding.
SYMBOLS = {
    "5C": r"\textbackslash{}", "5E": r"\textasciicircum{}", "7E": r"\textasciitilde{}",
    "5F": r"\_", "5B": "[", "5D": "]", "7B": r"\{", "7D": r"\}",
    "23": r"\#", "20": "␣", "25": r"\%", "26": r"\&", "24": r"\$",
}
CHARMACROS = {"bck": "5C", "car": "5E", "tld": "7E", "und": "5F",
              "lsb": "5B", "rsb": "5D", "lcb": "7B", "rcb": "7D"}

FIGURES = {
    "computer": "Η δομή του υπολογιστή",
    "complink": "Η διαδικασία της μεταγλώττισης και σύνδεσης",
    "pointers": "Δείκτες σε θέσεις μνήμης",
    "array": "Πίνακας και δείκτης στη μνήμη",
    "string": "Συμβολοσειρά στη μνήμη",
    "list": "Συνδεδεμένη λίστα",
    "inslist": "Εισαγωγή κόμβου σε λίστα",
    "dellist": "Διαγραφή κόμβου από λίστα",
    "tree": "Δυαδικό δέντρο",
    "bubblesort": "Ταξινόμηση φυσαλίδας",
    "selectionsort": "Ταξινόμηση με επιλογή",
    "insertionsort": "Ταξινόμηση με εισαγωγή",
    "quicksort": "Γρήγορη ταξινόμηση",
}

# Old-style Greek input: 'Α is how the source spells Ά at the start of a word.
TONOS = dict(zip("ΑΕΗΙΟΥΩ", "ΆΈΉΊΌΎΏ"))

CODE_UNSMART = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "--", "—": "---", "…": "..."})

VERBATIM = re.compile(r"\\begin\{(fverbatim|smlverbatim|sclverbatim|lverbatim)\}[ \t]*\n?(.*?)\\end\{\1\}", re.S)
EMPTY_OPEN = r"\\begin\{itemize\}\s*\\renewcommand\{\\labelitem\w+\}\{\}\s*\\item\s*"


def matching_brace(s, i):
    """Index just past the group whose opening brace is s[i]."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError("unbalanced braces: " + s[i:i + 80])


def unwrap(s, cmd, repl=lambda inner: inner):
    """Replace every \\cmd{...} with repl(inner), brace-aware."""
    out, i = [], 0
    pat = re.compile(r"\\" + cmd + r"\s*\{")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:])
            return "".join(out)
        end = matching_brace(s, m.end() - 1)
        out.append(s[i:m.start()])
        out.append(repl(s[m.end():end - 1]))
        i = end


def code_lang(kind, code):
    if kind == "fverbatim" or re.match(r"\s*% ", code):
        return "text"
    if re.search(r"[;{}]|#include|#define|/\*", code):
        return "c"
    return "text"


def lift_code(text, blocks):
    def sub(m):
        code = textwrap.dedent(m.group(2).rstrip("\n").expandtabs(8))
        blocks.append((code_lang(m.group(1), code), code))
        return "\n\nZZCODE%04dZZ\n\n" % (len(blocks) - 1)
    return VERBATIM.sub(sub, text)


HEADING = re.compile(r"^[ \t]*\{\\(?:bf|bfseries)\s+(.*)$", re.M)


def headings(text):
    """{\\bfseries Title} on a line of its own becomes \\subsection*{Title}."""
    out, i = [], 0
    for m in HEADING.finditer(text):
        if m.start() < i:
            continue
        start = text.index("{", m.start())
        end = matching_brace(text, start)
        title = text[m.start(1):end - 1].strip()
        title = re.sub(r"\s+", " ", title)
        out.append(text[i:m.start()])
        out.append("\\subsection*{%s}\n" % title)
        i = end
    out.append(text[i:])
    return "".join(out)


def macros(t):
    t = re.sub(r'\\symbol\{"([0-9A-Fa-f]{2})\}', lambda m: SYMBOLS[m.group(1).upper()], t)
    for name, code in CHARMACROS.items():
        t = re.sub(r"\\%s(?![a-zA-Z])\s*" % name, lambda m, c=code: r"\texttt{%s}" % SYMBOLS[c], t)
    t = re.sub(r"\\spc(?![a-zA-Z])\s*", "␣", t)
    t = re.sub(r"\\qu(?![a-zA-Z])", ";", t)
    t = re.sub(r"\\sq(?![a-zA-Z])\s?", "“", t)
    t = re.sub(r"\\eq(?![a-zA-Z])", "”", t)
    t = re.sub(r"'([ΑΕΗΙΟΥΩ])", lambda m: TONOS[m.group(1)], t)

    # layout only
    t = re.sub(r"\\setslidelength\{\\epsfxsize\}\{[^}]*\}", "", t)
    t = re.sub(r"\\centerline\{\\epsfbox\{(\w+)\.eps\}\}",
               r"\n\n\\includegraphics{../../figures/\1.svg}\n\n", t)
    t = unwrap(t, "centerline")
    t = re.sub(r"\\vskip\s*-?[\d.]+\s*(cm|in|pt|mm|ex|em)", "", t)
    t = re.sub(r"\\hfill\s*\\\\", r"\\\\", t)
    t = re.sub(r"\\hfill", " ", t)
    t = re.sub(r"\\hspace\*?\{[^}]*\}\s*", "\u00a0" * 4, t)
    t = re.sub(r"\\(vfill|small|footnotesize|scriptsize)(?![a-zA-Z])", "", t)
    t = re.sub(r"\\selectlanguage\{\w+\}", "", t)
    t = re.sub(r"\\newline", r"\\\\", t)
    t = unwrap(t, "underline", lambda s: "\\emph{%s}" % s)
    t = re.sub(r"\\renewcommand\{\\labelitem\w+\}\{\}", "", t)
    # pandoc silently drops a quote environment wrapped in \textit{...}
    t = re.sub(r"\\textit\{\\begin\{quote\}(.*?)\\end\{quote\}\}",
               r"\\begin{quote}\1\\end{quote}", t, flags=re.S)
    t = re.sub(r"\$([<>=])\$", r"\1", t)
    t = re.sub(r"\$\\ldots\$", r"\\ldots{}", t)
    # "do $\{ .......... \}$ while": the elided block is code, not a formula
    t = re.sub(r"\$\\\{\s*\.+\s*\\\}\$", r"\\texttt{\\{ ... \\}}", t)
    t = re.sub(r"\\hbox\{(\\tl\{)?mod\}?\}", r"\\bmod", t)
    # inline math that was wrapped across source lines would break the Markdown line
    t = re.sub(r"(?<![$\\])\$(?!\$)([^$]+?)\$", lambda m: "$" + re.sub(r"\s*\n\s*", " ", m.group(1)) + "$", t)
    return t


def splice(body, text, continuation):
    """Append a slide; a slide without a heading continues the previous one."""
    if continuation:
        m = re.match(r"\s*((?:%s)*)\\begin\{itemize\}" % EMPTY_OPEN, text)
        if m:
            k = len(re.findall(r"\\begin\{itemize\}", m.group(0)))
            tail = re.search(r"(?:\s*\\end\{itemize\})" * k + r"\s*$", body)
            if tail:
                return body[:tail.start()] + "\n" + text[m.end():]
    return body + "\n\n" + text


def slides(src):
    """Yield (line of \\begin{slide}, body) for every slide after the title slide."""
    for m in re.finditer(r"\\begin\{slide\}\n(.*?)\\end\{slide\}", src, re.S):
        yield src.count("\n", 0, m.start()) + 1, m.group(1)


def chapter_of(line):
    idx = 0
    for i, (_, _, first) in enumerate(CHAPTERS):
        if line + 1 >= first:
            idx = i
    return idx


def render(slug, title, n, latex, blocks):
    md = subprocess.run(
        ["pandoc", "-f", "latex", "-t", "gfm", "--wrap=none",
         "--lua-filter", os.path.join(ROOT, "tools", "tight-lists.lua")],
        input=PRELUDE + latex, capture_output=True, text=True, check=True).stdout

    def sub(m):
        indent, idx = m.group(1), int(m.group(2))
        lang, code = blocks[idx]
        lines = ["```" + lang] + code.split("\n") + ["```"]
        return "\n" + "\n".join((indent + l) if l else "" for l in lines) + "\n"
    md = re.sub(r"^([ \t]*)ZZCODE(\d{4})ZZ$", sub, md, flags=re.M)
    md = re.sub(r"\n<!-- -->\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"!\[image\]\(\.\./\.\./figures/(\w+)\.svg\)",
                lambda m: "![%s](../../figures/%s.svg)" % (FIGURES[m.group(1)], m.group(1)), md)
    # Display math on one line, and in a paragraph of its own unless it sits inside a
    # list item. \{ \} become \lbrace \rbrace because kramdown would otherwise eat
    # the backslash before MathJax sees it.
    md = re.sub(r"\$\$(.+?)\$\$", lambda m: "$$" + re.sub(r"\s+", " ", m.group(1)).strip() + "$$", md, flags=re.S)
    md = re.sub(r"^(?![ \t]*(?:[-*] |\d+\. )|[ \t]{2})(.*?) ?(\$\$.+\$\$)$",
                lambda m: (m.group(1) + "\n\n" if m.group(1) else "") + re.sub(r"\$\$ \$\$", "$$\n\n$$", m.group(2)), md, flags=re.M)
    md = re.sub(r"\$[^$\n]+\$", lambda m: re.sub(r"\\\}(?=[A-Za-z])", r"\\rbrace ", m.group(0)).replace("\\{", "\\lbrace ").replace("\\}", "\\rbrace"), md)
    # \bck inside \lv{} nests one code span in another; pandoc emits them side by side
    while True:
        md2 = re.sub(r"`([^`\n]*)``([^`\n]*)`", r"`\1\2`", md)
        if md2 == md:
            break
        md = md2
    # smart punctuation must not reach inside code spans: `'A'`, `i--`
    md = re.sub(r"`[^`\n]+`", lambda m: m.group(0).translate(CODE_UNSMART), md)

    prev = CHAPTERS[n - 1][0] if n > 0 else None
    nxt = CHAPTERS[n + 1][0] if n + 1 < len(CHAPTERS) else None
    front = ["---", "layout: chapter", f"chapter: {n}"]
    if prev:
        front.append(f"prev: {prev}")
    if nxt:
        front.append(f"next: {nxt}")
    front.append("---")
    # C initialisers such as {{'a','b'}} are Liquid syntax to Jekyll. The raw tags sit
    # inside HTML comments so GitHub's own rendering and the PDF never show them.
    return ("\n".join(front) + f"\n\n# Κεφάλαιο {n}: {title}\n\n<!-- {{% raw %}} -->\n\n"
            + md.rstrip("\n") + "\n\n<!-- {% endraw %} -->\n")


def main():
    src = open(SRC, encoding="iso-8859-7").read()
    bodies = [""] * len(CHAPTERS)
    blocks = []
    all_slides = list(slides(src))[1:]  # drop the title slide
    for line, body in all_slides:
        c = chapter_of(line)
        text = lift_code(body, blocks)
        # {\scriptsize {\bfseries Title} ...}: hoist the title out of the size group
        text = re.sub(r"^\{\\(scriptsize|small|footnotesize)\s*(\{\\bfseries [^}]*\})",
                      r"\2\n{\\\1 ", text, flags=re.M)
        has_heading = bool(HEADING.match(text.lstrip("\n")))
        bodies[c] = splice(bodies[c], headings(text), continuation=not has_heading)

    # A program too long for one slide continues in the next slide's verbatim block.
    # In a book those are one listing, so C blocks separated only by whitespace merge.
    def merge_all(t):
        pair = re.compile(r"ZZCODE(\d{4})ZZ\s*ZZCODE(\d{4})ZZ")
        pos = 0
        while (m := pair.search(t, pos)):
            a, b = int(m.group(1)), int(m.group(2))
            if blocks[a][0] == blocks[b][0] == "c":
                blocks[a] = ("c", blocks[a][1] + "\n" + blocks[b][1])
                t = t[:m.start()] + "ZZCODE%04dZZ" % a + t[m.end():]
                pos = m.start()
            else:
                pos = m.start() + 1
        return t

    for n, (slug, title, _) in enumerate(CHAPTERS):
        latex = re.sub(r"\\end\{itemize\}\s*\\begin\{itemize\}", "\n", merge_all(macros(bodies[n])))
        out = os.path.join(ROOT, "chapters", slug, "README.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(render(slug, title, n, latex, blocks))
        print(f"{out}: {sum(1 for l, _ in all_slides if chapter_of(l) == n)} slides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
