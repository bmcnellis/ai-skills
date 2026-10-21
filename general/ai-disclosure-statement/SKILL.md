---
name: ai-disclosure-statement
description: "General -- applies across all projects. Generate an auditable statement of Claude's contribution to a project for disclosure, acknowledgement or an AI-use declaration. Measures code contribution as entire lines written and percent of the final code base written or modified, by matching every line of the final files against everything Claude emitted in the recorded sessions, with a pre-Claude git commit as baseline. Measures writing contribution per paragraph and for the document overall: the type (overall organization, outline generation, prose composition, revision, line editing), the timing (early drafting, mid revision, final editing) and a qualitative amount (none, minor, moderate, significant, extensive, total). Load when asked how much of a paper, report, manuscript, script or repository Claude actually wrote, or to draft an AI contribution/authorship/acknowledgement statement."
scope: general
---

# AI disclosure statement

> **Scope — general.** This skill is not tied to any one project. Apply it to any
> project whose work falls under the description above.

Produces a defensible account of what Claude contributed to a finished piece of
work. Every number is computed from the session record and the files themselves;
nothing is estimated. The statement is for disclosure, so the method is built to
**understate rather than overstate** Claude's share, and to declare where it cannot see.

## What it produces

| File | Content |
|---|---|
| `claude_code_contribution.csv` | per file: total, pre-existing, Claude-written, Claude-modified, Claude-derived, author-original lines |
| `claude_writing_contribution.csv` | per paragraph and heading: share, type, timing, qualitative amount |
| `claude_disclosure_statement.md` | the statement itself |

Helpers load automatically from `kernel.py` (all prefixed `cds_`).

## Before starting

Settle three things with the user; do not guess.

1. **What is the end product?** A git repository, a manuscript, one `.Rmd`, a
   package. Everything is measured against *final* files, so the set must be explicit.
2. **Which files count as code and which as writing?** An `.Rmd` is both: code
   chunks go to the code count, narrative blocks to the writing count. Exclude
   vendored or third-party directories, and say so in the statement.
3. **Where is the baseline?** The state of the work immediately before Claude's
   first involvement. Git is the good case. Without git, use the artifact version
   history; with no prior version at all, the baseline is empty and
   `claude_modified` necessarily collapses to zero — declare that.

## Stage 1 — harvest the emission corpus (`repl` tool)

Everything Claude emitted: assistant prose, `edit_file` replacement text, and
code-cell sources. Tool *results* are excluded — they are the user's files and
the environment talking back, not Claude writing.

```python
import json, os
os.makedirs("handoff", exist_ok=True)
PID = "proj_XXXX"                      # target project; host.query(scope="global") to reach others
CODE_TOOLS = {"python", "bash", "r", "repl"}

frames = host.query("""SELECT id, created_at, updated_at, agent_name, model, effort
                       FROM frames WHERE project_id=? ORDER BY created_at""",
                    [PID], scope="global")["rows"]
emissions, fmeta = [], []
for fid, ca, ua, agent, model, effort in frames:
    d = host.frames(frame_id=fid, max_results=500); msgs = d.get("messages", [])
    while d.get("truncated"):
        d = host.frames(frame_id=fid, max_results=500, offset=len(msgs))
        msgs += d.get("messages", [])
    fmeta.append({"frame_id": fid, "created_at": ca, "updated_at": ua,
                  "agent": agent, "model": model, "effort": effort,
                  "n_messages": len(msgs)})   # model/effort: see "Which model" below
    for i, m in enumerate(msgs):
        if m.get("role") != "assistant": continue
        c = m.get("content")
        if isinstance(c, str): c = [{"type": "text", "text": c}]
        for b in c:
            if b.get("type") == "text":
                emissions.append({"frame_id": fid, "mi": i, "kind": "assistant_text",
                                  "path": None, "text": b.get("text", "")})
            elif b.get("type") == "tool_use":
                nm, inp = b.get("name"), b.get("input", {}) or {}
                if nm == "edit_file":
                    emissions.append({"frame_id": fid, "mi": i, "kind": "edit_file",
                                      "path": inp.get("file_path"),
                                      "text": inp.get("new_string", "")})
                elif nm in CODE_TOOLS:
                    emissions.append({"frame_id": fid, "mi": i, "kind": "cell_" + nm,
                                      "path": None,
                                      "text": inp.get("code") or inp.get("command") or ""})

# coverage probe: folded spans and files Claude wrote directly
arch = host.query("""SELECT frame_id, message_count FROM compaction_archives""",
                  scope="global")["rows"]
writes, off = [], 0
while True:                                  # json_extract, never the raw blob (see Gotchas)
    q = host.query("""SELECT e.created_at, json_extract(je.value,'$.path')
                      FROM execution_log e JOIN frames f ON f.id=e.frame_id,
                           json_each(e.files_written) je
                      WHERE f.project_id=? ORDER BY e.created_at
                      LIMIT 200 OFFSET ?""", [PID, off], scope="global", limit=200)
    writes += q["rows"]; off += len(q["rows"])
    if len(q["rows"]) < 200: break

json.dump({"project_id": PID, "frames": fmeta, "emissions": emissions,
           "compaction_archives": [{"frame_id": a, "n": b} for a, b in arch],
           "writes": [{"ts": a, "path": b} for a, b in writes]},
          open("handoff/claude_corpus.json", "w"))
print(len(fmeta), "sessions,", len(emissions), "emissions,", len(writes), "file writes")
```

