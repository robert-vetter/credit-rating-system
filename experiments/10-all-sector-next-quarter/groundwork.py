"""
Experiment 10 groundwork (free, no model call): the cross-sector rating-change table, the rating-only
and rating-history baselines refitted on all corporate issuers, frozen baseline predictions for the test
rows, and the candidate test cohort.

Written 2026-10-01 by Claude (Opus 5.5), directed by Robert Vetter (decision 3). Reads the all-sector
labels (data/all-sectors/moodys-quarterly-labels.json), the accepted mapping
(evaluation/all-sectors/proposed-mapping.json) and the gold set (excluded from fitting). Reuses the model
code of Experiment 08 (fit_models.py) so both experiments fit and score the same way.

Writes runs/groundwork/ (gitignored): base_rates.json, baselines.json, baseline_predictions_window.json,
cohort.json, tables.md. Refuses to overwrite.
    python3 experiments/10-all-sector-next-quarter/groundwork.py
"""
import collections
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "08-next-quarter-baselines"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "07-rating-change-base-rates"))
import fit_models as F  # noqa: E402
import run_study as E7  # noqa: E402

LABELS = os.path.join(ROOT, "data", "all-sectors", "moodys-quarterly-labels.json")
MAPPING = os.path.join(ROOT, "evaluation", "all-sectors", "proposed-mapping.json")
OUT = os.path.join(HERE, "runs", "groundwork")
GRID, QI = E7.GRID, E7.QI
TEST_DATES = ("2024-12-31", "2025-03-31")
NEXT = {"2024-12-31": "2025-03-31", "2025-03-31": "2025-06-30"}
SETS = {"M1": F.SETS["M1"], "M2": F.SETS["M2"]}


def records(labels):
    """Quarterly records per issuer in the Experiment 07 form."""
    out = collections.defaultdict(list)
    for oi, v in labels.items():
        prev_level = None
        for date, label, level, amb, persistence, changed in v["observations"]:
            if persistence is not None:
                a, b = E7.notch(persistence), E7.notch(label)
                out[oi].append({"company": oi, "date": date, "prev": persistence, "cur": label,
                                "changed": bool(changed), "delta": None if a is None or b is None else b - a,
                                "level_switch": prev_level is not None and level != prev_level, "level": level})
            prev_level = level
    return out


def base_rates(recs):
    Q = [q for qs in recs.values() for q in qs]
    by_cat = collections.defaultdict(list)
    for q in Q:
        by_cat[E7.category(q["prev"])].append(q)
    rows = []
    for c in E7.CATS:
        qs = by_cat.get(c, [])
        if qs:
            rows.append({"category": c, "n": len(qs), "change": sum(q["changed"] for q in qs) / len(qs),
                         "down": sum(1 for q in qs if q["changed"] and (q["delta"] or 0) > 0) / len(qs),
                         "up": sum(1 for q in qs if q["changed"] and (q["delta"] or 0) < 0) / len(qs)})
    ig = [q for q in Q if E7.investment_grade(q["prev"])]
    sg = [q for q in Q if E7.investment_grade(q["prev"]) is False]
    by_year = collections.defaultdict(list)
    for q in Q:
        by_year[q["date"][:4]].append(q)
    return {"quarterly_records": len(Q), "issuers": len(recs), "overall": sum(q["changed"] for q in Q) / len(Q),
            "by_category": rows,
            "investment_grade": sum(q["changed"] for q in ig) / len(ig), "speculative_grade": sum(q["changed"] for q in sg) / len(sg),
            "by_year": {y: {"n": len(v), "change": sum(q["changed"] for q in v) / len(v),
                            "down": sum(1 for q in v if q["changed"] and (q["delta"] or 0) > 0) / len(v),
                            "up": sum(1 for q in v if q["changed"] and (q["delta"] or 0) < 0) / len(v)}
                        for y, v in sorted(by_year.items())},
            "share_one_notch": (lambda ch: sum(1 for q in ch if q["delta"] and abs(q["delta"]) == 1) / len(ch))(
                [q for q in Q if q["changed"] and q["delta"]])}


