"""
Experiment 09: score GPT-5.1's answers against the Experiment 08 baselines (README.md section 9).

Written 2026-09-28 by Claude (Opus 5.5), directed by Robert Vetter, while the forecasts of run R3 were
running and before any forecast result was read. Reuses Experiment 08's metric, bootstrap and
direction functions so both experiments measure the same way.

Reads runs/<run_id>/: manifest.json, ledger.jsonl, responses/, bodies/; and Experiment 08's
predictions.json (experiment_09_window). Writes runs/<run_id>/results/{results.json, tables.md}.
    python3 experiments/09-gpt51-next-quarter/score.py R3
"""
import json
import os
import re
import sys
from decimal import Decimal

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experiments", "08-next-quarter-baselines"))
import fit_models as F  # noqa: E402
import supplement as S  # noqa: E402
import run as R  # noqa: E402

E08 = os.path.join(ROOT, "experiments", "08-next-quarter-baselines", "runs", "R1-2026-09-27", "predictions.json")
BASE = ["M0", "M1", "M2", "M3", "M4"]


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_verified(quote, text):
    pieces = [p for p in re.split(r"\.\.\.|…", quote) if len(p.strip()) >= 12]
    if not pieces:
        return None
    return all(norm(p) in text for p in pieces)


def segments_found(quote, text):
    """Post-hoc, added 2026-09-28 after reading the interim answers: quotes are often stitched from
    several places or retype table cells. Split at ellipses, line breaks and sentence ends; the
    share of pieces of at least 20 characters found verbatim (after whitespace and case)."""
    pieces = [p for p in re.split(r"\.\.\.|…|\n|(?<=[.;:])\s+", quote) if len(p.strip()) >= 20]
    if not pieces:
        return None
    return sum(1 for p in pieces if norm(p) in text) / len(pieces)


def load(run_dir):
    man = json.load(open(os.path.join(run_dir, "manifest.json")))
    ans = R.answers(run_dir, "forecast")
    base = {(r["company"], r["t"]): r for r in json.load(open(E08))["experiment_09_window"]}
    rows, missing = [], []
    for q in man["requests"]:
        if q["kind"] != "forecast":
            continue
        a = ans.get(q["request_id"])
        if a is None:
            missing.append(q["request_id"])
            continue
        b = base[(q["company"], q["t"])]
        assert b["target"] == q["target"]
        body = json.load(open(os.path.join(run_dir, "bodies", f"{q['request_id']}.json")))
        text = norm(body["messages"][1]["content"])
        checks = [quote_verified(x["quote"], text) for x in a["reasons"]]
        seg = [segments_found(x["quote"], text) for x in a["reasons"]]
        seg = [v for v in seg if v is not None]
        rows.append({"request_id": q["request_id"], "company": q["company"], "t": q["t"], "arm": q["arm"],
                     "target": q["target"], "gold": q["gold"], "rating_t": q["rating_t"], "answer": a,
                     "GPT": [a["p_unchanged"], a["p_down"], a["p_up"]],
                     **{m: b[m] for m in BASE},
                     "quotes": {"n": len(checks), "verified": sum(1 for c in checks if c),
                                "not_found": sum(1 for c in checks if c is False),
                                "segment_shares": seg}})
    return man, rows, missing


def block(rows, names):
    preds = {n: np.array([r[n] for r in rows]) for n in names}
    out = {"metrics": [F.metrics(rows, preds[n], n) for n in names]}
    if sum(r["target"] != 0 for r in rows) and len({r["company"] for r in rows}) > 1:
        out["pr_bootstrap"] = F.bootstrap(rows, preds, [n for n in names if n != "M0"],
                                          [("GPT", "M1"), ("GPT", "M3"), ("GPT", "M2")])
        y = F.y_of(rows)
        if (y != 0).sum() >= 2:
            out["direction"] = {"point": {n: S.direction(y, preds[n]) for n in names if n != "M0"},
                                **S.boot(rows, {n: preds[n] for n in names if n != "M0"},
                                         lambda yy, P: S.direction(yy, P) if (yy != 0).any() else None,
                                         [("GPT", "M1"), ("GPT", "M3")])}
        if (y == 1).sum() >= 2:
            stat = lambda yy, P: S.ap((yy == 1).astype(int), P[:, 1])
            out["downgrades"] = {"events": int((y == 1).sum()), "point": {n: stat(y, preds[n]) for n in names},
                                 **S.boot(rows, {n: preds[n] for n in names}, stat, [("GPT", "M1"), ("GPT", "M3")])}
    return out


