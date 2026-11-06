---
name: make-metadata-file-usgs
description: "General -- applies across all projects. Build, check or update USGS-style metadata for tabular data: the attribute metadata workbook (datatype, units/domain, min, max and definition per column, plus a Column Metadata value sheet), the seven-sheet USGS data-release workbook (Workbook Metadata, Attribute Metadata, Attribute Value Definitions, Process Steps, Cross References, Source Data, Data Limitations), software metadata and a file index for code released with data, species or other code tables, and reconciliation of metadata against the data and against a USGS metadata reviewer's comments. Use when asked to create, extend, correct or review a metadata file, data dictionary, codebook, software metadata or metadata review response, when handed a metadata template, or when preparing a USGS data release or FGDC/EML record. USDA Forest Service Research Data Archive releases use a different workbook -- read reference/usfs_data_release.md first."
scope: general
---

# Metadata workbooks (USGS template)

> **Scope — general.** This skill is not tied to any one project. Apply it to any
> project whose work falls under the description above.

Fills USGS/FGDC-style metadata from the dataset itself. The helpers in `kernel.py` do the
profiling, the spreadsheet mechanics and the data-versus-metadata checks, and **you write every
definition** — that part is not generated. The standard this work is held to is a USGS metadata
reviewer reading the workbook against the data: every statement on the form must be true of the
file, and every column and value in the file must be on the form.

## Which deliverable?

Read the sheet names of the template or file you were handed before anything else.

| You were asked for | Deliverable | Read |
| --- | --- | --- |
| A data dictionary against `metadata_attribute_template.xlsx` (header `Dataset Name … Attribute Definition`, one sheet) | The three-sheet attribute workbook described below | this file |
| A USGS data release workbook with sheets `Workbook Metadata`, `Attribute Metadata` (eight columns, incl. `Attribute Value Type`), `Attribute Value Definitions`, `Process Steps - Tabular Data`, `Cross References`, `Source Data`, `Data Limitations` | The seven-sheet data-release workbook | `reference/usgs_data_release_workbook.md` |
| Code or an R package released with the data (`Software Metadata` sheet, a file index, a code-to-data table) | Software metadata and file index | `reference/software_release.md` |
| A reviewer's comments to answer (the "metadata review reconciliation" Word form), or data and metadata that disagree | Reconciliation | `reference/reconciliation.md` |
| A USDA Forest Service Research Data Archive release | The RDA workbook | `reference/usfs_data_release.md` |

> **If the destination is a USDA Forest Service data release, not a USGS one, read
> `reference/usfs_data_release.md` before filling in anything.** The Forest Service Research
> Data Archive uses its own combined workbook: no datatype column, no minimum/maximum, a
> `Precision` column instead, enumerated domains interleaved into the variable sheet rather
> than held on a separate one, plus a file index and the full FGDC metadata record in the same
> file. The profiling workflow below still applies; the sheet layout below does not.

The seven-sheet layout and the software and reconciliation references were written from filled-in
USGS samples, not from blank templates. When a blank template is in hand, its header text, sheet
order and wording override the references; say so if they differ. **To start one of these
deliverables without a template, use the blanks generated from the samples**
(`reference/blank_templates.md`).

## What the three sheets are for (attribute workbook)

| Sheet | One row per | Maps to FGDC |
| --- | --- | --- |
| `Attribute Metadata` | column of the dataset, in file order | `attr`: `attrlabl`, `attrdef`, and the range (`rdom`) or unrepresentable (`udom`) domain |
| `Column Metadata` | observed value of each categorical column | `attrdomv/edom`: `edomv` + `edomvd`, the enumerated domain |
| `Dataset Notes` | file-level fact, then the open items | context the attribute form has no field for |

`Attribute Metadata` is the template's own sheet — keep its columns, order and wording
conventions exactly. The other two are additions; say so when you hand the file over, since a
strict template user may want them dropped.

## The datatype vocabulary

This is the distinction the form turns on, and the one most often got wrong:

- **`categorical`** — a text column whose values form a fixed, enumerable set. Every value is
  listed and defined on `Column Metadata`. This is an FGDC enumerated domain.
- **`text`** — a free-form string column with no enumerable domain: notes fields, comments,
  descriptions. No value list is possible. Most scientific tables contain none.
