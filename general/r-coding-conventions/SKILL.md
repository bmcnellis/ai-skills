---
name: r-coding-conventions
description: "General -- applies across all projects. House R style for BEM's projects: the two project shapes (R package for large portable work, single numbered directory for small interpretable work), the helper/plot/key function-file split, minimal dependencies with inline pkg:: qualification, base-R-leaning syntax with dplyr/ggplot2 as the only routine tidyverse, comment and function-design conventions, figure defaults and the ggplot2 traps that only appear on real data, and the R Markdown/knitr rules (compute-in-script, kable auto-printing, inline-R numbers and ordering, html_document limits) plus the cheap parse/scan checks that verify a document without rendering it. Load before writing or editing R code, or any .Rmd, in any of these projects."
scope: general
---

# R coding conventions

> **Scope — general.** This skill is not tied to any one project. Apply it to any
> project whose work falls under the description above.

House style for R work. Written from the two reference codebases: **`NEON1`**
(an R package — the portable, large-project shape) and **`RestoreDART`** (a
single working directory — the small, interpretable shape). When a new project
starts, pick one of the two shapes deliberately; don't drift into a third.

## Pick the project shape first

**(1) R package** — for a large project that has to be portable, installable,
or shared as a unit. `NEON1` is the reference.

```
PKG/
  DESCRIPTION            # Imports: with minimum versions; Depends: R (>= x.y.z)
  NAMESPACE              # roxygen2-generated, never hand-edited
  R/helpers.R            # general-purpose functions
  R/plot_functions.R     # figure functions only
  R/keys.R               # lookup/recode tables as functions
  R/external.R           # re-exports of other packages' functions
  R/data.R               # data object documentation
  man/                   # roxygen2-generated
  data/*.rda             # derived objects via usethis::use_data()
  exec/                  # the analysis scripts — import_*, analyze_*, make_*
```

Analysis scripts live in `exec/`, are numbered by pipeline position in their
header comment rather than their filename, and are named by verb:
`import_<thing>.R`, `analyze_<thing>.R`, `make_<thing>.R`, `eval_<thing>.R`,
`do_<thing>.R`. Scripts `library(PKG)` and call their own package's functions
**fully qualified** (`NEON1::posterior_from_coda(...)`) so it is obvious which
code is the project's own.

**(2) Single directory** — for a project meant to stay small and readable end
to end. `RestoreDART` is the reference.

```
project/
  0_<name>_setup.R       # constants, input read, all shared computation
  1_<name>_<step>.R      # numbered by pipeline position
  2_<name>_results.Rmd   # documents: display only, compute nothing
  helper_functions.R     # table/summary functions
  plot_functions.R       # figure functions only
  TODO.Rmd
```

Filenames carry the pipeline order as a numeric prefix. The setup script
computes and the documents display — a document should not set a threshold or
derive a quantity it shows. Source the function files explicitly:

```r
source('plot_functions.R', local = environment())
source('helper_functions.R', local = environment())
```

**Both shapes obey the same rule: functions live in function files, scripts
orchestrate.** A script that defines a function is a script that should have
put it in `helpers.R` / `helper_functions.R` / `plot_functions.R`. The split is
by *kind*, not by topic: helpers, plotting, and (in the package shape) keys.

`keys.R` holds the lookup tables — domain names, age-range recodes, factor
level orders — written as **functions** that return a `data.frame` or an
ordered factor, not as bare data objects, so they carry validation:

```r
key_field_domain_id <- function(id) {
  k0 <- data.frame(id = seq(20), name = c('Northeast', ...), row.names = NULL)
  if (missing(id)) return(k0)
  if (!all(id %in% seq(20))) stop('id(s) must be a domain number 1-20')
  k0[id, 'name']
}
```

## Dependencies: few, and always visible at the call site

- **Keep the dependency list short and ask before growing it.** `NEON1` imports
  10 packages for a Bayesian JSDM pipeline; `RestoreDART` uses exactly four
  (`dplyr`, `ggplot2`, `tidyr`, `knitr`) plus base `stats`. Adding a package is
  a decision to raise, not a convenience to take — no `kableExtra`, `patchwork`,
  `purrr`, `stringr`, `data.table` unless there is a real argument for it.
- **Qualify calls inline: `dplyr::filter()`, `tidyr::pivot_wider()`,
  `terra::extract()`, `Hmsc::sampleMcmc()`, `knitr::kable()`.** The point is to
  read a line and know where the function came from. This is the strongest
  convention in both codebases.