def calibration_fifths(rows):
    s = np.array([r["GPT"][1] + r["GPT"][2] for r in rows])
    ch = np.array([r["target"] != 0 for r in rows])
    order = np.argsort(s)
    return [{"n": len(p), "mean_predicted": float(s[p].mean()), "observed": float(ch[p].mean())}
            for p in np.array_split(order, 5)]


def spending(run_dir):
    led = R.Ledger(os.path.join(run_dir, "ledger.jsonl"))
    st = led.state()
    rec = [e for e in led.events() if e.get("event") == "reconcile"]
    return {"committed_usd": str(st["committed"]), "unresolved_usd": str(st["unresolved"]),
            "responses_charged": len(rec),
            "prompt_tokens": sum(e.get("prompt_tokens") or 0 for e in rec),
            "cached_tokens": sum(e.get("cached_tokens") or 0 for e in rec),
            "completion_tokens": sum(e.get("completion_tokens") or 0 for e in rec),
            "reasoning_tokens": sum(e.get("reasoning_tokens") or 0 for e in rec),
            "tiers": sorted({e.get("service_tier") for e in rec}), "models": sorted({e.get("model") for e in rec}),
            "failed_not_billed": sum(1 for e in led.events() if e.get("event") == "failed_not_billed"),
            "invalid": sum(1 for e in led.events() if e.get("event") == "invalid"),
            "halts": list(st["halts"])}


def main(run_id):
    run_dir = os.path.join(HERE, "runs", run_id)
    man, rows, missing = load(run_dir)
    names = ["GPT"] + BASE
    doc = [r for r in rows if r["arm"] == "documents"]
    hist = [r for r in rows if r["arm"] == "history_only"]
    res = {"missing": missing, "spending": spending(run_dir),
           "primary_documents": block(doc, names),
           "documents_without_gold": block([r for r in doc if not r["gold"]], names),
           "documents_by_date": {t: block([r for r in doc if r["t"] == t], names) for t in ("2024-12-31", "2025-03-31")},
           "history_only": {"metrics": [F.metrics(hist, np.array([r[n] for r in hist]), n) for n in names]},
           "calibration_fifths_GPT": calibration_fifths(doc),
           "quotes": {"reasons": sum(r["quotes"]["n"] for r in doc), "verified": sum(r["quotes"]["verified"] for r in doc),
                      "not_found": sum(r["quotes"]["not_found"] for r in doc),
                      "posthoc_segments_mean_share_found": float(np.mean([v for r in doc for v in r["quotes"]["segment_shares"]])),
                      "posthoc_reasons_with_no_segment_found": sum(1 for r in doc for v in r["quotes"]["segment_shares"] if v == 0)},
           "insufficient_information": sum(1 for r in rows if r["answer"]["insufficient_information"]),
           "changes": [{"company": r["company"], "t": r["t"], "arm": r["arm"], "rating_t": r["rating_t"],
                        "move": "down" if r["target"] == 1 else "up",
                        "GPT": r["GPT"], "M1": r["M1"], "M3": r["M3"],
                        "rank_GPT": 1 + sum(1 for x in (doc if r["arm"] == "documents" else hist)
                                            if x["GPT"][1] + x["GPT"][2] > r["GPT"][1] + r["GPT"][2]),
                        "reasons": r["answer"]["reasons"]} for r in rows if r["target"]],
           "distribution_GPT": {"p_change_min": min(r["GPT"][1] + r["GPT"][2] for r in doc),
                                "p_change_median": float(np.median([r["GPT"][1] + r["GPT"][2] for r in doc])),
                                "p_change_max": max(r["GPT"][1] + r["GPT"][2] for r in doc),
                                "most_likely_not_unchanged": sum(1 for r in doc if max(r["GPT"]) != r["GPT"][0])}}
    out = os.path.join(run_dir, "results")
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1, default=str)
    open(os.path.join(out, "tables.md"), "w").write(tables(res))
    print(tables(res))


