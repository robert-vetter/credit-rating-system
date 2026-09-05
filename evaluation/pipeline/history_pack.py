"""
History pack: the point-in-time historical context for a rating observation.

Written by Claude (Opus 5), directed by Robert Vetter (design decision 2026-08-30: determine
the new rating RELATIVE to the issuer's own history, so both prompt variants receive the
same history rather than deriving everything from a single filing).

For (company, observation date t) the pack contains, all filtered to what was public at t:
  - the Moody's rating path up to the previous quarter end (never the observation quarter)
  - the last three fiscal years of scorecard quantitative inputs from XBRL, deterministic:
    revenue, EBITDA (operating income + D&A), capex, interest, cash, CFO, dividends, debt
    (sum of tagged debt and lease components), and the four scorecard metrics derived from
    them. RCF is approximated as CFO - dividends because the working-capital swing is not
    an XBRL concept (stated in the pack)
  - the "current" fiscal year on the same basis: the latest FY whose 10-K was filed before t
  - the IMPLIED QUALITATIVE ANCHOR per prior year: given that year's actual rating and its
    quantitative scores, the average qualitative grade the scorecard arithmetic implies
    (rating's aggregate band midpoint minus the 55% quantitative contribution, divided by
    0.45). Moody's own factor scores are not public; this is the closest checkable proxy,
    and it turns "grade four factors from nothing" into "has anything changed versus the
    anchor". Notching and other considerations fold into the anchor - it is an anchor, not
    a decomposition.
  - the XBRL peer key-figure table at t (no ratings in it)

Output is plain text for the prompt plus a dict for logging. Foreign IFRS filers have no
XBRL fields and get a pack with the quantitative sections marked unavailable.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import peer_table   # noqa: E402
import scorecard    # noqa: E402

OUT = os.path.join(ROOT, "evaluation", "companies")
LT = ("LT CORPORATE FAMILY RATINGS", "LT ISSUER RATING", "ISSUER RATING", "ISSUER LT RATING")
DEBT_PARTS = ["lt_debt_noncurrent", "lt_debt_current", "st_borrowings",
              "finance_lease_current", "finance_lease_noncurrent",
              "operating_lease_current", "operating_lease_noncurrent"]
GRADE_OF = [(2.0, "Aaa"), (4.5, "Aa"), (7.5, "A"), (10.5, "Baa"), (13.5, "Ba"),
            (16.5, "B"), (19.0, "Caa"), (99, "Ca")]
QUANT_W = {"Revenue": 0.15, "Debt/EBITDA": 0.15, "(EBITDA-Capex)/Interest": 0.15, "RCF/Net Debt": 0.10}


def quarter_start(t):
    return t[:4] + {"03": "-01-01", "06": "-04-01", "09": "-07-01", "12": "-10-01"}[t[5:7]]


def fy_values(xbrl, filed_leq):
    """{fy_end: {field: val}} for fiscal years whose values were filed on/before filed_leq."""
    years = {}
    for field, blob in xbrl.get("fields", {}).items():
        for v in blob["annual"]:
            if v.get("filed", "9999") <= filed_leq:
                years.setdefault(v["end"], {})[field] = v["val"]
    return {k: v for k, v in years.items() if "revenue" in v}


def metrics_for(y):
    m = {"revenue_usd_bn": y["revenue"] / 1e9}
    ebitda = (y["operating_income"] + y["d_and_a"]) if "operating_income" in y and "d_and_a" in y else None
    parts = [y[p] for p in DEBT_PARTS if p in y]
    debt = sum(parts) if parts else None
    m["ebitda_usd_m"] = ebitda / 1e6 if ebitda else None
    m["debt_usd_m"] = debt / 1e6 if debt else None
    m["debt_components"] = [p for p in DEBT_PARTS if p in y]
    m["debt_ebitda"] = debt / ebitda if debt and ebitda and ebitda > 0 else None
    if ebitda and y.get("capex") is not None and y.get("interest"):
        m["ebitda_capex_interest"] = (ebitda - y["capex"]) / abs(y["interest"])
    else:
        m["ebitda_capex_interest"] = None
    if debt is not None and y.get("cash") is not None and y.get("cfo") is not None:
        net_debt = debt - y["cash"]
        rcf = y["cfo"] - y.get("dividends", 0)
        m["rcf_net_debt_pct"] = 100 * rcf / net_debt if net_debt > 0 else None
    else:
        m["rcf_net_debt_pct"] = None
    return m


def quant_contribution(m):
    """Weighted quantitative score (out of the 0.55 total) and which factors were scorable."""
    s = {}
    if m["revenue_usd_bn"] is not None:
        s["Revenue"] = scorecard.score_quant("revenue_usd_bn", m["revenue_usd_bn"])
    if m["debt_ebitda"] is not None:
        s["Debt/EBITDA"] = scorecard.score_quant("debt_ebitda", m["debt_ebitda"])
    if m["ebitda_capex_interest"] is not None:
        s["(EBITDA-Capex)/Interest"] = scorecard.score_quant("ebitda_capex_interest", m["ebitda_capex_interest"])
    if m["rcf_net_debt_pct"] is not None:
        s["RCF/Net Debt"] = scorecard.score_quant("rcf_net_debt_pct", m["rcf_net_debt_pct"])
    return s


def implied_anchor(rating, quant_scores):
    """Average qualitative grade implied by an actual rating and the quantitative scores."""
    ceilings = [c for c, lab in scorecard.OUTCOME]
    labels = [lab for c, lab in scorecard.OUTCOME]
    r = rating.replace("(P)", "").strip()
    if r not in labels or len(quant_scores) < 4:
        return None
    i = labels.index(r)
    lo = 0.5 if i == 0 else ceilings[i - 1]
    mid = (lo + ceilings[i]) / 2
    quant = sum(QUANT_W[k] * v for k, v in quant_scores.items())
    q = (mid - quant) / 0.45
    q = max(1.0, min(20.0, q))
    grade = next(g for c, g in GRADE_OF if q <= c)
    return {"implied_qual_score": round(q, 2), "implied_grade": grade}


def rating_at(ratings, t):
    """Entity-level LT rating in effect at t, else senior unsecured (same rule as elsewhere)."""
    ent, sen = [], []
    for e in ratings["entities"]:
        recs = sorted([r for r in (e.get("obligor_records") or [])
                       if r.get("RT", "").upper() in LT and r.get("RAD") and r["RAD"] <= t],
                      key=lambda r: r["RAD"])
        if recs and recs[-1].get("R") != "WR":
            ent.append((recs[-1]["RAD"], recs[-1]["R"]))
        for ins in (e.get("instruments") or []):
            recs = sorted([r for r in ins["records"] if r.get("RT") == "Senior Unsecured"
                           and r.get("RAD") and r["RAD"] <= t], key=lambda r: r["RAD"])
            if recs and recs[-1].get("R") != "WR":
                sen.append((recs[-1]["RAD"], recs[-1]["R"]))
    if ent:
        return max(ent)[1]
    return max(sen)[1] if sen else None


def quarterly_rows(xbrl, filed_leq, n=4):
    """Last n single-quarter values of the ten figures (issuer-tagged, filed on/before filed_leq)."""
    q = {}
    for field, blob in xbrl.get("fields", {}).items():
        for v in blob.get("quarterly", []):
            if v.get("filed", "9999") <= filed_leq:
                q.setdefault(v["end"], {})[field] = v["val"]
    ends = sorted(e for e, vals in q.items() if "revenue" in vals)[-n:]
    rows = []
    for e in ends:
        vals = q[e]
        f = lambda k: (f"{vals[k] / 1e6:,.0f}" if k in vals else "n/a")
        rows.append(f"  quarter ending {e}: revenue {f('revenue')}m; operating income {f('operating_income')}m; "
                    f"D&A {f('d_and_a')}m; capex {f('capex')}m; CFO {f('cfo')}m; cash {f('cash')}m; "
                    f"LT debt {f('lt_debt_noncurrent')}m; op-lease liab. {f('operating_lease_noncurrent')}m")
    return rows


def build(slug, t, n_prior=3, history_end=None):
    """history_end: cap the rating history there instead of at the observation quarter start
    (Experiment 03: the 17g-7 file ends 2025-08-11, observation dates lie after it)."""
    d = os.path.join(OUT, slug)
    company = json.load(open(os.path.join(d, "company.json")))
    ratings = json.load(open(os.path.join(d, "ratings.json")))
    obs = json.load(open(os.path.join(d, "observations.json")))["observations"]
    o = next((x for x in obs if x["date"] == t), None)
    if history_end:
        qs = history_end
        src = o or (obs[-1] if obs else None)
        path = [e for e in (src["rating_path"] if src else []) if e[0] <= history_end]
    else:
        qs = quarter_start(t)
        path = [e for e in (o["rating_path"] if o else []) if e[0] < qs]
    xp = os.path.join(d, "xbrl.json")
    xbrl = json.load(open(xp)) if os.path.exists(xp) else {}
    years = fy_values(xbrl, t)
    ends = sorted(years)
    current_end = ends[-1] if ends else None
    prior_ends = ends[-1 - n_prior:-1] if len(ends) > 1 else []

    rows, log = [], {"slug": slug, "date": t, "path_cutoff": qs, "years": {}}
    for end in prior_ends + ([current_end] if current_end else []):
        m = metrics_for(years[end])
        qsc = quant_contribution(m)
        if end == current_end:
            r_then = None
        elif history_end and end > history_end:
            r_then = rating_at(ratings, history_end)      # last known rating, not the rating "then"
        else:
            r_then = rating_at(ratings, end)
        anchor = implied_anchor(r_then, qsc) if r_then else None
        log["years"][end] = {"metrics": {k: v for k, v in m.items() if k != "debt_components"},
                             "quant_scores": qsc, "rating_then": r_then, "anchor": anchor}
        tag = ("current FY (latest 10-K before t)" if end == current_end else
               (f"last known rating {r_then or '?'} (history ends {history_end})"
                if history_end and end > history_end else f"rating then {r_then or '?'}"))
        f = lambda v, fmt: (fmt.format(v) if v is not None else "n/a")
        rows.append(f"  FY ending {end} [{tag}]: revenue {f(m['revenue_usd_bn'], '{:.1f}')}bn; "
                    f"EBITDA {f(m['ebitda_usd_m'], '{:,.0f}')}m; debt {f(m['debt_usd_m'], '{:,.0f}')}m; "
                    f"debt/EBITDA {f(m['debt_ebitda'], '{:.2f}x')}; (EBITDA-capex)/interest "
                    f"{f(m['ebitda_capex_interest'], '{:.1f}x')}; RCF/net debt {f(m['rcf_net_debt_pct'], '{:.0f}%')}"
                    + (f"; implied avg qualitative grade ≈ {anchor['implied_grade']} (score {anchor['implied_qual_score']})"
                       if anchor else ""))
    shown, last = [], None
    for e in path:
        if e[1] == "WR":
            continue                      # matured/withdrawn instruments are not rating changes
        if e[1] != last:
            shown.append(e); last = e[1]
    anchors = [log["years"][e]["anchor"]["implied_qual_score"] for e in prior_ends
               if log["years"].get(e, {}).get("anchor")]
    if anchors:
        med = sorted(anchors)[len(anchors) // 2]
        grade = next(g for c, g in GRADE_OF if med <= c)
        rows.append(f"  => median implied qualitative anchor over the prior years: {grade} (score {med}); "
                    "single shock years (e.g. 2020) distort the one-year figure")
    if any(end < "2019-06-01" for end in prior_ends):
        rows.append("  note: fiscal years ending before mid-2019 predate ASC 842, so their tagged debt "
                    "excludes operating-lease liabilities; the debt jump at adoption is accounting, not borrowing")
    hist = "\n".join(f"  {e[0]}  {e[1]}  ({e[2]}, {e[3]}-level)" for e in shown) or "  (no events on record)"
    # Strictly before the observation quarter: an action dated on the quarter's first day is
    # part of the quarter (Under Armour, 2020-04-01, leaked into a run before this fix).
    import datetime as _dt
    if history_end:
        r_qs = rating_at(ratings, history_end)
        hist += f"\n  => rating in effect at the end of the available history ({history_end}): {r_qs or 'none'}"
    else:
        prev_day = (_dt.date(*map(int, qs.split("-"))) - _dt.timedelta(days=1)).isoformat()
        r_qs = rating_at(ratings, prev_day)
        hist += f"\n  => rating in effect entering the quarter (as of {prev_day}): {r_qs or 'none'}"
    qrows = quarterly_rows(xbrl, t)
    if qrows:
        rows.append("  Recent single quarters (issuer-tagged XBRL, USD m, filed on or before the as-of date):")
        rows.extend(qrows)
    log["quarterly_rows"] = len(qrows)
    peers = peer_table.build(t, exclude_slug=slug) or "(peer table unavailable at this date)"
    text = (f"<history_pack company=\"{company['group']}\" as_of=\"{t}\">\n"
            f"Rating history (Moody's, complete through {qs}; nothing later is provided):\n{hist}\n\n"
            "Fiscal-year fundamentals from XBRL (issuer-tagged, USD; EBITDA = operating income + D&A; "
            "debt = tagged debt + lease liabilities; RCF approximated as CFO - dividends; scorecard "
            "metrics computed from these):\n" + ("\n".join(rows) if rows else "  (no XBRL data)") +
            "\n\nThe 'implied avg qualitative grade' is what the scorecard arithmetic requires the "
            "average of the four qualitative factors to have been, given that year's actual rating "
            "and its quantitative scores - an anchor for judging whether the qualitative picture "
            "has changed, not Moody's published factor scores.\n\n"
            f"<peer_table>\n{peers}\n</peer_table>\n</history_pack>")
    return text, log


if __name__ == "__main__":
    text, log = build(sys.argv[1], sys.argv[2])
    print(text)
