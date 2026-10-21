
"""Helpers for ai-disclosure-statement. All names prefixed cds_."""
import os
import re
import datetime
import json
import difflib
import subprocess

CDS_NGRAM = 5
CDS_TRIVIAL_MIN = 10
CDS_DERIVED_CUTOFF = 0.60

# ---------- tokenisation ----------

def cds_norm(s):
    """Normalise a code line for comparison: strip, collapse internal whitespace."""
    return re.sub(r"\s+", " ", s.strip())

def cds_tokens(s):
    """Identifier-like tokens used to block fuzzy candidate search."""
    return {t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.]{2,}", s.lower())}

def cds_words(s):
    """Prose tokens. Hyphens are DELETED, not split on: extractors eat the
    hyphen at a line break, and splitting makes real prose look paraphrased."""
    s = s.lower().replace("-", "").replace("\u2010", "").replace("\u2011", "")
    return re.findall(r"[a-z0-9]+", s)

def cds_ngrams(words, n=5):
    return {tuple(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}

# ---------- indices over what Claude emitted ----------

def cds_build_code_index(emissions, kinds=None):
    """Inverted index of every distinct line Claude emitted (>= 10 chars)."""
    exact, tok2id, lines, owners = {}, {}, [], []
    for j, e in enumerate(emissions):
        if kinds and e.get("kind") not in kinds:
            continue
        for ln in (e.get("text") or "").splitlines():
            n = cds_norm(ln)
            if len(n) < CDS_TRIVIAL_MIN:
                continue
            if n not in exact:
                exact[n] = len(lines)
                lines.append(n)
                owners.append([])
                for t in cds_tokens(n):
                    tok2id.setdefault(t, []).append(exact[n])
            owners[exact[n]].append(j)
    return {"exact": exact, "tok2id": tok2id, "lines": lines, "owners": owners}

def cds_build_prose_index(emissions, n=5):
    """n-gram -> emission indices, over everything Claude wrote."""
    g2e = {}
    for j, e in enumerate(emissions):
        for gr in cds_ngrams(cds_words(e.get("text") or ""), n):
            g2e.setdefault(gr, []).append(j)
    return g2e

def cds_containment(text, g2e, n=5):
    """(fraction of this block's n-grams present in the corpus, top emissions)."""
    gs = cds_ngrams(cds_words(text), n)
    if not gs:
        return 0.0, []
    hit, who = 0, {}
    for gr in gs:
        src = g2e.get(gr)
        if src:
            hit += 1
            for j in src:
                who[j] = who.get(j, 0) + 1
    return hit / len(gs), sorted(who, key=who.get, reverse=True)[:5]

def cds_nearest(idx, n, cutoff=0.60, max_cand=40):
    """Closest Claude-emitted line, searched only among token-sharing candidates."""
    cand = {}
    for t in cds_tokens(n):
        bucket = idx["tok2id"].get(t)
        if not bucket or len(bucket) > 2000:
            continue
        for i in bucket:
            cand[i] = cand.get(i, 0) + 1
    if not cand:
        return None
    top = sorted(cand, key=cand.get, reverse=True)[:max_cand]
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(n)
    best = None
    for i in top:
        sm.set_seq1(idx["lines"][i])
        if sm.real_quick_ratio() < cutoff or sm.quick_ratio() < cutoff:
            continue
        r = sm.ratio()
        if r >= cutoff and (best is None or r > best[1]):
            best = (i, r)
    return best

# ---------- git baseline ----------

def cds_git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True, errors="replace")
    return r.stdout if r.returncode == 0 else None

def cds_baseline_commit(repo, before_ms):
    """Last commit strictly before Claude's first recorded involvement."""
    out = cds_git(repo, "log", "--format=%H %ct", "--date-order")
    if not out:
        return None
    for line in out.splitlines():
        h, ct = line.split()
        if int(ct) * 1000 < before_ms:
            return h
    return None