- **`ggplot2` is the one exception.** Inside a plotting file, `require(ggplot2)`
  at the top of the function and then bare `ggplot()`, `aes()`, `geom_*()`,
  `theme_bw()`, `element_text()` — a fully qualified ggplot stack is unreadable.
  Everything else stays qualified.
- **Where to declare:** package shape → `Imports:` in DESCRIPTION with minimum
  versions, plus `require(pkg)` at the top of any function body that needs an
  attached package. Single-directory shape → `library(pkg)` once in the setup
  script, with `require(pkg)` still inside the functions so they work standalone.
  In a knitr context, attach in a message-suppressed setup chunk so the later
  `require()` calls are silent no-ops — otherwise "Loading required package:"
  lands in the middle of the rendered document.
- `magrittr` is loaded only for `%>%`, and only where `%>%` is the right call
  (see the pipe rule below). No `import::from()` in new code.

## Minimise tidyverse, keep base R in reach

`dplyr` and `ggplot2` are indispensable; `tidyr` for reshaping. Beyond those,
prefer base:

| Use | Not |
|---|---|
| `\(xx) ...` | `function(xx) ...` in `*apply`, `~ .x` formulas |
| `sapply()`, `lapply()`, `vapply()` | `purrr::map*()` |
| `ifelse()`, nested where needed | `dplyr::case_when()` |
| `paste0()`, `sub()`, `gsub()`, `grepl()`, `strsplit()` | `stringr::str_*()` |
| `setNames()`, `data.frame(..., row.names = NULL)` | `tibble()` |
| `for (i in seq_along(x))` when it reads better | forcing a functional |
| `table()`, `rowMeans()`, `colSums()`, `scale()` | tidy equivalents |

`dplyr` chains are used freely for data assembly — long `|>` pipelines of
`select` / `filter` / `mutate` / `group_by` / `summarise` / `left_join` are
house style. It is the *surrounding* code that stays base.

### Pipes: `|>` by default, `%>%` when the dot earns it

The native pipe is the default and covers almost everything. But `|>` can only
pipe into the **first** argument, whereas `%>%` places the left-hand side
anywhere via `.`:

```r
df %>% lm(y ~ x, data = .)          # the dot is the point
df |> (\(xx) lm(y ~ x, data = xx))()  # same thing, unwieldy
```

A lambda always gets you there, but when the wrapper is more noise than the
call it wraps, `%>%` is the correct choice — use it and move on. (`|>`'s `_`
placeholder is not a general substitute: it must be a *named* argument and may
appear only once, and it needs R >= 4.2, above `NEON1`'s declared floor.)
So: reach for `|>` first, switch to `%>%` for dot placement rather than
contorting a pipeline around the first-argument rule, and don't mix the two
within one chain.

## Syntax

- `<-` for assignment, never `=`.
- **Single quotes** for strings. (Double quotes only when the string contains an
  apostrophe.)
- `snake_case` for functions and objects. Function names lead with a verb:
  `get_`, `make_`, `plot_`, `summarize_`, `key_`, `check_`, `print_`, `fmt_`.
- Short, indexed working names inside a function or script are fine and expected
  — `df0`, `df1`, `mat_p`, `env0`, `stu0`, `s0`, `dir0`, `fc`, `xx`, `ii`, `i0`.
  The convention is that a trailing digit distinguishes parallel objects of the
  same kind (`m_p_0` / `m_p_1`, `env0` / `env1`), and doubled letters
  (`xx`, `ii`) mark a lambda or loop variable.
- Explicit `return()` at the end of a function that returns a value. Bare final
  expressions are acceptable in one-liners.
- Long signatures get one argument per line, with defaults spelled out.
- `T` / `F`, not `TRUE` / `FALSE` — this is the house standard, including in
  argument defaults (`add_zeros = T`, `na.rm = T`, `overwrite = T`).
- `file.path()` for paths, never string concatenation.
- `seq_along(x)` / `seq(n)`, never `1:length(x)`.

## Function design

- **One source of truth per decision.** When a mapping or convention is needed
  in more than one place, it becomes a function and every caller reads from it:
  `get_intended_sign()` for the sign a goal implies, `fig_conventions()` for
  figure colours/sizes/themes, `key_age_range()` for age-class recodes. Never
  hard-code a value that one of these owns.
- **A thin named wrapper over a generic is fine** when callers and prose refer
  to it by name (`txeco_threshold()` / `year_threshold()` both call
  `keyed_threshold()`).
- **One function with a `metric` / `type` / `direction` argument**, not two
  near-duplicate functions.
- **Validate at the top.** `stopifnot()` for structural invariants — this is
  load-bearing in both codebases, e.g. checking matrix/data-frame alignment
  before a model call:

  ```r
  stopifnot(
    identical(row.names(mat_p), row.names(env0)),
    identical(colnames(mat_p), row.names(tr0))
  )
  ```

  Use `stop()` with a message prefixed by the function name for a condition the
  caller can act on: `stop('get_intended_sign(): objective must start with ...')`.
- **Functions return objects; they do not print.** A figure function returns the
  `ggplot`; a table function returns the `data.frame` or the `knitr::kable`.
  Printing is the caller's job (and in knitr, wrapping a `kable` in `print()`
  breaks it).
