# USGS data-release workbook (seven metadata sheets)

Read this when the destination is a **USGS data release** whose metadata arrives as one workbook
with the sheets below, rather than the single-sheet `metadata_attribute_template.xlsx` described in
`SKILL.md`. The profiling workflow, the exactness rules and the never-invent-a-definition rule in
`SKILL.md` apply unchanged; this file adds the layout.

**Provenance, and what is inferred.** The layout below was read from one filled-in, partly
completed workbook (a Mesa Verde piñon-juniper release: 4 data tables, the largest 97,929 rows),
its reviewer's reconciliation form, a species code table and a software workbook. No blank
template was available. Cell positions and column widths are therefore those of the filled-in
copy; anything marked *(inferred)* is a reading of that copy, not a statement of the template.
The samples are cached in `<data-root>/claude/templates/usgs_data_release_samples/`.
Where a blank template is in hand, its text wins over this file. A blank generated from the
sample is in `<data-root>/claude/templates/usgs_blank_templates/` (`reference/blank_templates.md`). The workbook is an intake
format: the FGDC XML record that the Metadata Parser validates is built from it downstream
*(inferred from the reviewer's form naming an `.xml` file, and from the software sheet reserving
the DOI for "the data steward")* — so do not claim FGDC validity for the workbook itself.

## Sheet map

| Sheet | One row (or block) per | Feeds (FGDC CSDGM) | Notes |
| --- | --- | --- | --- |
| `Workbook Metadata` | release-level field, then one row per data table | citation, abstract, purpose, keywords, entity description | answers sit in column D; column B holds the template's instruction text |
| `Attribute Metadata` | column of each data table, in blocks | `attr`: `attrlabl`, `attrdef`, `attrdomv` (`rdom` / `edom` / `udom` / `codesetd`), `attrunit` | eight columns; one header and one dataset-name row per block |
| `Attribute Value Definitions` | observed value of a coded column | `edom`: `edomv`, `edomvd` | four columns, no banner row |
| `Process Steps - Tabular Data` | data table, plus a QA/QC step | `procstep`: `procdesc`, `procdate` | narrative per table |
| `Cross References` | publication the record cites | `lworkcit` / `crossref` | six fields per citation; blocks repeat |
| `Source Data` | input dataset used to build the tables | `srcinfo`: `srccite`, `typesrc`, `srctime`, `srccontr` | thirteen fields per source; blocks repeat |
| `Data Limitations` | the release | use-constraint and completeness elements (`useconst`, `complete`) *(inferred)* | one mandatory statement |

Every sheet except `Attribute Value Definitions` carries a bold banner in row 1 (merged across
the sheet) naming it in capitals. After the metadata sheets the workbook holds the **data
tables themselves**, one sheet per table, row 1 the header.

## `Workbook Metadata`

Answers go in column D. Column B holds the template's prompt for the row, and some prompts are
sentence frames the answer must complete:

| Row label | What goes there | Check |
| --- | --- | --- |
| `Data Release Citation Title` | the release title | matches the title everywhere else (software sheet, process steps) |
| `Publication Citation Title` | title of the paper the data support; blank if none | blank is an open item, not a pass |
| `Scientist(s) Name` | everyone who collected, compiled or processed the data, in order of contribution | order is a decision for the owner |
| `Dataset Credit` | one complete sentence naming organisations and individuals credited for support, funding, collection, analysis | a list of names is not a sentence |
| `Abstract/Description` | six frames: compiled for; objectives; these data represent; collected in (place **and dates**); collected by (organisation and how); can be used to | every frame answered; dates agree with the data |
| `Purpose` | three frames: purpose of the data; why created; how future researchers could use them | |
| `Keywords: Theme or Subject` / `Keywords: Place` | from the abstract and purpose, **not** from the paper; "more is always better" | a blank `Place` row is a gap |
| `Dataset Name` / `Description` | one row per data table | each name equals the table's sheet/file name exactly; two frames: "This data table represents … The purpose of this data table is …" |

## `Attribute Metadata`

Header (row 3; copy it from the template, do not retype): `Dataset Name | Attribute Label/Columns
| Units/Domain | Data Type | Attribute Value Type | Attribute values | Attribute Definition |
Additional Information`. One block per data table: a bold dataset-name row in column A, then one
row per attribute in file order, then two blank rows, then the header again. In the sample the
repeated header drifted (`Units/Domain` in the first block, `Units` in the others) — write one
header on every block (`write_attr_blocks()` does).

