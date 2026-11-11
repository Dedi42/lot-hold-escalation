"""Robustness checks of the replay.

    python scripts/run_robustness.py --line A=config/local_lineA.yaml --line B=config/local_lineB.yaml --out results_robustness

Same loading, split, models, and replay as run_hypotheses.py / run_diagnostics.py. Adds:

  C1  escalation effect that worsens with hold duration: alpha_g falls and delta_g rises with the median training
      duration of the department x reason group, with strength s = 0 ... 1; gain of the ensemble over oldest-first
      (test period) and the break-even strength.
  C2  credit truncation tau of the replay: 72, 168, 336 h and none (index unchanged), test period and rolling origins.
  C3  percentile rule whose unused budget is filled by oldest-first.
  C4  overlap of holds of the same lot (sum of hold hours vs union of hold intervals per lot).
  C5  purged labels: training/validation holds released after the end of their period are dropped (test period
      and rolling origins), ensemble vs oldest-first.
  C6  burn-in: holds of earlier periods still open in the replay window are candidates too (test and rolling origins).
  C7  Weibull shape within department x reason groups (is the decreasing hazard a mixture effect?).
  C8  share of test holds whose reason, step, or package family never occurs in training.

Only aggregated numbers are written (no dates, no codes, no hold-level records).
"""
from __future__ import annotations
import argparse, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import run_hypotheses as RH                                     # noqa: E402
import run_diagnostics as RV                                       # noqa: E402
from holdesc.policy import review_candidates, simulate          # noqa: E402
from holdesc import stats as S                                  # noqa: E402

CAP, ALPHA, DELTA = RH.CAP, RH.ALPHA0, RH.DELTA0
ROWS = {}


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def put(t, **r):
    ROWS.setdefault(t, []).append(r)


def candidates_window(cand, oc, r0, r1, review_h=4.0):
    """Review candidates for reviews r0 ... r1 drawn from the holds in `cand` (may start before r0)."""
    reviews = pd.date_range(r0, r1, freq=f"{int(review_h)}h")
    st, rl = cand.start_time.values, cand.rel.values
    out = []
    for r in reviews:
        m = (st < r.to_datetime64()) & (rl > r.to_datetime64())
        c = cand[m].copy()
        if c.empty:
            continue
        c["review"] = r
        c["e"] = (r - c.start_time).dt.total_seconds() / 3600
        c["R"] = (c.rel - r).dt.total_seconds() / 3600
        c["hold_index"] = c.index
        c["open_all_e"] = oc(np.full(len(c), r.value))
        c["open_dep_e"] = [oc(np.array([r.value]), d)[0] for d in c.department]
        c["hour_e"] = r.hour
        out.append(c)
    return pd.concat(out, ignore_index=True)


def window_of(test, review_h=4.0, warmup_h=24.0):
    r0 = (test.start_time.min() + pd.Timedelta(hours=warmup_h)).ceil(f"{int(review_h)}h")
    return r0, test.start_time.max()


def extra_scores(C, sm):
    ratio = sm.p90_ratio(C)
    return {"p90, filled by oldest-first": np.where(ratio > 1, 1e6 + ratio, C.e.values)}


def compare(tag, line, kind, ra, rb, days, a, B, **kw):
    r = S.block_test(ra, rb, days, a.bootstrap)
    put("comparisons", tag=tag, line=line, kind=kind, budget=B, rel=r["rel"], rel_lo=r["rel_lo"], rel_hi=r["rel_hi"],
        p_greater=r["p_greater"], a_h_per_day=r["a_h_per_day"], b_h_per_day=r["b_h_per_day"],
        log_ratio=r["log_ratio"], log_ratio_se=r["log_ratio_se"], weeks=r["weeks"], **kw)


