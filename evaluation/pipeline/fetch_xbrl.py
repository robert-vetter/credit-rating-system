"""
Structured financials per company from SEC's XBRL companyfacts API.

Written by Claude (Opus 5), directed by Robert Vetter.

Why: two uses, both without model cost. (1) Extraction verification: the analyst's job is to
read figures out of the filing text; XBRL carries the same figures machine-tagged, so the
extraction step can be scored automatically (check_extraction.py). (2) Peer key-figure tables
as an input configuration for the Market Position subfactor (peer_table.py), built from data
rather than from more model calls.

Source: https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json (free, no key). The raw
response is 5-20 MB per company; only the concepts the scorecard needs are kept, annual
(fiscal-year) values only, stored compactly as evaluation/companies/<slug>/xbrl.json with the
"filed" date preserved so downstream use can stay point-in-time (only facts filed before an
observation date may be shown for that date).

Concept fallback chains: issuers tag the same economic line under different us-gaap concepts,
and tag usage changes over time (revenue moved tags with ASC 606 around 2018). Values are
therefore MERGED across a field's accepted tags, keyed by period end, earlier-listed tags
winning conflicts - first-hit-only would lose the pre-2018 history. The tag used is recorded
per value. Companies whose filings predate XBRL (roughly 2009) simply have no data; recorded
as such, not an error.

Run after compile_folders.py: python3 evaluation/pipeline/fetch_xbrl.py
"""
import json
import os
import time
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "evaluation", "companies")
UA = {"User-Agent": "Robert Vetter robert@certus-ai.com"}
ANNUAL_FORMS = ("10-K", "10-K/A", "20-F", "40-F")

CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                "SalesRevenueNet", "SalesRevenueGoodsNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "d_and_a": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet",
                "DepreciationAndAmortization"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "interest": ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt",
                 "InterestIncomeExpenseNet"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue",
             "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "dividends": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "lt_debt_noncurrent": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "lt_debt_current": ["LongTermDebtCurrent"],
    "st_borrowings": ["ShortTermBorrowings", "CommercialPaper"],
    "finance_lease_current": ["FinanceLeaseLiabilityCurrent"],
    "finance_lease_noncurrent": ["FinanceLeaseLiabilityNoncurrent", "FinanceLeaseLiability"],
    "operating_lease_current": ["OperatingLeaseLiabilityCurrent"],
    "operating_lease_noncurrent": ["OperatingLeaseLiabilityNoncurrent", "OperatingLeaseLiability"],
}
INSTANT = {"cash", "lt_debt_noncurrent", "lt_debt_current", "st_borrowings",
           "finance_lease_current", "finance_lease_noncurrent",
           "operating_lease_current", "operating_lease_noncurrent"}


def annual_values(units, instant):
    """Fiscal-year values from a us-gaap concept's USD unit list, deduped by period end."""
    best = {}
    for e in units:
        if e.get("form") not in ANNUAL_FORMS or e.get("fp") != "FY" or "val" not in e:
            continue
        if not instant:
            start, end = e.get("start", ""), e.get("end", "")
            if not start or not end:
                continue
            days = (int(end[:4]) - int(start[:4])) * 365 + (int(end[5:7]) - int(start[5:7])) * 30
            if not 300 <= days <= 430:      # full-year durations only, not quarters
                continue
        k = e["end"]
        # Earliest filing wins: that is when the value first became public, which is what
        # point-in-time filtering needs. Later 10-Ks refile the same year as a comparative
        # (and occasionally restate); restatements are deliberately not applied retroactively.
        if k not in best or e.get("filed", "9999") < best[k]["filed"]:
            best[k] = {"end": e["end"], "val": e["val"], "filed": e.get("filed", ""),
                       "form": e.get("form", "")}
    return sorted(best.values(), key=lambda x: x["end"])


def main():
    done = empty = 0
    for slug in sorted(os.listdir(OUT)):
        cj = os.path.join(OUT, slug, "company.json")
        if not os.path.exists(cj):
            continue
        c = json.load(open(cj))
        time.sleep(0.3)
        try:
            raw = json.loads(urllib.request.urlopen(urllib.request.Request(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{c['cik']:010d}.json",
                headers=UA), timeout=60).read())
        except urllib.error.HTTPError as exc:
            print(f"  {slug:<30} keine companyfacts ({exc.code})", flush=True)
            json.dump({"cik": c["cik"], "note": f"no companyfacts (HTTP {exc.code})",
                       "fields": {}},
                      open(os.path.join(OUT, slug, "xbrl.json"), "w"))
            empty += 1
            continue
        gaap = raw.get("facts", {}).get("us-gaap", {})
        fields = {}
        for canon, tags in CONCEPTS.items():
            merged = {}
            for tag in tags:
                units = gaap.get(tag, {}).get("units", {}).get("USD", [])
                for v in annual_values(units, canon in INSTANT):
                    if v["end"] not in merged:            # earlier-listed tag wins
                        merged[v["end"]] = {**v, "tag": tag}
            if merged:
                fields[canon] = {"annual": sorted(merged.values(), key=lambda x: x["end"])}
        json.dump({"cik": c["cik"], "entity": raw.get("entityName", ""),
                   "source": "SEC companyfacts API, fetched 2026-08-29", "fields": fields},
                  open(os.path.join(OUT, slug, "xbrl.json"), "w"), indent=0)
        yrs = fields.get("revenue", {}).get("annual", [])
        print(f"  {slug:<30} {len(fields):>2}/16 Konzepte, Revenue {len(yrs)} Jahre"
              f"{'  (' + yrs[0]['end'][:4] + '-' + yrs[-1]['end'][:4] + ')' if yrs else ''}",
              flush=True)
        done += 1
    print(f"{done} mit Daten, {empty} ohne")


if __name__ == "__main__":
    main()
