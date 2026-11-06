ATTR_HEADER = ("Dataset Name", "Attribute Label/Columns", "Datatype", "Units/Domain",
               "Min", "Max", "Attribute Definition")
VALUE_HEADER = ("Dataset Name", "Attribute Label/Columns", "Value", "Value Definition",
                "N records", "% of records")
NOTE_HEADER = ("Item", "Value / note")
FULL_ATTR_HEADER = ("Dataset Name", "Attribute Label/Columns", "Units/Domain", "Data Type",
                    "Attribute Value Type", "Attribute values", "Attribute Definition",
                    "Additional Information")
FULL_VALUE_HEADER = ("Data Table", "Attribute", "Attribute Values", "Definition")
# strings that pandas turns into NaN by default; they must be read as text and counted
NA_TOKENS = ("NA", "N/A", "n/a", "na", "NaN", "nan", "NULL", "null", "None", "none", "unknown",
             "Unknown", "UNKNOWN", "?", "-", ".", "-9999", "-999", "9999", "999")
# template prompts and example text that must not survive into a delivered workbook
RESIDUE = ("complete this sentence", "example:", "insert ", "doi add", "have this yet",
           "will insert", "your text here", "[", "tbd")
# (units pattern, lowest plausible, highest plausible); a hit is a prompt to look, not a verdict
PLAUSIBLE = (("m3/m3|m3 m-3|volumetric", 0, 1), ("%|percent", 0, 100),
             ("celsius|celcius|degrees c|°c", -90, 60), ("decimal degrees|latitude", -180, 180))


def read_table(path, sheet=None, read_kwargs=None):
    """Read a CSV or Excel sheet with literal NA/null/None kept as text; blanks become NaN."""
    import pandas as pd
    kw = {"keep_default_na": False, "na_values": [""]}
    kw.update(read_kwargs or {})
    if str(path).lower().endswith((".xlsx", ".xlsm", ".xls")):
        return pd.read_excel(path, sheet_name=0 if sheet is None else sheet, **kw)
    return pd.read_csv(path, low_memory=False, **kw)


def audit_header(path_or_names, sep=",", encoding="utf-8-sig"):
    """Header facts pandas hides: duplicate names (it renames them x.1), padding, blanks."""
    import collections
    import csv
    if isinstance(path_or_names, (list, tuple)):
        row = [str(v) for v in path_or_names]
    else:
        with open(path_or_names, newline="", encoding=encoding) as f:
            row = next(csv.reader(f, delimiter=sep))
    n = collections.Counter(row)
    return {"columns": row, "n": len(row), "duplicates": [k for k, v in n.items() if v > 1],
            "padded": [k for k in row if k != k.strip()],
            "blank": sum(1 for k in row if not k.strip())}