def cds_rename_map(repo, base):
    """final path -> path at the baseline commit, for files renamed since."""
    out = cds_git(repo, "diff", "--find-renames", "--name-status", base) or ""
    m = {}
    for line in out.splitlines():
        p = line.split("\t")
        if p[0].startswith("R") and len(p) == 3:
            m[p[2]] = p[1]
    return m

def cds_unrecorded_ai_commits(repo, before_ms, pattern=None):
    """Commits advertising AI help that predate the transcript record.
    Non-empty means the measurement understates Claude: say so in the statement."""
    if pattern is None:
        pattern = r"claude|chatgpt|copilot|\bllm\b|\bai\b|gpt|gemini"
    out = cds_git(repo, "log", "--format=%h|%ct|%ad|%s", "--date=short") or ""
    hits = []
    for line in out.splitlines():
        p = line.split("|", 3)
        if len(p) == 4 and re.search(pattern, p[3], re.I) and int(p[1]) * 1000 < before_ms:
            hits.append({"sha": p[0], "date": p[2], "subject": p[3]})
    return hits

# ---------- code attribution ----------

def cds_attribute_file(baseline_text, final_text, idx):
    """Classify every line of final_text. Returns (per_line, counts).

    pre_existing     unchanged since the baseline commit -> the author's
    claude_written   new line, verbatim in Claude's emissions
    claude_modified  replaced a baseline line, verbatim in Claude's emissions
    claude_derived   close variant of a Claude line -> Claude drafted, author rewrote
    user_original    changed since baseline, not traceable to Claude
    """
    b = baseline_text.splitlines() if baseline_text is not None else []
    f = final_text.splitlines()
    bn, fn = [cds_norm(x) for x in b], [cds_norm(x) for x in f]
    sm = difflib.SequenceMatcher(None, bn, fn, autojunk=False)
    per = [None] * len(f)
    regions = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for j in range(j1, j2):
                per[j] = {"cls": "pre_existing", "region": None}
        else:
            regions.append((tag, bn[i1:i2], j1, j2))
    for rno, reg in enumerate(regions):
        tag, bl, j1, j2 = reg
        for j in range(j1, j2):
            n = fn[j]
            if not n:
                per[j] = {"cls": "blank", "region": rno}
            elif len(n) < CDS_TRIVIAL_MIN:
                per[j] = {"cls": "pending_trivial", "region": rno}
            elif n in idx["exact"]:
                cls = "claude_modified" if (tag == "replace" and bl) else "claude_written"
                per[j] = {"cls": cls, "region": rno,
                          "ev": idx["owners"][idx["exact"][n]][:3]}
            else:
                hit = cds_nearest(idx, n)
                per[j] = {"cls": "claude_derived" if hit else "user_original",
                          "region": rno}
    maj = {}
    for p in per:
        if p["region"] is not None and p["cls"] not in ("pending_trivial", "blank"):
            maj.setdefault(p["region"], []).append(p["cls"])
    for p in per:
        if p["cls"] == "pending_trivial":
            v = maj.get(p["region"])
            p["cls"] = max(set(v), key=v.count) if v else "unattributable"
    counts = {}
    for p in per:
        counts[p["cls"]] = counts.get(p["cls"], 0) + 1
    return per, counts

# ---------- prose attribution ----------

def cds_split_markdown(text):
    """Blocks of a .md/.Rmd/.qmd, skipping fenced code chunks and YAML front matter."""
    lines = text.splitlines()
    blocks, buf = [], []
    infence = False
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() in ("---", "..."):
                start = i + 1
                break
    def flush(ln):
        if buf and any(x.strip() for x in buf):
            blocks.append({"kind": "paragraph", "line": ln,
                           "text": "\n".join(buf).strip()})
        del buf[:]
    for i in range(start, len(lines)):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            flush(i)
            infence = not infence
            continue
        if infence:
            continue
        if re.match(r"^#{1,6}\s", ln):
            flush(i)
            blocks.append({"kind": "heading", "line": i, "text": ln.strip()})
            continue
        if not ln.strip():
            flush(i)
            continue
        buf.append(ln)
    flush(len(lines))
    return blocks

