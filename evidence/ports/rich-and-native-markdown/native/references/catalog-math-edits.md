# Math, text marks, and edit notation

- Read this file when the input uses math, subscripts, highlights, edit proposals, emoji, or keys.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E16 Inline math

- **How:** use `$x$` where supported; GitHub/GitLab also accept dollar-backtick wrappers.
- **When:** a short formula belongs in prose.
- **Where:** inline.
- **Why:** preserve notation. kramdown uses `$$x$$` even inline; never assume one delimiter
  policy.

- **Sources:**

  - [GH-MATH](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)
  - [P-MATH](https://pandoc.org/demo/example33/8.13-math.html)
  - [MYST-OPT](https://myst-parser.readthedocs.io/en/stable/syntax/optional.html)
  - [KRAM](https://kramdown.gettalong.org/syntax.html)

## E17 Display math

- **How:** use a supported `$$` block or `math` fence; MyST can label dollar math with `(eq-id)` after
  its closing delimiter.
- **When:** an equation needs its own line.
- **Where:** block flow.
- **Why:** make the relation easy to read. Do not put `$$` inside a math fence unless required by its
  owner.

- **Sources:**

  - [GH-MATH](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)
  - [P-MATH](https://pandoc.org/demo/example33/8.13-math.html)
  - [MYST-OPT](https://myst-parser.readthedocs.io/en/stable/syntax/optional.html)

## E18 Other math delimiters

- **How:** enable supported `\(...\)`, `\[...\]`, doubled-backslash forms, or AMS environments
  such as `\begin{align}...\end{align}`.
- **When:** retaining a known math dialect.
- **Where:** inline/display positions.
- **Why:** preserve intended formula boundaries. Math is an embedded language; its commands are
  not separate Markdown primitives.

- **Sources:**

  - [P-EXT](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)
  - [MYST-OPT](https://myst-parser.readthedocs.io/en/stable/syntax/optional.html)

## E19 Subscript and superscript

- **How:** use allowed `<sub>n</sub>`/`<sup>2</sup>`, or `H~2~O`/`x^2^` in supporting dialects;
  Pandoc `short_subsuperscripts` also accepts `x^2` or `O~2`.
- **When:** simple indices or exponents matter.
- **Where:** inline.
- **Why:** keep notation clear. Paired forms need escaped spaces; use math for complex
  relations.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  - [P-INLINE](https://pandoc.org/demo/example33/8.12-inline-formatting.html)
  - [MATERIAL-F](https://squidfunk.github.io/mkdocs-material/reference/formatting/)

## E20 Highlight and insertion

- **How:** use `==marked==` where enabled; PyMdown `^^added^^` or allowed `<ins>added</ins>` marks
  insertion.
- **When:** a selected passage or added text matters.
- **Where:** inline.
- **Why:** retain that role. Insertion is not generic decorative underlining.

- **Sources:**

  - [P-INLINE](https://pandoc.org/demo/example33/8.12-inline-formatting.html)
  - [P-EXT](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)
  - [MATERIAL-F](https://squidfunk.github.io/mkdocs-material/reference/formatting/)
  - [OBS-SYNTAX](https://obsidian.md/help/syntax)

## E21 CriticMarkup

- **How:** use `{++add++}`, `{--delete--}`, `{~~old~>new~~}`, `{==mark==}`, `{>>comment<<}`.
- **When:** proposing edits.
- **Where:** review text.
- **Why:** distinguish proposals from accepted prose. Crossing blocks can break previews;
  accepting or rejecting changes is a separate action.

- **Sources:**

  - [CRITIC](https://facelessuser.github.io/pymdown-extensions/extensions/critic/)
  - [MMD7](https://fletcher.github.io/MultiMarkdown-7/docs/user.html)

## E22 GitLab inline diff

- **How:** use `{+add+}`/`[+add+]` and `{-remove-}`/`[-remove-]`.
- **When:** reviewing short changes.
- **Where:** inline.
- **Why:** show additions and removals. Match bracket type; this is not CriticMarkup.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## E23 Emoji and icon shortcode

- **How:** use an enabled `:name:`, such as `:smile:`.
- **When:** a symbol aids scanning or tone.
- **Where:** beside text.
- **Why:** provide a compact cue. Names depend on the provider; Unicode emoji are plain text.
  Never make a symbol the only required meaning.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  - [EMOJI](https://facelessuser.github.io/pymdown-extensions/extensions/emoji/)

## E24 Keyboard notation

- **How:** use allowed `<kbd>Ctrl</kbd>` or PyMdown `++ctrl+enter++`.
- **When:** explaining keyboard input.
- **Where:** the action step.
- **Why:** distinguish keys from prose.

- **Sources:**

  - [KEYS](https://facelessuser.github.io/pymdown-extensions/extensions/keys/)
  - [GL](https://docs.gitlab.com/user/markdown/)
