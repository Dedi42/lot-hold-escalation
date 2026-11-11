"""Inventory of a folder of raw company files, run LOCALLY. Nothing is uploaded.

    python inventory_raw.py <raw_folder> --out raw_inventory

Writes two reports into --out:

  1. SHAREABLE_structure.csv   file name, type, sheet, number of rows, and COLUMN NAMES only (no values).
                               Read it first; if the file or column names reveal nothing confidential,
                               you may share it so that the analysis scripts can be adapted.
  2. LOCAL_ONLY_keyword_hits.txt  sentences from slides, documents and sheets that contain keywords about
                               escalation, hold limits, process type and hold reasons. This contains company
                               text: read it yourself and do NOT share it.

Reads csv, txt, xlsx/xlsm, xls (if xlrd is installed), pptx, docx, and the same types inside zip files.
Old binary .ppt and .doc files are listed but not read (save them as .pptx/.docx to include them).
"""
from __future__ import annotations
import argparse, csv, io, os, re, sys, zipfile

KEYWORDS = [
    # escalation practice (A2-A5)
    "escalat", "esc ", "overdue", "aging", "ageing", "long hold", "hold time", "hold limit", "time limit", "over 24",
    "> 24", ">24", "24h", "24 h", "48h", "48 h", "72h", "spec limit", "p90", "90th", "percentile", "kpi", "ocap",
    "daily meeting", "morning meeting", "supervisor", "owner", "sla", "lead time", "target hours",
    # process type (A1)
    "bump", "bumping", "rdl", "redistribution", "wlp", "wafer level", "fan-out", "fan-in", "ubm", "solder",
    "copper pillar", "cu pillar", "plating", "sputter",
    # hold reasons that internal escalation cannot speed up (A6, A7)
    "customer", "cust ", "mrb", "ecn", "engineering change", "material", "waiting", "disposition", "scrap",
    "rework", "release",
    # lot start time (cycle time)
    "start time", "track in", "track-in", "trackin", "lot start", "wafer start", "move in", "cycle time",
    # Chinese
    "升級", "逾時", "超時", "客戶", "待料", "工程變更", "凸塊", "重工", "報廢", "放行",
]
TABULAR = {".csv", ".txt", ".xlsx", ".xlsm", ".xls"}
TEXTDOC = {".pptx", ".docx"}


def xml_text(xml: bytes) -> list[str]:
    t = xml.decode("utf8", "ignore")
    paras = re.findall(r"<a:p>.*?</a:p>|<w:p[ >].*?</w:p>", t, re.S)
    out = []
    for p in paras:
        s = "".join(re.findall(r"<(?:a|w):t(?: [^>]*)?>([^<]*)</(?:a|w):t>", p))
        if s.strip():
            out.append(s.strip())
    return out


def office_text(data: bytes, ext: str) -> list[tuple[str, str]]:
    z = zipfile.ZipFile(io.BytesIO(data))
    out = []
    if ext == ".pptx":
        names = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
                       key=lambda n: int(re.findall(r"\d+", n)[-1]))
        for n in names:
            num = re.findall(r"\d+", n)[-1]
            out += [("slide " + num, s) for s in xml_text(z.read(n))]
    else:
        out += [("text", s) for s in xml_text(z.read("word/document.xml"))]
    return out