## Stage 2 — code attribution (`python` tool)

```python
import json, os, pandas as pd
H = json.load(open("handoff/claude_corpus.json"))
REPO = "/path/to/repo"
first_ms = min(f["created_at"] for f in H["frames"])

base = cds_baseline_commit(REPO, first_ms)       # last commit before Claude appears
rmap = cds_rename_map(REPO, base)                # files renamed since: follow them
idx  = cds_build_code_index(H["emissions"])

files = [f for f in cds_git(REPO, "ls-files").splitlines() if f.endswith((".R",".Rmd",".py"))]
files += [f for f in (cds_git(REPO,"ls-files","--others","--exclude-standard") or "").splitlines()
          if f.endswith((".R",".Rmd",".py"))]          # untracked new work counts too
rows = []
for rel in sorted(set(files)):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p): continue
    final = open(p, encoding="utf-8", errors="replace").read()
    per, cnt = cds_attribute_file(cds_git(REPO, f"show", f"{base}:{rmap.get(rel, rel)}"),
                                  final, idx)
    rows.append({"file": rel, **cnt})
CODE = cds_code_summary(rows)
```

Each final line lands in exactly one class:

| Class | Meaning | Counted to |
|---|---|---|
| `pre_existing` | unchanged since the baseline commit | author |
| `claude_written` | **new** line, verbatim in Claude's emissions | **Claude — "entire lines written"** |
| `claude_modified` | replaces a baseline line, verbatim in Claude's emissions | **Claude — "modified"** |
| `claude_derived` | close variant (ratio >= 0.60) of a Claude line | author (Claude drafted, author rewrote) |
| `user_original` | changed since baseline, not traceable to Claude | author |

Lines under 10 characters (`}`, `)`, `#`) carry no evidence on their own and
inherit the majority class of the diff hunk they sit in; a hunk with no
substantive line at all is `unattributable`. The headline percentage is
`pct_claude` = (written + modified) / non-blank final lines. Report
`pct_claude_incl_derived` alongside it as the upper bound.

## Stage 3 — writing attribution (`python` tool)

```python
g2e  = cds_build_prose_index(H["emissions"])
fmeta = {f["frame_id"]: f for f in H["frames"]}
DOC  = "2_report.Rmd"
final_txt = open(os.path.join(REPO, DOC), encoding="utf-8", errors="replace").read()
base_txt  = cds_git(REPO, "show", f"{base}:{rmap.get(DOC, DOC)}")
recs, PROSE = cds_score_document(final_txt, base_txt, g2e, H["emissions"], fmeta)
pd.DataFrame(recs).to_csv("claude_writing_contribution.csv", index=False)
```

Blocks are split on fenced chunks and YAML front matter; code chunks never enter
the prose count. Each block gets a 5-gram containment `share` against Claude's
corpus and a `pre_share` against the baseline document.

**Type** — what kind of contribution:

| Type | Rule | Reads as |
|---|---|---|
| `composition` | `pre_share` < 0.25 and `share` >= 0.45 | Claude supplied the sentences |
| `revision` | `pre_share` >= 0.25 and `share` >= 0.25 | Claude reworked existing text |
| `editing` | `share` >= 0.05, otherwise | phrase-level changes only |
| `none` | `share` < 0.05 | below the detection floor |

**Organization and outline** are measured separately, from the *heading* blocks:
`organization_share` is mean containment across headings. High heading
containment with low paragraph containment is the signature of outline
generation — Claude set the structure and the author wrote the prose. Say that
explicitly when the numbers show it; it is a real and common contribution that a
word count alone misses.

**Timing** — document completeness immediately *before* each contribution landed,
read off the document's own growth curve. Contributions from one edit share a
timestamp and therefore one timing label.

| Timing | Document was |
|---|---|
| `early drafting` | under 50% of its final prose |
| `mid revision` | 50–90% |
| `final editing` | 90% or more |

**Amount** — applied per paragraph and to the document overall, from the
word-weighted share:

| Share | Label |
|---|---|
| >= 0.95 | `total` |
| 0.70–0.95 | `extensive` |
| 0.45–0.70 | `significant` |
| 0.20–0.45 | `moderate` |
| 0.05–0.20 | `minor` |
| < 0.05 | `none` |

The overall document label is `cds_amount(overall_share)` where `overall_share`
is the word-weighted mean over all blocks — headings weight themselves naturally
by length, so no arbitrary constant enters. Report `organization_amount`
separately rather than folding it in.

## Which model produced the work

`frames.model` and `frames.effort` record what actually ran, per session. Use them:

