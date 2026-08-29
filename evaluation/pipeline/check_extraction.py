"""
Scores the extraction step against XBRL - no model call needed.

Written by Claude (Opus 5), directed by Robert Vetter.

The analyst's first job is reading ten figures out of filing text. The same figures exist
machine-tagged in XBRL (fetch_xbrl.py), which makes extraction accuracy checkable
automatically and for free. Two modes:

  --manual         checks the two hand-extracted input sets in system/scorecard.py (Walmart
                   FY2026, Kohl's FY2025) against XBRL - a validation of the check itself as
                   much as of those inputs
  --run <dir>      checks every observation result in an evaluation run directory; writes
                   extraction_check.json into it

What is comparable and what is not, stated up front: revenue, operating income, D&A, capex,
cash, dividends and CFO map one-to-one onto XBRL tags. Interest is compared but flagged -
issuers tag gross or net inconsistently. The debt figure and the working-capital swing are
Moody's-adjusted composites with no single tag; debt is compared against the sum of the
tagged components where they exist (expect small gaps from financing obligations and
untagged items), wc_swing is not checked. A deviation therefore means "investigate", not
automatically "wrong" - the point is to make deviations visible and countable.
"""
import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
OUT = os.path.join(ROOT, "evaluation", "companies")

DIRECT = ["revenue", "operating_income", "d_and_a", "capex", "cash", "dividends", "cfo"]
DEBT_PARTS = ["lt_debt_noncurrent", "lt_debt_current", "st_borrowings",
              "finance_lease_current", "finance_lease_noncurrent",
              "operating_lease_current", "operating_lease_noncurrent"]


def xbrl_year(slug, fy_end_leq, filed_leq=None):
    """{field: value} for the latest fiscal year ending on or before fy_end_leq."""
    p = os.path.join(OUT, slug, "xbrl.json")
    if not os.path.exists(p):
        return None, None
    fields = json.load(open(p)).get("fields", {})
    rev = [v for v in fields.get("revenue", {}).get("annual", [])
           if v["end"] <= fy_end_leq and (not filed_leq or v["filed"] <= filed_leq)]
    if not rev:
        return None, None
    end = rev[-1]["end"]
    out = {}
    for f, blob in fields.items():
        hit = [v for v in blob["annual"] if v["end"] == end]
        if hit:
            out[f] = hit[0]["val"]
    return end, out


def compare(figures_usd_m, slug, fy_end_leq, filed_leq=None):
    """figures in USD millions vs XBRL (USD). Returns (rows, fiscal_end) or (None, None)."""
    end, x = xbrl_year(slug, fy_end_leq, filed_leq)
    if not x:
        return None, None
    rows = []
    for f in DIRECT + ["interest"]:
        ours, theirs = figures_usd_m.get(f), x.get(f)
        if ours is None or theirs is None:
            rows.append({"field": f, "ours_m": ours, "xbrl_m": None if theirs is None else theirs / 1e6,
                         "dev_pct": None, "note": "no XBRL tag" if theirs is None else "not extracted"})
            continue
        theirs_m = theirs / 1e6
        dev = abs(ours - theirs_m) / max(abs(theirs_m), 1e-9) * 100
        rows.append({"field": f, "ours_m": ours, "xbrl_m": round(theirs_m, 1),
                     "dev_pct": round(dev, 1),
                     "note": "gross-vs-net ambiguity" if f == "interest" else ""})
    parts = {p: x[p] for p in DEBT_PARTS if p in x}
    if parts and figures_usd_m.get("debt") is not None:
        total_m = sum(parts.values()) / 1e6
        dev = abs(figures_usd_m["debt"] - total_m) / max(total_m, 1e-9) * 100
        rows.append({"field": "debt (vs sum of tagged components)",
                     "ours_m": figures_usd_m["debt"], "xbrl_m": round(total_m, 1),
                     "dev_pct": round(dev, 1),
                     "note": f"components: {', '.join(sorted(parts))}"})
    return rows, end


def show(rows, title):
    print(title)
    for r in rows:
        dev = f"{r['dev_pct']:6.1f}%" if r["dev_pct"] is not None else "     - "
        flag = "  <-- pruefen" if (r["dev_pct"] or 0) > 5 and "components" not in r["field"] else ""
        print(f"  {r['field']:<38} unsere {str(r['ours_m']):>12}  XBRL {str(r['xbrl_m']):>12}  "
              f"{dev}  {r['note']}{flag}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual", action="store_true")
    ap.add_argument("--run")
    args = ap.parse_args()
    if args.manual:
        import scorecard
        for slug, c in (("walmart", scorecard.WALMART), ("kohl-s", scorecard.KOHLS)):
            rows, end = compare(c, slug, "2026-12-31")
            if rows:
                show(rows, f"{c['label']}   (XBRL-Jahr endet {end})")
            else:
                print(f"{slug}: kein XBRL")
    if args.run:
        results = json.load(open(os.path.join(args.run, "results.json")))
        checks = []
        for r in results:
            if "extraction" not in r:
                continue
            rows, end = compare(r["extraction"]["figures_usd_m"], r["slug"],
                                r["date"], filed_leq=r["date"])
            if rows:
                checks.append({"slug": r["slug"], "date": r["date"], "fy_end": end, "rows": rows})
                show(rows, f"{r['slug']} @ {r['date']}   (XBRL-Jahr endet {end})")
        devs = [row["dev_pct"] for c in checks for row in c["rows"]
                if row["dev_pct"] is not None and row["field"] in DIRECT]
        if devs:
            devs.sort()
            summary = {"n_figures": len(devs), "median_dev_pct": devs[len(devs) // 2],
                       "share_within_2pct": round(sum(d <= 2 for d in devs) / len(devs), 3)}
            print("Zusammenfassung:", summary)
        json.dump(checks, open(os.path.join(args.run, "extraction_check.json"), "w"),
                  indent=1)


if __name__ == "__main__":
    main()
