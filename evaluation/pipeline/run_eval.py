"""
The evaluation runner: observations in, predictions and scores out.

Written by Claude (Opus 5), directed by Robert Vetter. Step 9 of the pipeline
(evaluation/README.md).

For each selected observation (company, quarter end t):
  1. assemble the input documents from the folder: the latest annual report before t plus the
     latest quarterly report between it and t, downloading from EDGAR via the manifest URLs
     if not on disk yet (8-Ks are deliberately excluded in v1: they are where downgrade
     announcements live)
  2. HTML -> line-preserving text, then redact rating disclosures (system/redact.py); the
     removed lines are stored with the run so redaction is auditable
  3. one raw API call (system/analyst.py, no tools array). Task B (default) includes the
     rating path up to the PREVIOUS quarter end - exactly the persistence baseline's
     information set; Task A omits it
  4. the deterministic scorecard (system/scorecard.py) turns the extracted inputs into the
     scorecard-indicated outcome; the model's free-form direct_rating is recorded alongside
  5. score both against the label and against persistence

Every run writes a self-contained directory under evaluation/runs/<tag>/ (gitignored):
run_meta.json with the frozen configuration, one JSON per observation with the full audit
trail (documents used, redacted lines, extracted figures, derived metrics, scorecard rows,
predictions, token usage), and summary.json plus a printed table.

Cost: one observation is one call with roughly 100-250k input tokens. Mind the bill before
running with a large --limit; --dry-run assembles everything and prints token estimates
without calling the API.

Examples:
    python3 evaluation/pipeline/run_eval.py --dry-run --company kohl-s --date 2022-12-31
    python3 evaluation/pipeline/run_eval.py --changed-only --limit 5 --tag smoke1
    python3 evaluation/pipeline/run_eval.py --task A --company walmart --date 2025-06-30
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
import redact                     # noqa: E402
import scorecard                  # noqa: E402

COMPANIES = os.path.join(ROOT, "evaluation", "companies")
RUNS = os.path.join(ROOT, "evaluation", "runs")
UA = {"User-Agent": "Robert Vetter robert@certus-ai.com"}
ANNUAL = ("10-K", "20-F", "40-F")
QUARTERLY = ("10-Q",)
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]


def notches(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def to_text(raw):
    """HTML to text, preserving line and cell structure for the redactor."""
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<td[^>]*>", "\t", raw, flags=re.I)
    raw = re.sub(r"<(tr|p|div|br|h[1-6]|li|table)[^>]*>", "\n", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[  ]+", " ", raw)
    return "\n".join(l.strip() for l in raw.split("\n") if l.strip())


def ensure_doc(slug, cik, filing):
    fdir = os.path.join(COMPANIES, slug, "filings")
    acc = filing["accessionNumber"].replace("-", "")
    fn = f"{filing['filingDate']}_{filing['form'].replace('/', '')}_{acc}.htm"
    path = os.path.join(fdir, fn)
    if not os.path.exists(path):
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{filing['primaryDocument']}"
        time.sleep(0.25)
        open(path, "wb").write(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=60).read())
    return path, fn


def pick_documents(obs, manifest):
    """Latest annual before t, plus the latest 10-Q filed after it and before t."""
    docs = [f for f in manifest if f["filingDate"] <= obs["date"]]
    annual = next((f for f in docs if f["form"] in ANNUAL), None)
    if not annual:
        return None, None
    quarterly = next((f for f in docs
                      if f["form"] in QUARTERLY and f["filingDate"] > annual["filingDate"]), None)
    return annual, quarterly


def select_observations(args):
    picked = []
    for slug in sorted(os.listdir(COMPANIES)):
        if args.company and slug not in args.company:
            continue
        p = os.path.join(COMPANIES, slug, "observations.json")
        if not os.path.exists(p):
            continue
        blob = json.load(open(p))
        if blob.get("scope") != "in" and not args.company:
            continue
        for o in blob["observations"]:
            if args.date and o["date"] != args.date:
                continue
            if args.changed_only and not o["changed"]:
                continue
            if not o["has_recent_annual"]:
                continue
            picked.append((slug, blob["cik"], o))
    if args.limit:
        picked = picked[:args.limit]
    return picked


def run_one(slug, cik, obs, args, run_dir):
    manifest = json.load(open(os.path.join(COMPANIES, slug, "filings", "manifest.json")))["filings"]
    annual, quarterly = pick_documents(obs, manifest)
    if not annual:
        return {"slug": slug, "date": obs["date"], "skipped": "no annual report before t"}
    documents, doc_meta, removed_all = [], [], {}
    for f in [annual] + ([quarterly] if quarterly else []):
        path, fn = ensure_doc(slug, cik, f)
        text = to_text(open(path, "rb").read().decode("utf-8", "ignore"))
        clean, removed = redact.redact(text)
        documents.append((f"{f['form']} filed {f['filingDate']}", clean))
        doc_meta.append({"form": f["form"], "filingDate": f["filingDate"], "file": fn,
                         "chars": len(clean), "redacted_lines": len(removed)})
        removed_all[fn] = removed
    est_tokens = sum(len(t) for _, t in documents) // 4

    result = {"slug": slug, "date": obs["date"], "label": obs["label"],
              "persistence": obs["persistence"], "changed": obs["changed"],
              "task": args.task, "documents": doc_meta, "est_input_tokens": est_tokens}
    if args.dry_run:
        return result

    import analyst
    path_arg = None
    if args.task == "B":
        # information set of the persistence baseline: events strictly before the
        # observation quarter (rating_path entries carry level as 4th element; drop it)
        prev_q = obs["persistence"]
        cutoff = obs["date"][:8]  # events in the observation quarter's last month still count?
        # No: use everything up to the previous quarter end = anything not in this quarter.
        qstart = {"Q1": "-01-01", "Q2": "-04-01", "Q3": "-07-01", "Q4": "-10-01"}[obs["quarter"]]
        cutoff = obs["date"][:4] + qstart
        path_arg = [(e[0], e[1], e[2]) for e in obs["rating_path"] if e[0] < cutoff]
        if prev_q is None:
            path_arg = None
    t0 = time.time()
    parsed, meta = analyst.analyze(documents, rating_path=path_arg,
                                   model=args.model, effort=args.effort)
    meta["seconds"] = round(time.time() - t0, 1)

    fig = dict(parsed["figures_usd_m"])
    fig["qualitative"] = parsed["qualitative"]
    fig["label"] = f"{slug} @ {obs['date']} ({parsed['fiscal_year_label']})"
    derived = scorecard.derive(fig)
    rows = scorecard.build(fig)
    agg = scorecard.aggregate(rows)
    sc_pred = scorecard.outcome(agg)

    result.update({
        "extraction": parsed, "api": meta,
        "derived_metrics": {k: round(v, 3) for k, v in derived.items()},
        "scorecard_rows": [(n, w, round(s, 2)) for n, w, s in rows],
        "scorecard_aggregate": round(agg, 3),
        "pred_scorecard": sc_pred, "pred_direct": parsed["direct_rating"],
        "err_scorecard": abs(notches(sc_pred) - notches(obs["label"])) if notches(obs["label"]) is not None else None,
        "err_direct": abs(notches(parsed["direct_rating"]) - notches(obs["label"])) if notches(obs["label"]) is not None else None,
        "err_persistence": (abs(notches(obs["persistence"]) - notches(obs["label"]))
                            if obs["persistence"] and notches(obs["label"]) is not None else None),
    })
    json.dump(removed_all, open(os.path.join(run_dir, f"{slug}_{obs['date']}_redacted.json"), "w"),
              indent=0, ensure_ascii=False)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", action="append", help="slug, repeatable; default all in-scope")
    ap.add_argument("--date")
    ap.add_argument("--changed-only", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--task", choices=["A", "B"], default="B")
    ap.add_argument("--model", default="claude-opus-5")
    ap.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--tag", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    picked = select_observations(args)
    if not picked:
        print("no observations match"); return
    tag = args.tag or ("dryrun" if args.dry_run else "run")
    run_dir = os.path.join(RUNS, f"{tag}")
    os.makedirs(run_dir, exist_ok=True)
    json.dump({"task": args.task, "model": args.model, "effort": args.effort,
               "dry_run": args.dry_run, "n_selected": len(picked),
               "selection": {"company": args.company, "date": args.date,
                             "changed_only": args.changed_only, "limit": args.limit},
               "note": "no tools array; documents redacted; Task B path ends at previous quarter"},
              open(os.path.join(run_dir, "run_meta.json"), "w"), indent=1)

    results = []
    for slug, cik, obs in picked:
        try:
            r = run_one(slug, cik, obs, args, run_dir)
        except Exception as exc:
            r = {"slug": slug, "date": obs["date"], "error": f"{type(exc).__name__}: {exc}"}
        results.append(r)
        json.dump(results, open(os.path.join(run_dir, "results.json"), "w"),
                  indent=1, ensure_ascii=False)
        if "error" in r:
            print(f"  {slug} {obs['date']}  ERROR {r['error'][:90]}")
        elif args.dry_run:
            print(f"  {slug:<26} {obs['date']}  label {obs['label']:<5} "
                  f"docs {len(r['documents'])}  ~{r['est_input_tokens']:,} tokens  "
                  f"redacted {sum(d['redacted_lines'] for d in r['documents'])} lines")
        else:
            print(f"  {slug:<26} {obs['date']}  label {r['label']:<5} "
                  f"scorecard {r['pred_scorecard']:<5} (err {r['err_scorecard']})  "
                  f"direct {r['pred_direct']:<5} (err {r['err_direct']})  "
                  f"persistence err {r['err_persistence']}  [{r['api']['seconds']}s]")

    done = [r for r in results if "pred_scorecard" in r]
    if done:
        def mae(key):
            vals = [r[key] for r in done if r.get(key) is not None]
            return round(sum(vals) / len(vals), 2) if vals else None
        summary = {"n": len(done), "mae_scorecard": mae("err_scorecard"),
                   "mae_direct": mae("err_direct"), "mae_persistence": mae("err_persistence")}
        json.dump(summary, open(os.path.join(run_dir, "summary.json"), "w"), indent=1)
        print(f"\nn={summary['n']}  MAE scorecard {summary['mae_scorecard']}  "
              f"direct {summary['mae_direct']}  persistence {summary['mae_persistence']}")
    print(f"run directory: {run_dir}")


if __name__ == "__main__":
    main()
