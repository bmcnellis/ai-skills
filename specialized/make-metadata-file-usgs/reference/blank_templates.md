# Blank USGS templates, generated from the samples

Read this **when a USGS template is needed and none was handed over**: to start a software metadata
workbook, a code-to-data table (`Software_Review`), a per-script data-folder table, a species code
table or a seven-sheet data-release workbook from scratch, or to check which cells of a template
are answers. Never write into the samples themselves.

## What exists

USGS supplied only filled-in samples (`<data-root>/claude/templates/usgs_data_release_samples/`).
The generator below rebuilds blank templates from them. It keeps every label, prompt, banner,
header, sheet, merge, column width and style, removes every answer and drops the data-table
sheets. Output: `<data-root>/claude/templates/usgs_blank_templates/`, regenerated 5 Nov 2026.

| Blank | From sample | Sheets | Answers go in |
| --- | --- | --- | --- |
| `Software_Metadata_blank.xlsx` | `PJFIRE_Software_Metadata.xlsx` | `Software Metadata`, `Add Info` | column B beside each label; `Add Info` one row per file |
| `Software_Review_blank.xlsx` | `Copy of Software_Review.xlsx` | `Data` | one row per (script, data file) |
| `Data_for_Rcode_Metadata_blank.xlsx` | `Data_for_Rcode_Metadata.xlsx` | `Sheet1` | one row per data file |
| `SpeciesCode_Metadata_blank.xlsx` | `SpeciesCode_Metadata.xlsx` | `Species Code Metadata` | one row per code |
| `Data_Release_Metadata_blank.xlsx` | `MesaVerde_Metadata.xlsx` | the seven metadata sheets | `Workbook Metadata` column D; `Attribute Metadata` from row 4 in blocks; `Cross References` column D; `Source Data` column C; `Data Limitations` column C beside the statement label |

**These are reconstructions, not USGS originals.** Where an original blank arrives, it wins: compare
its header rows and sheet order with these, and say so if they differ (`SKILL.md`).

## Which cells count as template text

Read from the samples cell by cell (5 Nov 2026), and the basis of the generator:

- **Kept as template text:** column A labels and banners; the yellow prompts (`… [COMPLETE THIS
  SENTENCE]`, `Insert all scientists …`); the `Attribute Metadata` header (row 3) and its column-H
  prompt `The attribute values represent … [Complete this sentence]` (kept once, in row 5); the
  `Process Steps` header text and the `Data Quality Assessment and Quality Control (QAQC)` label;
  the repeated label blocks of `Cross References` and `Source Data`, including the template's own
  `… repeat as necessary or delete` blocks.
- **Kept as template examples** (clear them from a deliverable, rule 9 of `SKILL.md`): `Software
  Metadata` column C (a SAS mussel study, a spotted-owl analysis, `EXAMPLE:` lines);
  `Source Data` column D under `EXAMPLES` (the NED DEM and PRISM normals) and the `For example:`
  hints in column E. Pass `--no-examples` to clear these too.