- **`numeric`** — continuous or real-valued. Carries units, minimum and maximum.
- **`integer`** — whole numbers (counts, years, identifiers, indices).
- **`logical`** — TRUE/FALSE. Put `TRUE / FALSE` in Units/Domain and leave Min/Max blank.
- **`date`** — give the format in Units/Domain (`MM/DD/YYYY`) and the earliest/latest in Min/Max.

An identifier column (`plot_id`, `polygon`) is `integer` or `categorical` by its storage, not
by its role — but say in the definition that it is an identifier and how many unique values it
takes. `suggest_datatype()` proposes a type from the profile; override it when the storage type
misreads the column's meaning. The seven-sheet workbook uses a coarser pair of fields
(`Data Type` = number / text / date; `Attribute Value Type` = range / enumerated /
unrepresentable); the mapping is in `reference/usgs_data_release_workbook.md`.

## Workflow

1. **Identify the deliverable, the template and a writable output directory.** Use the table
   above. The template is usually `metadata_attribute_template.xlsx` beside the data. Check
   `list_host_grants` — data directories are often read-only grants, and the user may have the
   template open in LibreOffice (a `.~lock.<name>#` file beside it), so never write back into the
   template itself. Name the output after the dataset: `<dataset_stem>_metadata.xlsx`.
2. **Read the template before filling it.** Its header row defines your column set, and its
   example rows define the voice of the definitions. Mimic both. The common form is
   `Dataset Name | Attribute Label/Columns | Datatype | Units/Domain | Min | Max | Attribute
   Definition`, with definitions written as "This attribute (x) is ...", Units/Domain left
   blank for non-numeric columns, and unique-value counts carried in the definition text. Note
   which cells are instructions or examples (they must not survive into the deliverable) and
   which are answers.
3. **Profile the whole dataset, not a sample.** `profile_table(path)` makes one chunked pass and
   returns per-column kind, null count, exact minimum and maximum, and — for every column under
   `cat_max` distinct values — the full value counts. It also returns what a default pandas read
   would have hidden: literal `NA`/`null`/`None` strings (`na_like`), non-numeric entries in a
   numeric column (`tokens`), padded values (`n_padded`), whether a numeric column holds only
   whole numbers (`all_whole`), and a `header` audit (duplicate or padded column names). Minima
   and maxima go on the form as facts; a sampled extreme is a wrong fact. State in the Notes
   sheet that they came from the full file and give the row count. Read the profile for what it
   flags before reading it for what it says.
4. **Verify the structural relations before describing them.** Cheap, and each one turns a guess
   into a statement. The checks that repeatedly earn their keep:
   - **The row key.** Which combination of columns is unique? Say it in the Notes sheet; it is
     the single most useful orienting fact for a new reader.
   - **Derived columns.** Does one column equal an expression of others (`year_diff ==
     year_b - year_a`, a flag equal to an interval excluding zero, a concatenation of indicator
     columns)? Then its definition says so, and the reader knows it carries no new information.
   - **Constancy.** Is a column constant within a group (a polygon-level attribute repeated down
     a pixel-level table)? That tells the reader the level the variable lives at.
   - **Index reuse.** Does an index restart within each group, so that the identifier is a pair
     of columns rather than one? Getting this wrong misleads every later join.
   - **Composite identifiers.** Is an ID a concatenation (`12PB` = transect 12, site P,
     treatment B)? Define the parts, and define them against the values that occur.
5. **Enumerate the categorical domains.** `enumerate_values(path, columns, delimiters=...)`
   returns exact value counts, and for delimited columns the component terms as well. Document
   both: component terms first under the label `<attribute> (component term)`, then the observed
   combinations. Component counts are row counts containing the term, so they sum past the
   attribute total — state that on the Notes sheet. Check the arithmetic with
   `check_value_sheet()`: every non-component attribute must sum to the dataset row count. Codes
   that come from an outside authority (species symbols, station IDs, method codes) are not
   defined by you: build a companion code table and verify each entry against the authority.
