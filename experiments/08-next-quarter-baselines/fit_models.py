"""
Experiment 08: fit and evaluate the next-quarter models M0 to M4 (README.md sections 5 and 9).

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. No model call.

Runs build_features.py into a new run folder, then:
  - splits by time: training rows have outcome quarters up to 2020-12-31 and are not gold;
    test rows have outcome quarters from 2021-03-31 (gold kept, with a sensitivity without it)
  - M0 persistence; M1 to M3 multinomial logistic regressions (L2), the strength chosen by
    time-ordered validation inside the training years (validation years 2017 to 2020, mean
    log loss); M4 a gradient-boosted tree model with fixed settings
  - preprocessing fitted on training rows only: financial features winsorised at the 1st and
    99th percentile, missing values filled with the training median, numeric features
    standardised
  - metrics: area under the precision-recall curve (headline), ROC area, precision and recall
    in the top 5% and 10%, direction accuracy on real changes, Brier score, log loss,
    calibration by tenth; company-block bootstrap (2,000) on the test years
  - the Experiment 09 window: refit on outcomes up to 2024-12-31, evaluate the outcome quarters
    2025-03-31 and 2025-06-30
  - the fitted function: M2 and M3 coefficients, with a worked example
  - exploratory pattern search on training rows only

Writes runs/<run_id>/: features.json, audit.json, manifest.json, results.json, tables.md.
Refuses to overwrite. Run from the repository root:
    python3 experiments/08-next-quarter-baselines/fit_models.py R1-2026-09-27
"""
import hashlib
import json
import math
import os
import random
import sys

import numpy as np
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_features as BF  # noqa: E402

ROOT = BF.ROOT
SEED = 20260927
BOOT = 2000
TRAIN_END, TEST_START = "2020-12-31", "2021-03-31"
VAL_YEARS = [2017, 2018, 2019, 2020]
C_GRID = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
W09_TRAIN_END, W09_OUTCOMES = "2024-12-31", ("2025-03-31", "2025-06-30")

CATS = ["Aa+", "A", "Baa", "Ba", "B", "Caa-"]
R_NUM = ["R2", "R3", "R4", "R5", "R6_down", "R6_up"]
F_NUM = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"]
WINSOR = {"F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F10", "F11", "F12", "F13"}
SETS = {
    "M1": {"cats": True, "num": []},
    "M2": {"cats": True, "num": R_NUM},
    "M3": {"cats": True, "num": R_NUM + F_NUM + ["F0"]},
}
LABELS = {
    "R2": "notch (higher is worse)", "R3": "downgrade in the last 4 quarters",
    "R4": "upgrade in the last 4 quarters", "R5": "quarters since the last change",
    "R6_down": "sector share downgraded, last 4 quarters", "R6_up": "sector share upgraded, last 4 quarters",
    "F0": "financials available", "F1": "revenue growth, TTM", "F2": "EBITDA margin, TTM",
    "F3": "change in EBITDA margin, points", "F4": "debt / EBITDA", "F5": "change in debt / EBITDA",
    "F6": "(EBITDA - capex) / interest", "F7": "change in coverage", "F8": "cash / debt",
    "F9": "negative EBITDA", "F10": "numbers-only scorecard score (higher is worse)",
    "F11": "change in scorecard score", "F12": "gap: rating notch minus numbers-implied notch",
    "F13": "days since the latest figures were filed",
}


def cat_of(c):
    return {"Aaa": "Aa+", "Aa": "Aa+", "Caa": "Caa-", "Ca-C": "Caa-"}.get(c, c)


# ----------------------------------------------------------------------------- preprocessing

class Prep:
    def __init__(self, spec):
        self.spec = spec

    def fit(self, rows):
        self.bounds, self.median, self.mean, self.sd = {}, {}, {}, {}
        for k in self.spec["num"]:
            vals = np.array([r[k] for r in rows if r[k] is not None], dtype=float)
            if k in WINSOR and len(vals):
                self.bounds[k] = (np.percentile(vals, 1), np.percentile(vals, 99))
                vals = np.clip(vals, *self.bounds[k])
            self.median[k] = float(np.median(vals)) if len(vals) else 0.0
        X = self._raw(rows)
        n = len(self.spec["num"])
        self.mean = X[:, :n].mean(axis=0) if n else np.array([])
        self.sd = X[:, :n].std(axis=0) if n else np.array([])
        self.sd[self.sd == 0] = 1.0
        return self

    def _raw(self, rows):
        cols = []
        for k in self.spec["num"]:
            v = np.array([self.median[k] if r[k] is None else r[k] for r in rows], dtype=float)
            if k in self.bounds:
                v = np.clip(v, *self.bounds[k])
            cols.append(v)
        if self.spec["cats"]:
            for c in CATS:
                cols.append(np.array([1.0 if cat_of(r["category"]) == c else 0.0 for r in rows]))
        return np.column_stack(cols)

    def transform(self, rows):
        X = self._raw(rows)
        n = len(self.spec["num"])
        if n:
            X[:, :n] = (X[:, :n] - self.mean) / self.sd
        return X

    def names(self):
        return list(self.spec["num"]) + ([f"rating {c}" for c in CATS] if self.spec["cats"] else [])


