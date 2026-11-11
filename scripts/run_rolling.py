"""Hypotheses H6-H8 on rolling origins, an age-dependent escalation effect, and discrimination within landmarks.

    python scripts/run_rolling.py --line A=config/local_lineA.yaml --line B=config/local_lineB.yaml --out results_rolling

Same loading, anonymisation, split, models, and warm-up replay as run_warmup.py. Adds:

  L1a H6, H7, and H8 on the rolling origins (warm-up replay), so that no decision rests on the five-week test period of
      Line B: H6 group-specific alpha and delta (--hetero-draws draws, totals over the windows); H7 gain-based vs
      mean-based index (TOST, +-3%); H8a model of the other line vs oldest-first, H8b vs the in-line model
      (non-inferiority, 3%). The transferred model is the other line's model of the paper split.
  L1b escalation effect that weakens with the age of the hold: alpha(e) = 0.5 (1 + e / 24 h)^(-gamma),
      gamma in --gammas (0 = constant effect, as in the paper); the policies rank exactly as before.
  L1c every comparison also gets an exact sign-flip test over weeks and a t interval of the mean weekly log ratio.
  L2  discrimination as in Table 4, but with scores ranked within each landmark (as a review ranks the holds open at
      that time), cluster bootstrap over lots with --lm-bootstrap replicates; and per-landmark C-index and AUC,
      including the landmark e = 0 (onset).

Policies pick the same holds whatever the escalation effect, so each policy is replayed once per window and budget
and only the credit of its picks changes between H6 draws and gamma values. Only aggregated numbers are written.
"""
from __future__ import annotations
import argparse, os, sys, time
import numpy as np
import pandas as pd
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import run_hypotheses as RH                                     # noqa: E402
import run_robustness as RC                                  # noqa: E402
import run_warmup as WU                                        # noqa: E402
from holdesc.features import landmark_frame                     # noqa: E402
from holdesc.evaluate import pooled_bootstrap                   # noqa: E402
from holdesc import stats as S                                  # noqa: E402
from lifelines.utils import concordance_index                   # noqa: E402
from sklearn.metrics import roc_auc_score                       # noqa: E402

CAP, ALPHA, DELTA = RH.CAP, RH.ALPHA0, RH.DELTA0
ROWS = {}
POLS = ["Age (oldest first)", "Kaplan–Meier (D×R)", "Ensemble", "Ensemble (gain)", "Transfer", "Oracle"]


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def put(t, **r):
    ROWS.setdefault(t, []).append(r)


# ------------------------------------------------------------------------------------ L2 prediction
def rank_e(L, v):
    return L.assign(_v=np.asarray(v, float)).groupby("e")["_v"].rank(pct=True).values