# ------------------------------------------------------------------------------------ C4, C7, C8 (data only)
def data_checks(name, D):
    h, tr, te = D["h"], D["tr"], D["te"]
    # C4 overlap of holds of one lot
    tot, uni = 0.0, 0.0
    for _, g in h.groupby("lot_id"):
        s = g.start_time.values.astype("int64"); r = g.rel.values.astype("int64")
        o = np.argsort(s); s, r = s[o], r[o]
        tot += (r - s).sum()
        cs, cr = s[0], r[0]
        for a_, b_ in zip(s[1:], r[1:]):
            if a_ <= cr:
                cr = max(cr, b_)
            else:
                uni += cr - cs; cs, cr = a_, b_
        uni += cr - cs
    put("data_checks", line=name, check="C4 hold hours overlapping another hold of the same lot (share)",
        value=1 - uni / tot)
    # C7 Weibull shape within groups
    try:
        from lifelines import WeibullFitter
        shapes, ws = [], []
        for _, g in h.groupby(["department", "reason"]):
            if len(g) < 300 or g.event.sum() < 100:
                continue
            wf = WeibullFitter().fit(g.dur_h.clip(lower=1e-3), g.event)
            rho = float(getattr(wf, "rho_", np.nan))
            if np.isnan(rho):
                rho = float(wf.summary.loc["rho_", "coef"])
            shapes.append(rho); ws.append(len(g))
        shapes, ws = np.array(shapes), np.array(ws)
        if len(shapes):
            put("data_checks", line=name, check="C7 groups with >= 300 holds (n)", value=len(shapes))
            put("data_checks", line=name, check="C7 share of their holds", value=ws.sum() / len(h))
            put("data_checks", line=name, check="C7 Weibull shape within groups: median", value=float(np.median(shapes)))
            put("data_checks", line=name, check="C7 within-group shape: 10th percentile", value=float(np.quantile(shapes, .1)))
            put("data_checks", line=name, check="C7 within-group shape: 90th percentile", value=float(np.quantile(shapes, .9)))
            put("data_checks", line=name, check="C7 share of groups with shape < 1", value=float((shapes < 1).mean()))
            put("data_checks", line=name, check="C7 hold-weighted mean within-group shape",
                value=float((shapes * ws).sum() / ws.sum()))
    except Exception as e:                                          # noqa: BLE001
        log(f"[{name}] C7 skipped: {e}")
    # C8 unseen categories in the test period
    for col in ("reason", "step", "product_family", "department"):
        if col in te:
            put("data_checks", line=name, check=f"C8 test holds whose {col} is unseen in training (share)",
                value=float((~te[col].isin(set(tr[col]))).mean()))


