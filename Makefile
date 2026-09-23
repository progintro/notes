# Build the downloadable artifacts from chapters/*/README.md:
#
#   build/NN-slug.pdf     one PDF per chapter
#   build/notes.pdf       the whole book: cover page, contents, continuous numbering
#   build/notes-md.zip    the Markdown sources plus figures
#
# pandoc and xelatex run in the same pinned image lab-material uses, so the two
# course sites typeset identically. `make PANDOC="pandoc"` runs a local pandoc
# instead (needs xelatex and the fonts below).

BUILD ?= build
IMAGE ?= ghcr.io/ethan42/pandoctex:20260825
PANDOC ?= docker run --rm -u $(shell id -u):$(shell id -g) -v $(CURDIR):/data -w /data \
	-e LANG=C.UTF-8 -e HOME=/tmp $(IMAGE) pandoc

CHAPTERS := $(sort $(wildcard chapters/*/README.md))
SLUGS := $(patsubst chapters/%/README.md,%,$(CHAPTERS))
CHAPTER_PDFS := $(SLUGS:%=$(BUILD)/%.pdf)
FIGURES := $(wildcard figures/*.pdf)
DEPS := tex/header.tex tools/pdf-prep.py $(FIGURES)

# The same typesetting flags for every PDF. -V babel-lang= and the \babelprovide in
# tex/header.tex work around pandoc 3.7's babel wiring; see lab-material/CLAUDE.md.
PDF_FLAGS = -f gfm+tex_math_dollars+raw_attribute -s --toc --toc-depth=2 \
	--pdf-engine=xelatex -H tex/header.tex \
	-V mainfont="Linux Libertine O" -V monofont="Noto Mono" -V fontsize=12pt \
	-V lang=el -V babel-lang= \
	-V colorlinks=true -V linkcolor=ditcharcoal -V urlcolor=ditcyan -V toccolor=ditcharcoal

all: $(CHAPTER_PDFS) $(BUILD)/notes.pdf $(BUILD)/notes-md.zip

$(BUILD):
	mkdir -p $(BUILD)

# The running header carries the chapter title, without its "Κεφάλαιο N:" prefix.
$(BUILD)/%.pdf: chapters/%/README.md $(DEPS) | $(BUILD)
	python3 tools/pdf-prep.py $< > $(BUILD)/$*.md
	$(PANDOC) $(BUILD)/$*.md $(PDF_FLAGS) \
		-V header-includes='\def\chaptitle{$(shell grep -m1 '^# ' $< | sed -e 's/^# //' -e 's/^[^:]*: //')}' \
		-o $@

$(BUILD)/notes.pdf: $(CHAPTERS) $(DEPS) tex/cover.tex | $(BUILD)
	python3 tools/pdf-prep.py --all > $(BUILD)/notes.md
	$(PANDOC) $(BUILD)/notes.md $(PDF_FLAGS) -H tex/cover.tex \
		-V header-includes='\def\chaptitle{Σημειώσεις}' \
		-o $@

$(BUILD)/notes-md.zip: $(CHAPTERS) $(wildcard figures/*.svg) | $(BUILD)
	rm -f $@
	zip -q -r $@ README.md chapters figures -x 'figures/*.pdf'

.PHONY: all lint check-code clean
lint:
	python3 tools/lint.py --strict

check-code:
	python3 tools/check-code.py

clean:
	rm -rf $(BUILD) _site
