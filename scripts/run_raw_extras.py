"""Extra evidence from the raw MES transaction file behind each line, run LOCALLY.

    python scripts/run_raw_extras.py --line A=config/local_lineA.yaml --line B=config/local_lineB.yaml --out results_raw_extras

Uses the same raw hold file and filters as the paper (the YAML configs). Adds:

  X1  hold share of cycle time: if the raw file has WAIT_TIME / WAIT_TIME_WITHOUT_HOLD / RUN_TIME /
      RUN_TIME_WITHOUT_HOLD (any case), share of waiting + run time that is hold time, over all transactions.
  X2  hold comments: if the raw file has comment columns (name contains COMMENT, REMARK, NOTE or MEMO), the share
      of holds with a comment, and a keyword classification of each hold into customer decision, engineering change,
      material, equipment, quality / measurement, scrap / rework, or other. Reported for all holds, for holds longer
      than 24 h and longer than tau = 168 h, and per anonymised reason label (R01, R02, ... as in the paper), so that
      reasons that internal escalation cannot speed up can be identified without revealing codes or text.

Shareable output: raw_extras.csv and raw_extras.md (aggregated, anonymised labels, no text, no dates).
local_only/: transaction-type counts and the original reason codes per label. Do not share.
"""
from __future__ import annotations
import argparse, os, re, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from holdesc.io import load_config, _read, _times               # noqa: E402
import run_warmup as WU                                         # noqa: E402

CAP = 168.0
CATS = [  # first match wins
    ("customer decision", r"customer|\bcust\b|cust\.|wait\s*cus|客戶|客户|待客|客訴|客户确认|客戶確認"),
    ("engineering change", r"\becn\b|\beco\b|engineering change|工程變更|工程变更|變更|变更|new recipe|trial|試作|试作"),
    ("material", r"material|mat'?l|待料|缺料|材料|物料"),
    ("equipment", r"\beqp\b|machine|tool|\bpm\b|\bdown\b|機台|机台|當機|当机|設備|设备"),
    ("quality / measurement", r"\booc\b|\boos\b|\bspc\b|inspect|\baoi\b|yield|defect|\bmrb\b|abnormal|measure|"
                              r"品質|品质|異常|异常|量測|量测|外觀|外观|不良"),
    ("scrap / rework", r"scrap|rework|重工|報廢|报废"),
]
ROWS = []


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def put(**r):
    ROWS.append(r)


def find(cols, name):
    for c in cols:
        if c.upper() == name:
            return c
    return None


def classify(text: pd.Series) -> pd.Series:
    t = text.fillna("").astype(str).str.lower()
    out = pd.Series("other / none", index=t.index)
    done = pd.Series(False, index=t.index)
    for cat, pat in CATS:
        m = t.str.contains(pat, regex=True) & ~done
        out[m] = cat; done |= m
    out[t.str.strip() == ""] = "no comment"
    return out