def y_of(rows):
    return np.array([r["target"] for r in rows])


def fit_logit(rows, spec, C):
    prep = Prep(spec).fit(rows)
    m = LogisticRegression(C=C, max_iter=5000)
    m.fit(prep.transform(rows), y_of(rows))
    return prep, m


def predict_logit(model, rows):
    prep, m = model
    P = m.predict_proba(prep.transform(rows))
    out = np.zeros((len(rows), 3))
    for j, c in enumerate(m.classes_):
        out[:, c] = P[:, j]
    return out


def choose_C(train, spec):
    scores = {}
    for C in C_GRID:
        losses = []
        for yv in VAL_YEARS:
            fit_rows = [r for r in train if int(r["outcome_date"][:4]) < yv]
            val_rows = [r for r in train if int(r["outcome_date"][:4]) == yv]
            if not val_rows or len({r["target"] for r in fit_rows}) < 3:
                continue
            P = predict_logit(fit_logit(fit_rows, spec, C), val_rows)
            losses.append(log_loss(y_of(val_rows), np.clip(P, 1e-9, 1), labels=[0, 1, 2]))
        scores[C] = float(np.mean(losses))
    return min(scores, key=scores.get), scores


def m4_matrix(rows):
    cols = [[np.nan if r[k] is None else float(r[k]) for r in rows] for k in R_NUM + F_NUM + ["F0"]]
    return np.array(cols, dtype=float).T


def fit_m4(rows):
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=3,
                                       min_samples_leaf=20, random_state=SEED)
    m.fit(m4_matrix(rows), y_of(rows))
    return m


def predict_m4(m, rows):
    P = m.predict_proba(m4_matrix(rows))
    out = np.zeros((len(rows), 3))
    for j, c in enumerate(m.classes_):
        out[:, c] = P[:, j]
    return out


# ----------------------------------------------------------------------------- metrics

def top_k(change, score, share, rng_seed):
    n = len(score)
    k = max(1, math.ceil(share * n))
    rng = np.random.RandomState(rng_seed)
    order = np.lexsort((rng.rand(n), -score))          # ties broken at random, seeded
    hits = int(change[order[:k]].sum())
    return hits / k, hits / max(1, int(change.sum()))


def metrics(rows, P, name):
    y = y_of(rows)
    change = (y != 0).astype(int)
    score = P[:, 1] + P[:, 2]
    res = {"model": name, "n": len(rows), "changes": int(change.sum()),
           "base_rate": float(change.mean()) if len(rows) else None}
    if change.sum() == 0 or change.sum() == len(rows):
        return res
    const = np.allclose(score, score[0])
    res["pr_auc"] = float(change.mean()) if const else float(average_precision_score(change, score))
    res["roc_auc"] = 0.5 if const else float(roc_auc_score(change, score))
    for s in (0.05, 0.10):
        p, r = top_k(change, score, s, SEED)
        res[f"precision_top{int(s * 100)}"], res[f"recall_top{int(s * 100)}"] = p, r
    real = y != 0
    res["direction_accuracy"] = (None if const else
                                 float(np.mean((P[real, 1] > P[real, 2]) == (y[real] == 1))))
    onehot = np.eye(3)[y]
    res["brier"] = float(np.mean(np.sum((P - onehot) ** 2, axis=1)))
    res["log_loss"] = None if const else float(log_loss(y, np.clip(P, 1e-9, 1), labels=[0, 1, 2]))
    return res


def calibration(rows, P):
    change = (y_of(rows) != 0).astype(int)
    score = P[:, 1] + P[:, 2]
    order = np.argsort(score)
    out = []
    for part in np.array_split(order, 10):
        out.append({"n": len(part), "mean_predicted": float(score[part].mean()),
                    "observed": float(change[part].mean())})
    return out


