# Software released with data (R package or scripts)

Read this when code accompanies a USGS data release: an R package, a folder of analysis scripts, the
SAS or Python equivalents. The code is released *with* the data, so three things must agree and be
documented: the software's own metadata, the list of files in the release, and the data the code
reads and writes. The exactness rules in `SKILL.md` apply; this file adds the layout and the checks.

**Provenance.** Read from one filled-in set: a `Software Metadata` workbook (two sheets), a
code-to-data table (`Software_Review`), a per-script data-folder table (`Data_for_Rcode_Metadata`) and
the R package they describe (44 release files plus four workspace entries, 32 MB zipped), cached with the other samples in
`<data-root>/claude/templates/usgs_data_release_samples/`. No blank template was available;
cell positions are those of the filled-in copy, readings marked *(inferred)* are mine. Blanks generated
from these samples (all three documents) are described in `reference/blank_templates.md`.

## The four documents

| Document | Sheet / columns | One row per | Purpose |
| --- | --- | --- | --- |
| Software metadata | `Software Metadata`: label (A), answer (B), template example (C) | field | citation, larger work, description, inputs and outputs, contact, access |
| File index | `Add Info`: `Folder`, `File name`, `Description` | file in the release | what each file is and does |
| Code-to-data table | `Data`: `Folder`, `File name`, `Data required in R code`, `Read`, `Write`, `In Data Release`, `Notes` | (script, data file) pair | which data each script touches, and whether each ships |
| Per-script data folders | `Sheet1`: `Folder name`, `Data`, `Description` | data file | the data files that ship, grouped in `Data_<script>` folders |

## `Software Metadata`

A banner `SOFTWARE CITATION INFORMATION`, then three groups of fields:

1. **Software citation**: Author; Publication Date; Software Title; Form (`R package`); Publication
   Place; Publisher; Online link to software (the DOI, reserved for the data steward).
2. **Larger Work Citation** (the paper the code supports): Author(s); Publication Date; Publication
   Title; Publication Form; Publication Place; Publisher; Online link (DOI).
3. **Descriptive fields**: Software Description (Abstract) including title; Software Purpose; Inputs
   (required data); Outputs; Supplemental Information; **Point of Contact** (person, organisation,
   address, voice, e-mail); How to access the software; Software citation (the language itself).

Rules:

- **Column C holds the template's examples from other releases** (in the sample: a SAS script on
  freshwater mussels, a spotted-owl occupancy analysis). They are not answers. Clear column C before
  delivery, or the record describes two studies.
- **Placeholders are open items, not text.** `DOI ADD`, `DON'T HAVE THIS YET` and `Data Steward will
  insert DOI URL` are legitimate while drafting; list each, and never invent a DOI.
- **Inputs and Outputs name files and columns the code actually uses.** Build them from the scan
  (below), not from memory: the sample's Inputs names three kinds of data (cryptoframe, line-point
  intercept, microclimate) while the code also reads a soil biogeochemistry table, a rare-plant
  table and a species list.
- **The language citation records the version used.** The sample's answer reproduces the template's
  example citation (an R release from 2012) word for word, with a link to the R 4 source tree; no
  minor version, package version, `sessionInfo()` or lock file appears anywhere in the package (0
  mentions in the saved history, no `renv`). Record `R.version.string` and the versions of the packages
  used, and cite them.
