"""
Experiment 08, supplement to run R1, written 2026-09-27 after reading R1 by Claude (Opus 5.5),
directed by Robert Vetter. Three parts, labelled by status:

  within the specification  - company-block bootstrap intervals for direction accuracy (section 9
                              asks for 95% intervals; R1 computed them for the PR area only)
                            - the per-row predictions of every model on the test years and on the
                              Experiment 09 window, which Experiment 09 needs as its baselines
  post-hoc                  - downgrades and upgrades ranked separately (P(down) for downgrades,
                              P(up) for upgrades), PR areas with bootstrap differences; prompted
                              by the training-years pattern search, where the numbers separate
                              downgrades far more than upgrades
                            - the negative-EBITDA feature (F9) as a yes/no table, because R1's
                              quintile display cannot split a binary feature

Reads runs/R1-2026-09-27/features.json and results.json; refits with the same code, split and
regularisation, and refuses to continue unless the refit reproduces R1's test metrics exactly.
Writes runs/R1-2026-09-27/supplement.json, supplement.md and predictions.json; refuses to overwrite.
    python3 experiments/08-next-quarter-baselines/supplement.py R1-2026-09-27
"""
import json
import os
import random
import sys

import numpy as np
from sklearn.metrics import average_precision_score

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_models as F  # noqa: E402

NAMES = ["M0", "M1", "M2", "M3", "M4"]


def ap(labels, score):
    if labels.sum() == 0:
        return None
    return float(labels.mean()) if np.allclose(score, score[0]) else float(average_precision_score(labels, score))


def direction(y, P):
    real = y != 0
    return float(np.mean((P[real, 1] > P[real, 2]) == (y[real] == 1)))


def boot(rows, preds, stat, pairs):
    rng = random.Random(F.SEED)
    comps = sorted({r["company"] for r in rows})
    idx = {c: [i for i, r in enumerate(rows) if r["company"] == c] for c in comps}
    y = F.y_of(rows)
    vals = {n: [] for n in preds}
    diffs = {f"{a}-{b}": [] for a, b in pairs}
    for _ in range(F.BOOT):
        sel = [i for _ in comps for i in idx[rng.choice(comps)]]
        v = {n: stat(y[sel], preds[n][sel]) for n in preds}
        if any(x is None for x in v.values()):
            continue
        for n in preds:
            vals[n].append(v[n])
        for a, b in pairs:
            diffs[f"{a}-{b}"].append(v[a] - v[b])
    q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return {"intervals": {n: q(v) for n, v in vals.items()},
            "differences": {k: {"interval": q(v), "share_above_zero": float(np.mean(np.array(v) > 0))}
                            for k, v in diffs.items()}}