def feature_rows(recs, gold):
    """One row per record: the move in the quarter ending at outcome_date, features at the quarter end
    before it, from rating history only. The market cycle uses every issuer's records up to t."""
    per_date = collections.defaultdict(lambda: [0, 0, 0])
    for qs in recs.values():
        for q in qs:
            c = per_date[q["date"]]
            c[0] += 1
            c[1] += q["changed"] and (q["delta"] or 0) > 0
            c[2] += q["changed"] and (q["delta"] or 0) < 0
    rows = []
    for oi, qs in recs.items():
        own = {q["date"]: q for q in qs}
        for q in qs:
            t = GRID[QI[q["date"]] - 1] if QI.get(q["date"], 0) > 0 else None
            if t is None:
                continue
            i = QI[t]
            window = GRID[max(0, i - 3):i + 1]
            recent = [own[x] for x in window if x in own]
            since = 0
            for x in reversed(GRID[:i + 1]):
                r = own.get(x)
                if r is None or r["changed"] or since >= 20:
                    break
                since += 1
            n = sum(per_date[x][0] for x in window)
            rows.append({"company": oi, "t": t, "outcome_date": q["date"], "rating_t": q["prev"],
                         "category": E7.category(q["prev"]), "R2": E7.notch(q["prev"]),
                         "R3": int(any(r["changed"] and (r["delta"] or 0) > 0 for r in recent)),
                         "R4": int(any(r["changed"] and (r["delta"] or 0) < 0 for r in recent)),
                         "R5": since,
                         "R6_down": sum(per_date[x][1] for x in window) / n if n else 0.0,
                         "R6_up": sum(per_date[x][2] for x in window) / n if n else 0.0,
                         "target": 0 if not q["changed"] else (1 if (q["delta"] or 0) > 0 else 2),
                         "gold": (oi, q["date"]) in gold, "level_switch": q["level_switch"], "level": q["level"]})
    return rows


def cohort(rows_by_key, mapping):
    """Candidate test rows: accepted matches filing a 10-K at t, a label at t and at the next quarter end;
    one row per SEC company and date (entity-level label preferred, then the lowest Moody's id)."""
    cand = collections.defaultdict(list)
    for oi, e in mapping.items():
        if e["status"] != "proposed":
            continue
        for t in TEST_DATES:
            if not e["files_10k_at"].get(t):
                continue
            r = rows_by_key.get((oi, NEXT[t]))
            if r is None:
                continue
            cand[(e["proposed_cik"], t)].append((0 if r["level"] == "entity" else 1, int(oi), oi, r))
    chosen, dropped = [], 0
    for (cik, t), lst in sorted(cand.items()):
        lst.sort(key=lambda x: (x[0], x[1]))
        _, _, oi, r = lst[0]
        dropped += len(lst) - 1
        chosen.append({**r, "cik": cik, "moodys_name": mapping[oi]["moodys_name"],
                       "sec_name": mapping[oi]["sec"]["name"], "sic": mapping[oi]["sec"].get("sic"),
                       "industry": mapping[oi]["sec"].get("industry"), "rule": mapping[oi]["rule"]})
    return chosen, dropped