def profile_table(path, chunksize=1000000, cat_max=200, usecols=None, read_kwargs=None):
    """One chunked pass over a delimited table.

    Returns {'n_rows', 'header', 'columns': {name: {dtype, kind, n_null, n_unique, values, min,
    max, tokens, na_like, n_padded, all_whole}}}. Blank cells are counted in n_null and shown as
    '<blank>' in values. Literal NA/null/None strings are kept as text (pandas would erase them):
    they appear in values and na_like. A text column that is >=90% numbers is kind 'numeric' with
    its non-numeric entries (T, NA, 5D ...) in tokens; min/max cover the numeric part only.
    n_unique/values are None above cat_max distinct values; counts are exact (see Pitfalls).
    """
    import collections
    import pandas as pd
    kw = {"keep_default_na": False, "na_values": [""]}
    kw.update(read_kwargs or {})
    counts = collections.defaultdict(collections.Counter)
    tok = collections.defaultdict(collections.Counter)
    nal = collections.defaultdict(collections.Counter)
    st, wide, n = {}, set(), 0

    def canon(k):
        if k is None or (isinstance(k, float) and k != k):
            return "<blank>"
        return str(int(k)) if isinstance(k, float) and k.is_integer() else str(k)

    nulls, pad, kinds = collections.Counter(), collections.Counter(), {}
    for ch in pd.read_csv(path, chunksize=chunksize, usecols=usecols, low_memory=False, **kw):
        n += len(ch)
        for c in ch.columns:
            s = ch[c]
            nulls[c] += int(s.isna().sum())
            d = st.setdefault(c, {"lo": None, "hi": None, "ok": 0, "nb": 0, "whole": True})
            if pd.api.types.is_bool_dtype(s):
                kinds[c] = "bool"
            elif pd.api.types.is_datetime64_any_dtype(s):
                kinds[c] = "datetime"
                d["lo"], d["hi"] = (s.min() if d["lo"] is None else min(d["lo"], s.min()),
                                    s.max() if d["hi"] is None else max(d["hi"], s.max()))
            else:
                v = s.dropna()
                num = v if pd.api.types.is_numeric_dtype(v) else pd.to_numeric(v, errors="coerce")
                good = num.dropna()
                d["nb"] += len(v)
                d["ok"] += len(good)
                if len(good):
                    lo, hi = good.min(), good.max()
                    d["lo"] = lo if d["lo"] is None else min(d["lo"], lo)
                    d["hi"] = hi if d["hi"] is None else max(d["hi"], hi)
                    d["whole"] = d["whole"] and bool((good % 1 == 0).all())
                if not pd.api.types.is_numeric_dtype(v):
                    bad = v[num.isna()]
                    if len(bad) and len(tok[c]) < 60:
                        tok[c].update(bad.astype(str).tolist())
                    txt = v.astype(str)
                    pad[c] += int((txt != txt.str.strip()).sum())
                    nal[c].update(txt[txt.isin(NA_TOKENS)].tolist())
            if c in wide:
                continue
            if s.nunique(dropna=False) > cat_max:
                wide.add(c)
                counts.pop(c, None)
                continue
            for k, nn in s.value_counts(dropna=False).items():
                counts[c][canon(k)] += int(nn)
            if len(counts[c]) > cat_max:
                wide.add(c)
                counts.pop(c, None)
    out = {}
    for c, d in st.items():
        sentinel_only = d["ok"] > 0 and bool(tok[c]) and set(tok[c]) <= set(NA_TOKENS)
        numeric = kinds.get(c) is None and d["nb"] > 0 and (d["ok"] / d["nb"] >= 0.9 or sentinel_only)
        kind = kinds.get(c) or ("numeric" if numeric else "text")
        e = {"dtype": kind, "kind": kind, "n_null": int(nulls[c]),
             "n_unique": None if c in wide else len(counts[c]),
             "values": None if c in wide else dict(counts[c].most_common()),
             "tokens": dict(tok[c]) if numeric else {}, "na_like": dict(nal[c]),
             "n_padded": int(pad[c]), "all_whole": bool(d["whole"]) if d["ok"] else None}
        if kind in ("numeric", "datetime"):
            e["min"], e["max"] = d["lo"], d["hi"]
        out[c] = e
    try:
        hdr = audit_header(path, sep=kw.get("sep", ","), encoding=kw.get("encoding") or "utf-8-sig")
    except (OSError, UnicodeError, StopIteration) as e:
        hdr = {"error": str(e)}
    return {"n_rows": n, "header": hdr, "columns": out}


def suggest_datatype(colprof):
    """Propose a template datatype from one profile_table column entry."""
    kind = colprof.get("kind")
    if kind == "bool" or str(colprof.get("dtype", "")).startswith("bool"):
        return "logical"
    if kind == "datetime" or str(colprof.get("dtype", "")).startswith("datetime"):
        return "date"
    if kind == "numeric":
        return "integer" if colprof.get("all_whole") else "numeric"
    dt = str(colprof.get("dtype", ""))
    if dt.startswith(("int", "uint")):
        return "integer"
    if dt.startswith("float"):
        return "numeric"
    return "categorical" if colprof.get("n_unique") is not None else "text"


def enumerate_values(path, columns, delimiters=None, chunksize=1000000, read_kwargs=None):
    """Exact value counts for categorical columns, plus component terms for delimited ones.

    delimiters maps a column name to its separator, e.g. {'objective': ', ', 'tx': ';'}.
    Literal NA/null strings are kept as values; blank cells are '<blank>'.
    Returns {'n_rows': int, 'columns': {name: {'values': {v: n}, 'components': {t: n}}}}.
    """
    import collections
    import pandas as pd
    kw = {"keep_default_na": False, "na_values": [""]}
    kw.update(read_kwargs or {})
    delimiters = delimiters or {}
    cols = list(columns)
    vals = {c: collections.Counter() for c in cols}
    comps = {c: collections.Counter() for c in delimiters}
    n = 0
    for ch in pd.read_csv(path, usecols=cols, chunksize=chunksize, low_memory=False, **kw):
        n += len(ch)
        for c in cols:
            for k, nn in ch[c].value_counts(dropna=False).items():
                vals[c]["<blank>" if k != k else (str(int(k)) if isinstance(k, float) and k.is_integer() else str(k))] += int(nn)
    for c, sep in delimiters.items():
        for v, k in vals[c].items():
            for part in v.split(sep):
                comps[c][part.strip()] += k
    return {"n_rows": n,
            "columns": {c: {"values": dict(vals[c].most_common()),
                            "components": dict(comps.get(c, collections.Counter()).most_common())}
                        for c in cols}}