| Column | Vocabulary seen | Rule |
| --- | --- | --- |
| `Units/Domain` | a unit with symbol (`Net Radiation (W/m2)`, `meters`, `degrees (°)`), or `integer number`, `free text`, `date` | a unit for every measured quantity; the unit belongs to the quantity (a position along a transect is metres) |
| `Data Type` | `number`, `text`, `date` | a numeric column holding text tokens is not plain `number` — say so in the definition |
| `Attribute Value Type` | `range`, `enumerated`, `unrepresentable` (and once `single value`, which is not a domain type) | see the mapping below |
| `Attribute values` | `Min: a, Max: b` for a range; the listed values for an enumerated attribute | copy min/max from the full-file profile; one list delimiter throughout (the sample mixed `and`, `,` and `to`) |
| `Attribute Definition` | one sentence beginning as the template does (`This attribute in the data table represents …`) | what it is, units, sign, denominator, interval, level |
| `Additional Information` | a completed sentence beginning `The attribute values represent …` | the template shipped the prompt on every row, yellow-filled; the sample left it unchanged on 58 of its 59 documented rows |

**Mapping to the three-sheet vocabulary in `SKILL.md`:**

| `SKILL.md` datatype | `Data Type` | `Attribute Value Type` | `Attribute values` |
| --- | --- | --- | --- |
| `numeric`, `integer` | `number` | `range` | `Min: …, Max: …` |
| `date` | `date` | `range` | `Min: <date>, Max: <date>` in the stated format |
| `logical` | `text` | `enumerated` | `TRUE; FALSE` |
| `categorical` | `text` | `enumerated` | every value, in the order of the value sheet |
| `text` (notes, comments) | `text` | `unrepresentable` | blank |
| identifier, composite code | `text` or `number` | `unrepresentable` (or `codeset`, below) | the count of distinct values, not an alphabetical range |

**Domains and FGDC.** `range` → `rdom` (`rdommin`/`rdommax`, with `attrunit`); `enumerated` →
`edom` (one `edomv` + `edomvd` per value: the value sheet); `unrepresentable` → `udom` (free text;
the definition carries the meaning). A reviewer's "Codeset" question maps to `codesetd`
(`codesetn` the name of the code system, `codesets` its source). The sample's value-type list has
no `codeset`; for a code system that has an authority (species symbols), write the authority and
the companion file in `Attribute Definition`, and ask the data steward whether the template accepts
a codeset type. Do not label a coded column `unrepresentable` and stop: the reviewer on the sample
rejected exactly that for its species codes.

**An alphabetical range is not a domain.** `JUNOST to YUCBAC` or `ALF to SCR` (as in the sample for
species codes and initials) says nothing a reader can use. Give the distinct-value count and the
value list (enumerated, ≤ ~25 values) or the companion table.

**Cell comments.** The sample carries three threaded comments on attribute rows, recording owner
decisions the data had not yet caught up with: drop a stray index column, rename a column in the
*data* to match the metadata, and remove two location columns the project partners asked not to
release. Treat such a comment as an open decision until the data and the sheet change together;
never resolve one by editing only the sheet.

## `Attribute Value Definitions`

Header (row 1): `Data Table | Attribute | Attribute Values | Definition` (the sample spells the last
`Defintion`; copy the template's spelling only if it is the template's). The table name sits on the
first row of each table's rows; one row per value; one blank row between tables. What belongs here:

- every value of every `enumerated` attribute, as it appears in the data;
- every placeholder or domain code in any column: `NA` (not applicable), `T` (trace), `?` (not
  recorded), `5D` (a degree value with a direction), with the reading the owner gives it;
- the parts of a composite identifier, *and* the identifiers that occur (the sample defined the single
  letters `L`, `P`, `W` for a column whose 46 values are composites like `12PB`).

Checks: the attribute named in column B is the column the values occur in; every observed value is
defined; every defined value occurs (or the definition says why it is kept). The sample failed all
three: definitions for `B`/`I`/`T` filed under `fire_site` while the data hold `B`/`I`/`T` in
`treatment` and `L`/`W`/`P` in `fire_site`; one initials column (`Observer`, eight values) had the
single entry `?`; the trace code `T` was filed once under a label that names no column, though 21
columns carry it.

## `Process Steps - Tabular Data`

Row 3 header (`Processing Steps` | template instruction); then per table a row `Development of the
<table> data table` and a narrative, then a row `Data Quality Assessment and Quality Control
(QAQC)`, then references. The template's instruction: the steps must let a reader **replicate the
final data products from the description alone**, and they differ from a paper's Methods in being
discrete steps that derive the product. The sample's own reviewer found each narrative described
field setup but not (a) how the data were collected (data sheets), (b) how the table was compiled or
derived (script, aggregation, which columns come from which source), or (c) a process date.

