"""Check LOCALLY whether the holds of the paper also appear in an archive of MES transaction files, and if so,
use those files for hold comments and for the share of cycle time spent on hold. Nothing confidential is printed.

    python scripts/run_match_txn.py --line A=config/local_lineA.yaml --line B=config/local_lineB.yaml --txn <archive_folder> --out results_match_txn

The archive is searched for csv / xls / xlsx files (also inside zip files) that have a lot column with the same name
as in the line's config, a transaction time column (TXN_TIME1 or similar), and optionally DETAIL_COMMENT* and
WAIT_TIME / WAIT_TIME_WITHOUT_HOLD / RUN_TIME / RUN_TIME_WITHOUT_HOLD columns. A paper hold is matched when the
same lot has a transaction at the same minute as the hold start.

Shareable output (results_match_txn/match_txn.csv, .md): only shares and counts per line and per anonymised reason
label (R01, R02, ... as in the paper). No file names, plant codes, dates, lot ids, codes, or comment text.
local_only/LOCAL_ONLY_nonescalable_holds.csv lists the paper holds whose comment points to a customer decision,
an engineering change, or material (lot and start time); run_warmup.py --nonescalable uses it. Do not share it.
"""
from __future__ import annotations
import argparse, io, os, re, sys, time, zipfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from holdesc.io import load_config, load_holds                  # noqa: E402
import run_warmup as WU                                         # noqa: E402
from run_raw_extras import classify, CATS                       # noqa: E402

ROWS = []
NONESC = ("customer decision", "engineering change", "material")
FLAGS_STARTED = False
ALL_LOTS: set = set()
FMTS: list = []
DIAG = {"lot_overlap": 0, "rows_lot_match": 0, "rows_time_ok": 0}


def parse_time(s):
    """Try the formats of the paper configs, common MES formats, and Excel serial days; keep the best."""
    s = s.astype(str).str.strip()
    best = pd.Series(pd.NaT, index=s.index)
    tries = [(f, n) for f, n in FMTS] + [(None, 19), ("%Y%m%d %H%M%S", 15), ("%Y%m%d%H%M%S", 14),
                                         ("%Y/%m/%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M:%S", 19)]
    for f, n in tries:
        try:
            t = pd.to_datetime(s.str.slice(0, n or 30), format=f, errors="coerce")
        except (ValueError, TypeError):
            continue
        if t.notna().sum() > best.notna().sum():
            best = t
    num = pd.to_numeric(s, errors="coerce")
    if num.notna().mean() > 0.5 and best.notna().mean() < 0.5:
        best = pd.to_datetime("1899-12-30") + pd.to_timedelta(num, unit="D")
    return best


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def put(**r):
    ROWS.append(r)


def frames(root):
    """Yield DataFrames of every readable table in the archive (csv/xls/xlsx, also inside zip)."""
    def read(data, ext):
        try:
            if ext in (".csv", ".txt"):
                for enc in ("utf-8-sig", "big5", "cp950", "latin-1"):
                    try:
                        return [pd.read_csv(io.BytesIO(data), encoding=enc, dtype=str, low_memory=False)]
                    except UnicodeDecodeError:
                        continue
            else:
                xl = pd.ExcelFile(io.BytesIO(data))
                return [xl.parse(s, dtype=str) for s in xl.sheet_names]
        except Exception:                                         # noqa: BLE001
            return []
        return []
    for d, _, files in os.walk(root):
        if "__MACOSX" in d:
            continue
        for f in files:
            p = os.path.join(d, f); ext = os.path.splitext(f)[1].lower()
            if ext == ".zip":
                try:
                    z = zipfile.ZipFile(p)
                except zipfile.BadZipFile:
                    continue
                for n in z.namelist():
                    e2 = os.path.splitext(n)[1].lower()
                    if e2 in (".csv", ".txt", ".xls", ".xlsx") and "__MACOSX" not in n:
                        yield from read(z.read(n), e2)
            elif ext in (".csv", ".txt", ".xls", ".xlsx", ".xlsm"):
                with open(p, "rb") as fh:
                    yield from read(fh.read(), ext)


def ratio_ci(num, den, groups, B=500, seed=11):
    """Ratio of sums with a 95% cluster bootstrap over lots (groups)."""
    g = pd.DataFrame({"n": np.asarray(num, float), "d": np.asarray(den, float), "g": np.asarray(groups)})
    s = g.groupby("g")[["n", "d"]].sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(s), (B, len(s)))
    r = s.n.values[idx].sum(1) / np.maximum(s.d.values[idx].sum(1), 1e-12)
    return float(s.n.sum() / s.d.sum()), float(np.quantile(r, .025)), float(np.quantile(r, .975))


