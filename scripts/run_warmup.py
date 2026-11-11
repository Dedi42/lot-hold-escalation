"""Warm-up replay, rolling-origin pooling, duration-dependent effects, and the tail beyond tau.

    python scripts/run_warmup.py --line A=config/local_lineA.yaml --line B=config/local_lineB.yaml --out results_warmup

Same loading, split, models, and replay as run_hypotheses.py / run_diagnostics.py / run_robustness.py. Adds:

  W1  warm-up replay: in every evaluation window (test period and each rolling origin) each policy is already run
      for --warmup-days before the window, on all holds open then, so that it meets the backlog its own earlier
      decisions left; only escalations inside the window are credited. Policies: oldest-first, oldest-first among
      holds <= tau, static p90 rule, p90 filled by oldest-first, Kaplan-Meier (DxR), ensemble, oracle. Also run
      without warm-up (as in the paper) on the rolling origins, so that the p90 rules get rolling-origin results.
      Rolling-origin comparisons are pooled over the lines (inverse variance, as H9).
  W2  escalation effect that worsens with hold duration (strength 0.5 and 1, as C1) under the warm-up replay.
  W3  H6 with more draws (default 200) of group-specific alpha, delta, test period.
  W4  hazard and remaining time beyond tau: per elapsed time up to 4 weeks, holds still open, share released
      within the next 24 h, median and truncated mean remaining time; and how close to release the holds are
      that oldest-first escalates (remaining time of its picks, by age).
  W5  sign-flip permutation test over weeks (exact when the number of weeks is small) next to the bootstrap.
  W6  which hold reasons the policies escalate: share of escalations by (anonymised) reason, with the reason's
      share of all holds and hold hours. The local-only file maps the anonymised labels back to the original
      codes so that you can mark which reasons cannot respond to internal escalation. DO NOT SHARE local_only/.
  W7  footprint of past escalation rules: hazard of release per hour of elapsed time (spikes after fixed limits
      such as 24 h) and per tenth of the group 90th percentile (a spike just after 1.0 would suggest a p90 rule).
  W8  delivery motivation (lines with due dates): share of the lateness of late lots that their hold hours
      could explain at most, sum_j min(hold hours_j, L_j) / sum_j L_j, and hold hours per lot.

Only aggregated numbers are written (no dates, no hold-level records). local_only/ contains the original
reason and department codes and must stay on your computer.
"""
from __future__ import annotations
import argparse, itertools, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import run_hypotheses as RH                                     # noqa: E402
import run_diagnostics as RV                                       # noqa: E402
import run_robustness as RC                                  # noqa: E402
from holdesc.io import load_config, load_holds, load_lots        # noqa: E402
from holdesc.anonymize import anonymize                         # noqa: E402
from holdesc.policy import review_candidates, simulate          # noqa: E402
from holdesc import stats as S                                  # noqa: E402

CAP, ALPHA, DELTA = RH.CAP, RH.ALPHA0, RH.DELTA0
ROWS = {}
POLS = ["Age (oldest first)", "Age <= tau", "Static p90 rule", "p90, filled by oldest-first",
        "Kaplan–Meier (D×R)", "Ensemble", "Oracle"]
ELIG = {"Static p90 rule", "Age <= tau"}
PAIRS = [("Ensemble", "Age (oldest first)"), ("Ensemble", "Age <= tau"), ("Kaplan–Meier (D×R)", "Age (oldest first)"),
         ("Ensemble", "Kaplan–Meier (D×R)"), ("Static p90 rule", "Age (oldest first)"),
         ("p90, filled by oldest-first", "Age (oldest first)"), ("Ensemble", "p90, filled by oldest-first")]


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def put(t, **r):
    ROWS.setdefault(t, []).append(r)


# ------------------------------------------------------------------------------------ loading (keeps code keys)
NONESC_FILE = None