def main(run_id):
    run = os.path.join(HERE, "runs", run_id)
    out = os.path.join(run, "supplement.json")
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")
    rows = json.load(open(os.path.join(run, "features.json")))
    r1 = json.load(open(os.path.join(run, "results.json")))
    Cs = {n: r1["chosen"][n]["C"] for n in F.SETS}
    train, test = F.split(rows)
    models, _ = F.fit_all(train, Cs)
    preds = F.predict_all(models, test)
    for m_old in r1["test"]:
        m_new = F.metrics(test, preds[m_old["model"]], m_old["model"])
        for k, v in m_old.items():
            if isinstance(v, float) and abs(v - m_new[k]) > 1e-12:
                sys.exit(f"refit does not reproduce R1: {m_old['model']} {k} {v} != {m_new[k]}")

    y = F.y_of(test)
    res = {"reproduces_R1": True}
    res["direction"] = {"point": {n: direction(y, preds[n]) for n in NAMES[1:]},
                        **boot(test, {n: preds[n] for n in NAMES[1:]},
                               lambda yy, P: direction(yy, P) if (yy != 0).any() else None,
                               [("M2", "M1"), ("M3", "M1"), ("M3", "M2"), ("M4", "M1")])}
    for side, cls in (("downgrades", 1), ("upgrades", 2)):
        stat = lambda yy, P, c=cls: ap((yy == c).astype(int), P[:, c])
        res[f"posthoc_{side}"] = {"events": int((y == cls).sum()),
                                  "point": {n: stat(y, preds[n]) for n in NAMES},
                                  **boot(test, {n: preds[n] for n in NAMES}, stat,
                                         [("M2", "M1"), ("M3", "M1"), ("M3", "M2"), ("M4", "M1")])}
    f9 = {}
    for v in (0, 1, None):
        rs = [r for r in train if r["F9"] == v]
        f9[str(v)] = {"n": len(rs), "down": sum(r["target"] == 1 for r in rs) / len(rs) if rs else None,
                      "up": sum(r["target"] == 2 for r in rs) / len(rs) if rs else None}
    res["posthoc_F9_training"] = f9

    w_train, _ = F.split(rows, train_end=F.W09_TRAIN_END, test_start="9999")
    w_test = [r for r in rows if r["outcome_date"] in F.W09_OUTCOMES]
    w_models, _ = F.fit_all(w_train, Cs)
    w_preds = F.predict_all(w_models, w_test)
    for m_old in r1["experiment_09_window"]["metrics"]:
        m_new = F.metrics(w_test, w_preds[m_old["model"]], m_old["model"])
        for k, v in m_old.items():
            if isinstance(v, float) and abs(v - m_new[k]) > 1e-12:
                sys.exit(f"window refit does not reproduce R1: {m_old['model']} {k}")
    keep = ["company", "t", "outcome_date", "rating_t", "target", "gold", "F0"]
    json.dump({"test": [{**{k: r[k] for k in keep}, **{n: [float(x) for x in preds[n][i]] for n in NAMES}}
                        for i, r in enumerate(test)],
               "experiment_09_window": [{**{k: r[k] for k in keep}, **{n: [float(x) for x in w_preds[n][i]] for n in NAMES}}
                                        for i, r in enumerate(w_test)]},
              open(os.path.join(run, "predictions.json"), "w"), indent=0)
    json.dump(res, open(out, "w"), indent=1)

    L = ["## Direction accuracy on real changes, test years (within the specification)\n",
         "| Model | Direction correct | 95% interval |", "|---|---|---|"]
    for n in NAMES[1:]:
        lo, hi = res["direction"]["intervals"][n]
        L.append(f"| {n} | {100 * res['direction']['point'][n]:.1f}% | {100 * lo:.1f}% to {100 * hi:.1f}% |")
    L += ["", "| Difference | 95% interval | Share above zero |", "|---|---|---|"]
    for k, v in res["direction"]["differences"].items():
        L.append(f"| {k} | {100 * v['interval'][0]:+.1f} to {100 * v['interval'][1]:+.1f} points | {100 * v['share_above_zero']:.1f}% |")
    for side in ("downgrades", "upgrades"):
        d = res[f"posthoc_{side}"]
        L += ["", f"## Post-hoc: {side} ranked on their own, test years ({d['events']} events)\n",
              "| Model | PR area | 95% interval |", "|---|---|---|"]
        for n in NAMES:
            lo, hi = d["intervals"][n]
            L.append(f"| {n} | {d['point'][n]:.3f} | {lo:.3f} to {hi:.3f} |")
        L += ["", "| Difference | 95% interval | Share above zero |", "|---|---|---|"]
        for k, v in d["differences"].items():
            L.append(f"| {k} | {v['interval'][0]:+.3f} to {v['interval'][1]:+.3f} | {100 * v['share_above_zero']:.1f}% |")
    L += ["", "## Post-hoc: negative EBITDA (F9), training years\n", "| F9 | n | Downgrade next quarter | Upgrade |", "|---|---|---|---|"]
    fmt = lambda x: "" if x is None else f"{100 * x:.1f}%"
    for v, s in f9.items():
        L.append(f"| {v} | {s['n']} | {fmt(s['down'])} | {fmt(s['up'])} |")
    open(os.path.join(run, "supplement.md"), "w").write("\n".join(L) + "\n")
    print(open(os.path.join(run, "supplement.md")).read())


if __name__ == "__main__":
    main(sys.argv[1])
