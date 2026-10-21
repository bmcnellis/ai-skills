# USFS data release (Forest Service Research Data Archive)

Read this *instead of* the USGS template conventions in `SKILL.md` whenever the
destination is the **USDA Forest Service Research Data Archive (RDA)** rather
than a USGS data release / ScienceBase record. The profiling workflow
(`profile_table`, `enumerate_values`, the structural checks, the
never-invent-a-definition rule) is unchanged; the **deliverable is a different
workbook with a different column set**, and the metadata record itself is part
of the same file.

Source: `https://www.fs.usda.gov/rds/archive/submittingData` and the templates
linked from it, retrieved 19 October 2026; combined template stamped
"February 2026 Edition". Field-level guidance lives in the archive's metadata
content guide at `https://www.fs.usda.gov/rds/archive/metavisthelp`. The
templates themselves are cached at
`<data-root>/claude/templates/usfs_rda_2026-02/`. `www.fs.usda.gov` is not
on the sandbox allowlist — `request_network_access` before fetching a fresh
copy, and prefer the cached copies for structure.

## What changes relative to a USGS release

| | USGS workbook (`SKILL.md`) | USFS RDA workbook |
| --- | --- | --- |
| Attribute sheet columns | `Dataset Name, Attribute Label, Datatype, Units/Domain, Min, Max, Attribute Definition` | `Filename, Variable, Units, Precision, Description, Domain Value, Domain Value Description` |
| Datatype column | required, controlled vocabulary | **does not exist** — do not add one |
| Minimum / maximum | required, from the full file | **do not exist** — replaced by `Precision` |
| Enumerated domains | separate `Column Metadata` sheet | **interleaved into the same sheet**, one row per value |
| Multiple data files | one workbook per dataset | one workbook for the whole package, keyed by `Filename` |
| Notes / open items | added `Dataset Notes` sheet | the template's own `Clarification_Notes` sheet |
| File-level record | not covered | `RDA_FileIndex` sheet, every file in the package |
| Discovery metadata | ScienceBase / separate FGDC XML | `RDA_Metadata` sheet, 66 FGDC fields, in the same workbook |
| Standard | FGDC CSDGM | FGDC CSDGM **+ Biological Data Profile (BDP)** |

Consequence for the profiling pass: minima and maxima are still worth computing
— they catch sentinel codes and sign errors — but they go in the `Description`
text or on `Clarification_Notes`, not in columns of their own.

## The deliverable

Fill the **combined template**, `RDA_Metadata_Fileindex_VarDescrips.xlsx`, which
carries all three documents as sheets. Individual templates
(`RDA_VariableDescriptions.xlsx`, `RDA_Fileindex.xlsx`, `Simple_Metadata_Form.docx`,
`_metadata_TEMPLATE.xml` for ArcGIS/Metavist) exist for submitters who prefer
separate files; use them only if asked. A completed `..._EXAMPLE.xlsx` ships
alongside and sets the voice.

Copy the template and fill it in place (`open_from_template` pattern) — the
sheets carry drop-down validations, fill-colour coding and column widths that a
from-scratch workbook loses.

**Every sheet has an instruction paragraph in row 1 and its header in row 2;
data starts at row 3.** `open_from_template()` in `kernel.py` assumes a row-1
header, so pass the header row explicitly or read the header off row 2
yourself. The example rows shipped in the template (`RDA_FileIndex` rows 3–7,
`RDA_VariableDescriptions` rows 3–14) must be **deleted**, not written over
piecemeal — the instructions say so explicitly.

## Sheet 3 — `RDA_VariableDescriptions`

Header (row 2): `Filename | Variable | Units | Precision | Description |
Domain Value | Domain Value Description`

- One row per variable per data file, **in the order the variables appear in
  the file**. `Filename` is the path within the package, e.g.
  `\Data\sitedata.csv`.
- A variable with an enumerated domain gets **one row per observed value**,
  repeating `Filename`, `Variable` and `Description`, with the value in
  `Domain Value` and its meaning in `Domain Value Description`. This replaces
  the USGS `Column Metadata` sheet; do not add a separate value sheet.
- `Units` must be **spelled out in full, no abbreviations** (`decimal degrees`,
  `grams per square metre`, `inches` — not `dd`, `g/m2`, `in`).
- `Precision` is the resolution of the recorded value, written as a number:
  `0.01` for DBH in hundredths of an inch, `1e-06` for coordinates at six
  decimal places. Leave it blank for categorical, text and identifier columns.
  Derive it from the observed decimal places in the profile, and say in the
  `Description` if the recorded precision overstates the measurement precision.
- Date columns: no datatype column exists, so put the format in the
  `Description` (`Date tree DBH was measured (mm/dd/yyyy)`), as the example does.
- Large families of near-identical variables may be collapsed into one generic
  entry (the instructions allow it); state the pattern in the `Description`.
- The `check_value_sheet()` arithmetic check does not apply — the domain rows
  carry no counts. Check instead that every variable in every file appears,
  in file order, and that every distinct value of each categorical variable has
  a `Domain Value` row.

## Sheet 2 — `RDA_FileIndex`

Header (row 2): `Filename | Folder | Description`. Every file in the submission,
including supplements. `Folder` must place each file under `\Data` or
`\Supplements` (subfolders allowed, e.g. `\Supplements\Images`). The
`Description` is one or two sentences and **names the format in words**
("Comma-separated values (CSV) file containing..."). A large set of similar
files may be one generic row with the varying parts bracketed
(`IMAGE_[SITENO]_[YYYY].jpg`, with the ranges given in the description).

## Sheet 1 — `RDA_Metadata`

