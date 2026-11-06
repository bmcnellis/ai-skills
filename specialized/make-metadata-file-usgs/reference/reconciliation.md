# Reconciliation: metadata against data, and against a reviewer

"Reconciliation" means two things in a USGS data release, and a hand-over needs both:

1. **The reviewer's reconciliation.** A qualified reviewer reads the metadata against the data,
   writes comments in a review form, and the author answers each comment (and changes the data or
   the metadata) until nothing is open. Section 1 below.
2. **The author's own reconciliation**, done *before* review: every statement on the form is
   checked against the file, in both directions. Section 2 below, and `reconcile_attributes()`.

A third comparison, of released **code** with released **data**, is in `software_release.md`.

Policy basis (US Geological Survey Manual, Fundamental Science Practices): SM 502.7 sets the
metadata requirements, SM 502.8 the review and approval of data for release; at least one metadata
review by a qualified reviewer is required; the record follows FGDC CSDGM or ISO 19115; the
reviewer validates the XML with the Metadata Parser; review documents and reconciliations are kept in
USGS's internal systems. Pages: `usgs.gov/survey-manual/5027-fundamental-science-practices-metadata-usgs-scientific-information-products`,
`usgs.gov/survey-manual/5028-fundamental-science-practices-review-approval-and-release-usgs-scientific-data`,
`usgs.gov/data-management/metadata-review`. Local practice (a centre's form, a data steward's
conventions) can differ; the sample below is one centre's form.

## 1. The reviewer's form (as seen in the sample)

**Anatomy.** A Word document titled `<centre> metadata Review reconciliation`. A header block of
labelled lines: date, information-product (IP) number, date approved, project, senior scientist,
metadata file name (the `.xml`), data file names, reviewer. A statement that the responses meet FGDC
content standards and USGS quality standards (SM 502.7). The instruction: *provide responses in the
"Response" section only, in blue text.* Then a run of numbered review items, each a question in
red bold italics, a `Comment:` by the reviewer, the specific tables and attributes concerned, and a
`Response:` block, items separated by lines of asterisks. Measured on the sample: reviewer question
text red (`FF0000`), responses and the reviewer's per-item prompts blue (`0070C0`), one reply in a
lighter blue (`5B9BD5`) — keep to the one blue.

**The review points in the sample (numbered here for reference; the form itself is unnumbered), and what each demands.**

| # | Reviewer's question | Typical comment | What a complete response contains | Where it lands in the workbook |
| --- | --- | --- | --- | --- |
| 1 | Is each field described, with units? Are attribute descriptions detailed enough? (Entity & Attribute) | "described, but additional information is needed": min/max of 12 sensor attributes queried; a unit queried (a transect position labelled in decimal degrees) | for each queried value: the true full-file extreme and the unit, or the corrected data table | `Attribute values`, `Units/Domain`; data re-issued if values were wrong |
| 2 | Are coded values explained by a data dictionary, with references? (Codeset) | six-letter species codes are not USDA PLANTS symbols; complete the species code file (scientific name, common name, USDA symbol) | the companion code table, covering **every** code in the data, with the authority's symbol | companion file; `Attribute Definition`; `Workbook Metadata` |
| 3 | Consistent structure and attribute names across the data tables? | a side-by-side list of two tables' columns: `Reader`/`Scribe` against `Observer`/`Recorder`; `Park Code` against `Park_Code` is visible in the same list | a two-column old → new name list per table, and the re-issued tables | data tables, `Attribute Metadata`, `Attribute Value Definitions` |
| 4 | Processing steps fully described, with approximate dates? | steps describe field set-up, not how the table was compiled; no process date | for each table: collection, compilation, process date `YYYY` | `Process Steps - Tabular Data` |
| 5 | QA/QC adequately described? | text is vague; `Tech_Checked` / `Date_Checked` columns exist and must be explained | separate **QA** (prevention) and **QC** (checking) paragraphs and one QAQC process date; the check protocol behind each check column | QAQC row of `Process Steps` |
| 6 | Published protocols cited in full? | cite with DOI or URL | full citations | closing row of `Process Steps`; `Cross References` |

**Writing the responses.**

1. Answer inside the `Response:` block only, in blue, under the same table and attribute headings the
   reviewer used. Quote the question you answer if the block has several.
2. **Answer every question and sub-question.** In the sample copy two queries have nothing written
   under them (the min/max correctness question for 12 attributes; whether the transect-position
   unit should be metres), and the processing-step response covers two of the three tables the
   reviewer named. An unanswered query is an open finding.
3. When the answer is "the data change", supply the revised table; when it is "the metadata change",
   name the sheet and attribute. Never answer a data question by editing only the form.
4. Renames are a table of old → new names; apply them in the data, the attribute sheet and the value
   sheet together, then re-run `reconcile_attributes()`. The sample's answer renames `Reader` and
   `Scribe` only; the `Park Code` / `Park_Code` difference in the same list is not addressed.
5. Give a process date (`YYYY`) for every step the reviewer named, and for the QAQC step. Check it
   against the data's last date.
6. Restate every count from the data you are shipping. The sample's reviewer counted 58 and 20 codes
   in two columns; the copy of the data in hand holds 65 and 23 distinct values after stripping spaces — the data changed,
   or the count was off. Either way the response must carry the current number.