- **One title per object across files.** The sample's data workbook titles the release `Data from
  observations of post-fire and thinning …`, the software sheet cites the same release as `Post-fire
  and thinning data from …`, and the data workbook leaves `Publication Citation Title` blank while
  the software sheet fills the paper's title. Compare titles, authors and years across every file.
- **Contact details come from the user** (rule 14); never copy them from a prior workbook.

## `Add Info`: the file index

`Folder | File name | Description`, one row per file, a folder row (blank file name) allowed where the
description covers the folder. Rules: names exactly as on disk (case, spaces, extension); folder paths
in the release's own separator and relative to the package root; **a folder is not a file**; every
file that ships has a row and a real description (not `NA`).

`reconcile_file_index("index.xlsx", "pkg_root", sheet="Add Info")` measured on the sample (24 listed
file rows against the unpacked zip: 44 release files and 4 workspace entries, `.git` and `.Rproj.user`
counted but not walked):

| Finding | Count | Examples |
| --- | --- | --- |
| listed, not on disk | 2 | a script name with one underscore missing (the helper suggests the real one); `main` |
| listed, differs only by case or spaces | 8 | `stats_tables.HTML` vs `.html`; folder `Supplementary Figures` vs `SupplementaryFigures` (7 scripts) |
| a folder listed as a file | 2 | `man`, `R` |
| on disk, not listed | 24 | 10 `data/*.rda`, 9 `man/*.Rd`, `R/data.R`, `R/make_eco_variables.R`, the misspelled script, `.gitignore`, `.Rbuildignore` |
| workspace junk in the zip | 4 | `.RData` (16.1 MB), `.Rproj.user/` (9.3 MB), `.git/` (0.8 MB), `.Rhistory` (26 KB) |

Descriptions of `NAMESPACE` and the `.Rproj` file are `NA`: write what they are, or leave the file out.

**Keep out of the release** (`list_release_files()` flags them): `.git/` (full history, and author
names and addresses in its logs), `.Rproj.user/` (editor state), `.RData` (a workspace image can hold
objects the release withholds — coordinates, rejected tables — and the data steward cannot see inside
it), `.Rhistory`, editor lock files, OS thumbnails. A `.Rbuildignore` keeps them out of a *package
build*, not out of a zip of the folder.

## The code-to-data table

One row per (script, data file) pair; the script on the first row of its group, `Read` / `Write`
marked `X`; `NA` for a script that touches no file; `In Data Release` marked `X`, `?` (undecided) or
`NA`; `Notes` carry the owner's decisions ("can be removed from the release", "derived for analysis,
attached separately"). Build it from the code, then let the owner fill the last two columns:

```python
scan = scan_r_io("PJFIRE")        # {'io': [{script, op, call, file}], 'packages': {...}, 'hardcoded': [...]}
reconcile_io_matrix("Software_Review.xlsx", scan)
```

The scan reads literal file names inside `read.csv`, `read_excel`, `load`, `readRDS`, `source`,
`write.csv`, `saveRDS`, `save`, `ggsave`, `use_data` and the graphics devices. **A file name built with
`paste0()` or read from a config is invisible to it**, so a clean result is a lower bound: read the
scripts for such cases.

Measured on the sample (hand-built table against the code):

| Finding | Detail |
| --- | --- |
| Scripts that read a file the table lists as `NA` | 5 figure scripts `load()` `meve_sensors_long.rda`; one figure script reads the crypto workbook |
| Files the code reads that the table omits | 4 of the 19 sensor files read by `processing_meve.R` (the `Pony_B_*` set) |
| Files the code writes that the table omits | the 9 package data objects written by `make_variables.R` (`use_data`) |
| Inputs that no script in the package produces | 25, of which 2 are flagged by the owner's own notes as derived or "attached separately" (`species_list.csv`, `vwc_min_mean_max_stats.csv`) — a provenance gap to close or declare |
| Run-order dependencies, nowhere stated | `stats_tables.Rmd` needs outputs of `Figure3.R`, `Supplementary_figure2.R`, `Supplementary_figure3.R`; five figure scripts need the object `processing_meve.R` writes |
| File names the code reads differ from the released names | the code reads `Mesa Verde PJ and Fire_LPI.csv` and a `…crypto.xlsx`; the release ships `MesaVerde_PJ_Fire_LPI_2021.csv` |
| Absolute paths | 4 hard-coded `C:/Users/…` paths in 2 scripts, naming a user and a folder tree that exist nowhere else |

Consequences to write up: a run-order statement in the abstract or supplemental information; every
input classed as (a) ships in the release, (b) produced by a named script, or (c) not releasable, with
the owner's reason; and **one set of file names** — edit the code to read the released names, or ship a
mapping. Do not edit the user's scripts yourself unless asked; report the lines.

## The per-script data folders

`Folder name | Data | Description`: in the sample the release holds the data each script needs in
folders named `Data_<script>`, 22 files in 4 folders. Rules: every row has a description of **that**
file; descriptions that differ only by file name are written from the name's parts (station,
treatment, date) or the owner is asked what the parts mean; a script's *output* is not "data required"
for it. Measured: 15 sensor files share one description ("soil moisture data from Mesa Verde National
Park"), one file has none, one listed file is an output of the script it is filed under, and the
folder omits the data tables the same scripts read (`meve_sensors_long.rda`, the crypto table).

## R-package checks

```python
reconcile_r_package("PJFIRE")     # data objects vs @name entries vs man/*.Rd, used vs declared packages
```

On the sample: 10 objects under `data/`; `seedlin` has no `@name` entry in `R/data.R` and no
Rd page (a probable stray, spelled like `seedling`); `schmol_count` has an entry but no Rd page (the
documentation was not regenerated); `DESCRIPTION` declares only `R (>= 2.10)`, `NAMESPACE` imports
nothing, **25 packages are used and declared nowhere**, and the two exported functions call
`dplyr` verbs unqualified, so they work only when the user has already attached `dplyr`. `BiocrustRecovery` is
loaded by 11 scripts; the package records neither its source nor its version, and I could not
confirm it is on CRAN — record both, or the release cannot be rebuilt. `DESCRIPTION`'s title field holds a sentence and its description
begins with a typo.

## The code reads the data's quirks

Metadata reconciliation can change the data, so check what the code expects *before* normalising a
variant. In the sample, the cover calculation builds a layer key from `layer_type` and `layer_number`
and selects six literal keys, one of them `Lower_canopy_2` with a lower-case `c` beside
`Lower_Canopy_1`, `_3` and `_4`. In the copy of the table in hand, `Lower_canopy` and `Lower_Canopy`
both occur for every layer number, so those six keys match 3,814 of 5,120 live rows and miss 1,306
(for example `Lower_canopy_1`, 697 rows). Either the code was run on a differently cleaned table than
the one released, or it silently drops a quarter of the hits. The data cannot say which; this is a
question for the owner, and the answer decides whether the case variants are cleaned in the data, kept,
or the code is changed. Search the consuming code for every column whose variants you are about to
merge.

## Procedure

1. Unpack the package; `list_release_files()` and remove, or ask about, the junk.
2. `scan_r_io()`, `reconcile_r_package()`; write `Inputs`/`Outputs` and the run order from them.
3. Fill the four documents from the user's answers and these scans; open items stay open.
4. `reconcile_file_index()` and `reconcile_io_matrix()` until nothing unexplained remains; keep the
   owner's decisions in a log beside the files (`reconciliation.md`, section 3).
5. Compare titles, authors, years and DOIs between the software sheet, the data workbook and the
   reviewer's form.