def col(df, *names):
    up = {str(c).upper(): c for c in df.columns}
    for n in names:
        if n in up:
            return up[n]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", action="append", required=True); ap.add_argument("--txn", required=True)
    ap.add_argument("--out", default="results_match_txn")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    specs = [tuple(s.split("=", 1)) for s in a.line]
    log("recovering the anonymised reason labels")
    _, _, keys = WU.load_lines_with_keys(specs)
    label_of = keys.get("reason", {})
    lines = {}
    for name, path in specs:
        cfg = load_config(path)
        h = load_holds(cfg)
        h["key"] = h.lot_id.astype(str).str.strip() + "|" + h.start_time.dt.floor("min").astype(str)
        lines[name] = (h, cfg["holds"]["columns"]["lot_id"])
        FMTS.append((cfg["holds"].get("time_format"), cfg["holds"].get("time_chars", 30)))
    lot_cols = {c.upper() for _, c in lines.values()}
    global ALL_LOTS
    ALL_LOTS = set().union(*[set(h.lot_id.astype(str).str.strip()) for h, _ in lines.values()])
    log("reading the archive")
    parts = []
    n_tab = 0
    for df in frames(a.txn):
        n_tab += 1
        tc = col(df, "TXN_TIME1", "TXN_TIME", "START_TIME", "HOLD_TIME")
        cands = [c for c in df.columns if str(c).upper() in lot_cols or "LOT" in str(c).upper()
                 or str(c).upper() in ("SCHEDULE", "ASSOCID")]
        if tc is None or not cands:
            continue
        # the lot column is the candidate whose values overlap most with the lots of the paper
        best, lc = -1, None
        for c in cands:
            v = set(df[c].dropna().astype(str).str.strip().unique())
            o = len(v & ALL_LOTS)
            if o > best:
                best, lc = o, c
        if best <= 0:
            continue
        cm = [c for c in df.columns if re.search(r"COMMENT|REMARK|NOTE|MEMO", str(c), re.I)]
        W, Wn, R, Rn = (col(df, n) for n in ("WAIT_TIME", "WAIT_TIME_WITHOUT_HOLD", "RUN_TIME", "RUN_TIME_WITHOUT_HOLD"))
        t = parse_time(df[tc])
        mlot = df[lc].astype(str).str.strip().isin(ALL_LOTS)
        DIAG["lot_overlap"] = max(DIAG["lot_overlap"], best)
        DIAG["rows_lot_match"] += int(mlot.sum()); DIAG["rows_time_ok"] += int((mlot & t.notna()).sum())
        x = pd.DataFrame({"lot": df[lc].astype(str).str.strip(), "t": t})
        x["key"] = x.lot + "|" + x.t.dt.floor("min").astype(str)
        x["text"] = df[cm].fillna("").astype(str).agg(" ".join, axis=1) if cm else ""
        for k, c in (("w", W), ("wn", Wn), ("r", R), ("rn", Rn)):
            x[k] = pd.to_numeric(df[c], errors="coerce") if c else np.nan
        parts.append(x.dropna(subset=["t"]))
    log(f"{n_tab} tables read, {len(parts)} share lots with the paper data")
    put(line="all", part="archive", item="tables read", value=n_tab)
    put(line="all", part="archive", item="tables that share at least one lot with the paper data", value=len(parts))
    put(line="all", part="diagnostics", item="largest number of paper lots shared by one table", value=DIAG["lot_overlap"])
    put(line="all", part="diagnostics", item="archive rows whose lot is a paper lot", value=DIAG["rows_lot_match"])
    put(line="all", part="diagnostics", item="... of which with a readable time", value=DIAG["rows_time_ok"])
    if not parts:
        return finish(a)
    T = pd.concat(parts, ignore_index=True).drop_duplicates()
    for name, (h, _) in lines.items():
        h = h.assign(lot=h.lot_id.astype(str).str.strip(), start_time=h.start_time.astype("datetime64[ns]")) \
            .sort_values("start_time").reset_index(drop=True)
        Ts = T[T.lot.isin(set(h.lot))].assign(t=lambda d: d.t.astype("datetime64[ns]")).sort_values("t")
        near = {}
        for tol in (1, 5, 60):
            nm = pd.merge_asof(h[["lot", "start_time"]], Ts[["lot", "t", "text"]], left_on="start_time", right_on="t",
                               by="lot", tolerance=pd.Timedelta(minutes=tol), direction="nearest")
            near[tol] = nm
            put(line=name, part="match", item=f"share of paper holds with a same-lot transaction within {tol} min",
                value=float(nm.t.notna().mean()))
        lots = set(h.lot)
        put(line=name, part="match", item="share of paper lots found in the archive",
            value=float(len(lots & set(T.lot)) / max(len(lots), 1)))
        m = near[5].t.notna().values
        if m.mean() < 0.05:
            continue
        # comments of the matched holds (same lot, transaction within 5 min of the hold start)
        hm = h[m].copy()
        hm["cat"] = classify(pd.Series(near[5].text.values[m], index=hm.index))
        lo = os.path.join(a.out, "local_only"); os.makedirs(lo, exist_ok=True)
        ne = hm[hm.cat.isin(NONESC)][["lot", "start_time"]].assign(line=name, category=hm.cat)
        fp = os.path.join(lo, "LOCAL_ONLY_nonescalable_holds.csv")
        ne.to_csv(fp, index=False, mode="a" if os.path.exists(fp) and FLAGS_STARTED else "w",
                  header=not (os.path.exists(fp) and FLAGS_STARTED))
        globals()["FLAGS_STARTED"] = True
        hm["dur"] = (hm.release_time - hm.start_time).dt.total_seconds() / 3600
        dur_h = hm.dur.fillna(0).values
        isne = hm.cat.isin(NONESC).values.astype(float)
        v, lo_, hi_ = ratio_ci(isne, np.ones(len(hm)), hm.lot.values)
        put(line=name, part="comments", item="share of holds whose comment points to customer, engineering change, or material",
            value=v, ci_lo=lo_, ci_hi=hi_)
        v, lo_, hi_ = ratio_ci(isne * dur_h, dur_h, hm.lot.values)
        put(line=name, part="comments", item="... share of hold hours", value=v, ci_lo=lo_, ci_hi=hi_)
        for thr, lab in ((24, "holds > 24 h"), (168, "holds > tau")):
            sel = dur_h > thr
            if sel.sum() > 20:
                v, lo_, hi_ = ratio_ci(isne[sel], np.ones(sel.sum()), hm.lot.values[sel])
                put(line=name, part="comments", item=f"... share among {lab}", value=v, ci_lo=lo_, ci_hi=hi_)
        put(line=name, part="comments", item="share of matched holds with a comment",
            value=float((hm.cat != "no comment").mean()))
        for sub, sel in (("all holds", hm.dur.notna()), ("holds > 24 h", hm.dur > 24), ("holds > tau", hm.dur > 168)):
            g = hm[sel]
            for c, s in g.cat.value_counts(normalize=True).items():
                put(line=name, part=f"comment categories, {sub}", item=c, value=float(s),
                    share_of_hold_hours=float(g.loc[g.cat == c, "dur"].sum() / max(g.dur.sum(), 1e-9)))
        hm["label"] = hm.reason.astype(str).map(label_of).fillna("unmapped")
        tot = hm.groupby("label").dur.sum().sort_values(ascending=False)
        for lab in tot.index[:15]:
            g = hm[hm.label == lab]; s = g.cat.value_counts(normalize=True)
            put(line=name, part="comments per reason label", item=lab, value=float(tot[lab] / tot.sum()),
                holds=len(g), **{f"share {k}": float(s.get(k, 0.0)) for k, _ in CATS},
                **{"share no comment": float(s.get("no comment", 0.0))})
        # hold share of cycle time on the lots of this line
        L = T[T.lot.isin(lots) & T.w.notna() & T.wn.notna()]
        if len(L):
            hold = (L.w - L.wn).clip(lower=0) + (L.r - L.rn).clip(lower=0).fillna(0)
            tot_t = L.w + L.r.fillna(0)
            v, lo_, hi_ = ratio_ci(hold.values, tot_t.values, L.lot.values)
            put(line=name, part="cycle time", item="share of waiting + run time that is hold time", value=v,
                ci_lo=lo_, ci_hi=hi_)
            v, lo_, hi_ = ratio_ci((L.w - L.wn).clip(lower=0).values, L.w.values, L.lot.values)
            put(line=name, part="cycle time", item="share of waiting time that is hold time", value=v, ci_lo=lo_, ci_hi=hi_)
            put(line=name, part="cycle time", item="lots used", value=int(L.lot.nunique()))
            put(line=name, part="cycle time", item="transaction records used", value=int(len(L)))
    finish(a)


def finish(a):
    df = pd.DataFrame(ROWS)
    df.to_csv(os.path.join(a.out, "match_txn.csv"), index=False, float_format="%.6g")
    try:
        md = df.round(4).to_markdown(index=False)
    except ImportError:
        md = df.round(4).to_string(index=False)
    open(os.path.join(a.out, "match_txn.md"), "w", encoding="utf-8").write("# Match with the transaction archive\n\n" + md + "\n")
    log(f"done -> {a.out}/match_txn.md (aggregated; safe to share)")


if __name__ == "__main__":
    main()