- **Titles, labels, and annotation data are arguments, not derived inside.**
  Where a figure annotates a value that is also printed in a table, pass the
  table in so the two cannot disagree.
- Restore global state you change: `on.exit(par(mfrow = c(1, 1)))`,
  `on.exit(try(dev.off(), silent = TRUE))`.

## Comments

Comments carry *rationale*, not restatement. Two patterns, both in use:

**Script header** — author initials, creation date, last-run date, then purpose,
then standing `TODO:` and `Caveats/Considerations:` blocks:

```r
# BEM
# created  29 July 2024
# last run 21 Sep 2024

# TODO:

# Caveats/Considerations:
#     * taxon not identified to species are excluded
#     * lava flow age is the median of the age range published on USGS maps
#     * pai, elev, age_median are centered and scaled
#     * time_since_fence NOT centered or scaled
```

Keep the caveat block current — it is the record of every analytical decision a
reader would otherwise have to reverse-engineer.

**In-function rationale** — a paragraph at the top of the body explaining why
the function exists, what it is the single source of, and what was deliberately
left out of it. Reference the sibling function or document section it has to
agree with.

Section banners: `### Libraries` / `### Data import` / `### Directories` in
scripts, or `# ---- constants ----------------------------------------------`
in the single-directory shape.

**Do not delete the record.** Commented-out parameter rounds, superseded
thresholds, and the notes on why a species or covariate was dropped stay in the
file — `make_models.R`'s ten-round comment block is the only account of how the
final model was reached. Mark them, don't tidy them away.

## Figures

- Figure functions live only in `plot_functions.R`.
- Base theme is `theme_bw()` plus black axis text:

  ```r
  theme_bw() +
    theme(
      axis.text.x = element_text(color = 'black', angle = 45, hjust = 1),
      axis.text.y = element_text(color = 'black')
    )
  ```

  Rotate x labels 45° with `hjust = 1` whenever the axis carries species or
  level names.
- Colour and size constants belong in one function — a palette function
  (`c25(option)`) or a full conventions list (`fig_conventions()`) — and figure
  functions read values off it rather than writing literals.
- Sample sizes annotate as `n = 1234`, no parentheses.
- Device pattern: either `ggplot2::ggsave(file.path(fig_dir, 'name.pdf'), ...)`
  or an explicit `pdf(...)` / `dev.off()` pair around the call. Write to a
  `fig_dir` constant, never a literal path mid-script.
- Facet a compiled multi-group figure on a **shared** y axis; free scales defeat
  the comparison the figure exists to make.
- Every figure in a report is followed by a bold `**Figure.**` paragraph naming
  the x axis, the y axis and every grouping (fill / colour / facets), plus what
  any error band represents. Where a figure carries two levels of sample-size
  label, the caption says why the numbers do not sum to each other.

### ggplot2 traps that only appear on real data

None of these reproduce against a small synthetic frame — they are found by
rendering the real figure, which is the argument for doing that once before
calling a new figure function done:

- A flag mapped to `shape` or `fill` needs `drop = FALSE` on its scale, or the
  legend key vanishes in any run where no row happens to carry that level.
- An `NA` in an error-bar column silently removes both the error bar **and** any
  label layer positioned off it. Substitute 0 before plotting if the row should
  still draw.
- A per-row justification aesthetic (`aes(vjust = ...)`) is applied unreliably.
  Draw two layers with a fixed `vjust` each instead.