- **Removed as answers:** `Software Metadata` column B; every row below the header of `Add Info`,
  `Data`, `Sheet1`, `Species Code Metadata` and `Attribute Value Definitions`; `Workbook Metadata`
  columns D-F; the per-table rows of `Workbook Metadata` (two blocks kept, the first named
  `<data table name>`, the second the template's `… repeat as necessary or delete`); every attribute
  row; the per-table process steps and their answers (row 4 becomes `Development of the <data
  table name> data table`) and a citation the sample appended; `Cross References` column D.
- **A trap:** `Data Limitations` column C is headed `EXAMPLE`, but the sample's text under it
  describes the Mesa Verde study. It is that release's statement, not template guidance, and is
  always cleared.
- **Template typos are kept verbatim** because they are the template's text: `Defintion`
  (`Attribute Value Definitions` D1), `ERSI Grid`, a malformed example date `1011923`. Report them
  if a reviewer asks; do not silently correct a header.

## Checks run on the blanks

Each blank read back with `openpyxl`: header rows identical to the sample's, column widths equal
(the seven-sheet file is not compared because its data sheets are dropped), and no
sample-specific text (Mesa Verde, MEVE, PJFIRE, the sample's authors, sites and species codes)
anywhere. Re-run the same three checks after regenerating.

## Use

Copy a blank to the project and fill it there; do not edit the files in `usgs_blank_templates/`.
`open_from_template()` works on these blanks as on the attribute template. For the seven-sheet
workbook write the attribute blocks with `write_attr_blocks()`; it repeats the header from row 3.

## The generator

Saved as `<data-root>/claude/templates/usgs_blank_templates/make_blank_templates.py`. Usage:
`python make_blank_templates.py [SAMPLE_DIR] [OUT_DIR] [--no-examples]`. Loading the seven-sheet
sample takes about 10 s and 1 GB, because of its 97,929-row data sheet.

```python
"""Build blank USGS metadata templates from the cached filled-in samples.

Usage: python make_blank_templates.py [SAMPLE_DIR] [OUT_DIR] [--no-examples]
Defaults: <data-root>/claude/templates/usgs_data_release_samples ->
          <data-root>/claude/templates/usgs_blank_templates

Every label, prompt, banner, header, sheet, merge, column width and style of the samples is
kept; every answer is removed; data-table sheets are dropped. The templates' own example text
(Software Metadata column C, Source Data column D 'EXAMPLES', Data Limitations column C
'EXAMPLE', the yellow prompts) is kept, because it is template guidance; pass --no-examples to
clear it too. Example text must still be cleared from a finished deliverable.
"""
import os, shutil, sys
import openpyxl

SAMPLES = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '<data-root>/claude/templates/usgs_data_release_samples'
OUT = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '<data-root>/claude/templates/usgs_blank_templates'
KEEP_EXAMPLES = '--no-examples' not in sys.argv
SEVEN = ['Workbook Metadata', 'Attribute Metadata', 'Attribute Value Definitions', 'Process Steps - Tabular Data',
         'Cross References', 'Source Data', 'Data Limitations']

def clear(ws, rows, cols):
    for r in rows:
        for c in cols:
            ws.cell(r, c).value = None

def below_header(ws, header_row=1):
    clear(ws, range(header_row + 1, ws.max_row + 1), range(1, ws.max_column + 1))

def software_metadata(wb):
    ws = wb['Software Metadata']
    for r in range(2, ws.max_row + 1):          # B = answers; A = labels and banners (row 1)
        ws.cell(r, 2).value = None
        if not KEEP_EXAMPLES: ws.cell(r, 3).value = None
    below_header(wb['Add Info'])

def seven_sheet(wb):
    for name in list(wb.sheetnames):             # data tables follow the seven metadata sheets
        if name not in SEVEN: wb.remove(wb[name])
    ws = wb['Workbook Metadata']
    clear(ws, range(2, ws.max_row + 1), [4, 5, 6])                  # D (and E, F) = answers
    ds = [r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == 'Dataset Name']
    first = ds[0] + 1                                               # one block per data table: keep two
    rows = [r for r in range(first, ws.max_row + 1) if ws.cell(r, 2).value]
    for k, r in enumerate(rows):
        if k == 0: ws.cell(r, 1).value = '<data table name>'
        elif k == 1: ws.cell(r, 1).value = 'Dataset Name … repeat as necessary or delete'
        else: clear(ws, [r], [1, 2])
    ws = wb['Attribute Metadata']                                   # banner row 1, header row 3
    prompt = next((ws.cell(r, 8).value for r in range(4, ws.max_row + 1)
                   if ws.cell(r, 8).value and '[Complete this sentence]' in str(ws.cell(r, 8).value)), None)
    clear(ws, range(4, ws.max_row + 1), range(1, 9))
    ws.cell(4, 1).value = '<data table name>'
    if prompt and KEEP_EXAMPLES: ws.cell(5, 8).value = prompt
    below_header(wb['Attribute Value Definitions'])
    ws = wb['Process Steps - Tabular Data']                         # banner, header row 3
    qa = next(r for r in range(4, ws.max_row + 1) if str(ws.cell(r, 1).value or '').startswith('Data Quality'))
    clear(ws, range(4, ws.max_row + 1), [2])
    for r in range(4, qa): ws.cell(r, 1).value = None
    ws.cell(4, 1).value = 'Development of the <data table name> data table'
    ws = wb['Cross References']
    clear(ws, range(2, ws.max_row + 1), [3, 4, 5])                  # D = answers (C, E kept empty)
    ws = wb['Source Data']                                          # C = answers ('All fields MUST be completed')
    clear(ws, range(4, ws.max_row + 1), [3])
    if not KEEP_EXAMPLES: clear(ws, range(4, ws.max_row + 1), [4, 5])
    ws = wb['Data Limitations']                                     # answer goes beside the statement label
    clear(ws, [4], [3])
    # column C under 'EXAMPLE' holds the sample release's own statement (it describes that
    # study), not template guidance, so it is always cleared; the instructions in B are kept
    clear(ws, range(8, ws.max_row + 1), [3])

SPECS = {                      # sample file -> (blank file name, blanking function)
    'PJFIRE_Software_Metadata.xlsx': ('Software_Metadata_blank.xlsx', software_metadata),
    'Copy of Software_Review.xlsx': ('Software_Review_blank.xlsx', lambda wb: below_header(wb['Data'])),
    'Data_for_Rcode_Metadata.xlsx': ('Data_for_Rcode_Metadata_blank.xlsx', lambda wb: below_header(wb['Sheet1'])),
    'SpeciesCode_Metadata.xlsx': ('SpeciesCode_Metadata_blank.xlsx', lambda wb: below_header(wb['Species Code Metadata'])),
    'MesaVerde_Metadata.xlsx': ('Data_Release_Metadata_blank.xlsx', seven_sheet),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for src, (dst, fn) in SPECS.items():
        wb = openpyxl.load_workbook(os.path.join(SAMPLES, src))
        fn(wb)
        wb.save(os.path.join(OUT, dst))
        print(dst, wb.sheetnames)
```
