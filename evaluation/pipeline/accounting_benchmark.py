"""Offline three-case accounting development review, not a gold benchmark.

Written by OpenAI Codex, directed by Robert Vetter, 2026-09-17.
Reads cached companyfacts, filing manifests/HTML and gold membership only.
Prints a review table; --out explicitly writes a fresh ignored run directory.
No fetching, models, rating-label analysis or modification of existing artifacts.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
from evidence_ledger import POLICY, FilingIndex, digest, normalize, select, REVENUE
from accounting_checks import annual_checks, row

CASES = (
    {"slug": "walmart", "start": "2025-02-01", "end": "2026-01-31"},
    {"slug": "nike", "start": "2025-06-01", "end": "2026-05-31"},
    {"slug": "signet", "start": "2025-02-02", "end": "2026-01-31"},
)
AS_OF = "2026-08-29"


def read_json(path):
    data = path.read_bytes()
    return json.loads(data), digest(data)


def gold_keys(root):
    raw, sha = read_json(root / "evaluation/goldset.json")
    return {(x["slug"], x["date"]) for x in raw["items"]}, sha


def legacy_value(compact, metric, end):
    key = {"annual_revenue": "revenue", "operating_income": "operating_income",
           "gross_interest_expense": "interest", "quarter_revenue": "revenue"}.get(metric)
    if not key:
        return {"value": None, "note": "No exact legacy comparison."}
    kind = "quarterly" if metric == "quarter_revenue" else "annual"
    hits = [v for v in compact.get("fields", {}).get(key, {}).get(kind, [])
            if v.get("end") == end and v.get("filed", "9999") <= AS_OF]
    return {"value": hits[0]["val"], "tag": hits[0].get("tag"),
            "note": "Legacy compact cache, not ground truth."} if hits else {"value": None, "note": "Missing in legacy compact cache."}


def build_case(root, case):
    slug = case["slug"]
    raw_path = root / f"data/edgar/companyfacts/{slug}.json"
    raw, sha = read_json(raw_path)
    if "error" in raw:
        raise ValueError("Cached companyfacts contains an error response.")
    source = {"path": str(raw_path.relative_to(root)), "sha256": sha}
    ends = {case["end"]}
    if slug == "walmart":
        ends.update(("2026-04-30", "2026-07-31"))
    records = normalize(raw, source, AS_OF, ends)
    rows = annual_checks(records, case["start"], case["end"])
    if slug == "walmart":
        quarter = select(records, REVENUE, "2026-02-01", "2026-04-30")
        rows.append(row("quarter_revenue", quarter,
                        "Exact Feb 1-Apr 30 interval: 88 elapsed days, not the legacy 60-day approximation."))
        rows.append(row("cash_flow_six_month_ytd", select(records,
            ("NetCashProvidedByUsedInOperatingActivities",), "2026-02-01", "2026-07-31"),
            "Six-month cumulative flow retained separately; not a single-quarter input. TTM deferred."))
    compact_path = root / f"evaluation/companies/{slug}/xbrl.json"
    sources, source_issues = [source], []
    def supplemental(path):
        try:
            data, sha = read_json(path)
            sources.append({"path": str(path.relative_to(root)), "sha256": sha})
            return data
        except (OSError, ValueError) as exc:
            source_issues.append({"path": str(path.relative_to(root)), "reason": str(exc)})
            return {}
    compact = supplemental(compact_path)
    for check in rows:
        check["legacy"] = legacy_value(compact, check["metric"], check["end"])
    manifest_path = root / f"evaluation/companies/{slug}/filings/manifest.json"
    manifest = supplemental(manifest_path)
    filings = {f["accessionNumber"]: f for f in manifest.get("filings", [])}
    needed = {i for check in rows for i in check.get("evidence_ids", [])}
    grouped = {}
    for record in records:
        if record["id"] in needed:
            grouped.setdefault(record["accn"], []).append(record)
    for accession, group in sorted(grouped.items()):
        metadata = filings.get(accession)
        if not metadata or metadata.get("form") not in ("10-K", "10-Q", "10-K/A", "10-Q/A"):
            continue
        directory = manifest_path.parent
        candidates = sorted(directory.glob(f"*_{accession.replace('-', '')}.htm"))
        if len(candidates) != 1:
            continue
        path = candidates[0]
        blob = path.read_bytes()
        text = blob.decode("utf-8")
        index = FilingIndex(text)
        filing_source = {"path": str(path.relative_to(root)), "sha256": digest(blob), "accession": accession}
        for record in group:
            if metadata["filingDate"] == record["filed"] and metadata["form"] == record["form"]:
                record["filing_locator"] = index.locate(record, filing_source)
    return {"case": case, "as_of": AS_OF, "status": "completed", "rows": rows,
            "sources": sources, "source_issues": source_issues,
            "records": records, "coverage": {
                "retained_facts": len(records), "quarantined_facts": sum(r["availability"] != "eligible" for r in records),
                "referenced_facts": len(needed),
                "matched_filing_facts": sum(r["id"] in needed and r["filing_locator"]["status"] == "matched_inline_fact" for r in records),
                "check_statuses": dict(sorted(Counter(r["status"] for r in rows).items()))}}


def build_report(root=ROOT, cases=CASES):
    keys, sha = gold_keys(root)
    results = []
    for case in cases:
        if (case["slug"], AS_OF) in keys:
            results.append({"case": case, "status": "excluded_gold", "reason": "Exact gold observation; no case analysis performed."})
            continue
        try:
            results.append(build_case(root, case))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            results.append({"case": case, "status": "unavailable", "reason": str(exc)})
    return {"policy": POLICY, "as_of": AS_OF, "gold_membership_sha256": sha,
            "author": "OpenAI Codex", "directed_by": "Robert Vetter", "date": "2026-09-17",
            "scope": "Previously exposed development cases, not a holdout. No rating performance measured.",
            "review_status": "pending_human_review", "results": results}


def money(value):
    return "unresolved" if value is None else f"{value / 1e6:,.3f}"


def render(report):
    lines = ["Accounting evidence development review", "OpenAI Codex, directed by Robert Vetter, 2026-09-17",
             "Verified scope: local structured facts and numeric filing matches; accounting judgements pending human review.",
             report["scope"], "Values below in USD millions. A passed check is mechanical, not expert approval."]
    for result in report["results"]:
        lines.extend(["", f"{result['case']['slug']} | as of {report['as_of']} | {result['status']}"])
        if result["status"] != "completed":
            lines.append(result["reason"])
            continue
        lines.append("Metric | Legacy | Proposed | Check | Evidence / outstanding review")
        records = {r["id"]: r for r in result["records"]}
        for check in result["rows"]:
            refs = []
            for ident in check.get("evidence_ids", []):
                record = records[ident]
                locator = record["filing_locator"]
                location = (f"{locator['source']['path']}:{locator['matches'][0]['line']}"
                            if locator["status"] == "matched_inline_fact" else locator["status"])
                refs.append(f"{record['tag']}={money(record['val'])}; public {record['filed']}; {record['accn']}; {location}")
            lines.append(f"{check['metric']} | {money(check['legacy']['value'])} | {money(check['value'])} | {check['status']} | {check['reason']}")
            lines.append(f"  period {check.get('start') or 'instant'} to {check['end']}; " + ("; ".join(refs) or "no eligible source"))
        lines.append("Coverage: " + json.dumps(result["coverage"], sort_keys=True))
        for issue in result.get("source_issues", []):
            lines.append(f"Unavailable supplemental source: {issue['path']}: {issue['reason']}")
    lines.extend(["", "Review next: gross interest definitions; borrowing/finance-lease inclusion; missing sources.",
                  "No total adjusted debt, RCF, full TTM or final rating is asserted."])
    return "\n".join(lines) + "\n"


def save_report(report, destination, root=ROOT):
    base = (root / "evaluation/runs").resolve()
    destination = Path(destination).resolve()
    if destination.parent != base or not destination.name.startswith("accounting-development-"):
        raise ValueError("Output must be a fresh accounting-development-* directory directly under evaluation/runs.")
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    text = render(report)
    destination.mkdir(exist_ok=False)
    (destination / "evidence.json").write_text(payload)
    (destination / "review.txt").write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Fresh evaluation/runs/accounting-development-* directory")
    args = parser.parse_args()
    report = build_report()
    print(render(report), end="")
    if args.out:
        save_report(report, args.out)
    return 0 if all(r["status"] == "completed" for r in report["results"]) else 1


if __name__ == "__main__":
    sys.exit(main())
