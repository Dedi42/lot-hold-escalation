"""Diagnostics of the replay: censoring, truncation, delivery, refined age rule, Kaplan-Meier, escalation counts.

    python scripts/run_diagnostics.py --line A=config/local_lineA.yaml --line B=config/local_lineB.yaml --out results_diagnostics

Uses exactly the same data loading, split, models, and replay as run_hypotheses.py and adds:

  D1  censoring and truncation diagnostics: holds still open at the end of the extract (right-censored),
      holds of earlier periods still open when the replay window starts (not candidates), training labels
      that end after the training period, and the share of credited hours that come from censored holds.
  D2  Eq. (3) vs replay credit: escalations of holds older than tau and their credit, and a sensitivity replay
      in which the credit is truncated like the index, alpha * (min(T, tau) - e - delta)^+.
  D3  H10 extended: lateness removed by ensemble + urgency vs plain ensemble (does the weight matter?), and the
      hold hours that the urgency weight costs.
  D4  refined age rule: oldest first among the holds not older than tau ("Age <= tau"), test period and rolling
      origins.
  D5  Kaplan-Meier (department x reason) on the rolling origins, and how much of the ensemble's gain over oldest
      first KM already achieves.
  D6  escalation counts: reviews, reviews with fewer than b candidates, hours per escalation, and hours per
      calendar day vs per elapsed review day.
  D7  daily hold volume per relative week (no dates), to explain why the test period of a line is short.

Only aggregated numbers are written (no dates, no codes, no hold-level records), so the output folder can be
shared. Runtime is about that of run_hypotheses.py without the benchmark.
"""
from __future__ import annotations
import argparse, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import run_hypotheses as RH                                     # noqa: E402  (same functions as the paper run)
from holdesc.policy import review_candidates                    # noqa: E402
from holdesc import stats as S                                  # noqa: E402

CAP, ALPHA, DELTA = RH.CAP, RH.ALPHA0, RH.DELTA0
MAIN = ["Age (oldest first)", "Age <= tau", "Kaplan–Meier (D×R)", "Ensemble", "Oracle"]
OUT_ROWS = {}


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def put(table, **row):
    OUT_ROWS.setdefault(table, []).append(row)


# ------------------------------------------------------------------------------------ replay with more detail
def simulate_ext(C, score, b, eligible_only=False, credit="remaining", alpha=ALPHA, delta=DELTA, cap=CAP):
    """As holdesc.policy.simulate, but keeps e, R, censoring and review of every escalation.
    credit='remaining': alpha * (min(R, tau) - delta)^+   (replay of the paper)
    credit='total':     alpha * (min(T, tau) - e - delta)^+ = alpha * (min(R, tau - e) - delta)^+  (truncated like Eq. 3)"""
    escalated, rec, short = set(), [], 0
    for r, c in C.groupby("review", sort=True):
        c = c[~c.hold_index.isin(escalated)]
        if eligible_only:
            c = c[c[score] >= 0]
        if len(c) < b:
            short += 1
        if c.empty:
            continue
        pick = c.loc[c[score].nlargest(b).index]
        for h, R, e, lot, ev in zip(pick.hold_index, pick.R, pick.e, pick.lot_id, pick.event):
            escalated.add(h)
            room = min(R, cap) if credit == "remaining" else min(R, max(cap - e, 0.0))
            rec.append((r.normalize(), r, lot, alpha * max(room - delta, 0.0), e, R, int(ev == 0)))
    out = pd.DataFrame(rec, columns=["day", "review", "lot_id", "saved_h", "e", "R", "censored"])
    out.attrs["reviews_short"] = short
    return out


def scores_for(C, rows, sm, lm, lmg=None, lots=None):
    sc = RH.score_candidates(C, rows, sm, lm, lmg, lots)
    sc["Age <= tau"] = np.where(C.e.values <= CAP, C.e.values, -1.0)
    sc["Oracle (credit as Eq. 3)"] = np.minimum(C.R.values, np.maximum(CAP - C.e.values, 0.0))
    return sc