def prediction(name, D, models, a):
    te, oc = D["te"], D["oc"]
    sm, lm, _ = models
    for lms, tag in ((RH.EVAL_LM, "pooled"), ([0] + list(RH.EVAL_LM), "by landmark")):
        L = landmark_frame(te, oc, lms, CAP)
        pos = pd.Series(np.arange(len(te)), index=te.index).loc[L.hold_index].values
        Sv = sm.survival(te)
        raw = {"LightGBM onset": sm.grid.cond_mean(Sv["LightGBM (log T)"][pos], L.e.values),
               "Landmark GBM": lm.predict(L), "Kaplan–Meier": sm.km_cond_mean(L), "Static p90": sm.p90_ratio(L)}
        if tag == "by landmark":
            y = L.remaining.values
            for e, idx in L.groupby("e").indices.items():
                ens = rank_e(L.iloc[idx], raw["Landmark GBM"][idx]) + rank_e(L.iloc[idx], raw["LightGBM onset"][idx])
                for m, v in list(raw.items()) + [("Ensemble", ens)]:
                    v = np.asarray(v, float)[idx] if m != "Ensemble" else ens
                    yb = (y[idx] > 8).astype(int)
                    put("pred_by_landmark", line=name, e=e, n=len(idx), model=m,
                        C=concordance_index(y[idx], v), AUC8=roc_auc_score(yb, v) if 0 < yb.mean() < 1 else np.nan)
            continue
        # Table 4 as published (scores pooled over landmarks) and within-landmark ranks (decision-aligned)
        ens_pub = pd.Series(raw["Landmark GBM"]).rank(pct=True).values + pd.Series(raw["LightGBM onset"]).rank(pct=True).values
        y = L.remaining.values; yb = (y > 8).astype(int)
        for m, v in list(raw.items()) + [("Ensemble", ens_pub)]:
            put("pred_pooled_point", line=name, model=m, version="pooled scores (Table 4 as published)",
                C=concordance_index(y, v), AUC8=roc_auc_score(yb, v))
        ens_w = rank_e(L, rank_e(L, raw["Landmark GBM"]) + rank_e(L, raw["LightGBM onset"]))
        cols = {"Ensemble": "w_ens", "LightGBM onset": "w_onset", "Landmark GBM": "w_land", "Kaplan–Meier": "w_km",
                "Static p90": "w_p90"}
        Lw = L.assign(w_ens=ens_w, w_onset=rank_e(L, raw["LightGBM onset"]), w_land=rank_e(L, raw["Landmark GBM"]),
                      w_km=rank_e(L, raw["Kaplan–Meier"]), w_p90=rank_e(L, raw["Static p90"]))
        pairs = [("Ensemble", "LightGBM onset"), ("Ensemble", "Landmark GBM"), ("Ensemble", "Kaplan–Meier"),
                 ("Landmark GBM", "Static p90")]
        log(f"[{name}] prediction bootstrap ({a.lm_bootstrap} replicates, {len(Lw):,} rows)")
        ci, diffs = pooled_bootstrap(Lw, cols, B=a.lm_bootstrap, pairs=pairs)
        for _, r in ci.iterrows():
            put("pred_within_landmark", line=name, **r.to_dict())
        fam = []
        for (x, y_), lab in zip(pairs, ["H3a", "H3b", "H3c", "H3d"]):
            for metric in ("AUC", "C"):
                r = diffs[(diffs.model_a == x) & (diffs.model_b == y_) & (diffs.metric == metric)].iloc[0]
                p1 = r.p_two_sided / 2 if r["diff"] > 0 else 1 - r.p_two_sided / 2
                p1 = max(p1, 1 / (a.lm_bootstrap + 1))            # resolution of the bootstrap
                fam.append(dict(line=name, hypothesis=lab, metric=metric, model_a=x, model_b=y_, diff=r["diff"],
                                lo=r.lo, hi=r.hi, p_one_sided=p1))
        F = pd.DataFrame(fam)
        for metric, g in F[F.hypothesis.isin(["H3a", "H3b", "H3c"])].groupby("metric"):
            F.loc[g.index, "p_holm"] = S.holm(g.p_one_sided.values)
        F.loc[F.hypothesis == "H3d", "p_holm"] = F.loc[F.hypothesis == "H3d", "p_one_sided"]
        for _, r in F.iterrows():
            put("pred_within_landmark_tests", **r.to_dict())


# ------------------------------------------------------------------------------------ L1 replay helpers
def picks(C, score, b, r0):
    """Rows picked by a policy (top b by score among open, not yet escalated holds at each review); only picks at
    reviews >= r0 are returned (the warm-up picks are made and remembered). Same rule as policy.simulate."""
    rev = C.review.values
    order = np.argsort(rev, kind="stable")
    bounds = np.flatnonzero(np.r_[True, rev[order][1:] != rev[order][:-1], True])
    hold = C.hold_index.values
    s = np.asarray(score, float)
    escalated, out = set(), []
    r0 = np.datetime64(r0)
    for i in range(len(bounds) - 1):
        rows = order[bounds[i]:bounds[i + 1]]
        rows = rows[[hold[j] not in escalated for j in rows]] if escalated else rows
        if len(rows) == 0:
            continue
        top = rows[np.argsort(-s[rows], kind="stable")[:b]]
        for j in top:
            escalated.add(hold[j])
        if rev[rows[0]] >= r0:
            out.extend(top.tolist())
    return np.array(out, dtype=int)


def rec_of(C, pos, credit):
    return pd.DataFrame({"day": pd.DatetimeIndex(C.review.values[pos]).normalize(), "saved_h": credit[pos]})