def cds_amount(share):
    """Qualitative band for a measured contribution share."""
    for lo, lab in ((0.95, "total"), (0.70, "extensive"), (0.45, "significant"),
                    (0.20, "moderate"), (0.05, "minor")):
        if share >= lo:
            return lab
    return "none"

def cds_classify(share, pre_share):
    """Kind of contribution to one block."""
    if share < 0.05:
        return "none"
    if pre_share < 0.25 and share >= 0.45:
        return "composition"
    if pre_share >= 0.25 and share >= 0.25:
        return "revision"
    return "editing"

def cds_emission_time(e, fmeta):
    """Timestamp interpolated from message position within its session."""
    f = fmeta[e["frame_id"]]
    n = max(1, f.get("n_messages", 1) - 1)
    span = (f.get("updated_at") or f["created_at"]) - f["created_at"]
    return f["created_at"] + span * (e.get("mi", 0) / n)

def cds_curve(records, baseline_words, final_words):
    """Growth curve of the document: (timestamp, fraction of final prose present)."""
    dated = sorted([r for r in records if r.get("t_first")], key=lambda r: r["t_first"])
    cum, pts = baseline_words, []
    for r in dated:
        cum += r["words"]
        pts.append((r["t_first"], min(1.0, cum / max(1, final_words))))
    return pts

def cds_timing(ts, curve):
    """When a contribution landed, read off document completeness BEFORE it.
    Ties share a batch, so one multi-paragraph edit gets one timing."""
    if ts is None or not curve:
        return "n/a"
    comp = 0.0
    for t, c in curve:
        if t < ts:
            comp = c
        else:
            break
    if comp < 0.50:
        return "early drafting"
    if comp < 0.90:
        return "mid revision"
    return "final editing"

def cds_score_document(final_text, baseline_text, g2e, emissions, fmeta, min_words=15):
    """Per-block prose attribution for one document. Returns (records, summary)."""
    blocks = cds_split_markdown(final_text)
    base_g = cds_ngrams(cds_words(baseline_text)) if baseline_text else set()
    base_w = 0
    if baseline_text:
        base_w = sum(len(cds_words(b["text"])) for b in cds_split_markdown(baseline_text)
                     if b["kind"] == "paragraph")
    recs = []
    for k, b in enumerate(blocks):
        w = len(cds_words(b["text"]))
        if b["kind"] == "paragraph" and w < min_words:
            continue
        share, who = cds_containment(b["text"], g2e)
        gs = cds_ngrams(cds_words(b["text"]))
        pre = len(gs & base_g) / len(gs) if gs else 0.0
        ts = [cds_emission_time(emissions[j], fmeta) for j in who] if who else []
        recs.append({"block": k, "kind": b["kind"], "line": b["line"] + 1, "words": w,
                     "share": round(share, 3), "pre_share": round(pre, 3),
                     "type": cds_classify(share, pre), "amount": cds_amount(share),
                     "t_first": min(ts) if ts else None,
                     "opening": " ".join(b["text"].split())[:70]})
    paras = [r for r in recs if r["kind"] == "paragraph"]
    final_w = sum(r["words"] for r in paras)
    curve = cds_curve(paras, base_w, final_w)
    for r in recs:
        r["timing"] = cds_timing(r["t_first"], curve)
    heads = [r for r in recs if r["kind"] == "heading"]
    tot_w = sum(r["words"] for r in recs) or 1
    summary = {
        "n_paragraphs": len(paras), "paragraph_words": final_w,
        "n_headings": len(heads),
        "overall_share": round(sum(r["share"] * r["words"] for r in recs) / tot_w, 3),
        "organization_share": round(
            sum(h["share"] for h in heads) / len(heads), 3) if heads else 0.0,
        "baseline_prose_words": base_w,
    }
    summary["overall_amount"] = cds_amount(summary["overall_share"])
    summary["organization_amount"] = cds_amount(summary["organization_share"])
    for key in ("type", "amount", "timing"):
        summary[key + "_counts"] = {
            v: sum(1 for r in paras if r[key] == v) for v in sorted({r[key] for r in paras})}
    return recs, summary