def bootstrap(rows, preds, names, pairs):
    rng = random.Random(SEED)
    comps = sorted({r["company"] for r in rows})
    idx = {c: [i for i, r in enumerate(rows) if r["company"] == c] for c in comps}
    y = y_of(rows)
    change = (y != 0).astype(int)
    draws = {n: [] for n in names}
    diffs = {f"{a}-{b}": [] for a, b in pairs}
    for _ in range(BOOT):
        sel = [i for _ in comps for i in idx[rng.choice(comps)]]
        ch = change[sel]
        if ch.sum() == 0:
            continue
        ap = {}
        for n in names:
            s = preds[n][sel, 1] + preds[n][sel, 2]
            ap[n] = float(ch.mean()) if np.allclose(s, s[0]) else float(average_precision_score(ch, s))
            draws[n].append(ap[n])
        for a, b in pairs:
            diffs[f"{a}-{b}"].append(ap[a] - ap[b])
    q = lambda v: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if v else (None, None)
    return {"pr_auc": {n: q(v) for n, v in draws.items()},
            "pr_auc_difference": {k: {"interval": q(v), "share_above_zero": float(np.mean(np.array(v) > 0))}
                                  for k, v in diffs.items()}}


# ----------------------------------------------------------------------------- analysis

def split(rows, train_end=TRAIN_END, test_start=TEST_START):
    """Training: outcome quarters up to train_end, gold rows excluded. Test: from test_start."""
    train = [r for r in rows if r["outcome_date"] <= train_end and not r["gold"]]
    test = [r for r in rows if r["outcome_date"] >= test_start]
    assert not any(r["outcome_date"] >= test_start for r in train)
    return train, test


def fit_all(train, Cs=None):
    models, chosen = {}, {}
    for name, spec in SETS.items():
        if Cs is None:
            C, grid = choose_C(train, spec)
            chosen[name] = {"C": C, "validation_log_loss": grid}
        else:
            C = Cs[name]
        models[name] = ("logit", fit_logit(train, spec, C))
    models["M4"] = ("m4", fit_m4(train))
    return models, chosen


def predict_all(models, rows):
    preds = {"M0": np.tile([1.0, 0.0, 0.0], (len(rows), 1))}
    for name, (kind, m) in models.items():
        preds[name] = predict_logit(m, rows) if kind == "logit" else predict_m4(m, rows)
    return preds


def coefficients(model, spec):
    prep, m = model
    classes = list(m.classes_)
    base = m.coef_[classes.index(0)]
    down = m.coef_[classes.index(1)] - base
    up = m.coef_[classes.index(2)] - base
    return [{"feature": n, "label": LABELS.get(n, n), "down_vs_unchanged": float(a), "up_vs_unchanged": float(b)}
            for n, a, b in zip(prep.names(), down, up)]


