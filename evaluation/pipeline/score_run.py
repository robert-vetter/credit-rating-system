"""
Scores a finished evaluation run: the metrics the experiment plan actually calls for.

Written by Claude (Opus 5), directed by Robert Vetter. Reads evaluation/runs/<tag>/results.json
(written by run_eval.py), prints a report and writes scores.json next to it.

Why a separate script: the runner records raw outcomes; what they mean is a scoring question
with its own definitions, and those definitions must be reusable across runs and models. The
headline constraint from docs/experiment-plan.md applies throughout: ratings are inert, so
accuracy alone flatters any system - the persistence baseline gets every unchanged quarter
right for free. Everything here is therefore reported per subset:

  all observations     MAE, exact-hit and within-1-notch rates, Spearman - context numbers
  changed subset       the primary experiment: MAE lift over persistence (persistence is
                       always wrong here by construction of "changed"), and direction
                       accuracy: did the prediction move from the previous rating the same
                       way the label did
  unchanged subset     false-alarm rate: how often the system predicts a change that did not
                       happen (persistence scores 0 here by definition)
  change detection     treating "prediction != previous rating" as an alarm: recall on
                       changed, false-alarm rate on unchanged

Uncertainty: paired bootstrap (resampling observations, 10,000 draws, fixed seed 17) on the
per-observation notch-error difference system-minus-persistence; reports the 95% interval and
the fraction of resamples in which the system beats persistence. With small n the interval
will be wide - that is the honest answer, not a defect.

Both prediction channels are scored: pred_scorecard (extraction + deterministic scorecard)
and pred_direct (the model's free-form rating).

Run: python3 evaluation/pipeline/score_run.py evaluation/runs/<tag>
"""
import json
import os
import random
import sys

SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return round(num / den, 3) if den else None


def mae(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 3) if vals else None


def score_channel(done, pred_key):
    """All metrics for one prediction channel ('pred_scorecard' or 'pred_direct')."""
    rows = []
    for r in done:
        lab, prev, pred = notch(r["label"]), notch(r.get("persistence")), notch(r.get(pred_key))
        if lab is None or pred is None:
            continue
        rows.append({"changed": r.get("changed"), "lab": lab, "prev": prev, "pred": pred,
                     "err": abs(pred - lab),
                     "err_pers": abs(prev - lab) if prev is not None else None})
    out = {"n": len(rows), "mae": mae([r["err"] for r in rows]),
           "mae_persistence": mae([r["err_pers"] for r in rows]),
           "exact_rate": round(sum(r["err"] == 0 for r in rows) / len(rows), 3) if rows else None,
           "within_1": round(sum(r["err"] <= 1 for r in rows) / len(rows), 3) if rows else None,
           "spearman_vs_label": spearman([r["pred"] for r in rows], [r["lab"] for r in rows])}

    ch = [r for r in rows if r["changed"] and r["prev"] is not None]
    if ch:
        dir_ok = sum(1 for r in ch if r["pred"] != r["prev"]
                     and (r["pred"] - r["prev"]) * (r["lab"] - r["prev"]) > 0)
        out["changed"] = {
            "n": len(ch), "mae": mae([r["err"] for r in ch]),
            "mae_persistence": mae([r["err_pers"] for r in ch]),
            "lift_notches": round(mae([r["err_pers"] for r in ch]) - mae([r["err"] for r in ch]), 3),
            "moved_at_all_rate": round(sum(r["pred"] != r["prev"] for r in ch) / len(ch), 3),
            "direction_correct_rate": round(dir_ok / len(ch), 3),
        }
    un = [r for r in rows if r["changed"] is False and r["prev"] is not None]
    if un:
        out["unchanged"] = {
            "n": len(un), "mae": mae([r["err"] for r in un]),
            "false_alarm_rate": round(sum(r["pred"] != r["prev"] for r in un) / len(un), 3),
        }

    paired = [r for r in rows if r["err_pers"] is not None]
    if len(paired) >= 4:
        rng = random.Random(17)
        deltas = []
        for _ in range(10_000):
            s = [paired[rng.randrange(len(paired))] for _ in paired]
            deltas.append(sum(r["err"] for r in s) / len(s) - sum(r["err_pers"] for r in s) / len(s))
        deltas.sort()
        out["bootstrap_err_minus_persistence"] = {
            "n_paired": len(paired), "mean": round(sum(deltas) / len(deltas), 3),
            "ci95": [round(deltas[249], 3), round(deltas[9749], 3)],
            "p_system_beats_persistence": round(sum(d < 0 for d in deltas) / len(deltas), 3),
            "seed": 17,
        }
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__.split("Run:")[1].strip()); return
    run_dir = sys.argv[1].rstrip("/")
    results = json.load(open(os.path.join(run_dir, "results.json")))
    done = [r for r in results if "pred_scorecard" in r]
    skipped = [r for r in results if "pred_scorecard" not in r]
    scores = {"run": os.path.basename(run_dir), "n_results": len(results),
              "n_scored": len(done), "n_skipped_or_error": len(skipped),
              "scorecard": score_channel(done, "pred_scorecard"),
              "direct": score_channel(done, "pred_direct")}
    json.dump(scores, open(os.path.join(run_dir, "scores.json"), "w"), indent=1)
    print(json.dumps(scores, indent=1))
    print(f"\ngeschrieben: {run_dir}/scores.json")


if __name__ == "__main__":
    main()