7. Leave header-block fields that only the user or the centre can supply (IP number, approval date,
   reviewer, project name) as the user gives them; never copy them from a sample.

## 2. The author's reconciliation: `reconcile_attributes()`

```python
tables = {"table_a": read_table("a.csv"), "table_b": read_table("b.csv")}   # keeps NA/null text
F = reconcile_attributes("out.xlsx", tables, codesets={"species": codes})   # list of dicts
import pandas as pd; pd.DataFrame(F).groupby(["severity", "check"]).size()
```

Works on the seven-sheet workbook (default sheet names) and on the three-sheet workbook
(`value_sheet="Column Metadata"`). `severity` is `error` when the form and the file disagree and
`review` when a person must look. Deliver with **no errors**, and every review finding either
fixed or explained in the hand-over.

| Check | Fires when | Usual resolution | Whose decision |
| --- | --- | --- | --- |
| `table_missing` | a dataset in the sheet has no data supplied | pass the table, or the dataset is not in the release | you |
| `duplicate_header` | the data header repeats a name (`count`, `count.1`) | rename in the data | owner |
| `column_undocumented` | a data column has no attribute row | add the row, or drop the column | owner (drop) |
| `label_not_in_data` | an attribute row names no data column | remove the row, or the column was withheld/renamed | owner |
| `label_whitespace`, `padded_label` | label differs from the header by spaces, or carries them | fix the header in the data and the label together | owner |
| `collapsed_range` | one row stands for several columns (`A to Z`) | one row per column | you |
| `definition_blank`, `template_residue` | no definition, or prompt/example text remains | write it, or list as open item | you |
| `datatype_mismatch` | `Data Type` says number, data is not numeric | correct the type, or fix the data | you / owner |
| `range_mismatch` | documented min/max differ from the file (numbers and dates) | re-copy from the profile | you |
| `undefined_tokens` | text in a numeric/date column is not on the value sheet | add each token with its meaning | owner for meaning |
| `values_not_defined`, `enumerated_without_values` | observed values missing from the value sheet (or codeset) | add rows, or point to the companion file | owner for meaning |
| `case_or_space_variants` | `A`/`a`/`A ` both occur | merge in the data, or document both | owner |
| `mixed_type_column` *(review)* | text tokens in a numeric/date column | document in the definition and on the value sheet; remains as a review item | you |
| `blank_cells_undocumented` *(review)* | blanks, with no statement of what blank means | say it in the definition | owner for meaning |
| `implausible_for_units` *(review)* | range outside the plausibility table for the unit | check the unit, then the data | owner |
| `units_vs_name` *(review)* | `decimal degrees` on a column not named lat/lon | correct the unit | you / owner |
| `integer_only_continuous` *(review)* | a continuous-looking column holds only whole numbers | ask whether values were rounded or are codes | owner |
| `uncertain_or_compound_values` *(review)* | `?`, `/`, `and` inside values | define the convention, or split the data | owner |
| `defined_not_observed` *(review)* | defined values that do not occur | wrong attribute, wrong table, or state the reason | you |
| `few_values_unrepresentable` *(review)* | few distinct values but `unrepresentable` | make it `enumerated`, or reference a codeset | you |
| `duplicate_definition` *(review)* | two attributes share one definition text | write each separately | you |
| `label_variant_across_tables` *(review)* | the same name differently spelled in two tables | one spelling | owner |

`PLAUSIBLE` in `kernel.py` is deliberately short (`m3/m3`, `%`, `°C`, decimal degrees). It raises
questions; it does not prove a value right. Add units to it when you meet a quantity whose range is
physically bounded.

**Worked example.** On the sample workbook against its own data sheets: 160 findings — 32 columns
undocumented, 4 attribute rows naming no column, 58 rows with the unfilled `Additional Information`
prompt, 6 value-coverage errors, 3 case/space-variant errors, and review items including a
volumetric water content of 0–7 m3/m3 and a transect position labelled in decimal degrees. A
negative control (changing one altitude and one timestamp in the data) is caught by `range_mismatch`
in both numbers and dates; a workbook that documents a trace code properly produces only the
`mixed_type_column` review item, and removing the token's value-sheet row turns it into
`undefined_tokens`. Run such a control on any new workbook shape before trusting a clean result.

## 3. Decision log

Findings that belong to the owner are written up, not resolved by the agent. Keep a log beside the
workbook (`<stem>_reconciliation.md`):

| # | Finding (check, table, attribute) | Evidence (counts from the file) | Options | Owner's decision | Applied in (data / metadata / both) | Re-checked |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `label_not_in_data`, table, `Latitude` | absent from the table | keep and add column / withhold and remove row | withheld per partner request | metadata; data already without | clean |

Recommended statements in the hand-over: what was changed, what was withheld and why (never the
withheld values), what is still open.

## 4. What this does not do

- It does not decide a rename, a drop, a withheld column or a corrected value. Those are the data
  owner's, and a reviewer will ask who decided.
- It does not certify FGDC compliance. The XML record is validated downstream.
- It does not read prose: counts and dates in abstracts, process steps and limitation statements must
  be recomputed by hand against the data (`SKILL.md`, rule 11).