def exploratory(train):
    out = {"quintiles": {}, "pairs": []}
    feats = R_NUM[:1] + ["R5", "R6_down", "R6_up"] + F_NUM
    for k in feats:
        vals = sorted(r[k] for r in train if r[k] is not None)
        if len(vals) < 50:
            continue
        cuts = [vals[int(len(vals) * q / 5)] for q in range(1, 5)]
        bins = [[] for _ in range(5)]
        for r in train:
            if r[k] is None:
                continue
            bins[sum(r[k] >= c for c in cuts)].append(r)
        miss = [r for r in train if r[k] is None]
        out["quintiles"][k] = [{"n": len(b), "down": sum(r["target"] == 1 for r in b) / len(b) if b else None,
                                "up": sum(r["target"] == 2 for r in b) / len(b) if b else None} for b in bins]
        out["quintiles"][k].append({"n": len(miss), "missing": True,
                                    "down": sum(r["target"] == 1 for r in miss) / len(miss) if miss else None,
                                    "up": sum(r["target"] == 2 for r in miss) / len(miss) if miss else None})
    med = {k: float(np.median([r[k] for r in train if r[k] is not None])) for k in feats
           if sum(r[k] is not None for r in train) >= 50}
    keys = sorted(med)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            rows = [r for r in train if r[a] is not None and r[b] is not None]
            cells = {}
            for r in rows:
                cells.setdefault((r[a] > med[a], r[b] > med[b]), []).append(r["target"] != 0)
            if len(cells) < 4 or min(len(v) for v in cells.values()) < 50:
                continue
            rates = {f"{a} {'high' if ka else 'low'}, {b} {'high' if kb else 'low'}": sum(v) / len(v)
                     for (ka, kb), v in cells.items()}
            out["pairs"].append({"pair": [a, b], "spread": max(rates.values()) - min(rates.values()),
                                 "cells": rates, "n": len(rows)})
    out["pairs"].sort(key=lambda p: -p["spread"])
    out["pairs"] = out["pairs"][:10]
    return out


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(run_id):
    out = os.path.join(HERE, "runs", run_id)
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")
    os.makedirs(out)
    rows, aud = BF.main(out)
    train, test = split(rows)
    models, chosen = fit_all(train)
    preds = predict_all(models, test)
    names = ["M0", "M1", "M2", "M3", "M4"]
    res = {"counts": {"train": len(train), "train_changes": int(sum(r["target"] != 0 for r in train)),
                      "test": len(test), "test_changes": int(sum(r["target"] != 0 for r in test)),
                      "gold_excluded_from_training": sum(1 for r in rows if r["outcome_date"] <= TRAIN_END and r["gold"])},
           "chosen": chosen, "audit": aud}
    res["test"] = [metrics(test, preds[n], n) for n in names]
    subsets = {
        "test without gold": [i for i, r in enumerate(test) if not r["gold"]],
        "test with financials (F0 = 1)": [i for i, r in enumerate(test) if r["F0"] == 1],
        "test, still-rated companies": [i for i, r in enumerate(test) if r["origin"] == "active"],
    }
    res["subsets"] = {k: [metrics([test[i] for i in ix], preds[n][ix], n) for n in names]
                      for k, ix in subsets.items()}
    years = sorted({r["outcome_date"][:4] for r in test})
    res["by_year"] = {y: [metrics([test[i] for i in ix], preds[n][ix], n) for n in names]
                      for y in years for ix in [[i for i, r in enumerate(test) if r["outcome_date"][:4] == y]]}
    res["bootstrap"] = bootstrap(test, preds, names[1:], [("M2", "M1"), ("M3", "M1"), ("M4", "M1"), ("M3", "M2")])
    res["calibration_M3"] = calibration(test, preds["M3"])
    res["calibration_M1"] = calibration(test, preds["M1"])
    res["coefficients"] = {n: coefficients(models[n][1], SETS[n]) for n in ("M1", "M2", "M3")}

    ex_rows = [r for r in test if r["target"] == 1 and r["F0"] == 1]
    ex = sorted(ex_rows, key=lambda r: (r["company"], r["t"]))[0]
    i = test.index(ex)
    res["worked_example"] = {"row": {k: ex[k] for k in ["company", "t", "outcome_date", "rating_t", "target"]
                                     + R_NUM + F_NUM + ["F0", "category"]},
                             "probabilities": {n: [float(x) for x in preds[n][i]] for n in names}}

    w_train = [r for r in rows if r["outcome_date"] <= W09_TRAIN_END and not r["gold"]]
    w_test = [r for r in rows if r["outcome_date"] in W09_OUTCOMES]
    w_models, _ = fit_all(w_train, {n: chosen[n]["C"] for n in SETS})
    w_preds = predict_all(w_models, w_test)
    res["experiment_09_window"] = {"train": len(w_train), "test": len(w_test),
                                   "metrics": [metrics(w_test, w_preds[n], n) for n in names]}
    res["exploratory"] = exploratory(train)

    manifest = {"run_id": run_id, "seed": SEED, "bootstrap": BOOT, "sklearn": sklearn.__version__,
                "numpy": np.__version__,
                "scripts": {os.path.basename(p): sha(p) for p in (
                    os.path.join(HERE, "fit_models.py"), os.path.join(HERE, "build_features.py"))},
                "companyfacts": {s: (p, sha(os.path.join(ROOT, p)) if p else None)
                                 for s, p in json.load(open(os.path.join(out, "audit.json")))["sources"].items()},
                "features_sha256": sha(os.path.join(out, "features.json"))}
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)
    open(os.path.join(out, "tables.md"), "w").write(to_markdown(res))
    print(f"wrote {out}")
    return res


# ----------------------------------------------------------------------------- tables

def f3(x):
    return "" if x is None else f"{x:.3f}"


def pct(x):
    return "" if x is None else f"{100 * x:.1f}%"