For each table the narrative should therefore contain, in order: collection (instrument or data
sheet, interval, who); compilation (files combined, script and language, transformations,
aggregation such as "two-minute scans averaged to hourly"); what was added at compile time (site,
treatment, species columns, and where they came from); and `These data were processed in YYYY.`
(the sample's form of the process date). Check that the year is not earlier than the last
observation in the table: the sample gave 2021 for a table whose records end in November 2022, and
the reviewer's response corrected it to 2022.

The QAQC row separates **QA** (protocols that prevent problems: training, calibration, field
protocol) from **QC** (checks that decide whether values meet quality goals: double entry,
range checks). Every column that records a check (`Tech_Checked`, `Date_Checked`) must be
explained here: who checks, against what, and what happens on a mismatch. References cited in a step
are listed in a closing row with full citation and DOI.

## `Cross References`

Banner, then blocks `Cross Reference 1`, `Cross Reference 2`, `Cross Reference … repeat as necessary
or delete`, six fields each: `Title of the article or manuscript`, `Author`, `Publisher`,
`Publication Place`, `Publication Date (format: YYYY)`, `URL Link to the Article or Manuscript
(DOI number URL)`. Delete unused blocks. In the sample, `Cross Reference 1` still held the
template's example (a population-genomics software paper unrelated to the study) — a reader cannot
tell it from a real citation. The release's own paper goes here (with DOI when one exists; an
absent DOI is an open item).

## `Source Data`

One block per **input dataset used to build the tables** (an elevation model, a climate normal),
not per data table. Thirteen fields, all mandatory: author/originator; publication date
(`YYYYMMDD`, `YYYYMM` or `YYYY`); title; form of data; publication place; publisher/provider; URL
or service; type of data; beginning date; ending date (`YYYYMMDD`); currentness reference;
abbreviation; contribution of the input to this release. Each source must be cited in the process
step that uses it. If the data are all first-hand observations, write that in `Data Limitations`
or the process steps and delete the blocks; do not leave the template's example sources in place
(the sample kept two). The template's own example rows give beginning and ending dates of `1011923`
and `12312014`: neither is `YYYYMMDD`. Write dates as eight-digit text.

## `Data Limitations`

A mandatory statement. The template's questions: how reliable are the data and what problems
remain; how should they be used; could a non-specialist misread them, and where. A good statement
is made of the findings of this skill's own checks: placeholder and trace codes and their counts,
mixed-type columns, uncertain identifications (`ALF?`, `DESPIN?`), case variants kept in the data,
columns withheld from the release and why (without giving the withheld values), the period and the
sites covered, and the intended and **un**intended uses. In the sample the statement text was typed
into the cell of the template's `EXAMPLE` column while the prompt `provide … here` stayed in
column B *(inferred: the entry cell is ambiguous in the copy)*; put the statement where the prompt
says and clear the example.

## Companion code table (species and other coded columns)

The reviewer's rule: values that are codes must be explained by a data dictionary or code book with
a reference, and six-letter codes built from the first three letters of genus and species are not the
USDA PLANTS symbol. The sample's answer is a separate workbook (`SpeciesCode_Metadata.xlsx`):

`Species code | Scientific Name | Common Name | USDA Plants symbol/abbreviation`

Rules for such a table:

1. **One row per distinct value that occurs in any code column of any table**, verbatim — suffix
   variants and compound entries included, or the table's grammar stated. Verify coverage by program.
   In the sample the four code columns (`species`, `Shrub_sp`, `cover_code`, `PB_code`) hold **72
   distinct strings after stripping spaces** (74 as stored: `LIT `, `PB ` carry a trailing space); the
   40-row table covers 37 of them and 35 are absent. They are unlisted species, probable variants of
   listed codes (`PINED`, `YUBAC`, `BROTECT`), uncertain identifications (`ACHNASP?`), a dead-plant
   suffix (`ACHHYM_dead`, while a `status` column also records `dead`), either/or entries
   (`PINEDU/JUNOST`, `PINEDU_JUNOST`), and short codes that do not look like taxa (`B`, `R`, `LC`,
   `SNAG`, `Standing dead`) and need the owner's definition.
2. **The authority's symbol is looked up, not typed from memory**, from the authority named in the
   header, and the retrieval date recorded. Check whether the PLANTS site is reachable
   (`request_network_access`) or ask the user for an export.