def tables(data: bytes, ext: str):
    """Yield (sheet, header list, n_rows, sample text cells for keyword search)."""
    try:
        import pandas as pd
    except ImportError:
        pd = None
    if ext in (".csv", ".txt"):
        for enc in ("utf-8-sig", "big5", "cp950", "latin-1"):
            try:
                txt = data.decode(enc); break
            except UnicodeDecodeError:
                continue
        lines = txt.splitlines()
        if not lines:
            return
        try:
            dialect = csv.Sniffer().sniff(lines[0][:2000], delimiters=",;\t|")
            delim = dialect.delimiter
        except csv.Error:
            delim = ","
        header = next(csv.reader([lines[0]], delimiter=delim))
        cells = []
        for row in csv.reader(lines[1:2001], delimiter=delim):
            cells += [c for c in row if c and not re.fullmatch(r"[\d\s.:/\-+]+", c)]
        yield "-", header, len(lines) - 1, cells
        return
    if pd is None:
        yield "-", ["(pandas not installed)"], -1, []
        return
    try:
        xl = pd.ExcelFile(io.BytesIO(data))
    except Exception as e:                                    # noqa: BLE001
        yield "-", [f"(could not read: {type(e).__name__})"], -1, []
        return
    for sh in xl.sheet_names:
        try:
            df = xl.parse(sh, header=None, dtype=str)          # whole sheet, every cell as text
        except Exception as e:                                # noqa: BLE001
            yield sh, [f"(could not read: {type(e).__name__}: {str(e)[:80]})"], -1, []
            continue
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            yield sh, ["(empty sheet)"], 0, []
            continue
        header = [str(c) for c in df.iloc[0].fillna("")]
        n = len(df) - 1
        body = df.iloc[1:]
        cells = [v for v in body.values.ravel() if isinstance(v, str) and v.strip()
                 and not re.fullmatch(r"[\d\s.:/\-+]+", v)]
        yield sh, header, n, cells
        continue


def hits(text: str) -> list[str]:
    low = text.lower()
    return [k for k in KEYWORDS if k in low]


def walk(root):
    for d, _, files in os.walk(root):
        for f in files:
            p = os.path.join(d, f)
            ext = os.path.splitext(f)[1].lower()
            if ext == ".zip":
                try:
                    z = zipfile.ZipFile(p)
                except zipfile.BadZipFile:
                    yield os.path.relpath(p, root), ext, None
                    continue
                for n in z.namelist():
                    e2 = os.path.splitext(n)[1].lower()
                    if n.endswith("/"):
                        continue
                    if e2 in TABULAR | TEXTDOC:
                        yield os.path.relpath(p, root) + "::" + n, e2, z.read(n)
                    else:
                        yield os.path.relpath(p, root) + "::" + n, e2, None
            elif ext in TABULAR | TEXTDOC:
                with open(p, "rb") as fh:
                    yield os.path.relpath(p, root), ext, fh.read()
            else:
                yield os.path.relpath(p, root), ext, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root"); ap.add_argument("--out", default="raw_inventory")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    struct = open(os.path.join(a.out, "SHAREABLE_structure.csv"), "w", newline="", encoding="utf-8-sig")
    sw = csv.writer(struct); sw.writerow(["file", "type", "sheet", "rows", "columns"])
    kw = open(os.path.join(a.out, "LOCAL_ONLY_keyword_hits.txt"), "w", encoding="utf-8")
    kw.write("LOCAL ONLY - contains company text. Do not share.\n\n")
    n_files = 0
    for name, ext, data in walk(a.root):
        n_files += 1
        if data is None:
            sw.writerow([name, ext, "", "", "(not read)"])
            continue
        try:
            if ext in TEXTDOC:
                paras = office_text(data, ext)
                sw.writerow([name, ext, "", len(paras), "(text document)"])
                for where, s in paras:
                    h = hits(s)
                    if h:
                        kw.write(f"[{name} | {where}] ({', '.join(h)})\n    {s[:400]}\n")
            else:
                for sh, header, n, cells in tables(data, ext):
                    sw.writerow([name, ext, sh, n, " | ".join(header)])
                    for c in header:
                        h = hits(c)
                        if h:
                            kw.write(f"[{name} | {sh} | column] ({', '.join(h)})  {c}\n")
                    seen = set()
                    for c in cells:
                        h = hits(c)
                        if h and c not in seen and len(seen) < 200:
                            seen.add(c)
                            kw.write(f"[{name} | {sh} | cell] ({', '.join(h)})  {c[:300]}\n")
        except Exception as e:                                # noqa: BLE001
            sw.writerow([name, ext, "", "", f"(error: {type(e).__name__})"])
    struct.close(); kw.close()
    print(f"{n_files} files scanned.")
    print(f"  {a.out}/SHAREABLE_structure.csv      <- column names only; check before sharing")
    print(f"  {a.out}/LOCAL_ONLY_keyword_hits.txt  <- company text; read yourself, do not share")


if __name__ == "__main__":
    sys.exit(main())
