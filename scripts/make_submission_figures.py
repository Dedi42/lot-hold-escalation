"""Figures 2-4 of 'Budgeted escalation of lot holds in semiconductor manufacturing' from the aggregated data in paper_results/figures_data/.

    python scripts/make_submission_figures.py [output folder]     (default: paper_output/figures)

Figure 2: concentration of hold hours (H1) and median remaining time by elapsed time (test of H2b);
Figure 3: policies as a share of the oracle's hold hours over rolling origins (warm-up replay);
Figure 4: benchmark over rolling origins, gain over the ensemble index (Holm per learner and line).
The data files contain only aggregated numbers.
Requires numpy, pandas, matplotlib.
"""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle

plt.rcParams["svg.fonttype"] = "none"          # SVG text stays editable text
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                     "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5,
                     "ytick.labelsize": 7.5, "legend.fontsize": 7.5, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                     "ytick.major.width": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#404040", "xtick.color": "#404040", "ytick.color": "#404040"})
ACC, GREY, DARK, LIGHT = "#2F5D8A", "#8C8C8C", "#262626", "#D9D9D9"
COL = {"A": ACC, "B": GREY}; MK = {"A": "o", "B": "s"}
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "paper_results", "figures_data")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "paper_output", "figures")
os.makedirs(OUT, exist_ok=True)
ACC, GREY, DARK, LIGHT = "#2F5D8A", "#8C8C8C", "#262626", "#D9D9D9"
COL = {"A": ACC, "B": GREY}; MK = {"A": "o", "B": "s"}
W = 6.3
B = [6, 12, 24, 48]
T = pd.read_csv(f"{DATA}/fig2_concentration.csv")
_RL = pd.read_csv(f"{DATA}/fig2_median_remaining.csv")
def tbl(name, L):
    return _RL[_RL.line == L].drop(columns="line").reset_index(drop=True)
def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(f"{OUT}/{name}.{ext}", dpi=600, bbox_inches="tight", pad_inches=0.03,
                    metadata={"png": {}, "pdf": {"CreationDate": None, "ModDate": None}, "svg": {"Date": None}}[ext])
    plt.close(fig)
def tag(ax, t):
    ax.text(-0.02, 1.04, t, transform=ax.transAxes, fontsize=8.5, fontweight="bold", va="bottom", ha="right")

# ------------------------------------------------------------------ Figure 2
fig = plt.figure(figsize=(W, 2.35))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.7], wspace=0.32)
ax = fig.add_subplot(gs[0])
for k, L in enumerate(["A", "B"]):
    sh = 100 * float(T[(T.hypothesis == "H1") & (T.line == L)].estimate.iloc[0])
    ax.barh(k, sh, color=COL[L], height=0.55)
    ax.barh(k, 100 - sh, left=sh, color="white", edgecolor=LIGHT, height=0.55, lw=0.6)
    ax.text(sh / 2, k, f"{sh:.0f}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.text(sh + (100 - sh) / 2, k, f"{100 - sh:.0f}%", ha="center", va="center", color=DARK, fontsize=8)
ax.set_yticks([0, 1]); ax.set_yticklabels(["Line A", "Line B"]); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.set_xlim(0, 100); ax.set_xticks([0, 50, 100]); ax.set_xlabel("Share of hold hours (%)")
ax.set_ylim(1.55, -1.05)
ax.text(37, -0.62, "longest 10% of holds", ha="center", va="center", fontsize=7.5, color=DARK)
ax.text(90, -0.62, "other 90%", ha="center", va="center", fontsize=7.5, color=DARK)
tag(ax, "(a)")
ax = fig.add_subplot(gs[1])
for L in ["A", "B"]:
    r = tbl("residual_life", L); r = r[r.elapsed_h > 0]
    ax.plot(r.elapsed_h, r.median_remaining_h, "-", marker=MK[L], ms=3.2, lw=1.1, color=COL[L], mfc="white" if L == "B" else COL[L], label=f"Line {L}")
x = np.array([0.4, 130]); ax.plot(x, x, ":", color=DARK, lw=0.8, label="$\\tilde{m}(e) = e$")
ax.set_xscale("log"); ax.set_yscale("log")
for a_ in (ax.xaxis, ax.yaxis): a_.set_major_formatter(FuncFormatter(lambda v, _: "%g" % v))
ax.set_xlabel("Elapsed time of the open hold, $e$ (h)"); ax.set_ylabel("Median remaining time, $\\tilde{m}(e)$ (h)")
ra, rb = tbl("residual_life", "A").set_index("elapsed_h"), tbl("residual_life", "B").set_index("elapsed_h")
f = lambda v: f"{v:.1f}" if v < 10 else f"{v:.0f}"
for e in (1, 8, 96):
    a_, b_ = ra.median_remaining_h[e], rb.median_remaining_h[e]
    top = max(a_, b_)
    ax.annotate(f"A {f(a_)} h\nB {f(b_)} h", xy=(e, top), xytext=(e, top * 3.6), ha="center", va="bottom", fontsize=7,
                color=DARK, linespacing=1.0, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5))
