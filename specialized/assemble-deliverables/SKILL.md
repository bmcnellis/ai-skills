---
name: assemble-deliverables
description: "Project-specific -- ohia1 only; do not apply to other projects unless explicitly asked. Assemble the ohia1 results package: results/ohia1_results_ddmmyyyy_HHMM.zip holding the current results document of the one paper (wound age, then wound dressing) and its two-file supplement, the two metadata workbooks (ohia1_metadata.xlsx, ohia1_rda_metadata.xlsx), the register file the user names, and a generated MANIFEST.txt that explains the file naming and describes every file in one or two sentences. Covers the pre-flight checks (documents current against their stats runs, superseded outputs and annotated copies archived by move, metadata current against its inputs), running claude/build_results_package.py, verifying the manifest, archiving the previous package, and delivering the zip. Load when asked to zip, package, bundle or send the ohia1 results, deliverables or manuscript files, or to add files or a manifest to that package. Load ohia1-context first for the project rules."
---

# Assemble the ohia1 deliverables

> **Scope: ohia1 only.** Paths, names and rules here belong to `<data-root>/ohia1`.
> **Load `ohia1-context` first.** Its rules govern everything below: stamps, the archive,
> the never-edit files, the generators. This skill does not restate them; it is the
> procedure for one task.

The package is built by **`claude/build_results_package.py`**, the single source of the
manifest text. Edit that script, never a zip or a `MANIFEST.txt` by hand.

## 1. What the package holds

| file | from | chosen by |
|---|---|---|
| `ohia1_results_<stamp>.docx` | `results/` | latest stamped run (`latest()`) |
| `ohia1_supplement_<stamp>.docx` and `.xlsx` | `results/` | latest stamped run; must share the document's stamp (asserted) |
| `ohia1_metadata.xlsx`, `ohia1_rda_metadata.xlsx` | `data/` | fixed names (unstamped deliverables) |
| the register, by default the generated `standing_questions.docx` | project root | the `REGISTER` constant |
| `MANIFEST.txt` | generated | written into the zip only |

The glob is `_ddmmyyyy_HHMM.<ext>` exactly, so a `_BEM` copy can never be picked up as a
document. The pattern `ohia1_results_<stamp>.docx` cannot match the package zip
(`ohia1_results_<stamp>.zip`) or a per-experiment document from before the one-paper layout.

