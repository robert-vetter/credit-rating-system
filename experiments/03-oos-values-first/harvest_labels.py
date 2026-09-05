"""
Label harvest for Experiment 03: every post-boundary filing, every Moody's mention.

Part of experiments/03-oos-values-first (README §3). Free: EDGAR only. For each in-scope
current filer, downloads every 10-K, 10-Q and 8-K (and amendments) with
B < filingDate <= as_of, scans for rating symbols within 400 characters of "Moody", and
renders every hit into label-review.md with a heuristic pre-classification:
  statement   - reads like a statement of the current rating ("as of", "our ... rating",
                "rated", ratings table)
  threshold   - covenant / pricing-grid language ("downgraded below", "step up", "if", "margin")
  other       - anything else (historical references, generic risk-factor text)
The heuristic only orders the reading; every accepted label is validated by a human before it
enters candidates.json (Exp 01 lesson: Kohl's "Baa3" was a threshold clause).

Run: python3 experiments/03-oos-values-first/harvest_labels.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
import run_eval  # noqa: E402  (ensure_doc, to_text)

B = "2025-09-30"
AS_OF = "2026-08-29"
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "8-K/A"}
OUT = os.path.join(ROOT, "evaluation", "companies")
SYM = re.compile(r"\(?P?\)?\b(Aaa|Aa[1-3]|A[1-3]|Baa[1-3]|Ba[1-3]|B[1-3]|Caa[1-3])\b")
THRESH = re.compile(r"downgrad\w* (to )?below|step[- ]?up|pricing grid|applicable margin|"
                    r"if (our|the company'?s?) (long-term |senior |issuer )?(debt |credit )?ratings?|"
                    r"in the event|would (increase|result)|lower than|at least", re.I)
STATE = re.compile(r"as of [A-Z][a-z]+ \d|our (long-term |senior unsecured |issuer |corporate )?(debt |credit |family )?"
                   r"ratings? (is|are|was|were|of|from)|rated|credit ratings? (were|are|is) as follows|"
                   r"rating agency|long-term debt|currently ha(ve|s)", re.I)


def classify(w):
    if THRESH.search(w) and not re.search(r"currently|as of|were as follows", w, re.I):
        return "threshold"
    if STATE.search(w):
        return "statement"
    return "other"


def main():
    res = {}
    n_docs = 0
    for slug in sorted(os.listdir(OUT)):
        cj = os.path.join(OUT, slug, "company.json")
        if not os.path.exists(cj):
            continue
        c = json.load(open(cj))
        if c.get("scope") != "in" or c.get("filing_status") != "aktueller Filer":
            continue
        manifest = json.load(open(os.path.join(OUT, slug, "filings", "manifest.json")))["filings"]
        window = sorted([f for f in manifest if f["form"] in FORMS and B < f["filingDate"] <= AS_OF],
                        key=lambda f: f["filingDate"], reverse=True)
        obs = json.load(open(os.path.join(OUT, slug, "observations.json")))["observations"]
        hits = []
        for f in window:
            try:
                path, _ = run_eval.ensure_doc(slug, c["cik"], f)
                text = run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore"))
            except Exception as exc:
                hits.append({"form": f["form"], "filed": f["filingDate"], "error": str(exc)[:80]})
                continue
            n_docs += 1
            for m in re.finditer(r"Moody", text, re.I):
                w = text[max(0, m.start() - 400):m.end() + 400]
                syms = sorted(set(SYM.findall(w)))
                if not syms:
                    continue
                hits.append({"form": f["form"], "filed": f["filingDate"],
                             "accession": f["accessionNumber"], "primaryDocument": f["primaryDocument"],
                             "symbols": syms, "class": classify(w),
                             "snippet": re.sub(r"\s+", " ", w[150:650]).strip()})
        # dedupe identical snippets within a filing
        seen, uniq = set(), []
        for h in hits:
            k = (h.get("filed"), h.get("snippet", "")[:120])
            if k not in seen:
                seen.add(k); uniq.append(h)
        res[slug] = {"group": c["group"], "cik": c["cik"],
                     "persistence_file_end": obs[-1]["label"] if obs else None,
                     "n_window_filings": len(window), "hits": uniq}
        st = sum(1 for h in uniq if h.get("class") == "statement")
        print(f"  {slug:<28} {len(window):>3} Filings  {len(uniq):>3} Treffer  ({st} statement)", flush=True)
    json.dump(res, open(os.path.join(HERE, "harvest.json"), "w"), indent=1, ensure_ascii=False)

    with open(os.path.join(HERE, "label-review.md"), "w") as f:
        f.write(f"# Label review — Experiment 03 (harvest of all filings with {B} < filed <= {AS_OF})\n\n")
        f.write(f"*{n_docs} documents scanned across {len(res)} companies. Every hit listed; heuristic class is a "
                "reading aid only. Accept = a statement of the CURRENT Moody's rating (not a covenant "
                "threshold, pricing grid or historical reference).*\n\n")
        for slug, v in res.items():
            f.write(f"## {v['group']} (`{slug}`) — file-end rating {v['persistence_file_end']}, "
                    f"{v['n_window_filings']} filings in window\n\n")
            if not v["hits"]:
                f.write("_no Moody's rating mentions_\n\n"); continue
            for h in v["hits"]:
                if "error" in h:
                    f.write(f"- {h['form']} {h['filed']}: download error {h['error']}\n"); continue
                url = (f"https://www.sec.gov/Archives/edgar/data/{v['cik']}/"
                       f"{h['accession'].replace('-', '')}/{h['primaryDocument']}")
                f.write(f"- **[{h['form']} {h['filed']}]({url})** `{h['class']}` symbols {h['symbols']}\n"
                        f"  > …{h['snippet']}…\n")
            f.write("\n")
    print(f"\n{n_docs} Dokumente gescannt; label-review.md geschrieben")


if __name__ == "__main__":
    main()
