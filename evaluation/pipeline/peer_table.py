"""
Peer key-figure table for an observation date, from XBRL - an input configuration for the
Market Position subfactor.

Written by Claude (Opus 5), directed by Robert Vetter.

Market Position is relative; a single filing cannot show it. This builds a plain-text table of
the in-scope retail peers' latest annual key figures as of the observation date, generated
from evaluation/companies/*/xbrl.json (fetch_xbrl.py) rather than from more model calls.

Point-in-time discipline: a fact enters the table only if its "filed" date is on or before the
observation date, and only period ends on or before it. Leakage stance, documented: the table
carries NO ratings, only reported figures; whether even peer identities are admissible input
is an experiment switch (--peers on the runner), not an assumption.

Numbers are as tagged by the issuers (no Moody's adjustments); the derived columns say exactly
what they are. Missing tags leave blanks - coverage varies by issuer and era.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "evaluation", "companies")

DEBT_PARTS = ["lt_debt_noncurrent", "lt_debt_current", "st_borrowings",
              "finance_lease_current", "finance_lease_noncurrent",
              "operating_lease_current", "operating_lease_noncurrent"]


def _latest(field, t):
    vals = [v for v in field.get("annual", []) if v["end"] <= t and v.get("filed", "9") <= t]
    return vals[-1]["val"] if vals else None


def build(t, exclude_slug=None):
    """Plain-text peer table for observation date t; None if too few peers have data."""
    rows = []
    for slug in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, slug)
        xp, cp = os.path.join(d, "xbrl.json"), os.path.join(d, "company.json")
        if slug == exclude_slug or not os.path.exists(xp) or not os.path.exists(cp):
            continue
        c = json.load(open(cp))
        if c.get("scope") != "in":
            continue
        f = json.load(open(xp)).get("fields", {})
        g = {k: _latest(v, t) for k, v in f.items()}
        if not g.get("revenue"):
            continue
        ebitda = (g["operating_income"] + g["d_and_a"]
                  if g.get("operating_income") is not None and g.get("d_and_a") is not None else None)
        debt_parts = [g[p] for p in DEBT_PARTS if g.get(p) is not None]
        debt = sum(debt_parts) if debt_parts else None
        rows.append({
            "name": c["group"], "revenue": g["revenue"], "ebitda": ebitda,
            "margin": ebitda / g["revenue"] if ebitda else None,
            "debt": debt,
            "debt_ebitda": debt / ebitda if debt and ebitda and ebitda > 0 else None,
            "capex": g.get("capex"), "cfo": g.get("cfo"), "dividends": g.get("dividends"),
        })
    if len(rows) < 5:
        return None
    rows.sort(key=lambda r: -r["revenue"])

    def bn(v):
        return f"{v / 1e9:8.1f}" if v is not None else "       -"

    def x(v, fmt):
        return fmt.format(v) if v is not None else "     -"

    lines = [f"Rated US retail/apparel peers, latest full fiscal year reported on or before {t}.",
             "Figures as XBRL-tagged by each issuer, USD bn; EBITDA = operating income + D&A;",
             "debt = sum of tagged debt and lease liabilities (coverage varies; no adjustments).",
             "",
             f"{'company':<28}{'revenue':>9}{'EBITDA':>9}{'margin':>8}{'debt':>9}{'dbt/EBI':>8}"
             f"{'capex':>9}{'CFO':>9}{'divid.':>9}"]
    for r in rows:
        lines.append(f"{r['name'][:27]:<28}{bn(r['revenue'])}{bn(r['ebitda'])}"
                     f"{x(r['margin'], '{:7.1%}')}{bn(r['debt'])}{x(r['debt_ebitda'], '{:7.1f}x')}"
                     f"{bn(r['capex'])}{bn(r['cfo'])}{bn(r['dividends'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else "2022-12-31") or "zu wenig Daten")