6. **Hunt the placeholder codes.** A dataset with no empty cells can still be full of missing
   data recorded as `na`, `unknown`, `-9999`, `NULL`, `none` or an out-of-range sentinel, and a
   numeric column can carry domain codes (`T` for trace, `5D`, a lone question mark). These appear in `na_like`,
   `tokens` and the value counts of step 5, and in the minima of step 3. Document each one with
   its row count and never let "no missing values" stand unqualified. Blank cells are a
   placeholder too: say what blank means in every column that has any.
7. **Write the definitions.** One sentence of what the column is, then what a reader needs to
   not misread it: units, the sign convention, the denominator of a percentage, the averaging
   interval of a mean or sum, what is excluded, the level the variable varies at. Reuse the
   project's own vocabulary — load the project context skill if one exists.
8. **Record what the data does not record, as open items.** See below.
9. **Reconcile before hand-over.** Load the finished workbook and the data (read with
   `read_table()`) into `reconcile_attributes()` — the default sheet names are the seven-sheet
   workbook's; pass `value_sheet="Column Metadata"` for the three-sheet one. Fix every `error`;
   for each `review`, either fix it or put it on the open-items list with the owner's question.
   A hand-over with unexplained findings is not finished. A clean result from a checker you have
   not seen fail proves little: change one value in a copy of the data and confirm it is caught.
   `reference/reconciliation.md` lists the checks and what each one means.
10. **Save, read back, and hand over.** Read the written workbook with `openpyxl` and check the
    sheet shapes, the datatype tally and the value-count sums before reporting. Save it as an
    artifact and copy it into the writable project directory. Say which decisions belong to the
    data owner (rename, drop, withhold, correct a value) — they are not yours to make.

## Exactness rules

Each of these has been a reviewer comment or a measured defect in a real USGS workbook. They apply
to every deliverable above.

1. **One row per column, label verbatim.** The label is the data header character for character:
   case, underscores, trailing spaces. Never one row standing for a run of columns ("A to Z"),
   never a tidied label. Whitespace or a typo in a header is a data defect — report it; do not
   fix it on one side only.
2. **Both directions.** Every attribute row is a column of the data, and every column of the data
   has a row. A mismatch is a finding with a decision for the owner: rename in the data, rename in
   the metadata, or drop the column from both. A column withheld from the release (coordinates a
   partner asked not to publish, say) leaves the data and the metadata together.
3. **Minimum and maximum are the full-file extremes, at the data's own precision** — and are
   checked for plausibility against the stated units. A range that matches the file but is
   impossible for its units (a volumetric water content of 7 m3/m3, a battery at 0–1 V, a
   continuous sensor reading stored as whole numbers) means the file or the units is wrong; ask.
4. **Units belong to the quantity.** A position along a transect is metres, not decimal degrees;
   say percent or fraction; give the time zone of timestamps; give the interval of every mean,
   sum or maximum ("hourly mean", "hourly sum").
5. **Every code is defined, or points to a named authority.** Every observed code, including
   placeholders and trace markers, has a row on the value sheet; codes that follow a published
   system point to a companion table carrying the authority's own symbol. Coverage is checked by
   program, not by eye.
6. **Defined equals observed.** Nothing observed is undefined; nothing defined is absent from
   the data (or the definition says it is kept for completeness). Check that definitions sit under
   the attribute they describe: values defined under the wrong attribute are invisible to a reader.
7. **Case and spacing variants are data defects, and the code may depend on them.**
   `Lower_canopy` / `Lower_Canopy`, `LIT` / `LIT `: report both spellings with their counts to the
   owner; document both only if the owner keeps both. Before anyone merges variants, search the
   code that consumes the column: in one release the analysis selected a literal lower-case
   spelling, so the data and the code had to change together (`reference/software_release.md`).
8. **A numeric column with text in it is not plain "number".** Say so in the definition and
   list each token with its count on the value sheet.
9. **No template residue.** Prompt sentences (`… [Complete this sentence]`), instruction and
   example columns, yellow fill and example rows from the template are removed or replaced
   before delivery. A field with nothing to say is either filled with the plain statement
   that nothing applies or listed as an open item — never left holding the prompt.
10. **Same concept, same name, in every table of a release.** `Reader`/`Observer`,
    `Park Code`/`Park_Code`: one spelling, one definition. If the owner renames, the data are
    re-issued with the new names.
