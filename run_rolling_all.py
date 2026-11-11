"""Rolling-origin hypotheses (run_rolling.py) and the benchmark over rolling origins, then one zip of tables.

Put this file in the repository root (next to scripts/ and src/), copy the three scripts of this package into
scripts/, and run:

    cd <repository folder>
    python run_rolling_all.py --lineA config\\local_lineA.yaml --lineB config\\local_lineB.yaml

Steps
  0. checks: PyTorch with GPU; the tuning tables of the first benchmark (results_bench_A/B/tables/bench_tuning.csv);
  1. smoke test (a few minutes): run_rolling.py --quick on Line A and one quick rolling benchmark window, so that an
     error shows up before the long runs; the smoke-test folders are deleted afterwards;
  2. run_rolling.py on both lines (H6-H8 on rolling origins, alpha(e), Table 4 within landmarks) -> results_rolling;
  3. run_benchmark.py --origin 1..4 --fixed-hp ... on both lines -> results_bench_A_ro1 ... results_bench_B_ro4;
  4. run_bench_rolling.py -> results_bench_rolling;
  5. EXPORT_rolling.zip next to the repository folder with ONLY aggregated tables (no cache, no logs, no local_only).

Rerun the same command after an interruption: finished steps are skipped (--redo to force them).
"""
from __future__ import annotations
import argparse, os, shutil, subprocess, sys, time, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(ROOT, "scripts")


def say(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def run(cmd, log_path):
    say("RUN " + " ".join(os.path.relpath(c, ROOT) if os.path.isabs(c) else c for c in cmd))
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    with open(log_path, "w", encoding="utf-8") as lg:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace", env=env)
        for line in p.stdout:
            if "Deprecation" in line or "_validate_eval_set" in line or "] epoch" in line:
                lg.write(line); continue
            print(line, end="", flush=True); lg.write(line)
        p.wait()
    if p.returncode != 0:
        say(f"!! step failed (code {p.returncode}); see the last 40 lines of {os.path.relpath(log_path, ROOT)}")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lineA", required=True); ap.add_argument("--lineB", required=True)
    ap.add_argument("--origins", type=int, default=4)
    ap.add_argument("--redo", action="store_true"); ap.add_argument("--skip-smoke", dest="skip_smoke", action="store_true")
    ap.add_argument("--zip", default=os.path.join(os.path.dirname(ROOT), "EXPORT_rolling.zip"))
    a = ap.parse_args()
    py = sys.executable
    os.makedirs(os.path.join(ROOT, "logs_r123"), exist_ok=True)
    L = lambda n: os.path.join(ROOT, "logs_r123", n)
    for f in ("run_rolling.py", "run_bench_rolling.py", "run_benchmark.py", "run_warmup.py"):
        if not os.path.exists(os.path.join(SC, f)):
            say(f"!! scripts/{f} not found"); sys.exit(1)
    if "--fixed-hp" not in open(os.path.join(SC, "run_benchmark.py"), encoding="utf-8").read():
        say("!! scripts/run_benchmark.py does not support --origin; use the version in this repository"); sys.exit(1)
    try:
        import torch
        say(f"PyTorch {torch.__version__}; GPU: {torch.cuda.is_available()}")
        if not torch.cuda.is_available():
            say("!! no GPU: the deep models will run on the CPU (slow)")
    except ImportError:
        say("!! PyTorch not installed: pip install torch --index-url https://download.pytorch.org/whl/cu121"); sys.exit(1)
    lines = {"A": a.lineA, "B": a.lineB}
    tun = {k: os.path.join(ROOT, f"results_bench_{k}", "tables", "bench_tuning.csv") for k in lines}
    for k, t in tun.items():
        if not os.path.exists(t):
            say(f"!! {os.path.relpath(t, ROOT)} not found (tuning table of the first benchmark run)"); sys.exit(1)

    # 1 smoke test
    if not a.skip_smoke and not os.path.exists(os.path.join(ROOT, "results_rolling", "rolling.md")):
        say("smoke test (a few minutes)")
        run([py, os.path.join(SC, "run_rolling.py"), "--line", f"A={lines['A']}", "--out", "smoke_rolling", "--quick"],
            L("smoke_rolling.txt"))
        run([py, os.path.join(SC, "run_benchmark.py"), "--config", lines["A"], "--out", "smoke_bench", "--origin", "1",
             "--fixed-hp", tun["A"], "--skip-extras", "--quick"], L("smoke_bench.txt"))
        for d in ("smoke_rolling", "smoke_bench"):
            shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
        say("smoke test passed")

    # 2 rolling-origin hypotheses
    if a.redo or not os.path.exists(os.path.join(ROOT, "results_rolling", "rolling.md")):
        run([py, os.path.join(SC, "run_rolling.py"), "--line", f"A={lines['A']}", "--line", f"B={lines['B']}",
             "--out", "results_rolling"], L("rolling.txt"))
    else:
        say("results_rolling exists, skipped")

    # 3 rolling benchmark
    dirs = {k: [] for k in lines}
    for k, cfg in lines.items():
        for o in range(1, a.origins + 1):
            out = f"results_bench_{k}_ro{o}"
            dirs[k].append(out)
            if not a.redo and os.path.exists(os.path.join(ROOT, out, "tables", "bench_daily.csv")):
                say(f"{out} exists, skipped"); continue
            run([py, os.path.join(SC, "run_benchmark.py"), "--config", cfg, "--out", out, "--origin", str(o),
                 "--fixed-hp", tun[k], "--skip-extras"], L(f"bench_{k}_ro{o}.txt"))

    # 4 combine
    run([py, os.path.join(SC, "run_bench_rolling.py")] + sum([["--run", f"{k}=" + ",".join(v)] for k, v in dirs.items()], [])
        + ["--out", "results_bench_rolling"], L("bench_rolling.txt"))

    # 5 zip (aggregated tables only)
    n = 0
    with zipfile.ZipFile(a.zip, "w", zipfile.ZIP_DEFLATED) as z:
        for d in ["results_rolling", "results_bench_rolling"] + [f"{x}/tables" for v in dirs.values() for x in v]:
            p = os.path.join(ROOT, d)
            for f in sorted(os.listdir(p)):
                if f.endswith((".csv", ".md")) and "local_only" not in f.lower():
                    z.write(os.path.join(p, f), f"{d}/{f}".replace("\\", "/")); n += 1
    say(f"all steps finished; shareable tables in {a.zip} ({n} files: tables only)")


if __name__ == "__main__":
    main()