```python
MODELS = cds_model_summary(H["frames"], H["emissions"])   # one row per (model, effort)
cds_model_sentence(MODELS)
# -> "claude-opus-5 at high effort (7 sessions, 29 September 2026 to 08 October 2026)"
```

Do **not** use `host.current_model()` as the source. That is the model writing the
statement, which is frequently not the model that did the work — a disclosure
generated today for work done months ago would name the wrong model. Pass
`H["emissions"]` so sessions that contributed nothing are dropped; upload frames
carry a NULL model and would otherwise show as `unrecorded`.

If several models appear — the model changed between sessions, or sub-agents ran on
a different one — **report all of them and do not try to attribute specific output to
a specific model.** Nothing in the record maps an individual line to the model that
emitted it, and reconstructing it from session boundaries would be guesswork in a
document whose whole purpose is to be auditable. A model with a NULL record is
reported as `unrecorded`, not silently dropped.

## Stage 4 — write the statement

Fill this template from the `CODE` and `PROSE` dicts. Never retype a number —
read it from the dict. Keep the three paragraphs; keep the limitations.

```
**Statement of AI assistance**

Claude was used in the preparation of this work. The contributions described
below were reconstructed from {n_sessions} recorded sessions spanning
{date_first} to {date_last} and measured against {baseline_ref}, the last
revision preceding Claude's first recorded involvement. The work was produced by
{model_sentence}. Where more than one model is listed, no attempt is made to
attribute particular passages to a particular model.

*Code.* The final code base comprises {nonblank_lines} non-blank lines across
{n_files} files, {n_files_touched} of which Claude touched. Claude wrote
{lines_written} entire lines ({pct_written}%) and modified a further
{lines_modified} ({pct_modified}%); Claude therefore wrote or modified
{pct_claude}% of the final code base. A further {lines_derived} lines are close
variants of text Claude produced — passages Claude drafted and the author then
rewrote — which are counted to the author here; including them the upper bound
is {pct_claude_incl_derived}%. The remaining lines predate Claude's involvement
({lines_pre_existing}) or were written by the author afterwards
({lines_user_original}). Claude's contribution was concentrated in {top_files}.

*Writing.* Of {n_headings} section headings, {organization_share:.0%} is
Claude's wording, making his contribution to the organization of the document
{organization_amount}. Across {n_paragraphs} paragraphs ({paragraph_words}
words), Claude composed {n_composition} outright, revised {n_revision}, and made
phrase-level edits to {n_editing}; {n_none} show no detectable contribution.
{n_early} of these contributions landed while the document was under half
written, {n_mid} during revision and {n_final} after it was essentially
complete. Weighted by length, Claude's contribution to the writing of this
document is {overall_amount}. A paragraph-level breakdown is available in
{writing_csv}.

*Basis and limitations.* {limitations}
```

The per-paragraph labels live in the CSV; the statement quotes the counts and
points at it. If the user wants labels in the prose, give the heading-level
rollup rather than 200 paragraph labels.

## Limitations that must always be declared

Write these into the statement, not just into chat. The first two are the ones
that matter and both bias the measurement **downward**:

1. **Attribution is by verbatim and near-verbatim match**, so paraphrase,
   discussion that changed the author's mind, suggested approaches that the
   author implemented, debugging and review all score zero. The figures measure
   text that survives into the final product, not influence.
2. **Only recorded sessions are visible.** Run
   `cds_unrecorded_ai_commits(REPO, first_ms)` — it returns commits whose
   messages advertise AI help but predate the transcript record. If it returns
   anything, say so and name the dates: earlier assistance exists that these
   numbers do not include. Check `compaction_archives` in the harvest likewise,
   and say whether work outside this tool is covered — you cannot know, so the
   statement should say the figures cover recorded sessions only.
3. **Below a 5% containment floor** a block is reported as `none`; short
   paragraphs can match by chance, which is why blocks under 15 words are skipped.
4. **Timing is interpolated** within a session from message position, so it
   resolves to the session, not the minute.
5. **Models are reported per session, not per passage.** The record names the model
   each session ran on; it does not map output to a model, so a multi-model project
   gets the full list and nothing finer.

## Gotchas

- `host.query` clips any cell over 2000 characters, so selecting
  `files_written` or `source` raw returns truncated JSON that fails to parse.
  Project what you need with `json_extract` / `json_each`, and page with
  `LIMIT`/`OFFSET` — the 100k-char total cap silently drops rows otherwise.
- **Follow renames.** A file moved since the baseline looks 100% new and will
  overstate Claude badly. `cds_rename_map` handles it; always pass
  `rmap.get(rel, rel)` to `git show`.
- **Use the working tree, not HEAD**, as the final state — uncommitted work is
  part of the end product.
- Fuzzy matching is blocked on shared tokens. A naive
  `difflib.get_close_matches` against the whole index is ~25x slower; on a
  12,000-line repository expect about 20 s, not 10 min.
- Don't index tool *results*. Claude reading the user's file back does not make
  it Claude's text.
- `edit_file`'s `old_string` is the author's text — index only `new_string`.
