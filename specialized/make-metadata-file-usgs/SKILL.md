---
name: make-metadata-file-usgs
description: "General -- applies across all projects. Build or update a USGS-style attribute metadata workbook for a tabular dataset, filling a metadata_attribute_template.xlsx from a full profile of the data: datatype, units/domain, minimum, maximum and a written definition per column, plus a Column Metadata sheet enumerating and defining every value of every categorical column. Use when asked to create, extend or correct a metadata file, data dictionary, attribute metadata, column metadata or codebook for a CSV or other tabular dataset, when handed a metadata template to fill in, or when preparing a dataset for a USGS data release or FGDC/EML record. Also covers USDA Forest Service Research Data Archive (RDA) releases, whose documentation workbook has a different column set -- read reference/usfs_data_release.md before filling anything for a USFS data release."
scope: general
---

# Attribute metadata workbooks (USGS template)

> **Scope — general.** This skill is not tied to any one project. Apply it to any
> project whose work falls under the description above.

Fills the USGS/FGDC-style attribute metadata spreadsheet from the dataset itself. The
deliverable is a workbook with three sheets; the helpers in `kernel.py` do the profiling and
the spreadsheet mechanics, and **you write every definition** — that part is not generated.

> **If the destination is a USDA Forest Service data release, not a USGS one, read
> `reference/usfs_data_release.md` before filling in anything.** The Forest Service Research
> Data Archive uses its own combined workbook: no datatype column, no minimum/maximum, a
> `Precision` column instead, enumerated domains interleaved into the variable sheet rather
> than held on a separate one, plus a file index and the full FGDC metadata record in the same
> file. The profiling workflow below still applies; the sheet layout below does not.

## What the sheets are for

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
misreads the column's meaning.

## Workflow

1. **Locate the template and a writable output directory.** The template is usually
   `metadata_attribute_template.xlsx` beside the data. Check `list_host_grants` — data
   directories are often read-only grants, and the user may have the template open in
   LibreOffice (a `.~lock.<name>#` file beside it), so never write back into the template
   itself. Name the output after the dataset: `<dataset_stem>_metadata.xlsx`.
2. **Read the template before filling it.** Its header row defines your column set, and its
   example rows define the voice of the definitions. Mimic both. The common form is
   `Dataset Name | Attribute Label/Columns | Datatype | Units/Domain | Min | Max | Attribute
   Definition`, with definitions written as "This attribute (x) is ...", Units/Domain left
   blank for non-numeric columns, and unique-value counts carried in the definition text.
3. **Profile the whole dataset, not a sample.** `profile_table(path)` makes one chunked pass and
   returns per-column dtype, null count, exact minimum and maximum, and — for every column under
   `cat_max` distinct values — the full value counts. Minima and maxima go on the form as facts;
   a sampled extreme is a wrong fact. State in the Notes sheet that they came from the full file
   and give the row count.
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
5. **Enumerate the categorical domains.** `enumerate_values(path, columns, delimiters=...)`
   returns exact value counts, and for delimited columns the component terms as well. Document
   both: component terms first under the label `<attribute> (component term)`, then the observed
   combinations. Component counts are row counts containing the term, so they sum past the
   attribute total — state that on the Notes sheet. Check the arithmetic with
   `check_value_sheet()`: every non-component attribute must sum to the dataset row count.
6. **Hunt the placeholder codes.** A dataset with no empty cells can still be full of missing
   data recorded as `na`, `unknown`, `-9999`, `NULL`, `none` or an out-of-range sentinel. These
   appear in the value counts of step 5 and in the minima of step 3. Document each one with its
   row count and never let "no missing values" stand unqualified.
7. **Write the definitions.** One sentence of what the column is, then what a reader needs to
   not misread it: units, the sign convention, the denominator of a percentage, what is excluded,
   the level the variable varies at. Reuse the project's own vocabulary — load the project
   context skill if one exists.
8. **Record what the data does not record, as open items.** See below.
9. **Save, read back, and hand over.** Read the written workbook with `openpyxl` and check the
   sheet shapes, the datatype tally and the value-count sums before reporting. Save it as an
   artifact and copy it into the writable project directory.

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
reference system of projected coordinates; and the intended reading of any coded vocabulary
whose labels you are reading plainly rather than from documentation.

Two things you *can* settle yourself, and should:

- **A projected CRS can be tested.** Transform the coordinate extremes under the candidate CRS
  with `pyproj` and check the result against the known study area. A match makes "consistent
  with EPSG:xxxx, not recorded in the file" a defensible statement; it is still not a
  confirmation, so leave it on the open-items list.
- **An enumerated vocabulary can be counted.** Report how many values there are, how often each
  occurs, and which combinations are observed, even when you cannot say what one of them means.

## Pitfalls

- **Per-chunk uniqueness undercounts.** Accumulate distinct values in one Counter across the
  whole pass; a per-chunk `nunique()` gate silently drops values. `profile_table()` does this
  correctly — if you hand-roll a pass, do not gate on the chunk.
- **Copy the template file to create the output.** `open_from_template()` copies it and blanks
  the data rows, which preserves the header formatting, column widths and sheet name. Building
  a workbook from scratch loses all of it.
- **Use `openpyxl`, from Python.** R's `openxlsx` / `writexl` are frequently not installed, and
  this is a one-off data-description task rather than project analysis code, so it does not need
  to live in the project's language.
- **Wrap the definition column** (`wrap_cols=`) and set a wide column width, or the sheet is
  unreadable in Excel. Freeze the header row and add an autofilter on the value sheet.
- **One categorical value per row.** Do not pack a comma-separated list of values into one cell;
  the enumerated domain is a table, and a user will filter and sort it.

## Helpers (`kernel.py`)

```python
p = profile_table("data.csv")              # one pass: n_rows + per-column dtype/nulls/min/max/value counts
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
```

`ATTR_HEADER` and `VALUE_HEADER` hold the default column sets; read the real header off the
template rather than assuming.

## Reference files

- `reference/usfs_data_release.md`: read **before filling in any sheet** when the release is to
  the USDA Forest Service Research Data Archive rather than USGS. Holds the RDA workbook's sheet
  and column structure, the 66 FGDC/BDP metadata fields with their required/optional split and
  drop-down vocabularies, the accepted formats, the submission process, and a mapping from the
  USGS sheets above to their RDA equivalents. Cached templates:
  `<data-root>/claude/templates/usfs_rda_2026-02/`.
