"""Combine the rolling-origin benchmark runs (run_benchmark.py --origin k --fixed-hp ...) of one or more lines.

    python scripts/run_bench_rolling.py --run A=results_bench_A_ro1,results_bench_A_ro2,... --run B=... --out results_bench_rolling

For every learner and budget, the recovered hours of the windows are concatenated and compared with the paper
ensemble and with oldest-first by the paired weekly block bootstrap (as in the paper) and by an exact sign-flip test
over weeks; the t interval of the mean weekly log ratio is reported as well. Holm adjustment within each learner and
line over the four budgets. Top-b recall is averaged over the reviews of all windows. Pooling over the lines uses
inverse-variance weights (descriptive). Only aggregated numbers are written; day offsets are mapped to artificial
dates (year 2000) only to form calendar weeks.
"""
from __future__ import annotations
import argparse, itertools, os, sys
import numpy as np
import pandas as pd
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from holdesc import stats as S  # noqa: E402

ENS, AGE = "Ensemble (paper)", "Age (oldest first)"


def sign_flip_p(A, B, n_max=20000, seed=3):
    d = A - B
    n = len(d)
    signs = np.array(list(itertools.product([1, -1], repeat=n))) if 2 ** n <= n_max else \
        np.random.default_rng(seed).choice([1, -1], size=(n_max, n))
    stat = (signs * d).sum(1)
    return float(np.mean(stat >= d.sum() - 1e-9)), float(np.mean(stat <= d.sum() + 1e-9))


def t_interval(A, B):
    m = (A > 0) & (B > 0)
    x = np.log(A[m] / B[m])
    if len(x) < 3:
        return np.nan, np.nan
    se = x.std(ddof=1) / np.sqrt(len(x)); t = st.t.ppf(0.975, len(x) - 1)
    return float(np.exp(x.mean() - t * se) - 1), float(np.exp(x.mean() + t * se) - 1)


def load_line(dirs):
    recs, days, topb = {}, [], []
    base = pd.Timestamp("2000-01-03")                        # a Monday
    for k, d in enumerate(dirs):
        t = os.path.join(d, "tables")
        info = pd.read_csv(os.path.join(t, "bench_days.csv")).iloc[0]
        start = base + pd.Timedelta(days=70 * k + int(info.first_weekday))
        days.append(pd.date_range(start, periods=int(info.n_days), freq="D"))
        D = pd.read_csv(os.path.join(t, "bench_daily.csv"))
        D["policy"] = D.policy.where(~D.policy.str.startswith("Ensemble new"), "Hybrid (deep + LightGBM)")
        D["day"] = start + pd.to_timedelta(D.day, unit="D")
        for (p, B), g in D.groupby(["policy", "budget"]):
            recs.setdefault((p, int(B)), []).append(g[["day", "saved_h"]])
        T = pd.read_csv(os.path.join(t, "bench_topb.csv")).assign(window=k + 1)
        T["policy"] = T.policy.where(~T.policy.str.startswith("Ensemble new"), "Hybrid (deep + LightGBM)")
        topb.append(T)
    alldays = days[0]
    for x in days[1:]:
        alldays = alldays.union(x)
    recs = {k: pd.concat(v, ignore_index=True) for k, v in recs.items()}
    return recs, alldays, pd.concat(topb, ignore_index=True), len(dirs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="append", required=True, help="LINE=dir1,dir2,...")
    ap.add_argument("--out", default="results_bench_rolling"); ap.add_argument("--bootstrap", type=int, default=2000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows, trows = [], []
    for spec in a.run:
        line, dirs = spec.split("=", 1)
        recs, days, topb, nwin = load_line([d for d in dirs.split(",") if d])
        empty = pd.DataFrame(columns=["day", "saved_h"])
        wk = pd.Index(days).to_period("W")
        pols = sorted({p for p, _ in recs})
        budgets = sorted({B for _, B in recs})
        for p in pols:
            for B in budgets:
                ra = recs.get((p, B), empty)
                r = dict(line=line, policy=p, budget=B, windows=nwin,
                         h_per_day=S.weekly_series(ra, days).sum() / len(days))
                for ref, tag in ((ENS, "ens"), (AGE, "age")):
                    if p == ref or (ref, B) not in recs:
                        continue
                    rb = recs[(ref, B)]
                    bt = S.block_test(ra, rb, days, a.bootstrap)
                    A = S.weekly_series(ra, days).groupby(wk).sum().values
                    Bw = S.weekly_series(rb, days).groupby(wk).sum().values
                    pg, pl = sign_flip_p(A, Bw)
                    tlo, thi = t_interval(A, Bw)
                    r.update({f"rel_vs_{tag}": bt["rel"], f"lo_{tag}": bt["rel_lo"], f"hi_{tag}": bt["rel_hi"],
                              f"p_greater_{tag}": bt["p_greater"], f"p_less_{tag}": bt["p_less"],
                              f"p_signflip_greater_{tag}": pg, f"p_signflip_less_{tag}": pl,
                              f"t_lo_{tag}": tlo, f"t_hi_{tag}": thi,
                              f"log_ratio_{tag}": bt["log_ratio"], f"log_ratio_se_{tag}": bt["log_ratio_se"],
                              "weeks": bt["weeks"]})
                rows.append(r)
        g = topb.groupby(["policy", "budget"]).apply(
            lambda x: pd.Series(dict(recall_top_b=np.average(x.recall_top_b, weights=x.reviews), reviews=x.reviews.sum())))
        for (p, B), v in g.iterrows():
            trows.append(dict(line=line, policy=p, budget=B, **v.to_dict()))
    R = pd.DataFrame(rows)
    # Holm within learner x line over the budgets, two-sided by direction of the estimate
    for tag in ("ens", "age"):
        col = f"p_{tag}_holm"
        R[col] = np.nan
        for (_, _), g in R.dropna(subset=[f"rel_vs_{tag}"]).groupby(["line", "policy"]):
            p1 = np.where(g[f"rel_vs_{tag}"] >= 0, g[f"p_greater_{tag}"], g[f"p_less_{tag}"])
            R.loc[g.index, col] = S.holm(p1)
    # pooled over lines (descriptive)
    P = []
    for (p, B), g in R.dropna(subset=["rel_vs_ens"]).groupby(["policy", "budget"]):
        if g.line.nunique() < 2:
            continue
        m = S.fixed_effect(g.log_ratio_ens.values, g.log_ratio_se_ens.values)
        P.append(dict(policy=p, budget=B, rel_vs_ens=m["rel"], lo=m["rel_lo"], hi=m["rel_hi"], Q_p=m["Q_p"], I2=m["I2"]))
    R.to_csv(f"{a.out}/bench_rolling.csv", index=False, float_format="%.6g")
    pd.DataFrame(trows).to_csv(f"{a.out}/bench_rolling_topb.csv", index=False, float_format="%.6g")
    pd.DataFrame(P).to_csv(f"{a.out}/bench_rolling_pooled.csv", index=False, float_format="%.6g")
    md = ["# Benchmark over rolling origins (frozen hyperparameters)\n"]
    for L, g in R.groupby("line"):
        show = g.assign(gain=(100 * g.rel_vs_ens).round(1)).pivot_table(index="policy", columns="budget", values="gain")
        md += [f"\n## Line {L}: gain over the paper ensemble (%)\n", show.to_string()]
    open(f"{a.out}/bench_rolling.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