# ------------------------------------------------------------------------------------ test period
def test_period(name, D, lots, a, budgets, purge_pass=False):
    h, oc, tr, va, te = D["h"], D["oc"], D["tr"], D["va"], D["te"]
    sm, lm, _ = RH.fit(tr, va, oc)
    C = review_candidates(te, oc); days = RH.day_index(C)
    sc = RV.scores_for(C, te, sm, lm)
    if purge_pass:
        recs = RV.run_policies(C, sc, budgets, ["Age (oldest first)", "Ensemble"])
        for B in budgets:
            compare("C5 purged labels: ensemble vs oldest-first", name, "test period",
                    recs[(B, "Ensemble")], recs[(B, "Age (oldest first)")], days, a, B)
        return
    sc.update(extra_scores(C, sm))
    # C2 credit truncation
    pols = ["Age (oldest first)", "Kaplan–Meier (D×R)", "Ensemble", "Oracle"]
    Ce = C.assign(**{"s::" + k: v for k, v in sc.items()})
    for cap in (72.0, 168.0, 336.0, 1e9):
        recs = {(B, k): RV.simulate_ext(Ce, "s::" + k, max(1, B // 6), cap=cap) for B in budgets for k in pols}
        for (B, k), rec in recs.items():
            put("credit_tau", line=name, kind="test period", cap_h=("none" if cap > 1e8 else int(cap)), budget=B,
                policy=k, h_per_calendar_day=rec.saved_h.sum() / len(days))
        for B in budgets:
            compare("C2 ensemble vs oldest-first", name, "test period", recs[(B, "Ensemble")],
                    recs[(B, "Age (oldest first)")], days, a, B, cap_h=("none" if cap > 1e8 else int(cap)))
    # C3 percentile rule filled by oldest-first
    recs = RV.run_policies(C, sc, budgets, ["Age (oldest first)", "Ensemble", "Static p90 rule", "p90, filled by oldest-first"])
    for B in budgets:
        for k in ("Static p90 rule", "p90, filled by oldest-first"):
            put("p90_filled", line=name, budget=B, policy=k, h_per_calendar_day=recs[(B, k)].saved_h.sum() / len(days),
                escalations=len(recs[(B, k)]))
        compare("C3 p90 filled by oldest-first vs oldest-first", name, "test period",
                recs[(B, "p90, filled by oldest-first")], recs[(B, "Age (oldest first)")], days, a, B)
        compare("C3 ensemble vs p90 filled by oldest-first", name, "test period",
                recs[(B, "Ensemble")], recs[(B, "p90, filled by oldest-first")], days, a, B)
    # C1 effect that worsens with duration
    grp = (C.department.astype(str) + "|" + C.reason.astype(str)).values
    med = tr.assign(g=tr.department.astype(str) + "|" + tr.reason.astype(str)).groupby("g").dur_h.median()
    q = med.rank(pct=True)
    qg = pd.Series(grp).map(q).fillna(0.5).values
    for s in (0.0, 0.25, 0.5, 0.75, 1.0):
        Cs = Ce.assign(alpha_h=0.5 + 0.3 * s * (1 - 2 * qg), delta_h=2.0 + 6.0 * s * qg)
        for B in budgets:
            ra = simulate(Cs, "s::Ensemble", max(1, B // 6), alpha_col="alpha_h", delta_col="delta_h")
            rb = simulate(Cs, "s::Age (oldest first)", max(1, B // 6), alpha_col="alpha_h", delta_col="delta_h")
            compare("C1 duration-dependent effect: ensemble vs oldest-first", name, "test period", ra, rb, days, a, B,
                    strength=s)
    # C6 burn-in
    r0, r1 = RV_window = window_of(te)
    cand = h[(h.start_time <= r1) & (h.rel > r0)]
    Cb = candidates_window(cand, oc, r0, r1)
    scb = RV.scores_for(Cb, cand, sm, lm)
    recs = RV.run_policies(Cb, scb, budgets, ["Age (oldest first)", "Ensemble"])
    db = RH.day_index(Cb)
    for B in budgets:
        compare("C6 burn-in: ensemble vs oldest-first", name, "test period", recs[(B, "Ensemble")],
                recs[(B, "Age (oldest first)")], db, a, B)


# ------------------------------------------------------------------------------------ rolling origins
def rolling(name, h, oc, a, budgets, purge_pass=False):
    t_end = h.start_time.max().normalize()
    keys = ["main", "burn-in"] if not purge_pass else ["purged"]
    caps = (72.0, 168.0, 336.0, 1e9) if not purge_pass else (168.0,)
    acc = {(v, cap, B, k): [] for v in keys for cap in caps for B in budgets for k in ("Age (oldest first)", "Ensemble")}
    days_all = {v: [] for v in keys}
    for k in range(a.origins, 0, -1):
        t0 = t_end - pd.Timedelta(days=k * a.window_days); t1 = t0 + pd.Timedelta(days=a.window_days)
        past, test = h[h.start_time < t0], h[(h.start_time >= t0) & (h.start_time < t1)]
        if len(past) < 2000 or len(test) < 200:
            continue
        cut = past.start_time.quantile(0.8)
        tr, va = past[past.start_time <= cut], past[past.start_time > cut]
        if purge_pass:                       # labels must be known at the end of each period
            tr, va = tr[tr.rel <= cut], va[va.rel <= t0]
        sm, lm, _ = RH.fit(tr, va, oc)
        variants = {}
        C = review_candidates(test, oc); C = C[C.review < t1]
        variants["purged" if purge_pass else "main"] = (C, test)
        if not purge_pass:
            r0, _ = window_of(test)
            cand = h[(h.start_time < t1) & (h.rel > r0)]
            Cb = candidates_window(cand, oc, r0, t1 - pd.Timedelta(hours=4))
            variants["burn-in"] = (Cb, cand)
        for v, (Cv, rows) in variants.items():
            sc = RV.scores_for(Cv, rows, sm, lm)
            Ce = Cv.assign(**{"s::" + kk: vv for kk, vv in sc.items()})
            for cap in caps if v != "burn-in" else (168.0,):
                for B in budgets:
                    for p in ("Age (oldest first)", "Ensemble"):
                        acc[(v, cap, B, p)].append(RV.simulate_ext(Ce, "s::" + p, max(1, B // 6), cap=cap))
            days_all[v].append(RH.day_index(Cv))
        log(f"[{name}] origin {a.origins - k + 1} of {a.origins} done ({'purged' if purge_pass else 'main'})")
    for v in keys:
        if not days_all[v]:
            continue
        days = days_all[v][0]
        for dd in days_all[v][1:]:
            days = days.union(dd)
        for cap in caps if v != "burn-in" else (168.0,):
            for B in budgets:
                ra = pd.concat(acc[(v, cap, B, "Ensemble")]); rb = pd.concat(acc[(v, cap, B, "Age (oldest first)")])
                tag = {"main": "C2 ensemble vs oldest-first", "burn-in": "C6 burn-in: ensemble vs oldest-first",
                       "purged": "C5 purged labels: ensemble vs oldest-first"}[v]
                compare(tag, name, "rolling origins", ra, rb, days, a, B,
                        **({"cap_h": ("none" if cap > 1e8 else int(cap))} if v == "main" else {}))


def report(a):
    os.makedirs(a.out, exist_ok=True)
    md = ["# Robustness checks (aggregated, no dates)\n"]
    for t, rows in ROWS.items():
        df = pd.DataFrame(rows)
        df.to_csv(f"{a.out}/{t}.csv", index=False, float_format="%.6g")
        try:
            body = df.round(4).to_markdown(index=False)
        except ImportError:
            body = df.round(4).to_string(index=False)
        md += [f"\n## {t}\n", body]
    open(f"{a.out}/robustness.md", "w", encoding="utf-8").write("\n".join(md) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", action="append", required=True); ap.add_argument("--out", default="results_robustness")
    ap.add_argument("--budgets", default="6,12,24,48"); ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--origins", type=int, default=4); ap.add_argument("--window-days", dest="window_days", type=int, default=14)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick:
        a.bootstrap, a.origins, a.budgets = 200, 2, "6,24"
    budgets = [int(x) for x in a.budgets.split(",")]
    specs = [tuple(s.split("=", 1)) for s in a.line]
    t0 = time.time()
    lines, lots = RH.load_lines(specs)
    for name, _ in specs:
        D = RH.prepare(lines[name], purge=False)
        log(f"[{name}] data checks"); data_checks(name, D)
        log(f"[{name}] test period"); test_period(name, D, lots, a, budgets)
        log(f"[{name}] rolling origins"); rolling(name, D["h"], D["oc"], a, budgets)
        report(a)
        Dp = RH.prepare(lines[name], purge=True)
        log(f"[{name}] purged labels"); test_period(name, Dp, lots, a, budgets, purge_pass=True)
        rolling(name, Dp["h"], Dp["oc"], a, budgets, purge_pass=True)
        report(a)
    log(f"done in {(time.time() - t0) / 60:.1f} min -> {a.out}/robustness.md")


if __name__ == "__main__":
    main()