`MANIFEST.txt` has a header (package name, assembly time HST, one-paragraph scope), a
**FILE NAMING** list (`ohia1_` prefix, `results_`/`supplement_` of the one paper, the run
stamp, why the metadata is unstamped, `_BEM` and `_claude`, the package name), and a **FILES** list:
one bullet per file, one or two sentences each. **Every count in it (the paper title,
section headings, table and figure ranges, sheet names, open items, release files, `[DRAFT]`
fields, the register's issue date, its Part A count and Part B headings, its annotations) is
read from the packaged file at build time.** `OHIA1_PACKAGE_DRYRUN=1` prints the manifest and
writes nothing; use it before every build. `describe()` raises on a file it has
no branch for; that is deliberate.

## 2. Procedure

Work from the project root. The `repl` kernel cannot see this folder: run all of this in
`python` or `bash`. **Never `rm` here**; archiving is `os.replace`.

1. **Rules.** Load `ohia1-context`. The standing-questions files (`standing_questions.docx`,
   the `_BEM` register the user names) are never modified or moved by this task.

2. **The document current against its stats runs.** The document takes the stamp of the
   three stats runs behind it (`run_date` in `wa_values`, `wd_values` and
   `shigo_cut_values`, which the generator asserts are one stamp). A mismatch means the
   generator was not rerun after the stats scripts: rebuild it first (`ohia1-context`
   reference `manuscript.md`, section 6), and remeasure the AI section if code changed.

```python
import csv, os, sys
sys.path.insert(0, 'claude'); from results_doc_common import latest
TR = 'results/technical_results'
runs = {x: dict(csv.reader(open(latest(f'{x}_values_*.csv', TR))))['run_date']
        for x in ('wa', 'wd', 'shigo_cut')}
doc = os.path.basename(latest('ohia1_results_' + '[0-9]'*8 + '_' + '[0-9]'*4 + '.docx', 'results'))
ok = len(set(runs.values())) == 1 and next(iter(runs.values())) in doc
print(runs, '| document', doc, '| OK' if ok else '| RERUN THE STATS SCRIPTS TOGETHER AND REBUILD')
```

3. **Archive what a later run or issue replaced.** `results/` keeps only the latest of each
   output. That includes the tables, figures and technical files of a rerun, and every annotated
   copy (`_BEM`, `_BEM_claude`) of a superseded issue. An annotated copy of the *current* issue
   stays. Before archiving an annotated copy, check that it has its `_BEM_claude` answer copy
   (review loop, `manuscript.md` section 5). Dry-run first and read the list:

```python
import os, re, collections
STAMP = re.compile(r'_(\d{2})(\d{2})(\d{4})(?:_(\d{4}))?(?=[._])')
def skey(m): return (int(m.group(3)), int(m.group(2)), int(m.group(1)), int(m.group(4) or 0))
def superseded(paths):
    """Files in results/ that a later run or issue has replaced. An annotated copy
    (<doc>_<stamp>_BEM.docx, ..._BEM_claude.docx) goes when its document has a later issue."""
    runs = collections.defaultdict(list)          # stem without stamp -> [(key, path)]
    notes = []                                     # (stem, key, path) of annotated copies
    for p in paths:
        d, f = os.path.split(p); m = STAMP.search(f)
        if not m: continue
        tail = f[m.end():]
        if re.match(r'_BEM', tail):
            notes.append((os.path.join(d, f[:m.start()] + os.path.splitext(f)[1]), skey(m), p))
        else:
            runs[os.path.join(d, f[:m.start()] + tail)].append((skey(m), p))
    out = []
    for v in runs.values():
        v.sort(); out += [p for _, p in v[:-1]]
    for stem, k, p in notes:
        if stem in runs and max(runs[stem])[0] > k: out.append(p)
    return sorted(out)

plan = superseded([os.path.join(dp, f) for dp, _, fs in os.walk('results') for f in fs])
print(*plan, sep='\n')
```

   Then move the reviewed `plan`. **Move, never copy**: a copied file is still in
   `results/`, which is the mistake this step exists to prevent. An archive file of the same
   name must be byte-identical, or the cell stops.

```python
import csv, datetime, hashlib, os, zoneinfo
stamp = datetime.datetime.now(zoneinfo.ZoneInfo('Pacific/Honolulu')).strftime('%d%m%Y_%H%M')
ARC = 'archive/results_archive'
assert plan, 'nothing to archive; write no move log'
h = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
moves = [(p, os.path.join(ARC, os.path.relpath(p, 'results'))) for p in plan]   # plan: the reviewed list
for s, d in moves:                       # check everything before moving anything
    assert os.path.exists(s), s
    assert not os.path.exists(d) or h(s) == h(d), f'different file already archived: {d}'
for s, d in moves:
    os.makedirs(os.path.dirname(d), exist_ok=True)
    os.replace(s, d)                     # a move: the source is gone afterwards
man = f'{ARC}/moved_to_archive_{stamp}.csv'
assert not os.path.exists(man)
with open(man, 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['file', 'from', 'to', 'moved', 'reason'])
    for s, d in moves:
        w.writerow([os.path.basename(s), s, d, stamp, 'superseded by a later run or issue'])
print(len(moves), 'moved;', man)
```

4. **Metadata current against its inputs.** The workbooks describe the datasets, not the
   results documents, so a stats rerun alone does not stale them. Rebuild only if an input is
   newer. The rebuild runs through the `make-metadata-file-usgs` helpers by `exec()`
   (`ohia1-context` section 9); copy the old workbooks to
   `archive/results_archive/ohia1_metadata_<stamp>.xlsx` and `ohia1_rda_metadata_<stamp>.xlsx` first.

```python
import glob, os
wb = min(os.path.getmtime(f) for f in ('data/ohia1_metadata.xlsx', 'data/ohia1_rda_metadata.xlsx'))
inputs = (['data/provided/ohia_wound_studies_master_dataset_2026_02-20.csv',
           'data/provided/ohia_wound_environmental_metadata_2026-02-20.csv',
           'data/provided/Trial Dates and Environmental Data_2026-10-19.xlsx',
           'data/ohia_wound_studies_analysis_dataset.csv', 'data/ohia_wound_trials.csv',
           'data/ohia_wound_environmental_daily_temperature.csv',
           'results/technical_results/provided_vs_master_summary.csv']
          + glob.glob('results/technical_results/detection_methods_values_*.csv'))
newer = [f for f in inputs if os.path.getmtime(f) > wb]
print('metadata current' if not newer else f'REBUILD the metadata workbooks; newer inputs: {newer}')
```

5. **Register.** Set `REGISTER` in `claude/build_results_package.py` to the register file
   the user names (by default the generated `standing_questions.docx`; an annotated `_BEM`
   copy works too). `describe()` reads the issue date, the Part A count, the Part B headings
   and any annotations by BEM or a collaborator from the file, so a new issue needs no edit unless its
   headings change ('Part A. Questions for the people who collected the data', a heading
   starting 'Part B. ', and 'Where the rest of the questions live' are required).

6. **Build.** Dry-run first (`OHIA1_PACKAGE_DRYRUN=1 python3 claude/build_results_package.py`,
   or set the variable in `os.environ` from python if the shell rejects the prefix), read the
   manifest, then `python3 claude/build_results_package.py`. It asserts the zip does not exist,
   so a second build in the same minute stops. Wait for the minute to turn rather than
   working around it.

7. **Verify.** `unzip -l` the package and `unzip -p <zip> MANIFEST.txt`. Read every
   description against its file: a count is read from the file, but the prose around it
   (what the experiment tests, the register's Part B topics) is typed. No em dashes.

8. **Archive the previous package.** The dry run in step 3 lists it once the new one exists
   (same stem, older stamp). Move it with the same cell. A draft package the user never saw
   goes the same way, with a reason saying so.

9. **Deliver.** Copy the zip (and `MANIFEST.txt`, extracted) into the session workspace,
   `save_artifacts`, and link the returned version ids. Give the host path too.

10. **Record.** Append a dated entry to `ohia1-context` `reference/changelog.md` (package name,
    what was archived, whether the metadata was rebuilt), publish, and rewrite
    `claude/ohia1-context/` from the published content.

## 3. Changing the manifest

- A new kind of file: add it to `FILES` and a branch to `describe()` that reads its counts
  from the file. Keep each description to one or two sentences.
- A changed naming convention: edit the `NAMING` list. The convention itself lives in
  `ohia1-context` section 10; change it there first.
- `captions()` accepts `Figure N.` or `Figure N:`; the 2025 captions used a colon, and an
  older document in the archive may still be packaged for comparison.

## 4. Pitfalls

- **The one-paper layout (27 October 2026)** replaced two per-experiment documents with one;
  the two-document builder is `archive/code_archive/build_results_package_20102026.py`, and
  the per-experiment documents of 20 October are in `archive/results_archive/`.
- **A renamed output is invisible to the step 3 detector**, which pairs files by stem: when
  the figure files were renamed by number (30 October 2026), the 30 files under their old
  names had no later version of the same name and were added to the move list by hand. After
  any rename, list `results/` for stems the latest run did not write.

Met building the first package (20 October 2026):

- **Copying instead of moving** left superseded supplements in `results/`. The move cell's
  `os.replace` and the dry run's empty list are the check.
- **A partial package**: only one experiment and no metadata. The precedent
  (`archive/ohia1_results_14102026.zip`) is both experiments, metadata and register; the
  builder now encodes it.
- **Reusing a kernel variable name** (`new`) clobbered a file list between cells; read lists
  back from disk, and keep the assert-before-move order so a bad list moves nothing.
- **LibreOffice does not run in this sandbox** (`soffice` aborts), so documents cannot be
  rendered to check layout; verify structure from the XML instead.
