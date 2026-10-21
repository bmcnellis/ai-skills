# Re-running the usage audit

Use this to repeat the 19 Oct 2026 audit or to compare against it.
About 15 tool calls; run it in a fresh, short session (rule 1).

## Access limits that shape the method

- `host.query()` (repl only) is hard-scoped to the current project.
  It gives exact `input_tokens`, `cache_read_tokens`,
  `cache_write_tokens`, `output_tokens` and `total_cost` per frame,
  but only for this project.
- The metadata SQLite is not mounted in the sandbox.
  `~/.claude-science` shows only conda, licenses, orgs, runtime and
  sbx-bind-src, and a host grant on that path is refused. Do not
  retry it.
- `host.frames(project_id="all")` does reach every project's
  transcripts. That is the cross-project route.

## Step 1 — inventory and transcript statistics (repl, one cell)

```python
import json, os, collections
os.makedirs("handoff", exist_ok=True)
frames = host.frames(project_id="all", roots_only=False, max_results=500)["frames"]
stats = {}
for f in frames:
    msgs, off = [], 0
    while True:                                    # paginate every transcript
        d = host.frames(frame_id=f["id"], max_results=500, offset=off)
        got = d.get("messages") or []
        msgs += got
        if not d.get("truncated") or not got: break
        off += len(got)
    run = ctx = n_asst = 0
    tools, per_turn = collections.Counter(), collections.Counter()
    for m in msgs:
        blocks = m["content"] if isinstance(m["content"], list) else [{"type": "text", "text": str(m["content"])}]
        run += sum(len(json.dumps(b)) for b in blocks)   # cumulative transcript size
        if m["role"] == "assistant":
            n_asst += 1; ctx += run                       # ctx_proxy
            tu = [b for b in blocks if isinstance(b, dict) and b.get("type") == "tool_use"]
            if tu: per_turn[len(tu)] += 1
            for b in tu: tools[b["name"]] += 1
    stats[f["id"]] = dict(project_id=f["project_id"], name=f["name"], n_messages=len(msgs),
                          n_assistant=n_asst, ctx_proxy=ctx, tools=dict(tools), per_turn=dict(per_turn))
json.dump(stats, open("handoff/frame_stats.json", "w"))
k = host.query("SELECT id, input_tokens, output_tokens, cache_read_tokens, "
               "cache_write_tokens, total_cost, model, effort FROM frames "
               "WHERE input_tokens IS NOT NULL")
json.dump(k, open("handoff/known_costs.json", "w"))
print(len(stats), "frames;", len(k["rows"]), "metered")
```

Run with `background: true` if there are many sessions. It took under a
second for 31 sessions and 7,605 messages.

## Step 2 — calibrate and extrapolate (python)

```python
import json, numpy as np, pandas as pd
st = pd.DataFrame(json.load(open("handoff/frame_stats.json"))).T
k = json.load(open("handoff/known_costs.json"))
kn = pd.DataFrame(k["rows"], columns=k["columns"]).set_index("id")
j = st.join(kn); j[["n_assistant", "ctx_proxy"]] = j[["n_assistant", "ctx_proxy"]].astype(float)
cal = j.dropna(subset=["total_cost"])
X = cal[["n_assistant", "ctx_proxy"]].values
coef, *_ = np.linalg.lstsq(X, cal["input_tokens"].values, rcond=None)
rate = cal["total_cost"].sum() / cal["input_tokens"].sum()       # $/token, blended
j["est_tok"] = j["input_tokens"].fillna(pd.Series(j[["n_assistant", "ctx_proxy"]].values @ coef, index=j.index))
j["est_cost"] = j["total_cost"].fillna(j["est_tok"] * rate)
```

Validate with leave-one-out on the metered frames before trusting
extrapolation. The 19 Oct fit was 62,289 tokens per turn and 0.455
tokens per ctx_proxy character, with 4.1% median error. Then fit
log(cost) against log(assistant_turns) for sessions over 5 turns; the
19 Oct exponent was 1.43.

## Step 3 — compare

Report against `audit_2026-10-19.md`: share of spend in sessions over
100 turns (was 85%), share of single-call turns (was 93%), host.llm and
host.delegate counts (were 6 and 0), Rscript versus r-kernel calls
(were 156 and 131), and the sizes of the context skills. Metered
sessions in other projects will differ in calibration; re-fit, do not
reuse the 19 Oct coefficients.