def metric_table(ms):
    L = ["| Model | n | Changes | PR area | ROC area | Precision top 5% | Recall top 5% | Precision top 10% | Recall top 10% | Direction | Brier | Log loss |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in ms:
        L.append(f"| {m['model']} | {m['n']} | {m['changes']} | {f3(m.get('pr_auc'))} | {f3(m.get('roc_auc'))} | "
                 f"{pct(m.get('precision_top5'))} | {pct(m.get('recall_top5'))} | {pct(m.get('precision_top10'))} | "
                 f"{pct(m.get('recall_top10'))} | {pct(m.get('direction_accuracy'))} | {f3(m.get('brier'))} | {f3(m.get('log_loss'))} |")
    return "\n".join(L)


def to_markdown(res):
    L = []
    w = L.append
    c = res["counts"]
    w(f"Training rows {c['train']} ({c['train_changes']} changes; {c['gold_excluded_from_training']} gold rows excluded); "
      f"test rows {c['test']} ({c['test_changes']} changes).\n")
    w("## Test years, 2021 to mid-2025\n")
    w(metric_table(res["test"]))
    w("\n### Bootstrap by company (2,000), PR area\n")
    w("| Model | 95% interval |")
    w("|---|---|")
    for n, (lo, hi) in res["bootstrap"]["pr_auc"].items():
        w(f"| {n} | {f3(lo)} to {f3(hi)} |")
    w("\n| Difference | 95% interval | Share of resamples above zero |")
    w("|---|---|---|")
    for k, v in res["bootstrap"]["pr_auc_difference"].items():
        w(f"| {k} | {f3(v['interval'][0])} to {f3(v['interval'][1])} | {pct(v['share_above_zero'])} |")
    for k, ms in res["subsets"].items():
        w(f"\n### {k}\n")
        w(metric_table(ms))
    w("\n### PR area by test year\n")
    w("| Year | n | Changes | M1 | M2 | M3 | M4 |")
    w("|---|---|---|---|---|---|---|")
    for y, ms in res["by_year"].items():
        d = {m["model"]: m for m in ms}
        w(f"| {y} | {d['M1']['n']} | {d['M1']['changes']} | {f3(d['M1'].get('pr_auc'))} | {f3(d['M2'].get('pr_auc'))} | "
          f"{f3(d['M3'].get('pr_auc'))} | {f3(d['M4'].get('pr_auc'))} |")
    w("\n### Calibration of P(change), test years, by tenth\n")
    w("| Tenth | n | M1 predicted | M1 observed | M3 predicted | M3 observed |")
    w("|---|---|---|---|---|---|")
    for i, (a, b) in enumerate(zip(res["calibration_M1"], res["calibration_M3"]), 1):
        w(f"| {i} | {b['n']} | {pct(a['mean_predicted'])} | {pct(a['observed'])} | {pct(b['mean_predicted'])} | {pct(b['observed'])} |")
    e = res["experiment_09_window"]
    w(f"\n## Experiment 09 window (training rows {e['train']}, outcome quarters 2025 Q1 and Q2)\n")
    w(metric_table(e["metrics"]))
    w("\n## Chosen regularisation\n")
    w("| Model | C | Validation log loss at chosen C |")
    w("|---|---|---|")
    for n, v in res["chosen"].items():
        w(f"| {n} | {v['C']} | {f3(v['validation_log_loss'][v['C']])} |")
    for n in ("M2", "M3"):
        w(f"\n## Coefficients of {n}, per standard deviation (rating categories as indicators)\n")
        w("| Feature | Meaning | Down vs unchanged (log odds) | Up vs unchanged (log odds) |")
        w("|---|---|---|---|")
        for r in res["coefficients"][n]:
            w(f"| {r['feature']} | {r['label']} | {r['down_vs_unchanged']:+.3f} | {r['up_vs_unchanged']:+.3f} |")
    ex = res["worked_example"]
    w("\n## Worked example\n")
    w("```\n" + json.dumps(ex, indent=1) + "\n```")
    w("\n## Exploratory, training years only\n")
    for k, q in res["exploratory"]["quintiles"].items():
        w(f"- {k} ({LABELS.get(k, k)}): " + "; ".join(
            (f"missing n={b['n']} down {pct(b['down'])} up {pct(b['up'])}" if b.get("missing")
             else f"Q{i + 1} n={b['n']} down {pct(b['down'])} up {pct(b['up'])}") for i, b in enumerate(q)))
    w("\nPairs with the largest spread of change rates (median splits, each cell at least 50 rows):\n")
    for p in res["exploratory"]["pairs"]:
        w(f"- {p['pair'][0]} x {p['pair'][1]}: spread {pct(p['spread'])}; " +
          "; ".join(f"{k} {pct(v)}" for k, v in p["cells"].items()))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run(sys.argv[1])
