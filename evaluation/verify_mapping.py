"""
Independent verification of the Moody's-to-SEC mapping via self-disclosure.

Written by Claude (Opus 5), directed by Robert Vetter.

The idea: companies disclose their own credit ratings in their filings (found originally as a
leakage channel, docs/leakage-audit.md). That turns into a mapping check: if the 10-K of the
SEC filer we mapped names the same Moody's rating that the mapped Moody's entity's 17g-7 file
carries at the filing date, then the company itself confirms the pair. This is independent of
name matching: it compares rating values across the join, not names.

For each company folder with a downloaded annual report, this script:
  1. computes the set of ratings in effect at the filing date from ratings.json
     (entity-level LT ratings and instrument-level senior unsecured, including one notch
     of history in case the filing text lags a recent action),
  2. extracts every Moody's rating symbol within 400 characters of a "Moody" mention,
  3. compares. Verdicts: MATCH (a disclosed symbol equals an in-effect rating),
     DISAGREE (symbols near Moody mentions, none in effect at any point of the entity's
     history window - the red flag worth eyeballing), MENTION_ONLY (Moody's mentioned,
     no symbol nearby), NO_MENTION (nothing; common for foreign filers and unrated shelf
     documents). Caveat, stated in the report: credit agreements quote rating GRIDS
     (pricing levels for many hypothetical ratings), so stray symbols can appear; grids
     produce extra symbols, which can never turn a MATCH into a DISAGREE.

Writes verification.json into each folder and a summary to evaluation/mapping-verification.md.

Run after fetch_filings.py: python3 evaluation/verify_mapping.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evaluation", "companies")
LT = ("LT CORPORATE FAMILY RATINGS", "LT ISSUER RATING", "ISSUER RATING", "ISSUER LT RATING")
SYM = re.compile(r"\(?P?\)?\b(Aaa|Aa[1-3]|A[1-3]|Baa[1-3]|Ba[1-3]|B[1-3]|Caa[1-3])\b")
MOODY = re.compile(r"Moody", re.I)


def text_of(path):
    raw = open(path, "rb").read().decode("utf-8", "ignore")
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


def in_effect(ratings, date):
    """Ratings in effect at `date`, plus the prior notch per line (filings lag actions)."""
    ok = set()
    for e in ratings["entities"]:
        recs = sorted([r for r in (e.get("obligor_records") or [])
                       if r.get("RT", "").upper() in LT and (r.get("RAD") or "") <= date],
                      key=lambda r: r["RAD"])
        ok.update(r["R"] for r in recs[-2:] if r.get("R") and r["R"] != "WR")
        for ins in (e.get("instruments") or []):
            if any(r.get("RT") == "Senior Unsecured" for r in ins["records"]):
                recs = sorted([r for r in ins["records"] if (r.get("RAD") or "") <= date],
                              key=lambda r: r["RAD"])
                ok.update(r["R"] for r in recs[-2:] if r.get("R") and r["R"] != "WR")
    return ok


def main():
    results = []
    for slug in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, slug)
        cj = os.path.join(d, "company.json")
        fdir = os.path.join(d, "filings")
        if not os.path.exists(cj) or not os.path.exists(fdir):
            continue
        docs = sorted(f for f in os.listdir(fdir) if f.endswith(".htm"))
        if not docs:
            continue
        doc = docs[-1]
        fdate = doc[:10]
        c = json.load(open(cj))
        ratings = json.load(open(os.path.join(d, "ratings.json")))
        eff = in_effect(ratings, fdate)
        t = text_of(os.path.join(fdir, doc))
        found = set()
        snippets = []
        for m in MOODY.finditer(t):
            w = t[max(0, m.start() - 400):m.end() + 400]
            syms = set(SYM.findall(w))
            if syms:
                found |= syms
                if len(snippets) < 6:
                    snippets.append(w[max(0, len(w) // 2 - 220):len(w) // 2 + 220].strip())
        if found & eff:
            verdict = "MATCH"
        elif found:
            verdict = "DISAGREE"
        elif MOODY.search(t):
            verdict = "MENTION_ONLY"
        else:
            verdict = "NO_MENTION"
        res = {"slug": slug, "group": c["group"], "cik": c["cik"], "document": doc,
               "in_effect_at_filing": sorted(eff), "symbols_near_moody": sorted(found),
               "verdict": verdict}
        json.dump({**res, "method": "self-disclosure check, see evaluation/verify_mapping.py",
                   "evidence": snippets},
                  open(os.path.join(d, "verification.json"), "w"), indent=1, ensure_ascii=False)
        results.append(res)
        print(f"  {slug:<28} {verdict:<13} offengelegt {sorted(found) or '—'} | in Kraft {sorted(eff) or '—'}")

    order = {"DISAGREE": 0, "MATCH": 1, "MENTION_ONLY": 2, "NO_MENTION": 3}
    results.sort(key=lambda r: (order[r["verdict"]], r["slug"]))
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    with open(os.path.join(ROOT, "evaluation", "mapping-verification.md"), "w") as f:
        f.write("# Mapping verification via self-disclosure\n\n")
        f.write("*Generated by evaluation/verify_mapping.py; method and caveats in its "
                "docstring. Independent of name matching: compares the rating the mapped SEC "
                "filer discloses in its own annual report against the rating the mapped "
                "Moody's entity carried at the filing date.*\n\n")
        f.write(f"Result: {counts}\n\n")
        f.write("| Company | Verdict | Disclosed near 'Moody' | In effect at filing |\n|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['group']} | {r['verdict']} | {', '.join(r['symbols_near_moody']) or '—'} "
                    f"| {', '.join(r['in_effect_at_filing']) or '—'} |\n")
        f.write("\nMATCH confirms the pair through the company's own words. DISAGREE means "
                "symbols appeared near Moody mentions but none was in effect on our side of "
                "the join: eyeball evidence in the folder's verification.json before trusting "
                "that pair. MENTION_ONLY and NO_MENTION are neutral (many filers, especially "
                "foreign ones, do not print their ratings), not evidence against.\n")
    print(f"\n{counts}")


if __name__ == "__main__":
    main()