Header (row 2): `Metadata Section | Field | Value | Description`. 66 FGDC/BDP
fields in five sections, pre-labelled; you fill the `Value` column only. Cell
fills encode status: red = required, yellow = optional, green = pre-filled
default to verify. The `Description` column of an optional field begins with
"(Optional)" — that is the reliable, colour-independent test.

Sections and their fields, in template order:

1. **IDENTIFICATION INFORMATION** — `origin, pubdate, title, geoform, pubplace,
   publish, abstract, purpose, supplinf*, caldate, begdate, enddate, current,
   progress, update, descgeog, eastbc, westbc, northbc, southbc, altunits*,
   altmax*, altmin*, themekey_ISO, themekey_RD, themekey_author, placekey, tax*,
   accconst, useconst,` the data point-of-contact block (`cntorg, cntper,
   cntpos, address, city, state, postal, country, cntvoice, cntemail`),
   `tool*, datacred*, native*, crossref*`
2. **DATA QUALITY INFORMATION** — `attraccr, logic, complete, methtype,
   methdesc, methkey*, methcite*, srccite*, procstep*, cloudcover*`
3. **ENTITY & ATTRIBUTE INFORMATION** — `eadetcit*` (the substance lives in
   sheet 3)
4. **DISTRIBUTION INFORMATION** — `formname`
5. **METADATA REFERENCE INFORMATION** — the metadata point-of-contact block
   (`cntorg_m, cntper_m, cntpos_m, address_m, city_m, state_m, postal_m,
   country_m, cntvoice_m, cntemail_m`)

(`*` = optional.)

Drop-down vocabularies — use the listed term verbatim:

- `geoform`: book chapter, conference proceedings, database, diagrams, document,
  figure, journal article, map, model, multimedia presentation, raster digital
  data, section, spreadsheet, table (non-digital), tabular digital data, vector
  digital data, video. Semicolon-separate multiples; typing your own is allowed.
- `caldate` kind: A single date / Multiple dates / A range of dates / Unknown.
  Give **either** `caldate` **or** `begdate` + `enddate`, never both.
- `current`: Ground condition / Publication date / Observed (or your own text).
- `progress`: Planned / In progress / Complete.
- `update`: Continually, Daily, Weekly, Monthly, Annually, As needed,
  None planned, Unknown, Irregular.
- `methtype`: Field / Lab.
- `altunits`: feet / meters.

Pre-filled defaults to verify rather than rewrite: `pubdate` = publication year,
`pubplace` = `Fort Collins, CO`, `publish` = `Forest Service Research Data
Archive`, `country`/`country_m` = `USA`, `accconst` = `None` (fixed for all RDA
publications; changing it requires archive-team approval), and the standard
`useconst` paragraph releasing the data as US-Government-funded with a citation
request — also fixed language.

Field notes that matter in practice:

- `origin` is `LAST, FIRST MI`, semicolon-separated.
- `title` must differ from the associated article's title.
- Bounding coordinates are decimal degrees, west and south negative in the
  western hemisphere. If the data carry projected coordinates, transform the
  extremes (`pyproj`) to fill these — and note the assumed CRS as an open item,
  per the CRS rule in `SKILL.md`.
- `themekey_ISO` and `themekey_RD` **must** be drawn from the archive's
  controlled lists. You cannot invent them and the lists are not in the
  template — leave them for the data owner and put them on the open-items list.
  `themekey_author` is free.
- `attraccr`, `logic` and `complete` are the natural home for what the profiling
  pass found: QA/QC performed, consistency checks, and every placeholder /
  sentinel code with its row count. The "no missing values" claim gets qualified
  here.
- `methdesc` is expected at dissertation length and must address every variable.
  It is the data owner's to write; do not synthesise it from the data.
- `formname` lists and defines each file format used in the package.

## Sheet 4 — `Clarification_Notes`

Free text, optional in the template, and the right place for everything the
USGS `Dataset Notes` sheet carried: row counts, the row key, derived columns,
constancy and index-reuse findings, the statement that minima/maxima came from
a full pass, and the numbered **OPEN ITEMS** list addressed to the archive team.
Keep the open-items discipline exactly as in `SKILL.md`.

## Accepted formats

Tabular: CSV, TXT, XLSX. GIS: TIF, GPKG (SHP retired in 2021), GDB. Databases:
MDB, SQLite. Documentation: PDF, TXT. Images: JPEG, PNG, TIFF. Audio: MP3.
Video: MP4. Lossless preferred for media. Anything can be submitted and the
archive team converts, but a release prepared in these formats avoids a review
cycle.

## Process context (so the hand-over says the right thing)

- Eligible submitters: Forest Service R&D researchers, Joint Fire Science
  Program-funded researchers, and anyone whose data came from FS R&D funding or
  FS R&D-managed land (Experimental Forests and Ranges, Research Natural Areas).
  Others must contact the archive team first.
- The package is: data file(s); supplements (code, study plans, photos,
  reports); this documentation workbook; and a **signed data submission form**
  (separate FS and non-FS PDFs, required for the first author and the first FS
  author, and signable only in Adobe Acrobat). Submitted by email or Pinyon.
- Review is manuscript-like: the team returns comments that must be resolved,
  the data are converted to archival format, and a DOI is assigned on
  acceptance. Expect the variable descriptions to be read closely.
- There is no submission cost for eligible submitters.

## Carry-overs that do not change

Profile the whole file, never a sample. Verify the row key, derived columns,
constancy and index reuse before describing them. Hunt placeholder codes. Never
invent a unit, a provenance, a CRS or a keyword — write the gap in plain words
and raise it as an open item. Read the written workbook back with `openpyxl`
and check sheet shapes and variable coverage before reporting.