def line_run(name, path, label_of, a):
    cfg = load_config(path); hc = cfg["holds"]
    raw = _read(hc["path"])
    for col, val in (hc.get("exclude") or {}).items():
        raw = raw[~raw[col].astype(str).isin([str(v) for v in np.atleast_1d(val)])]
    lo = os.path.join(a.out, "local_only"); os.makedirs(lo, exist_ok=True)
    for col in (hc.get("filters") or {}):
        raw[col].astype(str).value_counts().head(40).to_csv(f"{lo}/LOCAL_ONLY_{name}_transaction_types.csv")
    # X1 hold share of cycle time
    W, Wn, R, Rn = (find(raw.columns, n) for n in ("WAIT_TIME", "WAIT_TIME_WITHOUT_HOLD", "RUN_TIME", "RUN_TIME_WITHOUT_HOLD"))
    if W and Wn:
        w, wn = pd.to_numeric(raw[W], errors="coerce"), pd.to_numeric(raw[Wn], errors="coerce")
        r = pd.to_numeric(raw[R], errors="coerce") if R else 0 * w
        rn = pd.to_numeric(raw[Rn], errors="coerce") if Rn else r
        ok = w.notna() & wn.notna()
        hold = ((w - wn).clip(lower=0) + (r - rn).clip(lower=0).fillna(0))[ok]
        total = (w + r.fillna(0))[ok]
        put(line=name, part="X1 cycle time", item="share of waiting + run time that is hold time",
            value=float(hold.sum() / total.sum()))
        put(line=name, part="X1 cycle time", item="share of waiting time that is hold time",
            value=float((w - wn).clip(lower=0)[ok].sum() / w[ok].sum()))
        put(line=name, part="X1 cycle time", item="share of transaction records with hold time > 0",
            value=float((hold > 0).mean()))
        put(line=name, part="X1 cycle time", item="transaction records used", value=int(ok.sum()))
    else:
        put(line=name, part="X1 cycle time", item="WAIT_TIME columns not found", value=np.nan)
    # X2 comments of the holds used in the paper
    h = raw
    for col, val in (hc.get("filters") or {}).items():
        h = h[h[col].astype(str).isin([str(v) for v in np.atleast_1d(val)])]
    cm = [c for c in h.columns if re.search(r"COMMENT|REMARK|NOTE|MEMO", str(c), re.I)]
    put(line=name, part="X2 comments", item="comment columns found", value=len(cm))
    if not cm:
        return
    text = h[cm].fillna("").astype(str).agg(" ".join, axis=1)
    cat = classify(text)
    cols = hc["columns"]
    st = _times(h[cols["start_time"]], hc.get("time_format"), hc.get("time_chars", 30))
    rl = _times(h[cols["release_time"]], hc.get("time_format"), hc.get("time_chars", 30))
    dur = ((rl - st).dt.total_seconds() / 3600).clip(lower=0)
    ok = st.notna()
    reason = h[cols["reason"]].fillna("NA").astype(str)
    d = pd.DataFrame({"cat": cat, "dur": dur, "reason": reason})[ok]
    put(line=name, part="X2 comments", item="share of holds with a comment", value=float((d.cat != "no comment").mean()))
    for sub, m in (("all holds", d.dur.notna() | d.dur.isna()), ("holds > 24 h", d.dur > 24), ("holds > tau", d.dur > CAP)):
        g = d[m]
        if g.empty:
            continue
        for c, s in g.cat.value_counts(normalize=True).items():
            put(line=name, part=f"X2 categories, {sub}", item=c, value=float(s),
                share_of_hold_hours=float(g.loc[g.cat == c, "dur"].sum() / max(g.dur.sum(), 1e-9)), holds=int((g.cat == c).sum()))
    # per anonymised reason label (top 15 by hold hours)
    d["label"] = d.reason.map(label_of).fillna("unmapped")
    tot = d.groupby("label").dur.sum().sort_values(ascending=False)
    for lab in tot.index[:15]:
        g = d[d.label == lab]
        shares = g.cat.value_counts(normalize=True)
        put(line=name, part="X2 per reason label", item=lab, value=float(tot[lab] / tot.sum()), holds=len(g),
            median_h=float(g.dur.median()), **{f"share {k}": float(shares.get(k, 0.0)) for k, _ in CATS},
            **{"share no comment": float(shares.get("no comment", 0.0))})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", action="append", required=True); ap.add_argument("--out", default="results_raw_extras")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    specs = [tuple(s.split("=", 1)) for s in a.line]
    log("loading lines to recover the anonymised reason labels")
    _, _, keys = WU.load_lines_with_keys(specs)
    label_of = keys.get("reason", {})
    for name, path in specs:
        log(f"[{name}] raw file")
        try:
            line_run(name, path, label_of, a)
        except Exception as e:                                    # noqa: BLE001
            put(line=name, part="error", item=type(e).__name__, value=np.nan)
            log(f"[{name}] failed: {e}")
    df = pd.DataFrame(ROWS)
    df.to_csv(os.path.join(a.out, "raw_extras.csv"), index=False, float_format="%.6g")
    try:
        md = df.round(4).to_markdown(index=False)
    except ImportError:
        md = df.round(4).to_string(index=False)
    open(os.path.join(a.out, "raw_extras.md"), "w", encoding="utf-8").write("# Raw-file extras (aggregated)\n\n" + md + "\n")
    lo = os.path.join(a.out, "local_only")
    pd.DataFrame([(v, k) for k, v in label_of.items()], columns=["label", "original_reason_code"]).sort_values("label") \
        .to_csv(f"{lo}/LOCAL_ONLY_reason_codes.csv", index=False)
    log(f"done -> {a.out}/raw_extras.csv (shareable)  |  {lo} (do not share)")


if __name__ == "__main__":
    main()