- Labels centred on a point near a panel edge get clipped: give the axis room
  with `scale_x_continuous(expand = expansion(...))`. Rotated `n = ` labels
  above a bar need roughly half the tallest bar's height as upper expansion
  once the counts reach six digits.
- `facet_wrap(~ get(col))` is fragile — `get()` resolves outside the data mask,
  so the facet breaks at draw time with "object '<col>' not found" as soon as
  the column is not also in scope. Write
  `facet_wrap(ggplot2::vars(.data[[col]]))`.
- An axis break per integer (`breaks = seq(max(x))`) is readable to about a
  dozen levels; beyond that thin them
  (`by = ceiling(max(x) / 15)`) rather than falling back to ggplot's defaults,
  which will label fractional values of an integer count.

## R Markdown and knitr

**Compute in a script, display in the document.** A `.Rmd` should not set a
threshold or derive a quantity it shows — the numbered setup script owns that
(see the single-directory shape above). Source it from the document's setup
chunk as `source('0_<name>_setup.R', local = knitr::knit_global())`. That
argument is load-bearing, not style: anything that later looks objects up with
`ls(envir = parent.frame())` or `get()` is, from inside a chunk, looking at the
knit environment, and the default `local = TRUE` would hide the script's
objects from it.

- **`knitr::kable` objects must auto-print at chunk top level.** Wrapping one in
  `print()`, or returning it from inside an `if()`, bypasses
  `knit_print.knitr_kable` and dumps raw pipe-table text into the output. A
  function that builds several tables **returns** them; the chunk prints them.
- NA cells that stand for an undefined quantity render blank via
  `options(knitr.kable.NA = '')`, set immediately around the affected `kable()`
  call and restored afterwards — `kable()` substitutes at call time, so this
  need not be global.
- **`html_document` costs you three things** worth knowing before designing a
  document around them: `kable(caption = ...)` renders verbatim with **no
  auto-numbering**, `\@ref(tab:label)` does not resolve (cross-referencing
  needs a bookdown format), and GFM checkbox task lists (`- [ ]`) do not render
  — use plain bullets with bold lead-ins.
- **Numbers quoted in the prose are pulled from the results objects with inline
  R, never typed in.**
- Generated sentences are built as a character vector in the chunk and emitted
  with `` `r paste(vec, collapse = '\n')` ``, which knitr renders as a markdown
  list. Do not `cat()`. Keep the leading `'- '` on each element or it renders as
  a paragraph instead of a list item; write prose elements in **double** quotes,
  since the text almost always contains apostrophes, and escape any literal
  double quote.