11. **Numbers in prose equal numbers in the data.** Row counts, transect counts, sensor counts,
    date spans in the abstract, the process steps and the limitations statement are recomputed
    and compared. A process date cannot precede the last observation it covers.
12. **Dates carry a format.** State it. Store `YYYYMMDD` as text: spreadsheets drop leading zeros
    and reinterpret the digits. Do not copy a date format from a template's example row without
    checking it.
13. **A spelling pass** over every sentence you write and every label you copy, reporting
    typos in the owner's own labels rather than silently correcting them.
14. **Contact details come from the user.** Point-of-contact name, address, phone and e-mail are
    never carried over from another workbook, a sample or memory.

## Never invent a definition

The form has a field for units and a field for a definition, and a dataset will not supply
either for every column. Where the data is silent, the definition says so in plain words —
"the units are not recorded in the file", "the source dataset and formulation are not
recorded" — and the item goes on a numbered **OPEN ITEMS** list at the bottom of the Notes
sheet, phrased as a question to the data owner. A fabricated unit or provenance is worse than a
gap, because the gap is visible and the fabrication is not.

What the data cannot tell you, every time: the units of a derived terrain or climate index; the
source dataset and version behind a covariate; the depth interval or averaging window behind a
soil or climate summary; the nominal level and kind of an uncertainty interval; the coordinate
reference system of projected coordinates; the process date and the DOI of a release; and the
intended reading of any coded vocabulary whose labels you are reading plainly rather than from
documentation.

Two things you *can* settle yourself, and should:

- **A projected CRS can be tested.** Transform the coordinate extremes under the candidate CRS
  with `pyproj` and check the result against the known study area. A match makes "consistent
  with EPSG:xxxx, not recorded in the file" a defensible statement; it is still not a
  confirmation, so leave it on the open-items list.
- **An enumerated vocabulary can be counted.** Report how many values there are, how often each
  occurs, and which combinations are observed, even when you cannot say what one of them means.

## Pitfalls

- **Pandas erases the placeholder codes you are hunting.** `read_csv`/`read_excel` turn `NA`,
  `N/A`, `null`, `None` and `nan` into missing values by default, so the strings vanish and the
  null count absorbs them. `profile_table`, `enumerate_values` and `read_table` set
  `keep_default_na=False, na_values=[""]`; if you hand-roll a read, do the same.
- **Pandas renames duplicate headers** (`count`, `count` becomes `count`, `count.1`), hiding a
  defect in the file. `audit_header()` reads the raw header row.
- **Per-chunk uniqueness undercounts, and per-chunk string conversion splits counts.** Accumulate
  distinct values in one Counter across the whole pass, keyed on a canonical string (`2`, not
  `2` in one chunk and `2.0` in another). `profile_table()` does both — if you hand-roll a pass,
  do not gate or key on the chunk.
- **A data sheet inside a workbook can carry scratch cells** to the right of the table
  ("17 attributes", a repeated column name). Restrict the read to the table's own columns
  (`read_kwargs={"usecols": range(n)}`) and do not mistake the scratch for data.
- **Copy the template file to create the output.** `open_from_template()` copies it and blanks
  the data rows below `header_row`, which preserves the header formatting, column widths and
  sheet name. Building a workbook from scratch loses all of it. For the multi-block
  `Attribute Metadata` sheet use `write_attr_blocks()`, which repeats one header on every block.
- **Use `openpyxl`, from Python.** R's `openxlsx` / `writexl` are frequently not installed, and
  this is a one-off data-description task rather than project analysis code, so it does not need
  to live in the project's language.
- **Wrap the definition column** (`wrap_cols=`) and set a wide column width, or the sheet is
  unreadable in Excel. Freeze the header row and add an autofilter on the value sheet.
- **One categorical value per row.** Do not pack a comma-separated list of values into one cell
  of a value sheet; the enumerated domain is a table, and a user will filter and sort it.

## Helpers (`kernel.py`)

