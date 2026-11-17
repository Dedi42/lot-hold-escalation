"""Run everything the review needs from your data, in one go, LOCALLY.

    cd lot-hold-escalation
    python run_warmup_all.py --raw <raw_folder> --lineA config\\local_lineA.yaml --lineB config\\local_lineB.yaml

Steps
  1. inventory_raw.py on the raw folder      -> warmup_all\\raw_inventory\\
  2. scripts\\run_warmup.py on both lines   -> warmup_all\\results_warmup\\
  3. scripts\\run_raw_extras.py               -> warmup_all\\results_raw_extras\\ (hold share of cycle time, hold comments)
  4. warmup_all\\EXPORT_results_warmup.zip    : aggregated CSV + summary of step 2 (no dates, no codes) - shareable
     warmup_all\\CHECK_THEN_EXPORT_structure.csv: column names of the raw files - look at it, share only if harmless
     Everything named LOCAL_ONLY or inside local_only\\ stays on this computer.
"""
from __future__ import annotations
import argparse, os, shutil, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    print("\n>>> " + " ".join(cmd), flush=True)
    t = time.time()
    r = subprocess.run(cmd)
    print(f"    finished in {(time.time() - t) / 60:.1f} min (exit code {r.returncode})", flush=True)
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", required=True, help="folder with the raw company files")
    ap.add_argument("--lineA", required=True); ap.add_argument("--lineB", required=True)
    ap.add_argument("--out", default="warmup_all")
    ap.add_argument("--skip-inventory", action="store_true"); ap.add_argument("--skip-warmup", action="store_true")
    ap.add_argument("--skip-raw-extras", dest="skip_raw_extras", action="store_true")
    ap.add_argument("--quick", action="store_true", help="fast test run of step 2")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    inv_py = next((p for p in (os.path.join(HERE, "inventory_raw.py"), os.path.join(HERE, "tools", "inventory_raw.py"))
                   if os.path.exists(p)), None)
    rev_py = os.path.join(HERE, "scripts", "run_warmup.py")
    ok = True
    if not a.skip_inventory:
        if inv_py is None:
            print("inventory_raw.py not found next to this file or in tools\\ - step 1 skipped"); ok = False
        else:
            ok &= run([sys.executable, inv_py, a.raw, "--out", os.path.join(a.out, "raw_inventory")]) == 0
    if not a.skip_warmup:
        if not os.path.exists(rev_py):
            print("scripts\\run_warmup.py not found - step 2 skipped"); ok = False
        else:
            cmd = [sys.executable, rev_py, "--line", f"A={a.lineA}", "--line", f"B={a.lineB}",
                   "--out", os.path.join(a.out, "results_warmup")]
            ne = os.path.join(a.out, "results_match_txn", "local_only", "LOCAL_ONLY_nonescalable_holds.csv")
            if os.path.exists(ne):
                cmd += ["--nonescalable", ne]
                print("using " + ne)
            ok &= run(cmd + (["--quick"] if a.quick else [])) == 0
    rx_py = os.path.join(HERE, "scripts", "run_raw_extras.py")
    if not a.skip_raw_extras and os.path.exists(rx_py):
        ok &= run([sys.executable, rx_py, "--line", f"A={a.lineA}", "--line", f"B={a.lineB}",
                   "--out", os.path.join(a.out, "results_raw_extras")]) == 0
    # package what may leave this computer
    res = os.path.join(a.out, "results_warmup")
    if os.path.isdir(res) or os.path.isdir(os.path.join(a.out, "results_raw_extras")):
        os.makedirs(res, exist_ok=True)
        zp = os.path.join(a.out, "EXPORT_results_warmup.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(os.listdir(res)):
                if f.endswith((".csv", ".md")) and "LOCAL_ONLY" not in f:
                    z.write(os.path.join(res, f), f)
            rx = os.path.join(a.out, "results_raw_extras")
            for f in ("raw_extras.csv", "raw_extras.md"):
                if os.path.exists(os.path.join(rx, f)):
                    z.write(os.path.join(rx, f), f)
        print(f"\nSHARE:  {zp}")
    st = os.path.join(a.out, "raw_inventory", "SHAREABLE_structure.csv")
    if os.path.exists(st):
        shutil.copy(st, os.path.join(a.out, "CHECK_THEN_EXPORT_structure.csv"))
        print(f"CHECK, then share if harmless:  {os.path.join(a.out, 'CHECK_THEN_EXPORT_structure.csv')}")
    print(f"READ YOURSELF, do not share:  {os.path.join(a.out, 'raw_inventory', 'LOCAL_ONLY_keyword_hits.txt')}")
    print(f"KEEP LOCAL, do not share:     {os.path.join(res, 'local_only')}")
    print("\nall steps finished" if ok else "\nsome steps failed - see messages above")


if __name__ == "__main__":
    main()
