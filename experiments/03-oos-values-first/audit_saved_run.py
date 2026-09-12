"""Offline review of Experiment 03, by Codex, directed by Robert, 2026-09-12.

Inputs: saved batch requests/audits/outputs/results, cached primary filings, scorecard code.
Output: runs/offline-review-2026-09-12/audit.json. Never imports a model client or downloads.
Replays document redaction, checks request boundaries, joins reruns with original probes,
and reports recorded and corrected arithmetic separately, always against persistence.
This is an audit of saved evidence, not certification of label validity or absent memory.

Run from the repository root: python3 experiments/03-oos-values-first/audit_saved_run.py
"""
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
import math
from pathlib import Path
import random
import re
import sys
from datetime import date

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(ROOT / "system"), str(ROOT / "evaluation/pipeline")]
import redact
import run_eval
import scorecard

BATCHES = ("msgbatch_01EwnHhsKjahuwhmL8S5h2Sx", "msgbatch_01QsBQnMF1itHj1Ysz3jguKZ")
OUT = HERE / "runs/offline-review-2026-09-12/audit.json"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(hits, n):
    if not n:
        return None
    z = 1.959963984540054
    p = hits / n
    center = (p + z*z/(2*n)) / (1+z*z/n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    return [round(center-half, 4), round(center+half, 4)]


def metrics(rows, channel):
    if not rows:
        return {"n": 0}
    errors = [abs(run_eval.notches(r[channel])-run_eval.notches(r["label"])) for r in rows]
    diffs = [e-abs(run_eval.notches(r["persistence"])-run_eval.notches(r["label"]))
             for e, r in zip(errors, rows)]
    rng = random.Random(20260912)
    means = sorted(sum(rng.choices(diffs, k=len(diffs)))/len(diffs) for _ in range(10000))
    return {"n": len(rows), "exact": errors.count(0), "within_one": sum(e <= 1 for e in errors),
            "mae": round(sum(errors)/len(errors), 6), "exact_wilson95": wilson(errors.count(0), len(rows)),
            "mae_minus_persistence_bootstrap95": [means[249], means[9749]],
            "direction_correct": sum((run_eval.notches(r[channel])-run_eval.notches(r["persistence"])) *
                                     (run_eval.notches(r["label"])-run_eval.notches(r["persistence"])) > 0
                                     for r in rows if r["changed"]),
            "false_alarms": sum(r[channel] != r["persistence"] for r in rows if not r["changed"])}


def tables(rows):
    return {subset: {ch: metrics(rs, ch) for ch in ("recorded_scorecard", "corrected_scorecard", "direct", "persistence")}
            for subset, rs in (("all", rows), ("changed", [r for r in rows if r["changed"]]),
                               ("unchanged", [r for r in rows if not r["changed"]]))}


def check_request(params, boundary, as_of):
    checks = {"no_tools": "tools" not in params,
              "no_cache_control": '"cache_control"' not in json.dumps(params),
              "model": params["model"] == "claude-opus-4-6"}
    body = params["messages"][0]["content"]
    if isinstance(body, list):
        docs = re.findall(r'<document name="(.*?) filed (\d{4}-\d{2}-\d{2})">', body[0]["text"])
        checks["document_dates"] = bool(docs) and all(boundary < d <= as_of for _, d in docs)
        checks["document_forms"] = bool(docs) and all(f in ("10-K", "10-Q") for f, _ in docs)
    return checks


def audit():
    checks, hashes, probes, observations, successful = [], {}, {}, {}, {}
    attempts, recorded_cost = 0, 0
    for bid in BATCHES:
        folder = HERE / "runs" / bid
        for name in ("audit.json", "requests_raw.json", "raw_outputs.json", "results.json"):
            hashes[str((folder/name).relative_to(ROOT))] = sha(folder/name)
        saved, requests, outputs, result = (read(folder/name) for name in
                                          ("audit.json", "requests_raw.json", "raw_outputs.json", "results.json"))
        recorded_cost += result["cost_usd_batch"]
        requests = {r["custom_id"]: r["params"] for r in requests}
        attempts += sum(k.startswith("vf-") for k in requests)
        probes.update({k[6:]: {"batch": bid, "output": v} for k, v in outputs.items() if k.startswith("probe-")})
        for key, params in requests.items():
            checks.append({"batch": bid, "request": key,
                           "checks": check_request(params, saved["boundary_B"], saved["as_of"])})
        for item in saved["observations"]:
            if item.get("skipped"):
                continue
            obsid, slug = item["id"], item["slug"]
            doc_text = ""
            sources = []
            manifest = read(ROOT / "evaluation/companies" / slug / "filings/manifest.json")["filings"]
            for doc in item["documents"]:
                path = ROOT / "evaluation/companies" / slug / "filings" / doc["file"]
                clean, removed = redact.redact(run_eval.to_text(path.read_bytes().decode("utf-8", "ignore")))
                doc_text += f'<document name="{doc["form"]} filed {doc["filed"]}">\n{clean}\n</document>\n'
                match = [f for f in manifest if f["accessionNumber"].replace("-", "") in doc["file"]]
                sources.append({**doc, "source_sha256": sha(path), "removed_lines_replayed": removed,
                                "manifest_match": len(match) == 1 and match[0]["form"] == doc["form"]
                                and match[0]["filingDate"] == doc["filed"],
                                "primary_document": match[0]["primaryDocument"] if len(match) == 1 else None})
            body = requests["vf-"+obsid]["messages"][0]["content"]
            history = body[1]["text"]
            events = re.findall(r'^  (\d{4}-\d{2}-\d{2})  ', history, flags=re.M)
            check = {"documents_replay_exactly": doc_text == body[0]["text"],
                     "primary_manifest_matches": all(s["manifest_match"] for s in sources),
                     "rating_event_dates": all(d <= saved["history_end"] for d in events),
                     "label_filing_dates": saved["boundary_B"] < item["label_evidence"]["filed"] <= saved["as_of"]}
            checks.append({"batch": bid, "observation": obsid, "checks": check})
            observations[obsid] = {"slug": slug, "documents": sources,
                "label_filing_age_days": (date.fromisoformat(saved["as_of"])-date.fromisoformat(item["label_evidence"]["filed"])).days,
                "quarterly_rows": item.get("pack_quarterly_rows"),
                "pack_fact_provenance_saved": "pack_provenance" in item,
                "post_label_bankruptcy_text": bool(re.search(r'Chapter 11|bankruptcy', doc_text, re.I))}
        for row in result["results"]:
            v = outputs["vf-"+row["id"]]
            figures = {**v["figures_usd_m"], "qualitative": v["qualitative"]}
            # Historical collector rounded before the lookup; reproduce its number
            # separately and use full precision for corrected arithmetic.
            new_aggregate = scorecard.aggregate(scorecard.build(figures))
            successful[row["id"]] = {"id": row["id"], "slug": row["slug"], "batch": bid,
                "label": row["label"], "persistence": row["persistence"], "changed": row["changed"],
                "recorded_scorecard": row["scorecard"]["pred"],
                "recorded_aggregate": row["scorecard"]["aggregate"],
                "corrected_scorecard": scorecard.outcome(new_aggregate), "corrected_aggregate": new_aggregate,
                "direct": row["direct"]["pred"]}
    rows = list(sorted(successful.values(), key=lambda r: r["id"]))
    for row in rows:
        row["probe"] = probes.get(row["id"])
    failures = [c for c in checks if not all(c["checks"].values())]
    packages = {}
    for package in ("anthropic", "numpy", "scikit-learn"):
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            packages[package] = None
    return {"review_date": "2026-09-12", "model_calls": 0, "network_calls": 0,
        "review_environment": {"python": sys.version, "packages": packages,
                               "note": "Current review environment, not an original-run environment snapshot"},
        "source_sha256": hashes, "scorecard_sha256": sha(ROOT/"system/scorecard.py"),
        "mechanical_checks_pass": not failures, "checks": checks,
        "limitations": ["No certification of absent training memory or semantic rating leakage.",
                        "Saved history and peer facts lack per-field source provenance.",
                        "No independent August 29 label verification; Qurate label is stale and entity alignment needs review.",
                        "Seven successes selected by cost, failures, and selective reruns; intervals are descriptive.",
                        "Same-batch probe order is not verified. Prompt does not supply full methodology rubric."],
        "coverage": {"confirmed": 20, "scheduled_unique": len(observations), "vf_attempts": attempts,
                     "successful_unique": len(rows), "unsuccessful_vf_attempts": attempts-len(rows),
                     "unscored_scheduled": sorted(set(observations)-set(successful)),
                     "batch_cost_usd_saved": round(recorded_cost, 3)},
        "observations": observations, "rows": rows, "metrics": tables(rows),
        "without_qurate_sensitivity": tables([r for r in rows if r["id"] != "X14"])}


if __name__ == "__main__":
    report = audit()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({k: report[k] for k in ("mechanical_checks_pass", "coverage", "metrics", "without_qurate_sensitivity")}, indent=2))
    print(f"Saved {OUT}")
    if not report["mechanical_checks_pass"]:
        raise SystemExit(1)
