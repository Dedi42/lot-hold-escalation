"""Hazard analysis and static (onset) survival models."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import norm
import lightgbm as lgb
from lifelines import CoxPHFitter, LogNormalAFTFitter, WeibullFitter
from .features import NUM, CAT, TARGET, encode

ELAPSED = [0, 0.5, 1, 2, 4, 8, 16, 24, 48, 96]


def residual_life_table(h: pd.DataFrame, cap_days: float = 30) -> pd.DataFrame:
    T = np.minimum(h.dur_h.values, 24 * cap_days)
    rows = []
    for e in ELAPSED:
        s = T[T > e] - e
        rows.append(dict(elapsed_h=e, open=len(s), share=len(s) / len(T), median_remaining_h=np.median(s),
                         mean_remaining_h=s.mean(), p_remaining_gt_8h=(s > 8).mean()))
    return pd.DataFrame(rows)


def department_table(h: pd.DataFrame, cap_days: float = 30) -> pd.DataFrame:
    g = h.assign(Tc=np.minimum(h.dur_h, 24 * cap_days)).groupby("department")
    t = g.agg(holds=("dur_h", "size"), median_h=("dur_h", "median"), p90_h=("dur_h", lambda s: s.quantile(.9)),
              mean_h=("Tc", "mean"), hours=("dur_h", "sum"))
    t["share_holds"] = t.holds / t.holds.sum(); t["share_hours"] = t.hours / t.hours.sum()
    return t.sort_values("holds", ascending=False)


class Grid:
    """Time grid for survival curves and the truncated conditional means of Equations (2)-(3).

    TARGET "remaining": E[min(T - e, cap) | T > e] and E[(min(T - e, cap) - delta)^+ | T > e]
    TARGET "total":     E[(min(T, cap) - e)^+ | T > e] and E[(min(T, cap) - e - delta)^+ | T > e]"""

    def __init__(self, cap, horizon=None):
        self.cap = cap
        self.remaining = TARGET == "remaining"
        H = horizon or (30 * cap if self.remaining else cap)
        self.t = np.concatenate([[0], np.logspace(-2, np.log10(H), 600 if self.remaining else 400)])

    def _integral(self, S, lo, hi):
        dg = np.diff(self.t); mid = (S[:, 1:] + S[:, :-1]) / 2
        cum = np.concatenate([np.zeros((S.shape[0], 1)), np.cumsum(mid * dg, axis=1)], axis=1)
        out = np.empty(S.shape[0])
        for i in range(S.shape[0]):
            a, b = min(lo[i], self.t[-1]), min(hi[i], self.t[-1])
            out[i] = max(np.interp(b, self.t, cum[i]) - np.interp(a, self.t, cum[i]), 0.0) if b > a else 0.0
        return out

    def _upper(self, e):
        return e + self.cap if self.remaining else np.full(len(e), float(self.cap))

    def _S_at(self, S, e):
        return np.maximum(np.array([np.interp(min(ei, self.t[-1]), self.t, S[i]) for i, ei in enumerate(e)]), 1e-9)

    def cond_mean(self, S: np.ndarray, e: np.ndarray) -> np.ndarray:
        """Truncated conditional mean remaining time of Equation (3) from survival curves S (n x grid)."""
        e = np.asarray(e, float)
        if not self.remaining:                                   # alternative target (HOLDESC_TARGET=total)
            dg = np.diff(self.t); mid = (S[:, 1:] + S[:, :-1]) / 2
            out = np.empty(len(e))
            for i, ei in enumerate(e):
                m = self.t[1:] > ei
                out[i] = (mid[i, m] * dg[m]).sum() / max(np.interp(ei, self.t, S[i]), 1e-9)
            return out
        return self._integral(S, e, self._upper(e)) / self._S_at(S, e)

    def cond_gain(self, S: np.ndarray, e: np.ndarray, delta) -> np.ndarray:
        """Expected recovered time of Equation (2) per unit alpha; delta may differ by row."""
        e = np.asarray(e, float)
        delta = np.broadcast_to(np.asarray(delta, float), np.shape(e))
        if not self.remaining:                                   # alternative target (HOLDESC_TARGET=total)
            dg = np.diff(self.t); mid = (S[:, 1:] + S[:, :-1]) / 2
            out = np.empty(len(e))
            for i, (ei, di) in enumerate(zip(e, delta)):
                m = self.t[1:] > ei + di
                out[i] = (mid[i, m] * dg[m]).sum() / max(np.interp(ei, self.t, S[i]), 1e-9)
            return out
        return self._integral(S, e + delta, self._upper(e)) / self._S_at(S, e)


def _design(fit: pd.DataFrame, *others, topk=None):
    topk = topk or {"department": 6, "reason": 15, "step": 30, "product_family": 10, "lot_type": 3}
    levels = {c: fit[c].value_counts().index[:k].tolist() for c, k in topk.items()}
    mu, sd = fit[NUM].mean(), fit[NUM].std().replace(0, 1)
    out = []
    for d in (fit,) + others:
        X = (d[NUM] - mu) / sd
        X["lot_prev_h"] = np.log1p(d.lot_prev_h)
        for c, lv in levels.items():
            for l in lv[1:]:
                X[f"{c}={l}"] = (d[c] == l).astype(float)
        out.append(X.astype(float))
    return out


class StaticModels:
    """Kaplan-Meier (department x reason), Cox PH, log-normal AFT, XGBoost AFT, LightGBM on log T."""

    def __init__(self, cap: float = 168.0, seed: int = 1):
        self.grid, self.seed = Grid(cap), seed

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None):
        self.train = train
        T, E = train.dur_h.clip(lower=1e-3).values, train.event.values
        Xtr, = _design(train); self._design_ref = train
        df = pd.concat([Xtr, pd.DataFrame({"T": T, "E": E}, index=Xtr.index)], axis=1)
        self.cox = CoxPHFitter(penalizer=0.01).fit(df, "T", "E")
        self.aft = LogNormalAFTFitter(penalizer=0.01).fit(df, "T", "E")
        self.aft_sigma = float(np.exp(self.aft.params_.loc["sigma_"].iloc[0]))
        import xgboost as xgb
        d = xgb.DMatrix(Xtr.values); d.set_float_info("label_lower_bound", T)
        d.set_float_info("label_upper_bound", np.where(E == 1, T, np.inf))
        self.xgb_sigma = 2.0
        self.xgb = xgb.train(dict(objective="survival:aft", aft_loss_distribution="normal",
                                  aft_loss_distribution_scale=self.xgb_sigma, tree_method="hist", learning_rate=0.05,
                                  max_depth=6, min_child_weight=20, nthread=1, seed=self.seed), d, 20)
        self.cats = {c: pd.Categorical(train[c]).categories for c in CAT}
        self.gbm = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.03, num_leaves=63, min_child_samples=40,
                                     verbose=-1, n_jobs=1, random_state=self.seed)
        self.gbm.fit(encode(train, self.cats, NUM), np.log(T))
        self.gbm_sigma = float(np.std(np.log(T) - self.gbm.predict(encode(train, self.cats, NUM))))
        return self

    def _lognorm_S(self, mu, sig):
        return 1 - norm.cdf((np.log(np.maximum(self.grid.t, 1e-6))[None, :] - mu[:, None]) / sig)

    def survival(self, test: pd.DataFrame) -> dict:
        _, Xte = _design(self._design_ref, test)
        import xgboost as xgb
        bch = self.cox.baseline_cumulative_hazard_
        H0 = np.interp(self.grid.t, bch.index.values, bch.iloc[:, 0].values)
        lp = self.cox.predict_log_partial_hazard(Xte).values
        mu_aft = np.log(np.maximum(self.aft.predict_median(Xte).values, 1e-4))
        mu_x = np.log(np.maximum(self.xgb.predict(xgb.DMatrix(Xte.values)), 1e-4))
        mu_g = self.gbm.predict(encode(test, self.cats, NUM))
        self.onset_scores = {"Cox PH": -lp, "Log-normal AFT": mu_aft, "XGBoost AFT": mu_x, "LightGBM (log T)": mu_g}
        return {"Cox PH": np.exp(-np.outer(np.exp(lp), H0)),
                "Log-normal AFT": self._lognorm_S(mu_aft, self.aft_sigma),
                "XGBoost AFT": self._lognorm_S(mu_x, self.xgb_sigma),
                "LightGBM (log T)": self._lognorm_S(mu_g, self.gbm_sigma)}

    def km_cond_mean(self, rows: pd.DataFrame, min_n: int = 30) -> np.ndarray:
        """Empirical (Kaplan-Meier) truncated mean remaining time of Equation (3) by department x reason,
        falling back to department and to the whole line."""
        cap = self.grid.cap; tr = self.train
        rem = self.grid.remaining
        eg = np.r_[0, np.logspace(np.log10(0.25), np.log10(self.grid.t[-1] if rem else cap), 60 if rem else 40)]

        def mrl(T, e):
            s = T[T > e]
            return (np.minimum(s - e, cap).mean() if rem else np.minimum(s, cap).mean() - e) if len(s) else 0.0

        def table(keys):
            out = {}
            for k, g in tr.groupby(keys):
                T = g.dur_h.values
                out[k] = np.array([mrl(T, e) if (T > e).sum() >= min_n else np.nan for e in eg])
            return out
        if not hasattr(self, "_km"):
            Tg = tr.dur_h.values
            self._km = (table(["department", "reason"]), table("department"), np.array([mrl(Tg, e) for e in eg]), eg)
        dr, dd, gl, eg = self._km
        out = np.empty(len(rows))
        for i, (d, r, e) in enumerate(zip(rows.department, rows.reason, rows.e)):
            v = np.nan
            if (d, r) in dr:
                v = np.interp(e, eg, dr[(d, r)])
            if np.isnan(v) and d in dd:
                v = np.interp(e, eg, dd[d])
            out[i] = np.interp(e, eg, gl) if np.isnan(v) else v
        return out

    def p90_ratio(self, rows: pd.DataFrame) -> np.ndarray:
        """Elapsed time divided by the 90th percentile of the hold's department x reason group."""
        tr = self.train
        p = tr.groupby(["department", "reason"]).dur_h.quantile(.9)
        pd_ = tr.groupby("department").dur_h.quantile(.9); pg = tr.dur_h.quantile(.9)
        q = np.array([p.get((d, r), pd_.get(d, pg)) for d, r in zip(rows.department, rows.reason)])
        return rows.e.values / q

    def p90_rule(self, rows: pd.DataFrame) -> np.ndarray:
        """Static percentile rule: eligible only beyond the group p90 (score -1 otherwise)."""
        r = self.p90_ratio(rows)
        return np.where(r > 1, r, -1.0)


def weibull_shapes(h: pd.DataFrame, departments) -> pd.DataFrame:
    """Weibull shape rho with 95% CI; rho < 1 means a decreasing hazard of release."""
    rows = {}
    for name, g in [("All", h)] + [(d, h[h.department == d]) for d in departments]:
        wf = WeibullFitter().fit(g.dur_h.clip(lower=1e-3), g.event)
        r = wf.summary.loc["rho_"]
        rows[name] = dict(weibull_shape=float(r["coef"]), weibull_lo=float(r["coef lower 95%"]), weibull_hi=float(r["coef upper 95%"]))
    return pd.DataFrame(rows).T
