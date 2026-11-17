"""Tables 1, 3, 4 and 5 of the IISE Transactions article, rebuilt from the archived aggregated results.

    python scripts/make_tables.py [paper_results] [paper_output/tables]

Table 2 (hypotheses) and Supplemental Table S9 (positioning) are text tables in paper/.
Every number printed here is the number in the article; percentages use unrounded values.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "paper_results")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "paper_output", "tables")
os.makedirs(OUT, exist_ok=True)
BUDGETS = [6, 12, 24, 48]
MINUS = "−"


def holm(p):
    """Holm-adjusted p-values (step-down, monotone)."""
    p = np.asarray(p, float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


def pct(x, star=False, dagger=False):
    s = f"{100 * x:+.1f}".replace("-", MINUS)
    return s + ("*" if star else "") + ("†" if dagger else "")


def write(name, title, df, note):
    df.to_csv(os.path.join(OUT, f"{name}.csv"), index=False)
    md = [f"**{title}**", "", "| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    md += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    md += ["", f"Note: {note}", ""]
    with open(os.path.join(OUT, f"{name}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("wrote", name)


# ---------------------------------------------------------------- Table 1
ls = {L: pd.read_csv(f"{RES}/hypotheses/tables/{L}_line_summary.csv").iloc[0] for L in "AB"}
# Observation period: bulk of the extract (Line A also has 15 earlier holds, all in training; Supplemental Table S2).
# Test weeks: calendar weeks touched by the test days (the line summary counts complete weeks).
FIXED = {"A": {"months": 6, "weeks": 8, "dept": "about 70%"}, "B": {"months": 6, "weeks": 5, "dept": "over 90%"}}
rows = [
    ("Observation period (months)", lambda L: f"{FIXED[L]['months']}"),
    ("Holds / lots", lambda L: f"{int(ls[L].holds):,} / {int(ls[L].lots):,}"),
    ("Training / validation / test holds", lambda L: f"{int(ls[L].train):,} / {int(ls[L].val):,} / {int(ls[L].test):,}"),
    ("Test period: days (calendar weeks)", lambda L: f"{ls[L].test_days:.0f} ({FIXED[L]['weeks']})"),
    ("Median hold duration (h)", lambda L: f"{ls[L].median_h:.2f}"),
    ("Holds longer than 8 h (%)", lambda L: f"{100 * ls[L].share_gt8h:.1f}"),
    ("Departments; share of the largest", lambda L: f"{int(ls[L].departments)}; {FIXED[L]['dept']}"),
    ("Lots with a customer SOD", lambda L: (f"{100 * ls[L].lots_with_sod / ls[L].lots:.1f}%" if ls[L].lots_with_sod else "none")),
]
t1 = pd.DataFrame([{"": r, "Line A": f("A"), "Line B": f("B")} for r, f in rows])
write("Table1_lines", "Table 1. Data of the two production lines.", t1,
      "Test period: last 20% of holds by onset; test weeks: calendar weeks touched by the test days.")

# ---------------------------------------------------------------- Table 3
pw = pd.read_csv(f"{RES}/rolling/pred_within_landmark.csv")
order = ["Static p90", "Kaplan–Meier", "LightGBM onset", "Landmark GBM", "Ensemble"]
label = {"Static p90": "Static p90 rule", "Kaplan–Meier": "Kaplan–Meier (department × reason)",
         "Ensemble": "Ensemble index (4)"}
recs = []
for m in order:
    r = {"Model": label.get(m, m)}
    for L in "AB":
        x = pw[(pw.line == L) & (pw.model == m)]
        if x.empty:
            raise SystemExit(f"missing {m} for line {L} in pred_within_landmark.csv")
        x = x.iloc[0]
        r[f"C-index {L}"] = f"{x.C:.3f} [{x.C_lo:.3f}, {x.C_hi:.3f}]"
        r[f"AUC(> 8 h) {L}"] = f"{x.AUC:.3f} [{x.AUC_lo:.3f}, {x.AUC_hi:.3f}]"
    recs.append(r)
t3 = pd.DataFrame(recs)[["Model", "C-index A", "AUC(> 8 h) A", "C-index B", "AUC(> 8 h) B"]]
write("Table3_prediction", "Table 3. Discrimination among open holds (test period; landmarks 0.5–48 h, scores ranked "
      "within each landmark).", t3, "95% lot cluster bootstrap intervals (1,000 replicates) in brackets.")

# ---------------------------------------------------------------- Table 4
pol = pd.read_csv(f"{RES}/warmup/policies.csv")
cmp_ = pd.read_csv(f"{RES}/warmup/comparisons.csv")
ro = pol[(pol.kind == "rolling origins") & (pol.variant == "warm-up")]
cols = [f"{L}, B = {b}" for L in "AB" for b in BUDGETS]
plabel = [("Age (oldest first)", "Oldest-first"), ("Age <= tau", "Oldest-first, holds ≤ τ only"),
          ("Static p90 rule", "Static p90 rule"), ("p90, filled by oldest-first", "p90 rule, filled by oldest-first"),
          ("Kaplan–Meier (D×R)", "Kaplan–Meier (department × reason)"), ("Ensemble", "Ensemble index (4)"),
          ("Oracle", "Oracle")]
recs = []
for key, lab in plabel:
    r = {"Policy": lab}
    for L in "AB":
        for b in BUDGETS:
            v = ro[(ro.line == L) & (ro.budget == b) & (ro.policy == key)].h_per_calendar_day.iloc[0]
            r[f"{L}, B = {b}"] = f"{v:.1f}"
    recs.append(r)


def comp_row(tag, lab, kind, dagger_line=None):
    c = cmp_[(cmp_.tag == tag) & (cmp_.kind == kind) & (cmp_.variant == "warm-up")].copy()
    c["p_holm"] = c.groupby("line").p_greater.transform(holm)
    r = {"Policy": lab}
    for L in "AB":
        for b in BUDGETS:
            x = c[(c.line == L) & (c.budget == b)].iloc[0]
            dag = dagger_line == L
            r[f"{L}, B = {b}"] = pct(x.rel, star=(x.p_holm < 0.05 and not dag), dagger=dag)
    return r


recs += [comp_row("Ensemble vs Age (oldest first)", "Ensemble vs oldest-first (%)", "rolling origins"),
         comp_row("Kaplan–Meier (D×R) vs Age (oldest first)", "Kaplan–Meier vs oldest-first (%)", "rolling origins"),
         comp_row("Ensemble vs Kaplan–Meier (D×R)", "Ensemble vs Kaplan–Meier (%)", "rolling origins"),
         comp_row("Ensemble vs Age (oldest first)", "Ensemble vs oldest-first, test period (%)", "test period",
                  dagger_line="B")]
t4 = pd.DataFrame(recs)[["Policy"] + cols]
write("Table4_policies", "Table 4. Hold hours recovered per day over rolling origins (warm-up replay, α = 0.5, "
      "δ = 2 h); last row: single test period (hours in Supplemental Table S4b).", t4,
      "\"≤ τ only\": oldest-first among holds not older than τ; \"filled\": unused budget given to oldest-first; "
      "oracle: best holds at each review, not a bound for the whole replay. * p_Holm < 0.05 (one-sided, weekly block "
      "bootstrap); † fewer than six test weeks, not used for conclusions. Percentages use unrounded values.")

# ---------------------------------------------------------------- Table 5
h6 = pd.read_csv(f"{RES}/rolling/ro_h6.csv")
h7 = pd.read_csv(f"{RES}/rolling/ro_h7.csv")
h8 = pd.read_csv(f"{RES}/rolling/ro_h8.csv")
late = pd.read_csv(f"{RES}/diagnostics/lateness.csv")
mean_col, share_col = "mean", "share_positive"
recs = []
for L in "AB":
    r = {"Hypothesis": "H6 Heterogeneous α(c), δ(c): mean gain (share of draws > 0)", "Line": L}
    for b in BUDGETS:
        x = h6[(h6.line == L) & (h6.budget == b)].iloc[0]
        r[f"B = {b}"] = f"{pct(x[mean_col])} ({x[share_col]:.3g})".replace("(1)", "(1.00)")
    recs.append(r)
for L in "AB":
    r = {"Hypothesis": "H7 Gain-based vs mean-based index (TOST ±3%)", "Line": L}
    for b in BUDGETS:
        x = h7[(h7.line == L) & (h7.budget == b)].iloc[0]
        r[f"B = {b}"] = pct(x.rel, star=x.p_holm < 0.05)
    recs.append(r)
# ro_h8 lists models by the line they are evaluated on: B = trained on A, evaluated on B (A→B)
for test, lab in [("H8a", "H8a Transferred model vs oldest-first"),
                  ("H8b", "H8b Transferred vs in-line model (non-inferiority 3%)")]:
    for ev, arrow in [("B", "A→B"), ("A", "B→A")]:
        r = {"Hypothesis": lab, "Line": arrow}
        for b in BUDGETS:
            x = h8[(h8.line == ev) & (h8.budget == b) & (h8.test == test)].iloc[0]
            r[f"B = {b}"] = pct(x.rel, star=x.p_holm < 0.05)
        recs.append(r)
for b_pol, lab in [("Age (oldest first)", "H10 Lateness removed, ensemble + urgency vs oldest-first"),
                   ("Ensemble", "H10 Lateness removed, ensemble + urgency vs plain ensemble")]:
    x = late[(late.line == "A") & (late.a == "Ensemble + urgency") & (late.b == b_pol)].sort_values("budget")
    ph = holm(x.p_greater.values)
    r = {"Hypothesis": lab, "Line": "A"}
    for (_, row), p in zip(x.iterrows(), ph):
        r[f"B = {int(row.budget)}"] = pct(row.rel, star=p < 0.05)
    recs.append(r)
t5 = pd.DataFrame(recs)[["Hypothesis", "Line"] + [f"B = {b}" for b in BUDGETS]]
write("Table5_robustness", "Table 5. Robustness, transfer, and delivery (gain over oldest-first, %).", t5,
      "H6–H8 over rolling origins (warm-up replay); H10 on the test period of Line A (replay without warm-up). "
      "* significant after Holm correction (TOST for H7, one-sided otherwise).")