- **Inline R is evaluated in document order.** A heading that interpolates a
  value (`` ### `r label(ii)` ``) must sit *after* the chunk that defines the
  value; placed above, it silently picks up the previous section's value or
  fails in the first section. An `echo = F` chunk that prints nothing does not
  disturb the rendered order, so it can go first.
- **Never put a backtick inside an inline R expression.** knitr closes `` `r … ` ``
  at the first backtick it meets, so `` `r paste(sprintf('`%s`', x))` `` ends
  mid-string and the rest of the expression is emitted as literal text. There is
  no escape: move the backticks into the surrounding prose, or drop them.
- **Check inline expressions by evaluating them, not by reading them.** Extract
  every `` `r … ` `` from the prose (regex the non-chunk lines), `eval(parse())`
  each against the objects it will see, and print the results. It costs seconds,
  it is the only check that catches the backtick truncation above, and reading the
  rendered values is also how you confirm the sentence says what you meant.
- Attach packages in a message-suppressed setup chunk so the `require()` calls
  inside functions are silent no-ops (see Dependencies).
- **`rm()` the per-iteration names at the end of a loop that unpacks state into
  an environment.** If one is left behind, a document section that forgot to
  unpack it renders the *last* iteration's value instead of failing. Never tidy
  that `rm()` away.
- Key a section by element **name**, not position: open it with a literal name,
  `stopifnot(nm %in% names(x))`, and `ii <- match(nm, names(x))`. A literal
  index silently retitles or mis-sources a section when the upstream order
  changes.
- Removing a prior analysis is explained in a short prose paragraph in the
  document, not deleted silently — the same rule as "do not delete the record"
  for comments.

### Verifying a document without rendering it

A render costs minutes; all of this costs seconds, and the staircase is about
cost rather than capability.

1. **Purl and parse after every edit.** `knitr::purl()` each `.Rmd` to a
   temporary `.R` and `parse()` it. Sub-second, and it catches an edit that left
   the file unparseable.
2. **Scan statically for object references nothing defines.** Purl the chunks,
   then regex the `` `r ...` `` inline expressions out of the prose separately
   (purl drops them, and prose is where most of them live), `all.names()` both,
   and subtract what the function files, the setup script and the document
   itself define. **Validate the scanner with a negative control** — delete one
   assignment and confirm the name is reported — because an over-broad
   assigned-names heuristic reports a clean file either way. A clean run flags
   only `$` components, dplyr data-mask columns and `::` namespace halves.
3. **Exercise the changed function against a small synthetic frame** carrying
   the real column schema. State its ceiling honestly: a flat synthetic frame
   cannot trigger threshold-dependent branches, and a helper that asserts on the
   real data's structure may have to be stubbed to reach the code under test.
   When a change goes back unexercised, say so plainly rather than implying it
   was tested.

Counting outputs in a rendered self-contained HTML: **strip
`<script>...</script>` before counting `<table>`.** The bundled jQuery source
contains `<table>` string literals (`ge={thead:[1,"<table>",...]}`), which
inflates a naive `grep -o '<table'` by exactly 4 per document; `<img>` is
unaffected. To inspect a figure as it actually shipped, base64-decode the
`<img ... src="data:image/png;base64,...">` payloads out of the HTML — note
that `role`/`aria-label` precede `src`, and pandoc hard-wraps prose, so match on
a short phrase.

## Data, state, and reproducibility

- `set.seed(1)` at the top of every analysis script.
- Package shape: derived objects re-enter the project through
  `usethis::use_data(obj, overwrite = TRUE)` and are then read as `PKG::obj`.
- `rm()` intermediates you are done with, and `gc()` before and after anything
  large. For a multi-GB model object, load, immediately `rm()` everything except
  what is needed, then `gc()`.
- **Use relative paths from the project root.** Absolute paths rot: `NEON1`'s
  scripts still point at a data root that moved and at Windows OneDrive
  directories, which is the single biggest source of breakage in that codebase.
  Set one `dir0` / `data_dir` constant at the top and derive everything with
  `file.path()`; assert it exists:

  ```r
  stopifnot(dir.exists(data_dir), dir.exists(mod_dir))
  ```
- Paths are **case-sensitive** on Linux. A path literal that works in RStudio on
  one machine can fail on another for capitalisation alone.
- **Read only the columns you need** from a large delimited file (`colClasses`,
  or `select =`). On a multi-GB CSV that is the difference between a
  ~45-second read and minutes. The cost is that a column left out of the list is
  **silently absent** rather than an error, so extend the list before writing
  code that references a new column.
- **A `grepl()` or `subset()` filter on a misspelled level returns zero rows
  rather than erroring.** Confirm level names against the data
  (`unique(df$col)`), never against the prose describing it.
- **Staging data from Python for R:** `pandas.to_csv` writes booleans as
  `True`/`False`, which R reads as *character*; a downstream
  `table(df$flag)[['TRUE']]` then dies with an opaque "subscript out of bounds".
  Map the column to `'TRUE'`/`'FALSE'` before writing and
  `stopifnot(is.logical(df$flag))` after reading.
- Prefer a numbered/verb-named script that can be re-run top to bottom over an
  interactive fragment. Guard expensive steps with
  `if (!file.exists(f)) { ...fit...; save(...) } else { load(f) }`.

## Checklist before handing R code back

1. Shape matches the project (package vs single directory); functions are in a
   function file, not the script.
2. Every non-ggplot2 call from another package is `pkg::`-qualified.
3. No new dependency introduced without asking.
4. `<-`, single quotes, snake_case, `T`/`F`, `\(xx)`; `|>` unless dot
   placement calls for `%>%`.
5. `stopifnot()` on the structural assumptions; `stop()` messages name the
   function.
6. Returns an object; nothing prints unless the caller asked for it.
7. Constants at the top, paths relative and asserted, `set.seed(1)` if anything
   is stochastic.
8. Header comment says who, when, and what the caveats are; rationale comments
   explain the non-obvious choices; nothing informative was deleted to tidy up.
9. For an `.Rmd`: nothing is computed or thresholded in the document, `kable`s
   auto-print, quoted numbers are inline R, and the purl-and-parse check was run
   after the edit.
