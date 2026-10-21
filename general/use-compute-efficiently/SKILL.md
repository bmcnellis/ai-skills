---
name: use-compute-efficiently
description: "General -- applies across all projects. BEM's measured Claude Science usage habits and the rules that follow from them, from an audit of all 31 sessions on 19 Oct 2026 (~828M input tokens). Session cost grows as turns^1.43, so sessions over 100 assistant turns were 85% of spend; 93% of turns made one tool call; every metered session ran Opus at high effort with no host.llm or host.delegate offload; R ran through Rscript shellouts instead of the persistent r kernel; context skills were monolithic. Load at the start of a long working session, when a session passes ~100 assistant turns or ~18M input tokens, before choosing model or effort, before inventory, file-listing or setup work, before writing or growing a skill, before running R, or when BEM asks about usage limits, cost or efficiency. Holds the session-length check, the restart procedure, and the recipe to re-run the audit."
scope: general
---

# Use compute efficiently

> **Scope — General.** Applies to every project. Carries no project
> specifics; project state belongs in each project's own context skill.

This skill turns one measured audit of BEM's Claude Science usage into
standing rules. The rules are ordered by measured payoff. The numbers
behind them, the method and its caveats are in
`reference/audit_2026-10-19.md`; read it before quoting any figure.

## The five rules, by measured payoff

**1. End a session near 100 assistant turns, then restart from the
context skill.** Every turn re-reads the whole transcript, so session
cost scales as turns^1.43 (R² = 0.97 across all 31 sessions). A turn at turn
100 costs about 1.8× a turn at turn 25, and at turn 400 about 3.2×. The
three sessions over 200 turns were 45% of all spend; one 443-turn
session was 24% by itself. The same work split into sessions of at most
100 turns models out about 34% cheaper. Check the current session with
the snippet below. Past ~100 turns, run the restart procedure rather
than continuing.

**2. Batch independent tool calls into one turn.** 93% of tool-using
turns (2,994 of 3,220) issued a single call. Independent reads, edits,
listings and saves go in the same turn. Because of the 1.43 exponent, a
15% cut in turn count is worth about 21% of cost.

**3. Match model and effort to the task.** Every metered session ran
Opus at `effort: high`. Across 31 sessions there were zero `host.delegate`
calls and six `host.llm` calls. Inventory, path-discovery and setup
sessions were about 24% of spend.

| Work | Tier |
|---|---|
| Directory walks, file inventories, asset listings, environment setup, reformatting | Sonnet-class session, medium effort |
| Classify, extract or summarise across many files | `host.llm(...)` in a cell (Haiku-class by default), or `host.delegate(task, model=<haiku-class>)` |
| Model specification, statistical judgement, interpretation, manuscript prose, skill design | Opus, high effort |

The tier split is a recommendation, not a measured result. Quality on
BEM's own tasks at the lower tiers has not been benchmarked. Delegated
output never enters the main transcript, which also helps rule 1.

**4. Run R in the persistent `r` kernel, not `Rscript` in `bash`.**
There were 156 `Rscript` shellouts against 131 `r` kernel calls. Each shellout reloads packages, re-reads
data and prints startup noise into context. The kernel keeps fitted
models and data frames in memory between calls. Use `bash` for R only
when a clean process is the point, such as a render test or a check
that a script runs top to bottom.

**5. Keep context skills slim.** A skill's `SKILL.md` body stays in the
transcript once loaded and is re-read every turn; files under
`reference/` cost nothing until opened. Several context skills are still
single large files; `manuscript-prose-voice` is the model to follow, and one
context skill was split this way on 19 October 2026, roughly halving its
`SKILL.md` with five triggered `reference/` files and no content dropped.
When a skill passes
about 30 KB:
- Keep in `SKILL.md`: hard rules, paths, function signatures,
  terminology, caveats, current state.
- Move to `reference/`: long specifications, worked examples, data
  dictionaries, and dated history logs ("the run on 7–8 October").
- Give each pointer a trigger: "before editing any figure, read
  `reference/figures.md`", not a bare file list.
- Never move a must-follow rule into `reference/`; it may never be read.

The cost saving from this rule is small, because a loaded skill is
re-read mostly as cached input. The main gains are focus and later
compaction.

## Checking the current session

Run in `repl`. `host.query` is scoped to the current project, which
always contains the current session.

```python
r = host.query("SELECT input_tokens, output_tokens, total_cost, model, effort "
               "FROM frames WHERE id = ?", params=["<current frame id>"])
d = host.frames(frame_id="<current frame id>", max_results=1)
print(r["rows"][0], "messages:", d["total_messages"],
      "~assistant turns:", round(d["total_messages"] / 2.27))
```

The frame id is in the system prompt under Current Context. Thresholds:
100 assistant turns ≈ 18M input tokens; 150 ≈ 33M; 200 ≈ 50M. Messages
run about 2.27 per assistant turn.

## Restart procedure

1. Write current state into the project's context skill (or, for a
   one-off, a dated handoff note in the project's `claude/` directory):
   what was done, what is pending, decisions taken, open questions.
2. `write_memory` any durable fact learned this session.
3. Save every artifact the next session needs.
4. Start a new session. First turn: load the context skill and the
   convention skills it names, then continue.

Tell BEM when a session crosses ~100 turns and offer the restart. The
decision is BEM's.

## What does not save anything

- Splitting small skills (under ~30 KB): the extra read costs more than
  it saves.
- Skipping verification to save turns: the tool-error rate was already
  low (4.7%), and a wrong result costs a whole extra session.
- Asking fewer clarifying questions: user turns were 9% of messages and
  are not where the cost is.

## Reference files

- `reference/audit_2026-10-19.md`: read before quoting any number, or
  when BEM asks how efficient past work was. Session-length effect,
  tool and model use, the token model, the method, all caveats.
- `reference/reaudit.md`: read when BEM asks for a fresh audit or for a
  comparison with this one. The cross-project data route, calibration
  code, and the access limits that force it.

## Note to a future session

The audit could not read the metadata database directly. `host.query`
is hard-scoped to the current project; the SQLite file is not mounted
in the sandbox; a host grant on `~/.claude-science` is refused. Exact
token counts therefore exist only for the project the audit runs in.
Other projects are modelled from their transcripts (fit error ~4%,
modelled cost ±20%). Do not present modelled figures as billing
data. Usage-limit consumption is not exposed anywhere in the store;
cost is the closest available proxy.
