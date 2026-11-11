"""Look up the DOI and the bibliographic data of every reference of the manuscript in Crossref.

    python tools/check_references.py IJPR_hold_11022026.docx --out refs_check.csv [--mailto YOUR_EMAIL]

Reads the reference list of the .docx (the paragraphs after the heading "References" up to the first table
caption), queries the public Crossref API once per reference, and writes

  refs_check.csv   one row per reference: the DOI found, Crossref's title, journal, year, volume, issue and
                   pages, a title similarity, and a status:
                     OK         title and year match; volume/issue/pages agree with the reference (or are absent)
                     CHECK      a likely match, but year, volume, issue or pages differ: compare by hand
                     NOT FOUND  no convincing match (books, reports and very old papers often have no DOI)
  refs_with_doi.txt the reference list with " https://doi.org/<doi>." appended where the status is OK

Needs internet access; uses only the Python standard library (plus python-docx to read the .docx).
"""
from __future__ import annotations
import argparse, csv, difflib, json, re, sys, time, unicodedata, urllib.parse, urllib.request

API = "https://api.crossref.org/works"


def read_refs(path: str) -> list[str]:
    import docx
    paras = [p.text.strip() for p in docx.Document(path).paragraphs]
    try:
        start = next(i for i, t in enumerate(paras) if t.lower() in ("references", "reference"))
    except StopIteration:
        sys.exit("no paragraph 'References' found")
    out = []
    for t in paras[start + 1:]:
        if re.match(r"^(Table|Figure)\s+\w+[.:]", t) or t.lower().startswith(("appendix", "figure captions")):
            break
        if len(t) > 30 and re.search(r"\b(19|20)\d{2}[a-z]?\.", t):
            out.append(t)
    return out


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def title_of(ref: str) -> str:
    m = re.search(r"[\'‘’\"“](.+?)[\'’\"”]\s*(?:In |[A-Z])", ref)
    if m:
        return m.group(1).rstrip(".?")
    m = re.search(r"\b(?:19|20)\d{2}[a-z]?\.\s*(.+?)\.", ref)        # books: title follows the year
    return m.group(1) if m else ref[:120]


def year_of(ref: str):
    m = re.search(r"\b((?:19|20)\d{2})[a-z]?\.", ref)
    return int(m.group(1)) if m else None


def numbers_of(ref: str):
    """volume (issue): pages as written in the reference, if present."""
    m = re.search(r"\b(\d+)\s*(?:\(([\d–\-]+)\))?\s*:\s*([\w]+)(?:[–\-](\w+))?", ref.split("'")[-1])
    if not m:
        return None, None, None
    return m.group(1), m.group(2), m.group(3)


def query(ref: str, mailto: str | None):
    params = {"query.bibliographic": ref[:400], "rows": "5",
              "select": "DOI,title,container-title,issued,volume,issue,page,article-number,type"}
    if mailto:
        params["mailto"] = mailto
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "hold-escalation-refcheck/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)["message"]["items"]
        except Exception as e:                                   # network hiccup or rate limit: back off
            time.sleep(2 * (attempt + 1))
            err = e
    raise RuntimeError(f"Crossref query failed: {err}")


def best(ref: str, items):
    t, y = title_of(ref), year_of(ref)
    scored = []
    for it in items:
        ct = (it.get("title") or [""])[0]
        sim = difflib.SequenceMatcher(None, norm(t), norm(ct)).ratio()
        iy = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        scored.append((sim + (0.05 if (y and iy and abs(iy - y) <= 1) else 0), sim, iy, it))
    scored.sort(key=lambda z: -z[0])
    return scored[0] if scored else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx"); ap.add_argument("--out", default="refs_check.csv")
    ap.add_argument("--mailto", default=None, help="your e-mail for Crossref's polite pool (optional)")
    a = ap.parse_args()
    refs = read_refs(a.docx)
    print(f"{len(refs)} references found")
    rows, with_doi = [], []
    for n, ref in enumerate(refs, 1):
        has = re.search(r"doi\.org/(\S+?)\.?$", ref)
        try:
            b = best(ref, query(ref, a.mailto))
        except RuntimeError as e:
            b = None; print(f"{n:3d} query failed: {e}")
        y = year_of(ref); vol, iss, pg = numbers_of(ref)
        if b is None or b[1] < 0.80:
            status, it, sim, iy = "NOT FOUND", {}, (b[1] if b else 0.0), None
        else:
            _, sim, iy, it = b
            cr_pg = it.get("page") or it.get("article-number") or ""
            diff = []
            if y and iy and iy != y: diff.append(f"year {iy}")
            if vol and it.get("volume") and str(it["volume"]) != vol: diff.append(f"volume {it['volume']}")
            if iss and it.get("issue") and str(it["issue"]).replace("-", "–") != iss.replace("-", "–"): diff.append(f"issue {it['issue']}")
            if pg and cr_pg and not str(cr_pg).replace("-", "–").startswith(pg): diff.append(f"pages {cr_pg}")
            status = "OK" if (sim >= 0.90 and not diff) else "CHECK: " + ", ".join(diff or ["title similarity"])
        doi = it.get("DOI", "")
        rows.append(dict(n=n, reference=ref[:90], status=status, doi=doi, doi_in_reference=has.group(1) if has else "",
                         title_similarity=round(sim, 3), crossref_title=(it.get("title") or [""])[0],
                         journal=(it.get("container-title") or [""])[0], year=iy or "", volume=it.get("volume", ""),
                         issue=it.get("issue", ""), pages=it.get("page") or it.get("article-number") or ""))
        if status == "OK" and doi and not has:
            with_doi.append(ref.rstrip() + f" https://doi.org/{doi}.")
        else:
            with_doi.append(ref)
        print(f"{n:3d} {status:<10.10} {doi:<40} {ref[:60]}")
        time.sleep(0.2)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open("refs_with_doi.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(with_doi) + "\n")
    k = sum(r["status"] == "OK" for r in rows)
    print(f"\n{k} OK, {sum(r['status'].startswith('CHECK') for r in rows)} to check, "
          f"{sum(r['status'] == 'NOT FOUND' for r in rows)} not found -> {a.out}, refs_with_doi.txt")


if __name__ == "__main__":
    main()