def credit(C, alpha):
    return np.asarray(alpha, float) * np.maximum(np.minimum(C.R.values, CAP) - DELTA, 0.0)


def weekly(rec, days):
    wk = pd.Index(days).to_period("W")
    return S.weekly_series(rec, days).groupby(wk).sum().values


def compare(tag, line, variant, ra, rb, days, a, B, **kw):
    r = S.block_test(ra, rb, days, a.bootstrap)
    A, Bw = weekly(ra, days), weekly(rb, days)
    d = A - Bw
    n = len(d)
    import itertools
    signs = np.array(list(itertools.product([1, -1], repeat=n))) if 2 ** n <= 20000 else \
        np.random.default_rng(3).choice([1, -1], size=(20000, n))
    stat = (signs * d).sum(1)
    m = (A > 0) & (Bw > 0)
    x = np.log(A[m] / Bw[m])
    if len(x) >= 3:
        se = x.std(ddof=1) / np.sqrt(len(x)); t = st.t.ppf(0.975, len(x) - 1)
        tlo, thi = np.exp(x.mean() - t * se) - 1, np.exp(x.mean() + t * se) - 1
    else:
        tlo = thi = np.nan
    row = dict(tag=tag, line=line, variant=variant, budget=B, rel=r["rel"], rel_lo=r["rel_lo"], rel_hi=r["rel_hi"],
               p_greater=r["p_greater"], p_less=r["p_less"], p_signflip_greater=float(np.mean(stat >= d.sum() - 1e-9)),
               p_signflip_less=float(np.mean(stat <= d.sum() + 1e-9)), t_lo=tlo, t_hi=thi,
               a_h_per_day=r["a_h_per_day"], b_h_per_day=r["b_h_per_day"], log_ratio=r["log_ratio"],
               log_ratio_se=r["log_ratio_se"], weeks=n, **kw)
    put("ro_comparisons", **row)
    return r