def run_policies(C, sc, budgets, names, credit="remaining"):
    Ce = C.assign(**{"s::" + k: v for k, v in sc.items()})
    elig = {"Static p90 rule", "Age <= tau"}
    return {(B, k): simulate_ext(Ce, "s::" + k, max(1, B // 6), eligible_only=k in elig, credit=credit)
            for B in budgets for k in names if k in sc}


def compare(tag, line, kind, recs, days, a, B, x, y, credit="remaining"):
    r = S.block_test(recs[(B, x)], recs[(B, y)], days, a.bootstrap)
    put("comparisons", tag=tag, line=line, kind=kind, credit=credit, budget=B, a=x, b=y, rel=r["rel"],
        rel_lo=r["rel_lo"], rel_hi=r["rel_hi"], p_greater=r["p_greater"], p_less=r["p_less"],
        a_h_per_day=r["a_h_per_day"], b_h_per_day=r["b_h_per_day"], log_ratio=r["log_ratio"],
        log_ratio_se=r["log_ratio_se"], weeks=r["weeks"])
    return r


def lateness(rec_a, rec_b, lots, lot_ids, a):
    """Lateness removed (hours), as in H10: a lot is late by L = completion - due > 0 in the data; the hold hours
    recovered on its escalated holds, s, are assumed to bring its completion forward one for one, so the lateness
    removed is min(s, L). Bootstrap over late lots."""
    late = (lots.completion_time - lots.due_time).dt.total_seconds() / 3600
    late = late[(late > 0) & late.index.isin(lot_ids)]
    if len(late) == 0:
        return None
    def removed(rec):
        s = rec.groupby("lot_id").saved_h.sum().reindex(late.index, fill_value=0.0)
        return np.minimum(s.values, late.values)
    xa, xb = removed(rec_a), removed(rec_b)
    rng = np.random.default_rng(7)
    idx = rng.integers(0, len(late), (a.bootstrap, len(late)))
    d = xa[idx].sum(1) - xb[idx].sum(1)
    rel_bs = xa[idx].sum(1) / np.maximum(xb[idx].sum(1), 1e-12) - 1
    return dict(late_lots=len(late), total_lateness_h=float(late.sum()), a_removed_h=float(xa.sum()),
                b_removed_h=float(xb.sum()), a_lots_recovered=int((xa >= late.values - 1e-9).sum()),
                b_lots_recovered=int((xb >= late.values - 1e-9).sum()),
                rel=xa.sum() / max(xb.sum(), 1e-12) - 1, rel_lo=np.quantile(rel_bs, .025),
                rel_hi=np.quantile(rel_bs, .975), p_greater=(np.sum(d <= 0) + 1) / (a.bootstrap + 1),
                p_less=(np.sum(d >= 0) + 1) / (a.bootstrap + 1))


# ------------------------------------------------------------------------------------ D1, D6, D7 diagnostics
def diagnostics(name, D, C):
    h, tr, va, te = D["h"], D["tr"], D["va"], D["te"]
    t_first, t_end = h.start_time.min(), max(h.start_time.max(), h.release_time.max())
    span = (h.start_time.max() - t_first).total_seconds() / 86400
    def per_day(d):
        s = (d.start_time.max() - d.start_time.min()).total_seconds() / 86400
        return len(d) / max(s, 1e-9), s
    row = dict(line=name, holds=len(h), span_days=round(span, 1), holds_per_day_all=len(h) / span)
    for k, d in (("train", tr), ("val", va), ("test", te)):
        rate, s = per_day(d)
        row[f"{k}_days"], row[f"{k}_holds_per_day"] = round(s, 1), rate
    # right censoring: holds without release at the end of the extract
    cens = h.event == 0
    row.update(censored_holds=int(cens.sum()), censored_share=float(cens.mean()),
               censored_in_test=int((te.event == 0).sum()), censored_in_train=int((tr.event == 0).sum()),
               censored_in_val=int((va.event == 0).sum()))
    # labels of training/validation holds that end after their period (known only later)
    v0, t0 = va.start_time.min(), te.start_time.min()
    row.update(train_released_after_train_end=int((tr.rel > v0).sum()),
               val_released_after_val_end=int((va.rel > t0).sum()))
    # holds of earlier periods still open at the first review of the test replay (not candidates)
    r0 = C.review.min()
    prev = h[(h.start_time < t0) & (h.rel > r0)]
    row.update(earlier_holds_open_at_first_review=len(prev),
               earlier_holds_remaining_h=float(((prev.rel - r0).dt.total_seconds() / 3600).clip(upper=CAP).sum()),
               test_candidates_at_first_review=int((C.review == r0).sum()),
               reviews=int(C.review.nunique()), calendar_days=int(RH.day_index(C).size),
               elapsed_review_days=round((C.review.max() - C.review.min()).total_seconds() / 86400, 1),
               holds_older_than_tau_share_of_candidates=float((C.e > CAP).mean()),
               candidates_censored_share=float((C.event == 0).mean()),
               hours_from_end_of_extract_to_last_review=round((t_end - C.review.max()).total_seconds() / 3600, 1))
    put("diagnostics", **row)
    # weekly volume, relative weeks only (no dates)
    wk = ((h.start_time - t_first).dt.total_seconds() // (7 * 86400)).astype(int)
    sp = h.split.values
    for w, g in h.groupby(wk):
        put("weekly_volume", line=name, week=int(w), holds=len(g), holds_per_day=len(g) / 7,
            lots=int(g.lot_id.nunique()), split=pd.Series(sp[g.index]).mode().iloc[0],
            top_department_share=float(g.department.astype(str).value_counts(normalize=True).iloc[0]),
            departments=int(g.department.nunique()), reasons=int(g.reason.nunique()),
            median_h=float(g.dur_h.median()), share_gt_8h=float((g.dur_h > 8).mean()),
            share_gt_tau=float((g.dur_h > CAP).mean()), censored=int((g.event == 0).sum()),
            product_families=int(g.product_family.nunique()) if "product_family" in g else np.nan)


# ------------------------------------------------------------------------------------ per line
def analyze(name, D, lots, a, budgets):
    h, oc, tr, va, te = D["h"], D["oc"], D["tr"], D["va"], D["te"]
    log(f"[{name}] fitting models (as in run_hypotheses.py)")
    sm, lm, lmg = RH.fit(tr, va, oc, shift=DELTA)
    C = review_candidates(te, oc)
    days = RH.day_index(C)
    diagnostics(name, D, C)
    sc = scores_for(C, te, sm, lm, lmg, lots)
    names = MAIN + ["Static p90 rule", "Ensemble + urgency", "Oracle (credit as Eq. 3)"]
    for credit in ("remaining", "total"):
        log(f"[{name}] test-period replay, credit = {credit}")
        recs = run_policies(C, sc, budgets, names, credit)
        for (B, k), rec in recs.items():
            b = max(1, B // 6)
            old = rec.e > CAP
            put("policies", line=name, kind="test period", credit=credit, budget=B, policy=k,
                h_per_calendar_day=rec.saved_h.sum() / len(days),
                h_per_review_day=rec.saved_h.sum() / (C.review.nunique() / 6),
                escalations=len(rec), max_escalations=b * C.review.nunique(), reviews_short=rec.attrs["reviews_short"],
                h_per_escalation=rec.saved_h.mean() if len(rec) else 0.0,
                escalations_older_than_tau=int(old.sum()), credit_h_older_than_tau=float(rec.saved_h[old].sum()),
                escalations_censored=int(rec.censored.sum()), credit_h_censored=float(rec.saved_h[rec.censored == 1].sum()),
                share_credit_censored=float(rec.saved_h[rec.censored == 1].sum() / max(rec.saved_h.sum(), 1e-12)))
        for B in budgets:
            for x, y in (("Ensemble", "Age (oldest first)"), ("Age <= tau", "Age (oldest first)"),
                         ("Ensemble", "Age <= tau"), ("Kaplan–Meier (D×R)", "Age (oldest first)"),
                         ("Ensemble", "Kaplan–Meier (D×R)")):
                compare(f"{x} vs {y}", name, "test period", recs, days, a, B, x, y, credit)
            if credit == "remaining" and "Ensemble + urgency" in sc and lots is not None and "due_time" in lots:
                compare("urgency cost in hold hours", name, "test period", recs, days, a, B, "Ensemble + urgency", "Ensemble")
                for x, y in (("Ensemble + urgency", "Ensemble"), ("Ensemble + urgency", "Age (oldest first)"),
                             ("Ensemble", "Age (oldest first)")):
                    r = lateness(recs[(B, x)], recs[(B, y)], lots, set(h.lot_id), a)
                    if r:
                        put("lateness", line=name, budget=B, a=x, b=y, **r)
    if a.origins > 0:
        rolling(name, h, oc, a, budgets)
    return sm, lm


def rolling(name, h, oc, a, budgets):
    """Rolling origins exactly as run_hypotheses.rolling_origins, with more policies; no dates are printed."""
    t_end = h.start_time.max().normalize()
    pol = ["Age (oldest first)", "Age <= tau", "Kaplan–Meier (D×R)", "Ensemble", "Oracle"]
    allrec = {(B, k): [] for B in budgets for k in pol}
    days_all = []
    for k in range(a.origins, 0, -1):
        t0 = t_end - pd.Timedelta(days=k * a.window_days); t1 = t0 + pd.Timedelta(days=a.window_days)
        past, test = h[h.start_time < t0], h[(h.start_time >= t0) & (h.start_time < t1)]
        if len(past) < 2000 or len(test) < 200:
            log(f"[{name}] origin {a.origins - k + 1}: too few holds, skipped"); continue
        cut = past.start_time.quantile(0.8)
        sm, lm, _ = RH.fit(past[past.start_time <= cut], past[past.start_time > cut], oc)
        C = review_candidates(test, oc); C = C[C.review < t1]
        sc = scores_for(C, test, sm, lm)
        recs = run_policies(C, sc, budgets, pol)
        dd = RH.day_index(C)
        for key, rec in recs.items():
            allrec[key].append(rec)
            B, p = key
            put("rolling_windows", line=name, origin=a.origins - k + 1, budget=B, policy=p,
                h_per_calendar_day=rec.saved_h.sum() / len(dd), escalations=len(rec))
        days_all.append(dd)
        log(f"[{name}] origin {a.origins - k + 1} of {a.origins} done")
    if not days_all:
        return
    days = days_all[0]
    for d in days_all[1:]:
        days = days.union(d)
    recs = {key: pd.concat(v) for key, v in allrec.items() if v}
    for (B, p), rec in recs.items():
        put("policies", line=name, kind="rolling origins", credit="remaining", budget=B, policy=p,
            h_per_calendar_day=rec.saved_h.sum() / len(days), escalations=len(rec),
            h_per_escalation=rec.saved_h.mean() if len(rec) else 0.0)
    for B in budgets:
        for x, y in (("Ensemble", "Age (oldest first)"), ("Age <= tau", "Age (oldest first)"),
                     ("Ensemble", "Age <= tau"), ("Kaplan–Meier (D×R)", "Age (oldest first)"),
                     ("Ensemble", "Kaplan–Meier (D×R)")):
            compare(f"{x} vs {y}", name, "rolling origins", recs, days, a, B, x, y)


def pool(budgets):
    """Inverse-variance pooling across lines (as H9) of every comparison on the rolling origins."""
    C = pd.DataFrame(OUT_ROWS.get("comparisons", []))
    if C.empty:
        return
    for (tag, kind, credit, B), g in C.groupby(["tag", "kind", "credit", "budget"]):
        if g.line.nunique() < 2 or kind != "rolling origins":
            continue
        m = S.fixed_effect(g.log_ratio.values, g.log_ratio_se.values)
        put("comparisons", tag=tag, line="pooled", kind=kind, credit=credit, budget=B, a=g.a.iloc[0], b=g.b.iloc[0],
            rel=m["rel"], rel_lo=m["rel_lo"], rel_hi=m["rel_hi"], p_greater=m["p_greater"],
            p_less=1 - m["p_greater"], I2=m["I2"])


def report(a):
    os.makedirs(a.out, exist_ok=True)
    lines = ["# Replay diagnostics\n"]
    for t, rows in OUT_ROWS.items():
        df = pd.DataFrame(rows)
        df.to_csv(f"{a.out}/{t}.csv", index=False, float_format="%.6g")
        try:
            body = df.round(4).to_markdown(index=False)
        except ImportError:
            body = df.round(4).to_string(index=False)
        lines += [f"\n## {t}\n", body]
    open(f"{a.out}/diagnostics_summary.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", action="append", required=True, help="NAME=config.yaml (repeat)")
    ap.add_argument("--out", default="results_diagnostics"); ap.add_argument("--budgets", default="6,12,24,48")
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--origins", type=int, default=4); ap.add_argument("--window-days", dest="window_days", type=int, default=14)
    ap.add_argument("--purge", action="store_true", help="use the purged split (the paper run did not)")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick:
        a.bootstrap, a.origins, a.budgets = 200, 2, "6,24"
    budgets = [int(x) for x in a.budgets.split(",")]
    specs = [tuple(s.split("=", 1)) for s in a.line]
    t0 = time.time()
    lines, lots = RH.load_lines(specs)
    for name, _ in specs:
        D = RH.prepare(lines[name], a.purge)
        analyze(name, D, lots, a, budgets)
        report(a)                                   # write after every line, so a crash keeps what is done
    pool(budgets)
    report(a)
    log(f"done in {(time.time() - t0) / 60:.1f} min -> {a.out}/diagnostics_summary.md")


if __name__ == "__main__":
    main()