```python
t = read_table("data.csv")                 # CSV/Excel read that keeps NA/null strings as text
audit_header("data.csv")                   # duplicate / padded / blank column names
p = profile_table("data.csv")              # one pass: n_rows, header audit, per-column kind/nulls/min/max/values/tokens
suggest_datatype(p["columns"]["x"])        # -> 'categorical' | 'text' | 'numeric' | 'integer' | 'logical' | 'date'
v = enumerate_values("data.csv", ["objective", "treatment"],
                     delimiters={"objective": ", "})   # exact value counts + component terms
wb, ws, header = open_from_template("metadata_attribute_template.xlsx", "out.xlsx")
write_rows(ws, attr_rows, wrap_cols=(7,))  # fill the template sheet
add_sheet(wb, "Column Metadata", VALUE_HEADER, value_rows,
          widths=(32, 26, 46, 92, 12, 12), wrap_cols=(3, 4))
add_sheet(wb, "Dataset Notes", ("Item", "Value / note"), note_rows,
          widths=(46, 115), wrap_cols=(1, 2), autofilter=False)
wb.save("out.xlsx")
check_value_sheet("out.xlsx", p["n_rows"])  # per-attribute count sums, for the read-back check

# seven-sheet data-release workbook and the checks that prove it matches the data
write_attr_blocks(ws, {"table_a": rows_a, "table_b": rows_b})   # FULL_ATTR_HEADER on every block
findings = reconcile_attributes("out.xlsx", {"table_a": df_a, "table_b": df_b},
                                codesets={"species": set_of_codes})   # list of {table, attribute, severity, check, detail}

# software releases
scan = scan_r_io("pkg_root")                # files read/written, packages used, hard-coded paths
reconcile_file_index("index.xlsx", "pkg_root", sheet="Add Info")   # hand-written file index vs the disk
reconcile_io_matrix("code_data_matrix.xlsx", scan)                 # hand-built code/data table vs the code
reconcile_r_package("pkg_root")             # data objects vs docs vs Rd pages; used vs declared packages
```

`ATTR_HEADER`, `FULL_ATTR_HEADER`, `VALUE_HEADER` and `FULL_VALUE_HEADER` hold the default column
sets; read the real header off the template rather than assuming. `reconcile_attributes`
expects data read with `read_table()`; pass `read_kwargs={"usecols": ...}` for a sheet with
scratch cells.

## Reference files

- `reference/usgs_data_release_workbook.md`: read **before filling any sheet of the seven-sheet
  USGS data-release workbook**. Holds the sheet-by-sheet layout, the controlled vocabularies, the
  FGDC mapping, the companion code-table format, how to fill it with the helpers, and a table of
  defects measured in a real filled-in workbook, each tied to the rule that prevents it.
- `reference/reconciliation.md`: read **when a USGS metadata reviewer's comments have to be
  answered, or before handing over any workbook**. Holds the structure of the reviewer's form, how
  to write responses, the checks `reconcile_attributes()` runs and what each finding means, and a
  decision log for the questions that belong to the data owner.
- `reference/software_release.md`: read **when code accompanies a data release**. Holds the
  `Software Metadata` sheet, the file index, the code-to-data table and the per-script data folders,
  the R-package checks, what to keep out of the release, and the findings measured on a real
  package.
- `reference/usfs_data_release.md`: read **before filling in any sheet** when the release is to
  the USDA Forest Service Research Data Archive rather than USGS. Holds the RDA workbook's sheet
  and column structure, the 66 FGDC/BDP metadata fields with their required/optional split and
  drop-down vocabularies, the accepted formats, the submission process, and a mapping from the
  USGS sheets above to their RDA equivalents. Cached templates:
  `<data-root>/claude/templates/usfs_rda_2026-02/`.
- `reference/blank_templates.md`: read **when a USGS template is needed and none was handed over**,
  or to tell answer cells from template text. Holds the generator that rebuilds blank Software
  Metadata, Software Review, Data-for-Rcode, Species Code and seven-sheet data-release templates
  from the samples (output in `<data-root>/claude/templates/usgs_blank_templates/`), which
  cells it keeps and clears, and one trap (an `EXAMPLE` column holding a real answer).
- The filled-in USGS samples these references were built from are cached at
  `<data-root>/claude/templates/usgs_data_release_samples/` (a seven-sheet workbook, its
  reviewer reconciliation form, a species code table, a software metadata workbook with a file
  index, a code-to-data table, a per-script data folder table, and the R package they describe).
