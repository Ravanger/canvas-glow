#!/usr/bin/env python3
"""Analyze ngspice .tran print tables from a batch-mode log file.

ngspice paginates wide `print` tables in two ways that both break naive
parsing:
  1. Page breaks within one table reprint the "Index ..." header every ~57
     rows (same columns).
  2. When the requested vectors don't fit one page width, ngspice emits a
     *continuation table* with a different column set that REPEATS the time
     column.

This script merges all tables by row index (skipping the repeated time
column) and analyzes one column as a waveform: edge crossings, estimated
frequency, duty cycle, high/low levels.

Usage:
    parse_tran.py LOGFILE [--col N | --col NAME] [--thresh V]

--col is 0-based in the merged table (0 = time) or a vector name like "v(out)".
"""
import argparse


def load_table(path):
    """Merge paginated/continued print tables. Returns (rows, colnames)."""
    cur = None
    header = None
    tables = []          # column list of each distinct table seen
    for line in open(path):
        if line.startswith("Index"):
            cols = [c.strip() for c in line.split()[1:]]
            if cols and cols != header:
                header = cols
                tables.append(cols)
            continue
        p = line.split()
        if len(p) >= 2 and p[0].isdigit() and header is not None:
            if cur is None:
                cur = []
            idx = int(p[0])
            while idx >= len(cur):
                cur.append([])
            toks = p[1:]
            # continuation tables repeat the time column - skip it
            if len(tables) > 1 and "time" in header:
                ti = header.index("time")
                toks = toks[:ti] + toks[ti + 1:]
            for tok in toks:
                try:
                    cur[idx].append(float(tok))
                except ValueError:
                    pass
    names = []
    for i, cols in enumerate(tables):
        for c in cols:
            if c == "time" and i > 0:
                continue
            names.append(c)
    return (cur or []), names


def analyze(rows, names, col, thresh):
    if isinstance(col, str):
        col = names.index(col) if col in names else None
        if col is None:
            print(f"column {col!r} not found; available: {names}")
            return
    t = [r[0] for r in rows if len(r) > 0]
    v = [r[col] for r in rows if len(r) > col]
    n = min(len(t), len(v))
    t, v = t[:n], v[:n]
    if n < 3:
        print(f"not enough samples in column {col} (got {n})")
        return
    if thresh is None:
        thresh = (min(v) + max(v)) / 2
    t0, t1 = t[0], t[-1]

    edges = []
    last = None
    for i in range(n):
        s = 1 if v[i] > thresh else -1
        if last is not None and s != last:
            edges.append((t[i], s))
        last = s
    rises = [tt for tt, s in edges if s == 1]

    hi = [x for x in v if x > thresh]
    lo = [x for x in v if x <= thresh]
    print(f"column   : {names[col] if col < len(names) else col}")
    print(f"window   : {t0*1e3:.3f} .. {t1*1e3:.3f} ms  ({n} samples)")
    print(f"threshold: {thresh:.3f} V")
    print(f"freq est : {len(edges)/2/(t1-t0):.1f} Hz  ({len(edges)} crossings)")
    if len(rises) > 2:
        periods = [rises[i + 1] - rises[i] for i in range(len(rises) - 1)]
        print("periods  : " + ", ".join(f"{p*1e3:.4f}" for p in periods[:12]) + " ms")
    duty_hi = sum(1 for x in v if x > thresh) / n * 100
    print(f"duty high: {duty_hi:.2f} %")
    if hi:
        print(f"high avg : {sum(hi)/len(hi):.3f} V  (n={len(hi)})")
    if lo:
        print(f"low  avg : {sum(lo)/len(lo):.3f} V  (n={len(lo)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logfile")
    ap.add_argument("--col", default="1",
                    help="merged-table column: int index or vector name (default 1)")
    ap.add_argument("--thresh", type=float, default=None,
                    help="edge threshold in V (default: midpoint of min/max)")
    a = ap.parse_args()
    rows, names = load_table(a.logfile)
    if not rows:
        print("no data rows found (check for 'aborted' / errors in the log)")
        return
    col = int(a.col) if str(a.col).lstrip("-").isdigit() else a.col
    analyze(rows, names, col, a.thresh)


if __name__ == "__main__":
    main()