def load_lines_with_keys(specs):
    hs, ls = [], []
    flags = None
    if NONESC_FILE and os.path.exists(NONESC_FILE):
        flags = pd.read_csv(NONESC_FILE, dtype=str)
    for name, path in specs:
        cfg = load_config(path)
        h = load_holds(cfg); h["line"] = name
        h["nonesc"] = 0
        if flags is not None:
            f = flags[flags.line == name]
            key = h.lot_id.astype(str).str.strip() + "|" + h.start_time.astype(str)
            h["nonesc"] = key.isin(set(f.lot.str.strip() + "|" + pd.to_datetime(f.start_time).astype(str))).astype(int)
            log(f"[{name}] {int(h.nonesc.sum())} holds flagged as not escalable ({h.nonesc.mean():.1%})")
        h["lot_id"] = name + ":" + h["lot_id"].astype(str)
        hs.append(h)
        l = load_lots(cfg)
        if l is not None:
            l = l[~l.index.duplicated()]
            l.index = name + ":" + l.index.astype(str)
            ls.append(l)
    h_all = pd.concat(hs, ignore_index=True)
    lots_all = pd.concat(ls) if ls else None
    h_all, lots_all, keys = anonymize(h_all, lots_all)
    lines = {name: h_all[h_all.line == name].drop(columns="line").reset_index(drop=True) for name, _ in specs}
    return lines, lots_all, keys


# ------------------------------------------------------------------------------------ replay with warm-up
def simulate_window(C, score, b, r0, eligible_only=False, alpha=ALPHA, delta=DELTA, cap=CAP,
                    alpha_col=None, delta_col=None):
    """As simulate_ext, but escalations at reviews before r0 (the warm-up) are made and remembered, not credited."""
    escalated, rec = set(), []
    for r, c in C.groupby("review", sort=True):
        c = c[~c.hold_index.isin(escalated)]
        if eligible_only:
            c = c[c[score] >= 0]
        if c.empty:
            continue
        pick = c.loc[c[score].nlargest(b).index]
        al = pick[alpha_col].values if alpha_col else np.full(len(pick), alpha)
        de = pick[delta_col].values if delta_col else np.full(len(pick), delta)
        nes = pick["nonesc"].values if "nonesc" in pick else np.zeros(len(pick), int)
        for h, R, e, lot, rs, a_, d_, ne in zip(pick.hold_index, pick.R, pick.e, pick.lot_id, pick.reason, al, de, nes):
            escalated.add(h)
            if r >= r0:
                rec.append((r.normalize(), lot, a_ * max(min(R, cap) - d_, 0.0), e, R, rs, ne))
    return pd.DataFrame(rec, columns=["day", "lot_id", "saved_h", "e", "R", "reason", "nonesc"])


def scores(C, rows, sm, lm):
    sc = RV.scores_for(C, rows, sm, lm)
    sc.update(RC.extra_scores(C, sm))
    return {k: v for k, v in sc.items() if k in POLS}