def open_from_template(template_path, out_path, sheet=None, header_row=1):
    """Copy the template to out_path and blank the rows below header_row, keeping formatting.

    Returns (workbook, worksheet, header_values). Save with wb.save(out_path).
    """
    import shutil
    import openpyxl
    shutil.copyfile(template_path, out_path)
    wb = openpyxl.load_workbook(out_path)
    ws = wb[sheet] if sheet in wb.sheetnames else wb[wb.sheetnames[0]]
    header = [c.value for c in ws[header_row]]
    for r in range(header_row + 1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            ws.cell(r, c).value = None
    return wb, ws, header


def write_rows(ws, rows, start_row=2, wrap_cols=None):
    """Write rows of values from start_row, wrapping the 1-based columns in wrap_cols."""
    from openpyxl.styles import Alignment
    wrap_cols = wrap_cols or ()
    for i, row in enumerate(rows, start=start_row):
        for j, v in enumerate(row, start=1):
            ws.cell(i, j, v).alignment = Alignment(vertical="top", wrap_text=(j in wrap_cols))
    return ws.max_row


def write_attr_blocks(ws, blocks, header=None, start_row=3, wrap_cols=(7, 8)):
    """Write the multi-dataset Attribute Metadata sheet: per dataset a header row, a bold
    dataset-name row, one row per attribute, then two blank rows. blocks: {dataset: [row tuples
    that start at the Attribute Label column]}. The same header is written on every block."""
    from openpyxl.styles import Alignment, Font
    header = header or FULL_ATTR_HEADER
    r = start_row
    for name, rows in blocks.items():
        for j, h in enumerate(header, start=1):
            ws.cell(r, j, h).font = Font(bold=True)
        ws.cell(r + 1, 1, name).font = Font(bold=True)
        r += 2
        for row in rows:
            for j, v in enumerate(row, start=2):
                ws.cell(r, j, v).alignment = Alignment(vertical="top", wrap_text=(j in wrap_cols))
            r += 1
        r += 2
    return r


def add_sheet(wb, title, header, rows, widths=None, wrap_cols=None, autofilter=True):
    """Add (or replace) a sheet with a bold header, frozen top row and optional autofilter."""
    from openpyxl.styles import Font
    if title in wb.sheetnames:
        del wb[title]
    ws = wb.create_sheet(title)
    for j, h in enumerate(header, start=1):
        ws.cell(1, j, h).font = Font(bold=True)
    write_rows(ws, rows, 2, wrap_cols)
    if widths:
        for j, w in enumerate(widths, start=1):
            ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    ws.freeze_panes = "A2"
    if autofilter and rows:
        ws.auto_filter.ref = "A1:%s%d" % (ws.cell(1, len(header)).column_letter, len(rows) + 1)
    return ws


def check_value_sheet(out_path, n_rows=None, sheet=None, attr_col=2, count_col=5):
    """Read back a value sheet and sum record counts per attribute label.

    Every attribute whose label lacks '(component term)' must sum to n_rows. Returns
    {'totals': {label: sum}, 'ok': [...], 'bad': [...]} when n_rows is given.
    """
    import collections
    import openpyxl
    ws = openpyxl.load_workbook(out_path)[sheet or "Column Metadata"]
    tot = collections.Counter()
    for r in range(2, ws.max_row + 1):
        lab = ws.cell(r, attr_col).value
        if lab is not None:
            tot[lab] += ws.cell(r, count_col).value or 0
    res = {"totals": dict(tot)}
    if n_rows is not None:
        plain = [k for k in tot if "(component term)" not in str(k)]
        res["ok"] = sorted(k for k in plain if tot[k] == n_rows)
        res["bad"] = sorted((k, tot[k]) for k in plain if tot[k] != n_rows)
    return res


def read_attribute_blocks(path, sheet="Attribute Metadata"):
    """Parse an attribute sheet into {dataset: [row dicts keyed by the sheet's own headers]}.

    Handles the one-header simple template (dataset name on every row) and the multi-block data
    release sheet (a header row, a dataset-name row, then attributes, repeated). Each row dict
    also carries 'row' (sheet row number)."""
    import openpyxl
    ws = openpyxl.load_workbook(path)[sheet]
    blocks, cur, cols = {}, None, None
    for i, r in enumerate(ws.iter_rows(values_only=True), start=1):
        r = ["" if v is None else v for v in r]
        a = str(r[0]).strip() if r else ""
        if a == "Dataset Name":
            cols = [str(v).strip() for v in r]
            continue
        if cols is None:
            continue
        b = r[1] if len(r) > 1 else ""
        if a and b == "":
            cur = a
            blocks.setdefault(cur, [])
            continue
        if a:
            cur = a
        if b == "" or cur is None:
            continue
        row = {cols[k]: r[k] for k in range(min(len(cols), len(r))) if cols[k]}
        row["row"] = i
        blocks.setdefault(cur, []).append(row)
    return blocks


def read_value_definitions(path, sheet="Attribute Value Definitions"):
    """Parse the value sheet into {(table, attribute): {value: (definition, row)}}; the table
    name carries down from the last non-blank first-column cell."""
    import openpyxl
    ws = openpyxl.load_workbook(path)[sheet]
    out, table = {}, None
    for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        a, b, c, d = (list(r) + [None] * 4)[:4]
        if a not in (None, ""):
            table = str(a).strip()
        if b in (None, "") or c in (None, ""):
            continue
        if isinstance(c, float) and c.is_integer():
            c = int(c)
        out.setdefault((table, str(b).strip()), {})[str(c).strip()] = (d, i)
    return out


def reconcile_attributes(meta_path, tables, attr_sheet="Attribute Metadata",
                         value_sheet="Attribute Value Definitions", codesets=None, max_enum=25):
    """Compare a metadata workbook with its data, both directions. tables maps each dataset name
    to a DataFrame loaded with read_table() (so NA/null strings survive). codesets maps an
    attribute label to the set of codes a companion file defines (e.g. species codes). Returns
    a list of findings {table, attribute, severity, check, detail}; 'error' means the form and
    the data disagree, 'review' means look and decide. Deliver with no 'error' findings and every
    'review' finding fixed or explained (a documented trace code still shows as mixed_type_column).
    For the three-sheet attribute workbook pass value_sheet="Column Metadata"."""
    import collections
    import re
    import pandas as pd
    codesets = codesets or {}
    blocks = read_attribute_blocks(meta_path, attr_sheet)
    try:
        vdefs = read_value_definitions(meta_path, value_sheet)
    except KeyError:
        vdefs = {}
    F = []

    def add(t, a, sev, chk, detail):
        F.append({"table": t, "attribute": a, "severity": sev, "check": chk, "detail": detail})

    def pick(row, *names):
        for k in names:
            if row.get(k) not in (None, ""):
                return row[k]
        return ""

    seen = collections.defaultdict(set)
    for t, rows in blocks.items():
        df = tables.get(t)
        if df is None:
            add(t, "", "error", "table_missing", "no data table supplied under this dataset name")
            continue
        cols = [str(c) for c in df.columns]
        stripped = {c.strip(): c for c in cols}
        for c in cols:
            m = re.match(r"(.*)\.(\d+)$", c)
            if m and m.group(1) in cols:
                add(t, c, "error", "duplicate_header", "data header repeats %r" % m.group(1))
        labels = [str(pick(r, "Attribute Label/Columns", "Attribute Label")) for r in rows]
        lab_set = {x.strip() for x in labels}
        for c in cols:
            if c.strip() not in lab_set:
                add(t, c, "error", "column_undocumented", "data column has no attribute row")
        defs = collections.defaultdict(list)
        for r, lab in zip(rows, labels):
            key = lab.strip()
            seen[re.sub(r"[\W_]+", "", key.lower())].add(lab)
            text = {k: str(r.get(k, "")) for k in ("Attribute Definition", "Additional Information", "Attribute values")}
            if not text["Attribute Definition"].strip():
                add(t, lab, "error", "definition_blank", "no attribute definition")
            for k, v in text.items():
                if any(p in v.lower() for p in RESIDUE if p != "[") or "[Complete" in v:
                    add(t, lab, "error", "template_residue", "%s still holds template text" % k)
            defs[text["Attribute Definition"].strip()].append(lab)
            if lab != key:
                add(t, lab, "error", "padded_label", "label %r has leading/trailing whitespace" % lab)
            if lab not in cols:
                if key in stripped:
                    add(t, lab, "error", "label_whitespace", "label %r vs data header %r" % (lab, stripped[key]))
                elif " to " in lab:
                    add(t, lab, "error", "collapsed_range", "one row stands for several columns")
                else:
                    add(t, lab, "error", "label_not_in_data", "documented attribute is not a data column")
                if key not in stripped:
                    continue
            s = df[stripped[key]]
            nb = s.dropna()
            nb = nb[nb.astype(str).str.strip() != ""]
            nblank = int(len(s) - len(nb))
            isdate, toks_d = pd.api.types.is_datetime64_any_dtype(s), None
            if not isdate and len(nb):
                dm = nb.map(lambda v: hasattr(v, "month") and hasattr(v, "year"))
                if dm.mean() >= 0.9:
                    toks_d, nb, isdate = nb[~dm].astype(str).value_counts(), pd.to_datetime(nb[dm]), True
            num = pd.Series(dtype=float) if isdate else pd.to_numeric(nb, errors="coerce")
            known = set(vdefs.get((t, key), {})) | {str(v) for v in codesets.get(key, ())}
            numlike = (not isdate) and len(nb) > 0 and (num.notna().mean() >= 0.9 or (
                num.notna().any() and set(nb[num.isna()].astype(str)) <= set(NA_TOKENS) | known))
            dtype = str(pick(r, "Data Type", "Datatype")).lower()
            vtype = str(pick(r, "Attribute Value Type")).lower()
            units = str(pick(r, "Units/Domain", "Units")).lower()
            if toks_d is not None and len(toks_d):
                add(t, lab, "review", "mixed_type_column", "text in a date column: %s" % {k: int(v) for k, v in toks_d.items()})
                miss = {k: int(v) for k, v in toks_d.items() if k not in known}
                if miss:
                    add(t, lab, "error", "undefined_tokens", "not on the value sheet: %s" % miss)
            if nblank and not any(w in (text["Attribute Definition"] + units).lower() for w in ("blank", "missing", "not recorded")) \
                    and not known & {"NA", "<blank>", "blank", "NaN"}:
                add(t, lab, "review", "blank_cells_undocumented", "%d blank cells; definition and value sheet do not say what blank means" % nblank)
            if dtype in ("number", "numeric", "integer") and not numlike:
                add(t, lab, "error", "datatype_mismatch", "declared %s, data is not numeric" % dtype)
            m = re.search(r"Min:\s*([^,]+?)\s*(?:,\s*Max:\s*([^,]+))?\s*$", text["Attribute values"].strip())
            mn, mx = (pick(r, "Min"), pick(r, "Max")) if not m else (m.group(1), m.group(2) or "")
            if isdate and len(nb) and mn != "" and mx != "":
                d1, d2 = pd.to_datetime(str(mn).strip(), errors="coerce"), pd.to_datetime(str(mx).strip(), errors="coerce")
                if pd.isna(d1) or pd.isna(d2) or d1 != nb.min() or d2 != nb.max():
                    add(t, lab, "error", "range_mismatch", "documented %s..%s, data %s..%s" % (mn, mx, nb.min(), nb.max()))
            if numlike:
                good = num.dropna()
                lo, hi = good.min(), good.max()
                toks = nb[num.isna()].astype(str).value_counts()
                if len(toks):
                    miss = {k: int(v) for k, v in toks.items() if k not in known}
                    add(t, lab, "review", "mixed_type_column", "text in a numeric column: %s" % {k: int(v) for k, v in toks.items()})
                    if miss:
                        add(t, lab, "error", "undefined_tokens", "not on the value sheet: %s" % miss)
                try:
                    if mn != "" and mx != "" and (abs(float(mn) - lo) > 1e-9 * max(1, abs(lo)) or abs(float(mx) - hi) > 1e-9 * max(1, abs(hi))):
                        add(t, lab, "error", "range_mismatch", "documented %s..%s, data %s..%s" % (mn, mx, lo, hi))
                except ValueError:
                    pass
                for pat, plo, phi in PLAUSIBLE:
                    if re.search(pat, units) and (lo < plo or hi > phi):
                        add(t, lab, "review", "implausible_for_units", "%s..%s outside %s..%s for %r" % (lo, hi, plo, phi, units.strip()))
                if "decimal degrees" in units and not re.search("lat|lon", lab.lower()):
                    add(t, lab, "review", "units_vs_name", "decimal degrees on a column not named lat/lon (range %s..%s)" % (lo, hi))
                if bool((good % 1 == 0).all()) and good.nunique() <= 12 and not re.search("integer|count|number|index|id|year|record|code", units + lab.lower()):
                    add(t, lab, "review", "integer_only_continuous", "only whole numbers %s..%s but units %r" % (lo, hi, units.strip()))
            elif not isdate and len(nb):
                vc = nb.astype(str).value_counts()
                if nb.nunique() <= max_enum or known:
                    low = collections.defaultdict(set)
                    for v in vc.index:
                        low[v.strip().lower()].add(v)
                    for k, vs in low.items():
                        if len(vs) > 1:
                            add(t, lab, "error", "case_or_space_variants", "%s" % sorted(vs))
                    odd = {v: int(n) for v, n in vc.items() if re.search(r"[?/]|\band\b", v) and v not in known}
                    if odd:
                        add(t, lab, "review", "uncertain_or_compound_values", "%s" % odd)
                if known:
                    und = {v: int(n) for v, n in vc.items() if v not in known}
                    if und:
                        add(t, lab, "error", "values_not_defined", "%d of %d observed values are on neither the value sheet nor a codeset: %s" % (len(und), len(vc), dict(list(und.items())[:12])))
                    gone = sorted(k for k in known if k not in set(vc.index) and k.upper() != "NA" and k not in codesets.get(key, ()))
                    if gone:
                        add(t, lab, "review", "defined_not_observed", "%s" % gone)
                elif nb.nunique() <= max_enum:
                    if vtype == "enumerated":
                        add(t, lab, "error", "enumerated_without_values", "no rows on the value sheet")
                    elif vtype == "unrepresentable":
                        add(t, lab, "review", "few_values_unrepresentable", "%d distinct value(s); enumerate, or reference a codeset" % nb.nunique())
        for d, labs in defs.items():
            if d and len(labs) > 1:
                add(t, "; ".join(labs), "review", "duplicate_definition", d[:80])
    for k, v in seen.items():
        if len({x.strip() for x in v}) > 1 or len(v) > 1:
            add("(all)", "; ".join(sorted(repr(x) for x in v)), "review", "label_variant_across_tables", "same concept, different spelling")
    return F


def list_release_files(root):
    """Every file under root as {folder, file, bytes, junk}. .git and .Rproj.user are reported as
    one junk entry each, not walked. junk marks workspace state that is not part of a release."""
    import os
    import re
    if not os.path.isdir(root):
        raise FileNotFoundError("not a directory: %s" % root)
    out = []
    pat = re.compile(r"^(\.RData|\.Rhistory|\.Rapp\.history|\.Ruserdata|\.DS_Store|Thumbs\.db|\.~lock.*)$")
    for dp, dn, fn in os.walk(root):
        rel = os.path.relpath(dp, root)
        rel = "" if rel == "." else rel.replace(os.sep, "/")
        for d in list(dn):
            if d in (".git", ".Rproj.user", "__pycache__", ".ipynb_checkpoints", ".svn"):
                tot = sum(os.path.getsize(os.path.join(a, b)) for a, _, bs in os.walk(os.path.join(dp, d)) for b in bs)
                out.append({"folder": rel, "file": d + "/", "bytes": tot, "junk": True})
                dn.remove(d)
        for f in fn:
            out.append({"folder": rel, "file": f, "bytes": os.path.getsize(os.path.join(dp, f)),
                        "junk": bool(pat.match(f))})
    return out


def scan_r_io(root):
    """Static scan of R scripts for the files they read and write, the packages they use and any
    hard-coded paths. Returns {'io': [{script, op, call, file}], 'packages': {pkg: n_scripts},
    'hardcoded': [(script, text)]}. A literal-string scan: paths built with paste0() or read from
    config are invisible to it, so a clean result is a lower bound."""
    import collections
    import glob
    import os
    import re
    rd = r"(read\.csv2?|read_csv2?|read\.table|read_delim|read_excel|read_xlsx|readRDS|read_rds|fread|load|source|read\.xlsx|read_tsv|read\.delim)"
    wr = r"(write\.csv2?|write_csv|write\.table|saveRDS|save|ggsave|write_rds|fwrite|write\.xlsx|png|pdf|tiff|jpeg|svg|save\.image|write_xlsx|writeLines)"
    fre = re.compile(r"""["']([^"']+\.(?:csv|rda|rds|RData|rdata|xlsx|xls|txt|tsv|png|pdf|tif|tiff|jpg|html|tex|shp|R))["']""")
    files = sorted(set(glob.glob(os.path.join(root, "**", "*.R"), recursive=True)
                       + glob.glob(os.path.join(root, "**", "*.r"), recursive=True)
                       + glob.glob(os.path.join(root, "**", "*.Rmd"), recursive=True)))
    if not os.path.isdir(root):
        raise FileNotFoundError("not a directory: %s" % root)
    io, pk, hard = [], collections.defaultdict(set), []
    for f in files:
        rel = os.path.relpath(f, root).replace(os.sep, "/")
        if rel.startswith((".git/", ".Rproj.user/")):
            continue
        t = open(f, encoding="utf-8", errors="replace").read()
        for op, rx in (("read", rd), ("write", wr)):
            for m in re.finditer(r"\b(?:\w+::)?" + rx + r"\s*\(([^)]*)\)", t):
                for s in fre.findall(m.group(2)):
                    io.append({"script": rel, "op": op, "call": m.group(1), "file": os.path.basename(s.replace("\\", "/"))})
        for m in re.finditer(r"\buse_data\s*\(([^)]*)\)", t):
            for nm in re.findall(r"\b([A-Za-z_][\w.]*)\b", re.sub(r"overwrite\s*=\s*\w+", "", m.group(1))):
                io.append({"script": rel, "op": "write", "call": "use_data", "file": nm + ".rda"})
        for m in re.finditer(r"(?:library|require)\(\s*[\"']?([A-Za-z][A-Za-z0-9.]+)|\b([A-Za-z][A-Za-z0-9.]+)::", t):
            pk[m.group(1) or m.group(2)].add(rel)
        for m in re.finditer(r"""(?:setwd\([^)]*\)|["'](?:[A-Za-z]:[\\/]|/Users/|/home/|~/)[^"']*["'])""", t):
            hard.append((rel, m.group(0)[:90]))
    seen = set()
    io = [d for d in io if not (tuple(d.values()) in seen or seen.add(tuple(d.values())))]
    return {"io": io, "packages": {k: len(v) for k, v in sorted(pk.items())}, "hardcoded": hard}


def reconcile_file_index(index_path, root, sheet=None, folder_col=0, file_col=1):
    """Compare a hand-written file index (Folder | File name | Description) with the disk.

    Returns {listed, not_on_disk: [(folder, file, closest match)], case_or_space_only: [...],
    folder_listed_as_file: [...], unlisted: [(folder, file)], junk_on_disk: [...]}."""
    import difflib
    import os
    import openpyxl
    ws = openpyxl.load_workbook(index_path)[sheet] if sheet else openpyxl.load_workbook(index_path).worksheets[0]
    disk = list_release_files(root)
    exact = {(d["folder"], d["file"]) for d in disk}
    key = lambda fo, f: (fo + "/" + f).strip("/").lower().replace(" ", "")
    loose = {key(d["folder"], d["file"]) for d in disk}
    names = [d["file"] for d in disk]
    base, cur, listed = os.path.basename(os.path.abspath(root)), "", []
    for r in ws.iter_rows(min_row=2, values_only=True):
        a = r[folder_col] if len(r) > folder_col else None
        b = r[file_col] if len(r) > file_col else None
        if a not in (None, ""):
            cur = str(a).replace("\\", "/").strip().strip("/")
            if cur == base:
                cur = ""
            elif cur.startswith(base + "/"):
                cur = cur[len(base) + 1:]
        if b not in (None, ""):
            listed.append((cur, str(b).strip()))
    res = {"listed": len(listed), "not_on_disk": [], "case_or_space_only": [],
           "folder_listed_as_file": [], "unlisted": [], "junk_on_disk": []}
    for fo, f in listed:
        if (fo, f) in exact:
            continue
        if os.path.isdir(os.path.join(root, fo, f)):
            res["folder_listed_as_file"].append((fo, f))
        elif key(fo, f) in loose:
            res["case_or_space_only"].append((fo, f))
        else:
            near = difflib.get_close_matches(f, names, n=1, cutoff=0.8)
            res["not_on_disk"].append((fo, f, near[0] if near else None))
    lk = {key(fo, f) for fo, f in listed}
    for d in disk:
        if d["junk"]:
            res["junk_on_disk"].append((d["folder"], d["file"], d["bytes"]))
        elif key(d["folder"], d["file"]) not in lk:
            res["unlisted"].append((d["folder"], d["file"]))
    return res


def reconcile_io_matrix(matrix_path, scan, sheet=None):
    """Compare a hand-built code-data matrix (Folder | File name | Data required | Read | Write |
    ...; script cells blank on continuation rows) with scan_r_io() output. Returns
    {'scripts_with_unlisted_files': {script: [files]}, 'listed_not_found_in_code': {...},
     'never_produced': [files read by code that no script writes]}."""
    import collections
    import os
    import openpyxl
    wb = openpyxl.load_workbook(matrix_path)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    listed, cur = collections.defaultdict(set), None
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[1] not in (None, ""):
            cur = str(r[1]).strip()
        d = r[2]
        if cur and d not in (None, "") and str(d).strip().upper() != "NA":
            listed[cur].add(str(d).strip())
    found = collections.defaultdict(set)
    for d in scan["io"]:
        found[os.path.basename(d["script"])].add(d["file"])
    skip = (".tif", ".png", ".pdf", ".tiff", ".jpg", ".html", ".tex")
    un = {s: sorted(f for f in fs if f not in listed.get(s, set()) and not f.lower().endswith(skip))
          for s, fs in found.items()}
    gone = {s: sorted(f for f in fs if f not in found.get(s, set())) for s, fs in listed.items()}
    wrote = {d["file"] for d in scan["io"] if d["op"] == "write"}
    never = sorted({d["file"] for d in scan["io"] if d["op"] == "read"} - wrote)
    return {"scripts_with_unlisted_files": {k: v for k, v in un.items() if v},
            "listed_not_found_in_code": {k: v for k, v in gone.items() if v},
            "never_produced": never}


def reconcile_r_package(root):
    """Cross-check an R package: data/*.rda objects vs their @name entries in R/ vs man/*.Rd pages,
    and packages the code uses vs those DESCRIPTION/NAMESPACE declare. Returns a dict of sets."""
    import glob
    import os
    import re
    rd = lambda p: open(p, encoding="utf-8", errors="replace").read()
    data = {os.path.splitext(os.path.basename(f))[0] for f in glob.glob(root + "/data/*")
            if f.lower().endswith((".rda", ".rdata"))}
    doc = {m for f in glob.glob(root + "/R/*.R") for m in re.findall(r"@name\s+(\S+)", rd(f))}
    pages = {m for f in glob.glob(root + "/man/*.Rd") for m in re.findall(r"\\name\{([^}]*)\}", rd(f))}
    declared = set()
    if os.path.exists(root + "/DESCRIPTION"):
        for fld in ("Depends", "Imports", "LinkingTo"):
            m = re.search(r"^%s:(.*?)(?=^\S|\Z)" % fld, rd(root + "/DESCRIPTION"), re.M | re.S)
            declared |= set(re.findall(r"[A-Za-z][A-Za-z0-9.]*", re.sub(r"\([^)]*\)", "", m.group(1)))) if m else set()
    if os.path.exists(root + "/NAMESPACE"):
        declared |= set(re.findall(r"import(?:From)?\(\s*([A-Za-z][A-Za-z0-9.]*)", rd(root + "/NAMESPACE")))
    used = set(scan_r_io(root)["packages"])
    base = {"base", "stats", "utils", "grid", "methods", "graphics", "grDevices", "tools", "R"}
    return {"data_objects": data, "data_without_doc_entry": data - doc,
            "data_without_rd_page": data - pages, "declared": declared,
            "used_not_declared": used - declared - base - {os.path.basename(os.path.abspath(root))}}
