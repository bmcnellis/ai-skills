ATTR_HEADER = ("Dataset Name", "Attribute Label/Columns", "Datatype", "Units/Domain",
               "Min", "Max", "Attribute Definition")
VALUE_HEADER = ("Dataset Name", "Attribute Label/Columns", "Value", "Value Definition",
                "N records", "% of records")
NOTE_HEADER = ("Item", "Value / note")


def profile_table(path, chunksize=1000000, cat_max=200, usecols=None, read_kwargs=None):
    """One chunked pass over a delimited table.

    Returns {'n_rows': int, 'columns': {name: {dtype, n_null, n_unique, values, min, max}}}.
    n_unique/values are None for columns with more than cat_max distinct values. Distinct
    values accumulate across the whole file, so the counts are exact (see SKILL.md Pitfalls).
    """
    import collections
    import pandas as pd
    if read_kwargs is None:
        read_kwargs = {}
    counts = collections.defaultdict(collections.Counter)
    num, wide = {}, set()
    nulls, dtypes, n = collections.Counter(), {}, 0
    for ch in pd.read_csv(path, chunksize=chunksize, usecols=usecols,
                          low_memory=False, **read_kwargs):
        n += len(ch)
        for c in ch.columns:
            s = ch[c]
            nulls[c] += int(s.isna().sum())
            dtypes[c] = str(s.dtype)
            if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
                d = num.setdefault(c, {"min": s.min(), "max": s.max()})
                d["min"] = min(d["min"], s.min())
                d["max"] = max(d["max"], s.max())
            if c in wide:
                continue
            if s.nunique(dropna=False) > cat_max:
                wide.add(c)
                counts.pop(c, None)
                continue
            counts[c].update(s.astype(str).values.tolist())
            if len(counts[c]) > cat_max:
                wide.add(c)
                counts.pop(c, None)
    out = {}
    for c in dtypes:
        d = {"dtype": dtypes[c], "n_null": int(nulls[c]),
             "n_unique": None if c in wide else len(counts[c]),
             "values": None if c in wide else dict(counts[c].most_common())}
        if c in num:
            d["min"], d["max"] = num[c]["min"], num[c]["max"]
        out[c] = d
    return {"n_rows": n, "columns": out}


def suggest_datatype(colprof):
    """Propose a template datatype from one profile_table column entry."""
    dt = str(colprof.get("dtype", ""))
    if dt.startswith("bool"):
        return "logical"
    if dt.startswith("datetime"):
        return "date"
    if dt.startswith("int") or dt.startswith("uint"):
        return "integer"
    if dt.startswith("float"):
        return "numeric"
    return "categorical" if colprof.get("n_unique") is not None else "text"


def enumerate_values(path, columns, delimiters=None, chunksize=1000000, read_kwargs=None):
    """Exact value counts for categorical columns, plus component terms for delimited ones.

    delimiters maps a column name to its separator, e.g. {'objective': ', ', 'tx': ';'}.
    Returns {'n_rows': int, 'columns': {name: {'values': {v: n}, 'components': {t: n}}}}.
    """
    import collections
    import pandas as pd
    if delimiters is None:
        delimiters = {}
    if read_kwargs is None:
        read_kwargs = {}
    cols = list(columns)
    vals = {c: collections.Counter() for c in cols}
    comps = {c: collections.Counter() for c in delimiters}
    n = 0
    for ch in pd.read_csv(path, usecols=cols, chunksize=chunksize,
                          low_memory=False, **read_kwargs):
        n += len(ch)
        for c in cols:
            vals[c].update(ch[c].astype(str).values.tolist())
    for c, sep in delimiters.items():
        for v, k in vals[c].items():
            for part in v.split(sep):
                comps[c][part.strip()] += k
    return {"n_rows": n,
            "columns": {c: {"values": dict(vals[c].most_common()),
                            "components": dict(comps.get(c, collections.Counter()).most_common())}
                        for c in cols}}


def open_from_template(template_path, out_path, sheet=None):
    """Copy the template to out_path and blank its data rows, preserving header formatting.

    Returns (workbook, worksheet, header_values). Save with wb.save(out_path).
    """
    import shutil
    import openpyxl
    shutil.copyfile(template_path, out_path)
    wb = openpyxl.load_workbook(out_path)
    ws = wb[sheet] if sheet in wb.sheetnames else wb[wb.sheetnames[0]]
    header = [c.value for c in ws[1]]
    for r in range(2, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            ws.cell(r, c).value = None
    return wb, ws, header


def write_rows(ws, rows, start_row=2, wrap_cols=None):
    """Write rows of values from start_row, wrapping the 1-based columns in wrap_cols."""
    from openpyxl.styles import Alignment
    if wrap_cols is None:
        wrap_cols = ()
    for i, row in enumerate(rows, start=start_row):
        for j, v in enumerate(row, start=1):
            ws.cell(i, j, v).alignment = Alignment(vertical="top", wrap_text=(j in wrap_cols))
    return ws.max_row


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
    if sheet is None:
        sheet = "Column Metadata"
    ws = openpyxl.load_workbook(out_path)[sheet]
    tot = collections.Counter()
    for r in range(2, ws.max_row + 1):
        lab = ws.cell(r, attr_col).value
        if lab is None:
            continue
        tot[lab] += ws.cell(r, count_col).value or 0
    res = {"totals": dict(tot)}
    if n_rows is not None:
        plain = [k for k in tot if "(component term)" not in str(k)]
        res["ok"] = sorted(k for k in plain if tot[k] == n_rows)
        res["bad"] = sorted((k, tot[k]) for k in plain if tot[k] != n_rows)
    return res