def run_window(C, sc, budgets, r0, pols=POLS, **kw):
    Ce = C.assign(**{"s::" + k: v for k, v in sc.items()})
    return {(B, k): simulate_window(Ce, "s::" + k, max(1, B // 6), r0, eligible_only=k in ELIG, **kw)
            for B in budgets for k in pols if k in sc}


def days_from(C, r0):
    return pd.date_range(r0.normalize(), C.review.max().normalize(), freq="D")


def sign_flip_p(rec_a, rec_b, days, n_max=20000, seed=3):
    """One-sided sign-flip permutation test over weekly differences (H1: a > b); exact if 2^weeks <= n_max."""
    a, b = S.weekly_series(rec_a, days), S.weekly_series(rec_b, days)
    wk = pd.Index(days).to_period("W")
    d = (a.groupby(wk).sum() - b.groupby(wk).sum()).values
    obs = d.sum()
    n = len(d)
    if 2 ** n <= n_max:
        signs = np.array(list(itertools.product([1, -1], repeat=n)))
    else:
        signs = np.random.default_rng(seed).choice([1, -1], size=(n_max, n))
    stat = (signs * d).sum(1)
    return float((np.sum(stat >= obs - 1e-9)) / len(stat)), n


def compare(tag, line, kind, variant, ra, rb, days, a, B, **kw):
    r = S.block_test(ra, rb, days, a.bootstrap)
    p_perm, n = sign_flip_p(ra, rb, days)
    put("comparisons", tag=tag, line=line, kind=kind, variant=variant, budget=B, rel=r["rel"], rel_lo=r["rel_lo"],
        rel_hi=r["rel_hi"], p_greater=r["p_greater"], p_less=r["p_less"], p_signflip=p_perm,
        a_h_per_day=r["a_h_per_day"], b_h_per_day=r["b_h_per_day"], log_ratio=r["log_ratio"],
        log_ratio_se=r["log_ratio_se"], weeks=n, **kw)


def effect_cols(C, tr, s):
    grp = (C.department.astype(str) + "|" + C.reason.astype(str)).values
    med = tr.assign(g=tr.department.astype(str) + "|" + tr.reason.astype(str)).groupby("g").dur_h.median()
    qg = pd.Series(grp).map(med.rank(pct=True)).fillna(0.5).values
    return C.assign(alpha_h=0.5 + 0.3 * s * (1 - 2 * qg), delta_h=2.0 + 6.0 * s * qg)


def evaluate_window(name, kind, h, oc, sm, lm, tr, test, r0, r1, a, budgets, acc):
    """Main (no warm-up, candidates start in the window) and warm-up variants of one window."""
    out = {}
    # main: as in the paper
    C = review_candidates(test, oc); C = C[C.review <= r1]
    sc = scores(C, test, sm, lm)
    rm = run_window(C, sc, budgets, C.review.min())
    out["main"] = (rm, days_from(C, C.review.min()))
    # warm-up: all holds open at any time in [r0 - W, r1]
    w0 = (r0 - pd.Timedelta(days=a.warmup_days)).ceil("4h")
    cand = h[(h.start_time <= r1) & (h.rel > w0)]
    Cw = RC.candidates_window(cand, oc, w0, r1)
    scw = scores(Cw, cand, sm, lm)
    rw = run_window(Cw, scw, budgets, r0)
    out["warm-up"] = (rw, days_from(Cw[Cw.review >= r0], r0))
    if "nonesc" in Cw and Cw.nonesc.sum() > 0:                   # holds that escalation cannot speed up are removed
        Cf = Cw[Cw.nonesc == 0]
        scf = scores(Cf, cand, sm, lm)
        out["warm-up, non-escalable removed"] = (run_window(Cf, scf, budgets, r0), out["warm-up"][1])
    for s in (0.5, 1.0):
        Cs = effect_cols(Cw.assign(**{"s::" + k: v for k, v in scw.items()}), tr, s)
        for B in budgets:
            for p in ("Age (oldest first)", "Ensemble"):
                out.setdefault(f"warm-up, effect worsening {s:g}", ({}, out["warm-up"][1]))[0][(B, p)] = \
                    simulate_window(Cs, "s::" + p, max(1, B // 6), r0, alpha_col="alpha_h", delta_col="delta_h")
    for v, (recs, days) in out.items():
        acc.setdefault(v, {"days": [], "recs": {}})
        acc[v]["days"].append(days)
        for key, rec in recs.items():
            acc[v]["recs"].setdefault(key, []).append(rec)
    return out, (Cw, scw)


def summarise(name, kind, acc, a, budgets):
    for v, d in acc.items():
        days = d["days"][0]
        for dd in d["days"][1:]:
            days = days.union(dd)
        recs = {k: pd.concat(r, ignore_index=True) for k, r in d["recs"].items()}
        for (B, p), rec in recs.items():
            put("policies", line=name, kind=kind, variant=v, budget=B, policy=p,
                h_per_calendar_day=rec.saved_h.sum() / len(days), escalations=len(rec),
                h_per_escalation=rec.saved_h.mean() if len(rec) else 0.0)
        for x, y in PAIRS:
            for B in budgets:
                if (B, x) in recs and (B, y) in recs:
                    compare(f"{x} vs {y}", name, kind, v, recs[(B, x)], recs[(B, y)], days, a, B)
        if kind == "test period" and v == "warm-up":
            reason_picks(name, recs, budgets)
            oldest_picks(name, recs, budgets)


# ------------------------------------------------------------------------------------ W4, W6, W7, W8
def tail_table(name, h):
    T, ev = h.dur_h.values, h.event.values
    for e in (0, 8, 24, 48, 96, 168, 240, 336, 504, 672):
        m = T > e
        if m.sum() < 20:
            continue
        R = T[m] - e
        rel24 = ((R <= 24) & (ev[m] == 1)).mean()
        put("tail", line=name, elapsed_h=e, open=int(m.sum()), share_released_next_24h=float(rel24),
            median_remaining_h=float(np.median(R)), mean_remaining_trunc_tau_h=float(np.minimum(R, CAP).mean()),
            share_remaining_gt_8h=float((R > 8).mean()), censored_share=float(1 - ev[m].mean()))


def oldest_picks(name, recs, budgets):
    for B in budgets:
        for p in ("Age (oldest first)", "Ensemble"):
            r = recs.get((B, p))
            if r is None or r.empty:
                continue
            for lab, m in (("all", np.ones(len(r), bool)), ("e <= tau", r.e.values <= CAP), ("e > tau", r.e.values > CAP)):
                if m.sum() == 0:
                    continue
                put("picks_by_age", line=name, budget=B, policy=p, ages=lab, escalations=int(m.sum()),
                    share_nonescalable=float(r.nonesc.values[m].mean()) if "nonesc" in r else np.nan,
                    share_R_lt_delta=float((r.R.values[m] < DELTA).mean()),
                    share_R_lt_24h=float((r.R.values[m] < 24).mean()),
                    median_R_h=float(np.median(r.R.values[m])), mean_credit_h=float(r.saved_h.values[m].mean()))


REASON_STATS = {}


def reason_picks(name, recs, budgets):
    hs = REASON_STATS[name]
    for B in budgets:
        for p in ("Ensemble", "Age (oldest first)", "Oracle"):
            r = recs.get((B, p))
            if r is None or r.empty:
                continue
            share = r.reason.value_counts(normalize=True)
            for rs, s in share.head(10).items():
                put("reason_picks", line=name, budget=B, policy=p, reason=rs, share_of_escalations=float(s),
                    share_of_holds=float(hs["n"].get(rs, 0)), share_of_hold_hours=float(hs["h"].get(rs, 0)),
                    median_duration_h=float(hs["med"].get(rs, np.nan)))


def rule_footprint(name, h, tr):
    T, ev = h.dur_h.values, h.event.values
    for lo in range(0, 200):
        m = T > lo
        if m.sum() < 50:
            break
        put("footprint_hour", line=name, from_h=lo, to_h=lo + 1, open=int(m.sum()),
            hazard=float(((T[m] <= lo + 1) & (ev[m] == 1)).mean()))
    p = tr.groupby(["department", "reason"]).dur_h.quantile(.9)
    q = np.array([p.get((d, r), np.nan) for d, r in zip(h.department, h.reason)])
    ratio = T / q
    for lo in np.round(np.arange(0.0, 3.0, 0.1), 1):
        m = ratio > lo
        if np.nansum(m) < 50:
            break
        put("footprint_p90", line=name, from_ratio=float(lo), to_ratio=float(lo + 0.1), open=int(np.nansum(m)),
            hazard=float(((ratio[m] <= lo + 0.1) & (ev[m] == 1)).mean()))


def delivery_share(name, h, lots):
    if lots is None or "due_time" not in lots:
        return
    L = (lots.completion_time - lots.due_time).dt.total_seconds() / 3600
    L = L[L.index.isin(set(h.lot_id))]
    hh = h.groupby("lot_id").dur_h.sum()
    late = L[L > 0]
    hold_late = hh.reindex(late.index, fill_value=0.0)
    put("delivery", line=name, lots_with_due=int(L.notna().sum()), late_lots=int(len(late)),
        share_late=float(len(late) / max(L.notna().sum(), 1)),
        max_share_of_lateness_explained_by_holds=float(np.minimum(hold_late, late).sum() / late.sum()),
        share_late_lots_with_hold_hours_ge_lateness=float((hold_late >= late).mean()),
        hold_h_per_lot_mean=float(hh.mean()), hold_h_per_lot_median=float(hh.median()),
        hold_h_per_late_lot_mean=float(hold_late.mean()))


# ------------------------------------------------------------------------------------ main loop per line
def line_run(name, D, lots, a, budgets):
    h, oc, tr, va, te = D["h"], D["oc"], D["tr"], D["va"], D["te"]
    REASON_STATS[name] = dict(n=h.reason.value_counts(normalize=True),
                              h=h.groupby("reason").dur_h.sum() / h.dur_h.sum(),
                              med=h.groupby("reason").dur_h.median())
    log(f"[{name}] tail, footprint, delivery"); tail_table(name, h); rule_footprint(name, h, tr)
    delivery_share(name, h, lots)
    # test period
    log(f"[{name}] test period")
    sm, lm, _ = RH.fit(tr, va, oc)
    r0, r1 = RC.window_of(te)
    acc = {}
    _, (Cw, scw) = evaluate_window(name, "test period", h, oc, sm, lm, tr, te, r0, te.start_time.max(), a, budgets, acc)
    summarise(name, "test period", acc, a, budgets)
    # W3 H6 with more draws (test period, as in the paper: no warm-up)
    log(f"[{name}] H6 with {a.hetero_draws} draws")
    C = review_candidates(te, oc)
    sc = scores(C, te, sm, lm)
    Ce = C.assign(**{"s::" + k: v for k, v in sc.items()})
    grp = C.department.astype(str) + "|" + C.reason.astype(str); groups = grp.unique()
    for B in budgets:
        rels = []
        for k in range(a.hetero_draws):
            rng = np.random.default_rng(100 + k)
            al = dict(zip(groups, rng.uniform(0.2, 0.8, len(groups)))); de = dict(zip(groups, rng.uniform(1, 8, len(groups))))
            Ch = Ce.assign(alpha_h=grp.map(al).values, delta_h=grp.map(de).values)
            ra = simulate(Ch, "s::Ensemble", max(1, B // 6), alpha_col="alpha_h", delta_col="delta_h").saved_h.sum()
            rb = simulate(Ch, "s::Age (oldest first)", max(1, B // 6), alpha_col="alpha_h", delta_col="delta_h").saved_h.sum()
            rels.append(ra / max(rb, 1e-12) - 1)
        rels = np.array(rels)
        put("h6", line=name, budget=B, draws=len(rels), mean=float(rels.mean()), q05=float(np.quantile(rels, .05)),
            q50=float(np.median(rels)), q95=float(np.quantile(rels, .95)), share_positive=float((rels > 0).mean()))
    # rolling origins
    t_end = h.start_time.max().normalize()
    acc = {}
    for k in range(a.origins, 0, -1):
        t0 = t_end - pd.Timedelta(days=k * a.window_days); t1 = t0 + pd.Timedelta(days=a.window_days)
        past, test = h[h.start_time < t0], h[(h.start_time >= t0) & (h.start_time < t1)]
        if len(past) < 2000 or len(test) < 200:
            continue
        cut = past.start_time.quantile(0.8)
        trk, vak = past[past.start_time <= cut], past[past.start_time > cut]
        smk, lmk, _ = RH.fit(trk, vak, oc)
        r0k, _ = RC.window_of(test)
        evaluate_window(name, "rolling origins", h, oc, smk, lmk, trk, test, r0k, t1 - pd.Timedelta(hours=4), a,
                        budgets, acc)
        log(f"[{name}] origin {a.origins - k + 1} of {a.origins} done")
    summarise(name, "rolling origins", acc, a, budgets)


def pool():
    C = pd.DataFrame(ROWS.get("comparisons", []))
    if C.empty:
        return
    for (tag, variant, B), g in C[C.kind == "rolling origins"].groupby(["tag", "variant", "budget"]):
        if g.line.nunique() < 2:
            continue
        m = S.fixed_effect(g.log_ratio.values, g.log_ratio_se.values)
        w = 1 / np.maximum(g.log_ratio_se.values, 1e-12) ** 2
        put("pooled", tag=tag, variant=variant, budget=B, rel=m["rel"], rel_lo=m["rel_lo"], rel_hi=m["rel_hi"],
            p_greater=m["p_greater"], Q_p=m["Q_p"], I2=m["I2"], weight_line_A=float(w[0] / w.sum()))


def report(a, keys=None):
    os.makedirs(a.out, exist_ok=True)
    md = ["# Warm-up replay (aggregated, no dates)\n"]
    for t, rows in ROWS.items():
        df = pd.DataFrame(rows)
        df.to_csv(f"{a.out}/{t}.csv", index=False, float_format="%.6g")
        try:
            body = df.round(4).to_markdown(index=False)
        except ImportError:
            body = df.round(4).to_string(index=False)
        md += [f"\n## {t}\n", body]
    open(f"{a.out}/warmup.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    if keys:
        lo = os.path.join(a.out, "local_only"); os.makedirs(lo, exist_ok=True)
        for col in ("reason", "department"):
            if col in keys:
                pd.DataFrame([(v, k) for k, v in keys[col].items()], columns=["label", "original_code"]) \
                    .sort_values("label").to_csv(f"{lo}/LOCAL_ONLY_{col}_codes.csv", index=False)
        open(f"{lo}/README.txt", "w").write(
            "These files contain the ORIGINAL company codes. Keep them on this computer. Do not share or upload.\n"
            "Use them only to look up which anonymised reason labels (R01, R02, ...) in reason_picks.csv mean\n"
            "'waiting for customer decision', 'engineering change', or 'waiting for material'.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", action="append", required=True); ap.add_argument("--out", default="results_warmup")
    ap.add_argument("--budgets", default="6,12,24,48"); ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--origins", type=int, default=4); ap.add_argument("--window-days", dest="window_days", type=int, default=14)
    ap.add_argument("--warmup-days", dest="warmup_days", type=int, default=14)
    ap.add_argument("--hetero-draws", dest="hetero_draws", type=int, default=200)
    ap.add_argument("--nonescalable", default=None, help="local-only file from run_match_txn.py (optional)")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    global NONESC_FILE
    NONESC_FILE = a.nonescalable
    if a.quick:
        a.bootstrap, a.origins, a.budgets, a.hetero_draws, a.warmup_days = 200, 2, "6,24", 10, 7
    budgets = [int(x) for x in a.budgets.split(",")]
    specs = [tuple(s.split("=", 1)) for s in a.line]
    t0 = time.time()
    lines, lots, keys = load_lines_with_keys(specs)
    for name, _ in specs:
        D = RH.prepare(lines[name], purge=False)
        line_run(name, D, lots, a, budgets)
        pool(); report(a, keys)
    ROWS.pop("pooled", None); pool(); report(a, keys)
    log(f"done in {(time.time() - t0) / 60:.1f} min -> {a.out}/warmup.md  (do not share {a.out}/local_only/)")


if __name__ == "__main__":
    main()