3. **Names that are not taxa** (litter, woody debris, bare ground) carry an explicit "not a taxon"
   in the symbol column, not `NA`, which is also a data placeholder. The sample used `NA` for 7 rows.
4. **No padding, no typos.** The sample table holds a trailing-space name, a name ending in a
   non-breaking space, `Artemisia tridenta`, and a name `carex dp` for the code `CAREX SP`. Strip,
   spell-check against the authority, and report the correction.
5. The table is a release file: list it in `Workbook Metadata`, the file index and the process step
   that explains the codes.

## Filling the workbook

1. Copy the template to `<stem>_metadata.xlsx`; never write into the template.
2. For each data table: `read_table()` it, `profile_table()` it, write one attribute row per column
   (`write_attr_blocks()`), and one value-sheet row per value, tokens included.
3. Fill `Workbook Metadata`, `Process Steps`, `Cross References`, `Source Data`, `Data Limitations`
   from what the user and the data supply. What neither supplies — contact details, DOI, process
   date, QA protocol, partner restrictions — goes on an open-items list, kept **beside** the workbook
   (`<stem>_open_items.md`), not as a new sheet inside the intake template.
4. `reconcile_attributes(path, tables, codesets=...)`; resolve or explain every finding
   (`reconciliation.md`).
5. Recompute every number quoted in prose; spell-check; clear every prompt, example and fill.

## Defects measured in the filled-in sample

`reconcile_attributes()` on the sample returned 160 findings (the sample is a work in progress, and
several of these are already visible in the reviewer's comments). Each row maps to a rule in
`SKILL.md`.

| Measured | Check | Rule |
| --- | --- | --- |
| The `Additional Information` prompt unchanged on 58 of 59 documented rows; two example blocks left on `Cross References` and `Source Data` | `template_residue` | 9 |
| 29 species/ground-cover columns collapsed into one row labelled `Light Cyanobacteria to Aspicilia white`; those 29 columns therefore undocumented | `collapsed_range`, `column_undocumented` | 1 |
| `Index` and `PPFD` documented, absent from the table (it holds `PAR`); `Latitude`/`Longitude` documented, absent from the table | `label_not_in_data`, `column_undocumented` | 2 |
| Labels `Tech_Entered `, `Date_Entered `, `total ` carry a trailing space (as does the data header) | `padded_label` | 1 |
| `count` and `total ` each appear twice in one header row | `duplicate_header` | 1 |
| `Lower_canopy` / `Lower_Canopy` (1,289 and 963 rows); `LIT` / `LIT `; `PB` / `PB ` | `case_or_space_variants` | 7 |
| `fire_site` values `L/W/P` and `treatment` values `B/I/T` documented under the wrong attributes; `Transect_ID` defined by 3 letters, 46 composites occur | `values_not_defined`, `defined_not_observed`, `enumerated_without_values` | 6 |
| 7 of 8 `Observer` initials undefined (only `?` is defined); `Recorder` holds `ALF?` (106 rows) and `ELG/ALF` (92 rows) | `values_not_defined`, `uncertain_or_compound_values` | 5, 6 |
| `Slope` is documented as a number but 146 rows hold `5D (down from start?)` and 241 hold `NA` | `mixed_type_column` | 8 |
| `point_number` and `layer_number` share one definition text | `duplicate_definition` | 6 |
| `Transect_Location` (0.3–30.3) carries units `decimal degrees`; the reviewer asked whether they should be metres | `units_vs_name` | 4 |
| `VWC` in m3/m3 documented as 0–7; `BattV` 0–1 V; the sensor columns hold only whole numbers 0–7 with identical counts in `EC`, `TSoil` and `VWC` | `implausible_for_units`, `integer_only_continuous` | 3 |
| 8 columns with blank cells whose meaning is stated nowhere | `blank_cells_undocumented` | 5 |
| `Park Code` vs `Park_Code`, `Notes` vs `notes`, `total` vs `total ` across tables. (`Reader`/`Scribe` against `Observer`/`Recorder` is the reviewer's finding; different names for one concept cannot be detected from the spelling.) | `label_variant_across_tables` | 10 |

The sensor values in the sample copy look like placeholders (small integers with identical value
counts across three different measurements); the documented 0–1 and 0–7 ranges agree with *that*
file, so the check against units is what raised them. Treat the sample's magnitudes as unreliable and
do not generalise from them.

What these checks do **not** catch, and you must still do by hand: a fluent but wrong definition; a
unit magnitude outside the short plausibility table (`m3/m3`, `%`, `°C`, decimal degrees); typos;
prose numbers (transect counts, date spans) and process dates; whether the QA/QC narrative describes
the protocol that was actually used.