def cds_code_summary(per_file):
    """Aggregate per-file counts into the exact figures the statement quotes.
    per_file: [{"file": str, **counts from cds_attribute_file}]"""
    keys = ("pre_existing", "claude_written", "claude_modified", "claude_derived",
            "user_original", "unattributable", "blank")
    tot = {k: sum(f.get(k, 0) or 0 for f in per_file) for k in keys}
    total_lines = sum(tot.values())
    nonblank = total_lines - tot["blank"]
    den = max(1, nonblank)
    claude_any = tot["claude_written"] + tot["claude_modified"]
    touched = [f for f in per_file
               if (f.get("claude_written", 0) or 0) + (f.get("claude_modified", 0) or 0) > 0]
    return {
        "n_files": len(per_file), "n_files_touched": len(touched),
        "total_lines": total_lines, "nonblank_lines": nonblank,
        "lines_written": tot["claude_written"],
        "lines_modified": tot["claude_modified"],
        "lines_claude": claude_any,
        "lines_derived": tot["claude_derived"],
        "lines_pre_existing": tot["pre_existing"],
        "lines_user_original": tot["user_original"],
        "lines_unattributable": tot["unattributable"],
        "pct_written": round(100 * tot["claude_written"] / den, 1),
        "pct_modified": round(100 * tot["claude_modified"] / den, 1),
        "pct_claude": round(100 * claude_any / den, 1),
        "pct_claude_incl_derived": round(100 * (claude_any + tot["claude_derived"]) / den, 1),
        "pct_pre_existing": round(100 * tot["pre_existing"] / den, 1),
        "top_files": sorted(
            [{"file": f["file"],
              "claude": (f.get("claude_written", 0) or 0) + (f.get("claude_modified", 0) or 0)}
             for f in touched], key=lambda d: -d["claude"])[:8],
    }


def cds_model_summary(fmeta, emissions=None):
    """Which models produced the work. One row per (model, effort) actually used.

    frames.model is the record of what ran; host.current_model() is only the model
    writing the statement, which is often not the model that did the work. Pass
    emissions to drop sessions that contributed nothing (upload frames carry no model).
    """
    live = {e["frame_id"] for e in emissions} if emissions is not None else None
    agg = {}
    for f in fmeta:
        if live is not None and f["frame_id"] not in live:
            continue
        key = (f.get("model") or "unrecorded", f.get("effort") or "")
        d = agg.setdefault(key, {"model": key[0], "effort": key[1], "sessions": 0,
                                 "first_ms": None, "last_ms": None})
        d["sessions"] += 1
        c = f.get("created_at")
        u = f.get("updated_at") or c
        if c is not None:
            d["first_ms"] = c if d["first_ms"] is None else min(d["first_ms"], c)
        if u is not None:
            d["last_ms"] = u if d["last_ms"] is None else max(d["last_ms"], u)
    rows = sorted(agg.values(), key=lambda d: -d["sessions"])
    for d in rows:
        for src, dst in (("first_ms", "first"), ("last_ms", "last")):
            d[dst] = (datetime.datetime.fromtimestamp(
                d[src] / 1000, datetime.timezone.utc).strftime("%d %B %Y")
                if d[src] else None)
    return rows

def cds_model_sentence(rows):
    """Render cds_model_summary rows as a clause for the statement."""
    parts = []
    for d in rows:
        s = d["model"]
        if d["effort"]:
            s += " at %s effort" % d["effort"]
        s += " (%d session%s" % (d["sessions"], "" if d["sessions"] == 1 else "s")
        if d["first"]:
            s += ", %s" % d["first"]
            if d["last"] and d["last"] != d["first"]:
                s += " to %s" % d["last"]
        s += ")"
        parts.append(s)
    if not parts:
        return "no model recorded"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]
