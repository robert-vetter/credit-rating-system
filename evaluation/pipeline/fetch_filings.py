"""
Fetches each company's SEC filing history into its evaluation folder.

Written by Claude (Opus 5), directed by Robert Vetter. See evaluation/README.md.

For every folder under evaluation/companies/ this writes:

  filings/manifest.json   the company's complete filing metadata from the EDGAR submissions
                          API (all pages, not just the recent window), filtered to the forms
                          the evaluation cares about: annual and quarterly reports, their
                          amendments, current reports (8-K), and foreign equivalents. This is
                          the basis for "documents filed before t" in the observation builder.
  filings/<date>_<form>_<accession>.htm
                          the primary document of the most recent annual report (10-K/20-F/
                          40-F), downloaded for current filers. Older documents are fetched
                          on demand later; the manifest carries every URL needed.

Throttled well under the SEC's 10 requests/second. Re-runnable; existing downloads are kept.

Run: python3 evaluation/pipeline/fetch_filings.py
"""
import json
import os
import time
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "evaluation", "companies")
UA = {"User-Agent": "Robert Vetter robert@certus-ai.com"}
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "8-K/A", "20-F", "20-F/A", "40-F", "40-F/A", "6-K"}
ANNUAL = ("10-K", "20-F", "40-F")


def get(url):
    time.sleep(0.25)
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def rows(block):
    keys = ["form", "filingDate", "reportDate", "accessionNumber", "primaryDocument",
            "primaryDocDescription", "items", "size"]
    n = len(block.get("form", []))
    for i in range(n):
        r = {k: (block.get(k) or [None] * n)[i] for k in keys}
        if r["form"] in FORMS:
            yield r


def manifest(cik):
    j = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    out = list(rows(j["filings"]["recent"]))
    for f in j["filings"].get("files", []):
        older = json.loads(get(f"https://data.sec.gov/submissions/{f['name']}"))
        out.extend(rows(older))
    out.sort(key=lambda r: r["filingDate"], reverse=True)
    return j.get("name", ""), out


def main():
    done = errs = 0
    for slug in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, slug)
        cj = os.path.join(d, "company.json")
        if not os.path.exists(cj):
            continue
        c = json.load(open(cj))
        fdir = os.path.join(d, "filings")
        os.makedirs(fdir, exist_ok=True)
        try:
            edgar_name, m = manifest(c["cik"])
            json.dump({"cik": c["cik"], "edgar_name": edgar_name,
                       "fetched": "2026-08-29", "filings": m},
                      open(os.path.join(fdir, "manifest.json"), "w"), indent=0)
            note = ""
            if c.get("filing_status") == "aktueller Filer":
                latest = next((r for r in m if r["form"] in ANNUAL), None)
                if latest:
                    acc = latest["accessionNumber"].replace("-", "")
                    fn = f"{latest['filingDate']}_{latest['form'].replace('/', '')}_{acc}.htm"
                    path = os.path.join(fdir, fn)
                    if not os.path.exists(path):
                        url = (f"https://www.sec.gov/Archives/edgar/data/{c['cik']}/"
                               f"{acc}/{latest['primaryDocument']}")
                        open(path, "wb").write(get(url))
                    note = f" + {latest['form']} {latest['filingDate']} ({os.path.getsize(path)//1024} KB)"
            print(f"  {slug:<28} {len(m):>4} Filings im Manifest{note}", flush=True)
            done += 1
        except Exception as exc:
            print(f"  {slug:<28} FEHLER {str(exc)[:60]}", flush=True)
            errs += 1
    print(f"{done} Ordner, {errs} Fehler")


if __name__ == "__main__":
    main()