def f3(x):
    return "" if x is None else f"{x:.3f}"


def pct(x):
    return "" if x is None else f"{100 * x:.1f}%"


def tables(res):
    L = []
    w = L.append
    sp = res["spending"]
    w(f"Spending: ${Decimal(sp['committed_usd']):.4f} committed, {sp['responses_charged']} responses charged, "
      f"{sp['prompt_tokens']:,} prompt tokens ({sp['cached_tokens']:,} cached), {sp['completion_tokens']:,} completion "
      f"({sp['reasoning_tokens']:,} reasoning); tiers {sp['tiers']}; models {sp['models']}; "
      f"not billed {sp['failed_not_billed']}; invalid {sp['invalid']}; halts {sp['halts']}. Missing answers: {len(res['missing'])}.\n")
    b = res["primary_documents"]
    w("## Primary: documents arm\n")
    w(F.metric_table(b["metrics"]))
    if "pr_bootstrap" in b:
        w("\n| Difference, PR area | 95% interval | Share above zero |\n|---|---|---|")
        for k, v in b["pr_bootstrap"]["pr_auc_difference"].items():
            w(f"| {k} | {f3(v['interval'][0])} to {f3(v['interval'][1])} | {pct(v['share_above_zero'])} |")
    if "direction" in b:
        w("\n| Direction | Point | 95% interval |\n|---|---|---|")
        for n, p in b["direction"]["point"].items():
            lo, hi = b["direction"]["intervals"][n]
            w(f"| {n} | {pct(p)} | {pct(lo)} to {pct(hi)} |")
    if "downgrades" in b:
        d = b["downgrades"]
        w(f"\n| Downgrades ranked on their own ({d['events']}) | PR area | 95% interval |\n|---|---|---|")
        for n, p in d["point"].items():
            lo, hi = d["intervals"][n]
            w(f"| {n} | {f3(p)} | {f3(lo)} to {f3(hi)} |")
        for k, v in d["differences"].items():
            w(f"| {k} (difference) | | {f3(v['interval'][0])} to {f3(v['interval'][1])}, above zero {pct(v['share_above_zero'])} |")
    w("\n## Documents arm without gold\n")
    w(F.metric_table(res["documents_without_gold"]["metrics"]))
    for t, bb in res["documents_by_date"].items():
        w(f"\n## Documents arm, prediction date {t}\n")
        w(F.metric_table(bb["metrics"]))
    w("\n## History-only arm\n")
    w(F.metric_table(res["history_only"]["metrics"]))
    w("\n## Calibration of GPT-5.1's P(change), documents arm, by fifth\n\n| Fifth | n | Predicted | Observed |\n|---|---|---|---|")
    for i, c in enumerate(res["calibration_fifths_GPT"], 1):
        w(f"| {i} | {c['n']} | {pct(c['mean_predicted'])} | {pct(c['observed'])} |")
    dg = res["distribution_GPT"]
    w(f"\nP(change) from GPT-5.1: min {pct(dg['p_change_min'])}, median {pct(dg['p_change_median'])}, max {pct(dg['p_change_max'])}; "
      f"rows where its most likely outcome is a change: {dg['most_likely_not_unchanged']}.")
    q = res["quotes"]
    w(f"\nQuotes: {q['reasons']} reasons, {q['verified']} verified in the supplied text, {q['not_found']} not found. "
      f"Post-hoc piece check: mean share of quote pieces found {pct(q['posthoc_segments_mean_share_found'])}; "
      f"reasons with no piece found {q['posthoc_reasons_with_no_segment_found']}. "
      f"Answers flagged insufficient information: {res['insufficient_information']}.")
    w("\n## The changes\n\n| Company | t | Arm | Rating | Move | GPT down / up | GPT rank of P(change) | M1 down / up | M3 down / up |\n|---|---|---|---|---|---|---|---|---|")
    for c in res["changes"]:
        w(f"| {c['company']} | {c['t']} | {c['arm']} | {c['rating_t']} | {c['move']} | {pct(c['GPT'][1])} / {pct(c['GPT'][2])} | "
          f"{c['rank_GPT']} | {pct(c['M1'][1])} / {pct(c['M1'][2])} | {pct(c['M3'][1])} / {pct(c['M3'][2])} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main(sys.argv[1])