ax.set_ylim(0.5, 2500)
ax.legend(frameon=False, loc="upper left", handlelength=1.6, borderaxespad=0.1)
tag(ax, "(b)")
save(fig, "Figure2_concentration_remaining_time")

# ------------------------------------------------------------------ Figure 3 (warm-up replay, test period)
P0 = pd.read_csv(f"{DATA}/fig3_policies_rolling_origins.csv")
Bs = [6, 12, 24, 48]
rows = []
for L in "AB":
    P = P0[P0.line == L].pivot(index="policy", columns="budget", values="h_per_calendar_day")
    for b in Bs:
        o = P.loc["Oracle", b]
        rows.append(dict(line=L, B=b, p90=P.loc["Static p90 rule", b] / o, km=P.loc["Kaplan–Meier (D×R)", b] / o,
                         age=P.loc["Age (oldest first)", b] / o, idx=P.loc["Ensemble", b] / o))
R = pd.DataFrame(rows)
fig, ax = plt.subplots(figsize=(W, 2.6))
ys = []
for k, r in R.iterrows():
    y = k + (0.6 if r.line == "B" else 0); ys.append(y)
    vals = [r.p90, r.age, r.idx, r.km]
    ax.plot([min(vals) * 100, 100], [y, y], color=LIGHT, lw=0.8, zorder=1)
    ax.plot([r.age * 100, r.idx * 100], [y, y], color=ACC, lw=2.2, zorder=2, solid_capstyle="butt")
    ax.plot(r.p90 * 100, y, "^", ms=4.5, mfc="white", mec=DARK, mew=0.8, zorder=3)
    ax.plot(r.km * 100, y, "D", ms=3.6, mfc="white", mec=GREY, mew=0.9, zorder=3)
    ax.plot(r.age * 100, y, "o", ms=4.5, mfc="white", mec=DARK, mew=0.9, zorder=4)
    ax.plot(r.idx * 100, y, "o", ms=4.8, color=ACC, zorder=5)
    g = 100 * (r.idx / r.age - 1)
    ax.text(114, y, f"{g:+.1f}%", ha="center", va="center",
            fontsize=7.5, color=ACC, fontweight="bold")
ax.axvline(100, color=DARK, lw=0.8); ax.text(100, -0.9, "oracle", ha="center", fontsize=7.5, color=DARK)
ax.text(114, -0.9, "index vs\noldest-first", ha="center", va="bottom", fontsize=7, color=ACC, linespacing=0.95)
ax.set_yticks(ys); ax.set_yticklabels([f"$B$ = {b}" for b in R.B]); ax.invert_yaxis()
ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
for L, y in [("Line A", 1.5), ("Line B", 4 + 0.6 + 1.5)]:
    ax.text(-0.13, y, L, transform=ax.get_yaxis_transform(), rotation=90, va="center", ha="center", fontsize=8, fontweight="bold")
ax.set_xlim(0, 121); ax.set_xticks([0, 20, 40, 60, 80, 100]); ax.spines["bottom"].set_bounds(0, 100)
ax.set_xlabel("Hold hours recovered (% of oracle)", x=100 / 121 / 2)
h = [plt.Line2D([], [], marker="^", ls="", mfc="white", mec=DARK, label="static p90 rule"),
     plt.Line2D([], [], marker="D", ls="", mfc="white", mec=GREY, label="Kaplan–Meier"),
     plt.Line2D([], [], marker="o", ls="", mfc="white", mec=DARK, label="oldest-first"),
     plt.Line2D([], [], marker="o", ls="-", color=ACC, lw=2.2, label="index; bar = its gain over oldest-first")]
