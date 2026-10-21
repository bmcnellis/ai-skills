import json
import os
import re
import subprocess

PATTERNS = {
    "secret_shape": r"(sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
    "secret_word": r"(?i)\b(api[_-]?keys?|secrets?|passwords?|passwd|bearer|private[_ -]?keys?|credentials?|oauth|access[_-]?tokens?)\b",
    "assignment": r"(?i)\b(key|token|secret|password|pwd)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
    "email": r"[\w.+-]+@[\w-]+\.[A-Za-z][\w.]*",
    "phone": r"(?<![\w.])(\+?\d{1,3}[ .-])?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\w.])",
    "ip": r"(?<![\w.])\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?![\w.])",
    "uuid": r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    "abs_path": r"(/home/[^/\s`'\")]+|/media/[^/\s`'\")]+|/Users/[^/\s`'\")]+|/mnt/[^/\s`'\")]+|[A-Za-z]:\\\\Users\\\\[^\\\\\s]+)",
    "app_id": r"\b(proj|mem|skill|frame|art|ver)_[0-9A-Za-z]{8,}\b",
    "money": r"(?<![\w$])\$\s?\d[\d,]*(\.\d+)?([kKmM]\b)?|\b\d[\d,.]*\s?(USD|dollars)\b",
    "url": r"https?://[^\s)`'\">]+",
}


def git_out(repo, *args):
    """Run git in `repo` and return stdout; raise on failure."""
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + ": " + r.stderr.strip())
    return r.stdout


def public_files(repo):
    """Files git would publish: tracked plus untracked-not-ignored."""
    out = git_out(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    return sorted(f for f in set(out.split("\0")) if f and os.path.isfile(os.path.join(repo, f)))


def is_ignored(repo, relpath):
    """True when git would ignore `relpath` (a file or a directory ending in /)."""
    r = subprocess.run(["git", "-C", repo, "check-ignore", "-q", relpath])
    return r.returncode == 0


def scan_public(repo, extra=None, categories=None, files=None, skip=None):
    """Scan the publishable files. `extra` adds {category: regex}, e.g. project or
    collaborator names; `skip` lists files to leave out (e.g. this kernel.py, whose
    pattern table matches itself). Returns a list of hits {category, file, line, match, text}."""
    pats = dict(PATTERNS)
    if extra:
        pats.update(extra)
    if categories:
        pats = {k: v for k, v in pats.items() if k in categories}
    comp = {k: re.compile(v) for k, v in pats.items()}
    hits = []
    for f in (files or public_files(repo)):
        if skip and f in skip:
            continue
        try:
            text = open(os.path.join(repo, f), encoding="utf-8").read()
        except UnicodeDecodeError:
            hits.append({"category": "binary", "file": f, "line": 0, "match": "", "text": "not UTF-8 text; inspect by hand"})
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for k, p in comp.items():
                for m in p.finditer(line):
                    hits.append({"category": k, "file": f, "line": i, "match": m.group(0), "text": line.strip()[:160]})
    return hits


def summarize_hits(hits, max_locs=3):
    """Compact view: {category: {match: [count, first locations]}}. Print this, not the raw hits."""
    agg = {}
    for h in hits:
        slot = agg.setdefault(h["category"], {}).setdefault(h["match"][:80], [0, []])
        slot[0] += 1
        if len(slot[1]) < max_locs:
            slot[1].append(h["file"] + ":" + str(h["line"]))
    return agg


def write_report(repo, hits, scratch="scratch"):
    """Write the full hit list as JSON into the git-ignored scratch dir; refuse if it is not ignored."""
    if not is_ignored(repo, scratch.rstrip("/") + "/"):
        raise RuntimeError(scratch + "/ is not git-ignored; add it to .gitignore before writing reports")
    os.makedirs(os.path.join(repo, scratch), exist_ok=True)
    path = os.path.join(repo, scratch, "sanitize_scan.json")
    json.dump(hits, open(path, "w", encoding="utf-8"), indent=1)
    return path


def replace_literals(repo, mapping, files=None, scratch="scratch", dry_run=True):
    """Replace each exact string in `mapping` {real: placeholder} across the publishable files.
    Longest keys first. Appends the reversal map to scratch/placeholder_map.json (git-ignored).
    dry_run=True only counts. Returns {file: {real: n}}."""
    if not is_ignored(repo, scratch.rstrip("/") + "/"):
        raise RuntimeError(scratch + "/ is not git-ignored; the reversal map would be published")
    keys = sorted(mapping, key=len, reverse=True)
    changed = {}
    for f in (files or public_files(repo)):
        p = os.path.join(repo, f)
        try:
            text = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        new, counts = text, {}
        for k in keys:
            n = new.count(k)
            if n:
                counts[k] = n
                new = new.replace(k, mapping[k])
        if counts:
            changed[f] = counts
            if not dry_run:
                open(p, "w", encoding="utf-8").write(new)
    if not dry_run and changed:
        os.makedirs(os.path.join(repo, scratch), exist_ok=True)
        mp = os.path.join(repo, scratch, "placeholder_map.json")
        old = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
        old.update({mapping[k]: k for k in keys})
        json.dump(old, open(mp, "w", encoding="utf-8"), indent=1)
    return changed


def history_hits(repo, needles):
    """Commits whose diffs add or remove any of `needles` (git log -S). Sanitizing HEAD does not
    clean history; a hit here means the value is already in published history."""
    found = {}
    for n in needles:
        try:
            out = git_out(repo, "log", "--all", "--format=%h %s", "-S", n)
        except RuntimeError:
            return {"error": "no commits yet"}
        if out.strip():
            found[n] = out.strip().splitlines()
    return found