def main():
    if os.path.exists(OUT):
        sys.exit(f"refusing to overwrite {OUT}")
    labels = json.load(open(LABELS))["issuers"]
    gold_items = json.load(open(os.path.join(ROOT, "evaluation", "goldset.json")))["items"]
    gold = {(g["label_oi"], g["date"]) for g in gold_items}
    recs = records(labels)
    rates = base_rates(recs)
    rows = feature_rows(recs, gold)
    train, test = F.split(rows)
    chosen = {n: F.choose_C(train, spec) for n, spec in SETS.items()}
    models = {n: F.fit_logit(train, SETS[n], chosen[n][0]) for n in SETS}
    preds = {"M0": np.tile([1.0, 0.0, 0.0], (len(test), 1)), **{n: F.predict_logit(models[n], test) for n in SETS}}
    evals = [F.metrics(test, preds[n], n) for n in ("M0", "M1", "M2")]
    yv = F.y_of(test)
    real = yv != 0
    direction = {n: float(np.mean((preds[n][real, 1] > preds[n][real, 2]) == (yv[real] == 1))) for n in ("M1", "M2")}
    downgrade_pr = {n: F.average_precision_score((yv == 1).astype(int), preds[n][:, 1]) for n in ("M1", "M2")}

    mapping = json.load(open(MAPPING))["issuers"]
    keyed = {(r["company"], r["outcome_date"]): r for r in rows}
    test_rows, dup = cohort(keyed, mapping)
    w_train = [r for r in rows if r["outcome_date"] <= "2024-12-31" and not r["gold"]]
    w_models = {n: F.fit_logit(w_train, SETS[n], chosen[n][0]) for n in SETS}
    w_preds = {n: F.predict_logit(w_models[n], test_rows) for n in SETS}
    frozen = [{"oi": r["company"], "cik": r["cik"], "t": r["t"], "target": r["target"],
               **{n: [float(x) for x in w_preds[n][i]] for n in SETS}} for i, r in enumerate(test_rows)]

    os.makedirs(OUT)
    json.dump(rates, open(os.path.join(OUT, "base_rates.json"), "w"), indent=1)
    json.dump({"train_rows": len(train), "train_changes": int(sum(r["target"] != 0 for r in train)),
               "test_rows": len(test), "test_changes": int(sum(r["target"] != 0 for r in test)),
               "chosen_C": {n: c[0] for n, c in chosen.items()}, "metrics": evals, "direction": direction,
               "downgrade_pr_area": downgrade_pr,
               "coefficients": {n: F.coefficients(models[n], SETS[n]) for n in SETS}},
              open(os.path.join(OUT, "baselines.json"), "w"), indent=1, default=float)
    json.dump({"fitted_on": "outcome quarters up to 2024-12-31, all corporate issuers, gold excluded",
               "frozen": "before any Experiment 10 model request", "rows": frozen},
              open(os.path.join(OUT, "baseline_predictions_window.json"), "w"), indent=0)
    ch = [r for r in test_rows if r["target"] != 0]
    json.dump({"rows": [{k: r[k] for k in ("company", "cik", "t", "rating_t", "target", "moodys_name", "sec_name",
                                           "sic", "industry", "rule", "level_switch")} for r in test_rows],
               "duplicates_removed": dup}, open(os.path.join(OUT, "cohort.json"), "w"), indent=0)
    summary = {"cohort_rows": len(test_rows), "changes": len(ch),
               "down": sum(1 for r in ch if r["target"] == 1), "up": sum(1 for r in ch if r["target"] == 2),
               "stable": len(test_rows) - len(ch), "by_date": dict(collections.Counter(r["t"] for r in test_rows)),
               "changes_by_date": dict(collections.Counter(r["t"] for r in ch)),
               "changes_by_category": dict(collections.Counter(r["category"] for r in ch)),
               "duplicates_removed": dup, "companies": len({r["cik"] for r in test_rows})}
    json.dump(summary, open(os.path.join(OUT, "cohort_summary.json"), "w"), indent=1)
    print(json.dumps({"base_rates": {k: rates[k] for k in ("issuers", "quarterly_records", "overall", "investment_grade",
                                                           "speculative_grade", "share_one_notch")},
                      "by_category": rates["by_category"],
                      "baselines": {"train": [len(train), int(sum(r["target"] != 0 for r in train))],
                                    "test": [len(test), int(sum(r["target"] != 0 for r in test))],
                                    "metrics": [{k: m.get(k) for k in ("model", "pr_auc", "roc_auc", "precision_top10", "brier")} for m in evals],
                                    "direction": direction, "downgrade_pr_area": downgrade_pr},
                      "cohort": summary}, indent=1, default=float))


if __name__ == "__main__":
    main()