ax.legend(handles=h, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.17), handletextpad=0.3, columnspacing=1.2)
save(fig, "Figure3_policies_vs_oracle")


# ------------------------------------------------------------------ Figure 4: benchmark over rolling origins
SEL = [("LightGBM landmark (ext. features)", "LightGBM landmark"), ("LightGBM gain regression (ext.)", "LightGBM gain"),
       ("LightGBM LambdaRank (ext.)", "LightGBM LambdaRank"), ("MLP survival (ext.)", "MLP survival"),
       ("FT-Transformer survival (ext.)", "FT-Transformer survival"), ("LotSeq survival (ext. + history)", "LotSeq survival"),
       ("LotSeq decision-focused ranker", "LotSeq ranker"), ("Ensemble new", "Hybrid (deep + LightGBM)")]
nb = len(B); V = np.full((len(SEL), 2 * nb), np.nan); S = np.zeros_like(V, dtype=bool)
RR = pd.read_csv(f"{DATA}/fig4_benchmark_rolling_origins.csv")
for c0, L in [(0, "A"), (nb, "B")]:
    P = RR[(RR.line == L) & ~RR.policy.str.contains(r"\[mean score\]")]
    for i, (key, _) in enumerate(SEL):
        key = "Hybrid (deep + LightGBM)" if key == "Ensemble new" else key
        g = P[P.policy.str.startswith(key)]
        for j, b in enumerate(B):
            r = g[g.budget == b]
            if not len(r) or pd.isna(r.rel_vs_ens.iloc[0]): continue
            r = r.iloc[0]
            V[i, c0 + j] = 100 * r.rel_vs_ens; S[i, c0 + j] = r.p_ens_holm < 0.05
cmap = LinearSegmentedColormap.from_list("muted", ["#A0574A", "#E8D3CE", "#F7F7F7", "#CBD8E6", ACC])
fig, ax = plt.subplots(figsize=(W, 2.65))
im = ax.imshow(np.clip(V, -10, 10), cmap=cmap, norm=TwoSlopeNorm(vmin=-10, vcenter=0, vmax=10), aspect="auto")
for i in range(V.shape[0]):
    for j in range(V.shape[1]):
        v = V[i, j]
        if np.isnan(v): continue
        t = ("0.0" if abs(v) < 0.05 else f"{v:+.1f}".replace("-", "−")) + ("*" if S[i, j] else "")
        ax.text(j, i, t, ha="center", va="center", fontsize=7, color="white" if abs(v) > 7 else DARK)
ax.set_xticks(range(2 * nb)); ax.set_xticklabels([str(b) for b in B] * 2); ax.xaxis.tick_top()
ax.set_yticks(range(len(SEL))); ax.set_yticklabels([n for _, n in SEL]); ax.tick_params(length=0)
for s_ in ax.spines.values(): s_.set_visible(False)
ax.set_xticks(np.arange(-0.5, 2 * nb, 1), minor=True); ax.set_yticks(np.arange(-0.5, len(SEL), 1), minor=True)
ax.grid(which="minor", color="white", lw=0.8); ax.tick_params(which="minor", length=0)
ax.axvline(nb - 0.5, color="white", lw=4)
for y in [2.5, 6.5]: ax.axhline(y, color="white", lw=2.5)
ax.text((nb - 1) / 2, -1.3, "Line A,  $B$", ha="center", va="bottom", fontsize=8, fontweight="bold")
ax.text(nb + (nb - 1) / 2, -1.3, "Line B,  $B$", ha="center", va="bottom", fontsize=8, fontweight="bold")
for y, t in [(1.0, "GBM"), (4.5, "deep"), (7.0, "hybrid")]:
    ax.text(-0.36, y, t, transform=ax.get_yaxis_transform(), rotation=90, va="center", ha="center", fontsize=7, color=GREY, style="italic")
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.015, ticks=[-10, 0, 10])
cb.ax.set_yticklabels(["≤ −10", "0", "≥ +10"]); cb.ax.tick_params(labelsize=7, length=2, width=0.5); cb.outline.set_linewidth(0.4)
cb.set_label("gain over index (%)", fontsize=7.5)
save(fig, "Figure4_benchmark")


print("figures written to", OUT)