# ------------------------------------------------------------------------------------ L1 rolling origins
def rolling(name, D, models_src, a, budgets, gammas):
    h, oc = D["h"], D["oc"]
    t_end = h.start_time.max().normalize()
    groups = np.array(sorted((h.department.astype(str) + "|" + h.reason.astype(str)).unique()))
    acc = {}                       # (variant, B, policy) -> list of recs
    days_all = None
    h6 = {B: np.zeros((a.hetero_draws, 2)) for B in budgets}
    for k in range(a.origins, 0, -1):
        t0 = t_end - pd.Timedelta(days=k * a.window_days); t1 = t0 + pd.Timedelta(days=a.window_days)
        past, test = h[h.start_time < t0], h[(h.start_time >= t0) & (h.start_time < t1)]
        if len(past) < 2000 or len(test) < 200:
            log(f"[{name}] origin {k}: too few holds, skipped"); continue
        cut = past.start_time.quantile(0.8)
        trk, vak = past[past.start_time <= cut], past[past.start_time > cut]
        log(f"[{name}] origin {a.origins - k + 1} of {a.origins}: fitting")
        smk, lmk, lmgk = RH.fit(trk, vak, oc, shift=DELTA)
        r0, _ = RC.window_of(test)
        r1 = t1 - pd.Timedelta(hours=4)
        w0 = (r0 - pd.Timedelta(days=a.warmup_days)).ceil("4h")
        cand = h[(h.start_time <= r1) & (h.rel > w0)]
        C = RC.candidates_window(cand, oc, w0, r1)
        sc = RH.score_candidates(C, cand, smk, lmk, lmgk)
        if models_src is not None:
            sc["Transfer"] = RH.score_candidates(C, cand, models_src[0], models_src[1])["Ensemble"]
        days = WU.days_from(C[C.review >= r0], r0)
        days_all = days if days_all is None else days_all.union(days)
        grp = (C.department.astype(str) + "|" + C.reason.astype(str)).values
        gidx = np.searchsorted(groups, grp)
        cr0 = credit(C, ALPHA)
        crg = {g: credit(C, ALPHA * (1 + C.e.values / 24.0) ** (-g)) for g in gammas if g > 0}
        Rc = np.minimum(C.R.values, CAP)
        for B in budgets:
            b = max(1, B // 6)
            P = {p: picks(C, sc[p], b, r0) for p in POLS if p in sc}
            for p, pos in P.items():
                acc.setdefault(("warm-up", B, p), []).append(rec_of(C, pos, cr0))
                for g, cg in crg.items():
                    if p in ("Age (oldest first)", "Kaplan–Meier (D×R)", "Ensemble", "Oracle"):
                        acc.setdefault((f"alpha(e), gamma {g:g}", B, p), []).append(rec_of(C, pos, cg))
            # effect-aware oracle under alpha(e) (upper bound when the effect weakens with age)
            for g in crg:
                pos = picks(C, crg[g], b, r0)
                acc.setdefault((f"alpha(e), gamma {g:g}", B, "Oracle, effect-aware"), []).append(rec_of(C, pos, crg[g]))
            # H6: credit of the same picks under group-specific alpha, delta
            for d in range(a.hetero_draws):
                rng = np.random.default_rng(100 + d)
                al = rng.uniform(0.2, 0.8, len(groups))[gidx]; de = rng.uniform(1, 8, len(groups))[gidx]
                c = al * np.maximum(Rc - de, 0.0)
                h6[B][d, 0] += c[P["Ensemble"]].sum(); h6[B][d, 1] += c[P["Age (oldest first)"]].sum()
        log(f"[{name}] origin {a.origins - k + 1} of {a.origins} done")
    recs = {key: pd.concat(v, ignore_index=True) for key, v in acc.items()}
    for (v, B, p), rec in recs.items():
        put("ro_policies", line=name, variant=v, budget=B, policy=p, h_per_calendar_day=rec.saved_h.sum() / len(days_all),
            escalations=len(rec))
    for B in budgets:
        g = lambda v, p: recs.get((v, B, p))
        for v in ["warm-up"] + [f"alpha(e), gamma {x:g}" for x in gammas if x > 0]:
            compare("Ensemble vs Age (oldest first)", name, v, g(v, "Ensemble"), g(v, "Age (oldest first)"), days_all, a, B)
            compare("Kaplan–Meier (D×R) vs Age (oldest first)", name, v, g(v, "Kaplan–Meier (D×R)"),
                    g(v, "Age (oldest first)"), days_all, a, B)
            compare("Ensemble vs Kaplan–Meier (D×R)", name, v, g(v, "Ensemble"), g(v, "Kaplan–Meier (D×R)"), days_all, a, B)
        if g("warm-up", "Ensemble (gain)") is not None:
            r = compare("H7 Ensemble (gain) vs Ensemble", name, "warm-up", g("warm-up", "Ensemble (gain)"),
                        g("warm-up", "Ensemble"), days_all, a, B)
            t = S.tost_bootstrap(r["rel_bs"], a.margin)
            put("ro_h7", line=name, budget=B, rel=r["rel"], ci90_lo=t["ci90_lo"], ci90_hi=t["ci90_hi"], p_tost=t["p_tost"])
        if g("warm-up", "Transfer") is not None:
            r = compare("H8a Transfer vs Age (oldest first)", name, "warm-up", g("warm-up", "Transfer"),
                        g("warm-up", "Age (oldest first)"), days_all, a, B)
            put("ro_h8", line=name, budget=B, test="H8a", rel=r["rel"], lo=r["rel_lo"], hi=r["rel_hi"], p=r["p_greater"])
            r = compare("H8b Transfer vs Ensemble", name, "warm-up", g("warm-up", "Transfer"), g("warm-up", "Ensemble"),
                        days_all, a, B)
            put("ro_h8", line=name, budget=B, test="H8b", rel=r["rel"], lo=r["rel_lo"], hi=r["rel_hi"],
                p=S.noninferior(r["rel_bs"], a.margin))
        rels = h6[B][:, 0] / np.maximum(h6[B][:, 1], 1e-12) - 1
        if a.hetero_draws:
            put("ro_h6", line=name, budget=B, draws=a.hetero_draws, mean=float(rels.mean()),
                q05=float(np.quantile(rels, .05)), q50=float(np.median(rels)), q95=float(np.quantile(rels, .95)),
                share_positive=float((rels > 0).mean()))


def holm_tables():
    C = pd.DataFrame(ROWS.get("ro_comparisons", []))
    if C.empty:
        return
    C["p_holm"] = np.nan
    for _, g in C.groupby(["tag", "line", "variant"]):
        p1 = np.where(g.rel >= 0, g.p_greater, g.p_less)
        C.loc[g.index, "p_holm"] = S.holm(p1)
        p2 = np.where(g.rel >= 0, g.p_signflip_greater, g.p_signflip_less)
        C.loc[g.index, "p_signflip_holm"] = S.holm(p2)
    ROWS["ro_comparisons"] = C.to_dict("records")
    for t, key in (("ro_h8", ["line", "test"]), ("ro_h7", ["line"])):
        T = pd.DataFrame(ROWS.get(t, []))
        if T.empty:
            continue
        pc = "p" if t == "ro_h8" else "p_tost"
        for _, g in T.groupby(key):
            T.loc[g.index, "p_holm"] = S.holm(g[pc].values)
        ROWS[t] = T.to_dict("records")
    P = []
    for (tag, v, B), g in C.groupby(["tag", "variant", "budget"]):
        if g.line.nunique() < 2:
            continue
        m = S.fixed_effect(g.log_ratio.values, g.log_ratio_se.values)
        P.append(dict(tag=tag, variant=v, budget=B, rel=m["rel"], rel_lo=m["rel_lo"], rel_hi=m["rel_hi"],
                      p_greater=m["p_greater"], Q_p=m["Q_p"], I2=m["I2"]))
    ROWS["ro_pooled"] = P


def report(a):
    os.makedirs(a.out, exist_ok=True)
    md = ["# Rolling-origin hypotheses (aggregated, no dates)\n"]
    for t, rows in ROWS.items():
        df = pd.DataFrame(rows)
        df.to_csv(f"{a.out}/{t}.csv", index=False, float_format="%.6g")
        try:
            body = df.round(4).to_markdown(index=False)
        except ImportError:
            body = df.round(4).to_string(index=False)
        md += [f"\n## {t}\n", body]
    open(f"{a.out}/rolling.md", "w", encoding="utf-8").write("\n".join(md) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--line", action="append", required=True); ap.add_argument("--out", default="results_rolling")
    ap.add_argument("--budgets", default="6,12,24,48"); ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--lm-bootstrap", dest="lm_bootstrap", type=int, default=1000)
    ap.add_argument("--origins", type=int, default=4); ap.add_argument("--window-days", dest="window_days", type=int, default=14)
    ap.add_argument("--warmup-days", dest="warmup_days", type=int, default=14)
    ap.add_argument("--hetero-draws", dest="hetero_draws", type=int, default=200)
    ap.add_argument("--gammas", default="0,0.25,0.5,1"); ap.add_argument("--margin", type=float, default=0.03)
    ap.add_argument("--skip-prediction", dest="skip_prediction", action="store_true")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick:
        a.bootstrap, a.lm_bootstrap, a.origins, a.budgets, a.hetero_draws, a.warmup_days = 200, 50, 1, "6,24", 5, 7
    budgets = [int(x) for x in a.budgets.split(",")]
    gammas = [float(x) for x in a.gammas.split(",")]
    specs = [tuple(s.split("=", 1)) for s in a.line]
    t0 = time.time()
    lines, lots, _ = WU.load_lines_with_keys(specs)
    Ds, models = {}, {}
    for name, _ in specs:
        Ds[name] = RH.prepare(lines[name], purge=False)
        log(f"[{name}] fitting the models of the paper split")
        models[name] = RH.fit(Ds[name]["tr"], Ds[name]["va"], Ds[name]["oc"], shift=DELTA)
    for name, _ in specs:
        if not a.skip_prediction:
            prediction(name, Ds[name], models[name], a)
            report(a)
        other = [n for n, _ in specs if n != name]
        rolling(name, Ds[name], models[other[0]] if other else None, a, budgets, gammas)
        holm_tables(); report(a)
    log(f"done in {(time.time() - t0) / 60:.1f} min -> {a.out}/rolling.md")


if __name__ == "__main__":
    main()
