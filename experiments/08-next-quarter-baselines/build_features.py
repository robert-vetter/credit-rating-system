"""
Experiment 08: point-in-time features for every company-quarter of the Experiment 07 R2 cohort.

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. Implements section 6 of
README.md in this folder. No model call.

One row per Experiment 07 quarterly record: the outcome is the rating move in the quarter ending
at `outcome_date`; the prediction date t is the quarter end before it. Every feature at t uses only
labels of rating actions on or before t and only XBRL facts filed on or before t.

Financial facts are read from the raw SEC companyfacts files (not from the compact xbrl.json,
whose quarterly extraction drops quarters that run from the 1st to the last day of a month):
    still-rated companies    data/edgar/companyfacts/<slug>.json
    withdrawn-rating groups  data/edgar/companyfacts-withdrawn/CIK##########.json
Concepts and fallback order are those of evaluation/pipeline/fetch_xbrl.py (CONCEPTS). Durations
are true calendar days. Scorecard metrics come from evaluation/pipeline/history_pack.py
(metrics_for, quant_contribution) and system/scorecard.py, unchanged.

Trailing twelve months (TTM) at a fiscal period end p, known at t:
    1. an annual value ending at p (330 to 400 days), else
    2. year-to-date at p + the previous annual value - the year-to-date a year earlier, else
    3. the sum of four consecutive single quarters (80 to 100 days) ending at p, where a missing
       fourth fiscal quarter is the annual value minus the first three quarters of that year.
The earliest filing of a value wins; later restatements are ignored.
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
sys.path.insert(0, os.path.join(ROOT, "system"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "07-rating-change-base-rates"))
import history_pack as hp  # noqa: E402
import run_study as E7  # noqa: E402
import scorecard  # noqa: E402
from fetch_xbrl import CONCEPTS, INSTANT  # noqa: E402

GRID, QI = E7.GRID, E7.QI
WITHDRAWN_INPUTS = os.path.join(ROOT, "experiments", "07-rating-change-base-rates", "runs", "R2-inputs-withdrawn")
CF_ACTIVE = os.path.join(ROOT, "data", "edgar", "companyfacts")
CF_WITHDRAWN = os.path.join(ROOT, "data", "edgar", "companyfacts-withdrawn")
FLOWS = [f for f in CONCEPTS if f not in INSTANT]
FORMS = ("10-Q", "10-Q/A", "10-K", "10-K/A")
OUTCOME_NOTCH = {lab: i for i, lab in enumerate(E7.SCALE)}


def d(s):
    return dt.date.fromisoformat(s)


def days(start, end):
    return (d(end) - d(start)).days


# ----------------------------------------------------------------------------- facts

def extract_facts(raw):
    """{field: {"flows": [...]} or {"instants": [...]}} merged across the concept chain.
    A key (start, end) for flows or end for instants is taken from the first tag in the chain
    that has it; within a tag, the earliest filing wins."""
    g = (raw or {}).get("facts", {}).get("us-gaap", {})
    out = {}
    for field, tags in CONCEPTS.items():
        instant = field in INSTANT
        chosen = {}
        for tag in tags:
            units = g.get(tag, {}).get("units", {}).get("USD", [])
            best = {}
            for e in units:
                if e.get("form") not in FORMS or "val" not in e or not e.get("filed") or not e.get("end"):
                    continue
                if instant:
                    key = e["end"]
                else:
                    if not e.get("start"):
                        continue
                    key = (e["start"], e["end"])
                if key not in best or e["filed"] < best[key]["filed"]:
                    best[key] = {"start": e.get("start"), "end": e["end"], "val": e["val"],
                                 "filed": e["filed"], "tag": tag}
            for key, v in best.items():
                chosen.setdefault(key, v)
        out[field] = sorted(chosen.values(), key=lambda v: (v["end"], v.get("start") or ""))
    return out


def known(values, t):
    return [v for v in values if v["filed"] <= t]


def near(a, b, tol):
    return abs((d(a) - d(b)).days) <= tol


def ttm(values, p, t):
    """(value, max filed date, method) of the trailing twelve months ending at p, or None."""
    vs = known(values, t)
    at_p = [v for v in vs if v["end"] == p]
    annual = [v for v in at_p if 330 <= days(v["start"], v["end"]) <= 400]
    if annual:
        v = annual[0]
        return v["val"], v["filed"], "annual"
    ytd = sorted((v for v in at_p if 80 <= days(v["start"], v["end"]) <= 290),
                 key=lambda v: -days(v["start"], v["end"]))
    for y in ytd:
        n = days(y["start"], y["end"])
        prev_a = [v for v in vs if 330 <= days(v["start"], v["end"]) <= 400
                  and 0 < (d(y["start"]) - d(v["end"])).days <= 10]
        prev_y = [v for v in vs if near(v["end"], (d(p) - dt.timedelta(days=364)).isoformat(), 10)
                  and abs(days(v["start"], v["end"]) - n) <= 10]
        if prev_a and prev_y:
            val = prev_a[0]["val"] + y["val"] - prev_y[0]["val"]
            return val, max(y["filed"], prev_a[0]["filed"], prev_y[0]["filed"]), "ytd"
    quarters = [v for v in vs if 80 <= days(v["start"], v["end"]) <= 100]
    annuals = [v for v in vs if 330 <= days(v["start"], v["end"]) <= 400]
    chain, end, filed = [], p, ""
    for _ in range(4):
        q = next((v for v in quarters if v["end"] == end), None)
        if q is None:
            a = next((v for v in annuals if v["end"] == end), None)
            if a is None:
                return None
            inside = [v for v in quarters if d(a["start"]) <= d(v["start"]) and v["end"] < a["end"]]
            if len(inside) != 3:
                return None
            val = a["val"] - sum(v["val"] for v in inside)
            start = (max(d(v["end"]) for v in inside) + dt.timedelta(days=1)).isoformat()
            q = {"val": val, "start": start, "filed": max([a["filed"]] + [v["filed"] for v in inside])}
        chain.append(q)
        filed = max(filed, q["filed"])
        end = (d(q["start"]) - dt.timedelta(days=1)).isoformat()
        end = next((v["end"] for v in quarters + annuals if near(v["end"], end, 4)), end)
    return sum(q["val"] for q in chain), filed, "quarters"


def instant_at(values, p, t):
    vs = [v for v in known(values, t) if near(v["end"], p, 3)]
    return (vs[0]["val"], vs[0]["filed"], vs[0]["tag"]) if vs else None


def period_values(facts, p, t):
    """The dict history_pack.metrics_for expects, at fiscal period end p, known at t."""
    y, tags, filed = {}, {}, []
    for f in FLOWS:
        r = ttm(facts.get(f, []), p, t)
        if r:
            y[f], filed = r[0], filed + [r[1]]
    for f in INSTANT:
        r = instant_at(facts.get(f, []), p, t)
        if r:
            y[f], tags[f], filed = r[0], r[2], filed + [r[1]]
    y["_tags"] = tags
    return y, (max(filed) if filed else None)


def latest_period(facts, t):
    """The latest fiscal period end with a TTM revenue known at t."""
    ends = sorted({v["end"] for v in known(facts.get("revenue", []), t)}, reverse=True)
    for p in ends[:6]:
        if ttm(facts["revenue"], p, t):
            return p
    return None


def financial_features(facts, t):
    empty = {k: None for k in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11",
                               "F10_implied", "F13")}
    if not facts:
        return dict(empty, F0=0, period=None, max_filed=None)
    p = latest_period(facts, t)
    if p is None:
        return dict(empty, F0=0, period=None, max_filed=None)
    y, filed = period_values(facts, p, t)
    p4 = (d(p) - dt.timedelta(days=364)).isoformat()
    ends = sorted({v["end"] for v in known(facts.get("revenue", []), t)})
    p4 = next((e for e in ends if near(e, p4, 10)), None)
    y4 = period_values(facts, p4, t)[0] if p4 else {}

    def block(v):
        if "revenue" not in v:
            return None
        m = hp.metrics_for(v)
        s = hp.quant_contribution(m)
        ebitda = m["ebitda_usd_m"] * 1e6 if m["ebitda_usd_m"] is not None else None
        debt = m["debt_usd_m"] * 1e6 if m["debt_usd_m"] is not None else None
        agg = sum(hp.QUANT_W[k] * s[k] for k in s) / 0.55 if len(s) == 4 else None
        return {"rev": v["revenue"], "margin": ebitda / v["revenue"] if ebitda is not None and v["revenue"] else None,
                "lev": m["debt_ebitda"], "cov": m["ebitda_capex_interest"],
                "liq": v["cash"] / debt if debt and v.get("cash") is not None else None,
                "neg": (ebitda < 0) if ebitda is not None else None, "agg": agg}

    b, b4 = block(y), block(y4) if y4 else None

    def diff(k, scale=1.0):
        if b and b4 and b[k] is not None and b4[k] is not None:
            return scale * (b[k] - b4[k])
        return None
    f = {
        "F1": (b["rev"] / b4["rev"] - 1) if b and b4 and b4["rev"] else None,
        "F2": b["margin"] if b else None,
        "F3": diff("margin", 100.0),
        "F4": b["lev"] if b else None,
        "F5": diff("lev"),
        "F6": b["cov"] if b else None,
        "F7": diff("cov"),
        "F8": b["liq"] if b else None,
        "F9": (1 if b["neg"] else 0) if b and b["neg"] is not None else None,
        "F10": b["agg"] if b else None,
        "F11": diff("agg"),
        "F10_implied": OUTCOME_NOTCH.get(scorecard.outcome(b["agg"])) if b and b["agg"] is not None else None,
        "F13": (d(t) - d(filed)).days if filed else None,
    }
    f["F0"] = 1 if any(f[k] is not None for k in ("F2", "F4", "F6", "F10")) else 0
    f["period"], f["max_filed"] = p, filed
    return f


# ----------------------------------------------------------------------------- rating features

def rating_features(company_quarters, t, rating_t, all_quarters_by_date):
    i = QI[t]
    window = GRID[max(0, i - 3):i + 1]
    own = {q["date"]: q for q in company_quarters}
    recent = [own[x] for x in window if x in own]
    since = 0
    for x in reversed(GRID[:i + 1]):
        q = own.get(x)
        if q is None or q["changed"] or since >= 20:
            break
        since += 1
    cyc = [q for x in window for q in all_quarters_by_date.get(x, [])]
    n = E7.notch(rating_t)
    return {
        "category": E7.category(rating_t),
        "R2": n,
        "R3": int(any(q["changed"] and (q["delta"] or 0) > 0 for q in recent)),
        "R4": int(any(q["changed"] and (q["delta"] or 0) < 0 for q in recent)),
        "R5": since,
        "R6_down": sum(1 for q in cyc if q["changed"] and (q["delta"] or 0) > 0) / len(cyc) if cyc else 0.0,
        "R6_up": sum(1 for q in cyc if q["changed"] and (q["delta"] or 0) < 0) / len(cyc) if cyc else 0.0,
    }


# ----------------------------------------------------------------------------- companies

def facts_for(slug, origin, company_doc):
    if origin == "active":
        path = os.path.join(CF_ACTIVE, f"{slug}.json")
        paths = [path] if os.path.exists(path) else []
    else:
        ciks = sorted({int(m["decided_cik"]) for m in company_doc["members"] if m.get("decided_cik")})
        paths = [p for p in (os.path.join(CF_WITHDRAWN, f"CIK{c:010d}.json") for c in ciks) if os.path.exists(p)]
    best, best_n, best_path = None, -1, None
    for path in paths:
        raw = json.load(open(path))
        if "facts" not in raw:
            continue
        facts = extract_facts(raw)
        n = sum(1 for v in facts["revenue"] if 80 <= days(v["start"], v["end"]) <= 290)
        if n > best_n:
            best, best_n, best_path = facts, n, path
    return best, best_path


def build(gold_keys):
    companies = [c for c in E7.load(WITHDRAWN_INPUTS) if c[1]["scope"] == "in"]
    records = {}
    for slug, doc, ratings, _, _ in companies:
        records[slug] = E7.company_records(slug, doc, ratings)["quarters"]
    by_date = {}
    for qs in records.values():
        for q in qs:
            by_date.setdefault(q["date"], []).append(q)
    rows, sources = [], {}
    for slug, doc, ratings, _, _ in companies:
        origin = doc["origin"]
        cdoc = None
        if origin == "withdrawn":
            cdoc = json.load(open(os.path.join(WITHDRAWN_INPUTS, slug, "company.json")))
        facts, path = facts_for(slug, origin, cdoc)
        sources[slug] = os.path.relpath(path, ROOT) if path else None
        for q in records[slug]:
            t = GRID[QI[q["date"]] - 1]
            # the cycle feature must not see the outcome quarter itself
            cycle_view = {x: v for x, v in by_date.items() if x <= t}
            r = rating_features(records[slug], t, q["prev"], cycle_view)
            fin = financial_features(facts, t)
            fin["F12"] = (r["R2"] - fin["F10_implied"]) if r["R2"] is not None and fin["F10_implied"] is not None else None
            target = 0 if not q["changed"] else (1 if q["delta"] > 0 else 2)
            rows.append({"company": slug, "origin": origin, "t": t, "outcome_date": q["date"],
                         "rating_t": q["prev"], "target": target, "delta": q["delta"],
                         "gold": (slug, q["date"]) in gold_keys, **r, **fin})
    return rows, sources


def audit(rows):
    bad = [r for r in rows if r["max_filed"] and r["max_filed"] > r["t"]]
    return {"rows": len(rows), "facts_filed_after_t": len(bad),
            "rows_with_financials": sum(r["F0"] for r in rows)}


def main(out_dir):
    gold = json.load(open(os.path.join(ROOT, "evaluation", "goldset.json")))
    items = gold["items"] if isinstance(gold, dict) else gold
    gold_keys = {(g["slug"], g["date"]) for g in items}
    rows, sources = build(gold_keys)
    a = audit(rows)
    if a["facts_filed_after_t"]:
        sys.exit(f"point-in-time violation: {a}")
    json.dump(rows, open(os.path.join(out_dir, "features.json"), "w"), indent=0)
    json.dump({"audit": a, "sources": sources}, open(os.path.join(out_dir, "audit.json"), "w"), indent=1)
    return rows, a


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    print(main(out)[1])
