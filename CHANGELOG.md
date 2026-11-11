# Changelog

## 2.3.0 — first public release, the version cited in the manuscript

* `src/holdesc/`: data loading and anonymisation, onset and landmark remaining-time models, ensemble index,
  replay of budgeted escalation policies, statistics (block bootstrap, sign-flip test, Holm, TOST, pooling),
  deep-learning benchmark models.
* `scripts/run_hypotheses.py`: hypotheses H1–H10 on the test period (Tables 2–6).
* `scripts/run_benchmark.py`, `scripts/run_bench_rolling.py`: benchmark of nine learners, tuned once and refitted on
  rolling origins (Figure 4, Supplementary S1).
* `scripts/run_diagnostics.py`, `scripts/run_robustness.py`, `scripts/run_warmup.py`, `scripts/run_rolling.py`:
  replay diagnostics, robustness checks, warm-up replay, and hypotheses H6–H8 on rolling origins (Tables 4–6,
  Supplementary S2–S8).
* `scripts/run_match_txn.py`, `scripts/run_raw_extras.py`, `tools/inventory_raw.py`: hold share of cycle time and
  comment categories from the raw transactions.
* `run_warmup_all.py`, `run_rolling_all.py`: one-command runs of the steps above that write aggregated tables only.
* `scripts/make_submission_figures.py`: Figures 2–4.
* `paper_results/`: aggregated results behind every table and figure (no dates, codes, or identifiers).
* `scripts/make_synthetic.py`, `config/synthetic*.yaml`, `tests/`: synthetic data with the same schema and tests.
