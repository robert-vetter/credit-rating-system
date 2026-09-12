"""
Scorecard calibration on the historical frame: the numbers-only rung, no model involved.

Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-11. Pipeline step 13.

Why: Experiment 03 reported 46 of 47 figures within 2% of XBRL. XBRL was also in the input,
so this is agreement, not independent extraction validation. The scorecard
arithmetic sits systematically above Moody's assigned rating, and the model's own judgement
is reluctant to call a change. Both can be studied on the historical frame without a model.
Every observation whose four quantitative subfactors are computable from point-in-time XBRL
is scored with system/scorecard.py and compared with the rating Moody's actually had in
effect. This is rung 1 of the blinding ladder in docs/experiment-plan.md: numbers only, so
no training memory and no document leakage can be involved, and it is the floor that every
model-based channel has to beat.

What it measures
  1. The gap: assigned rating minus quantitative-only scorecard outcome, in notches, by
     rating level, by era (fiscal years with and without operating-lease tags, ASC 842) and
     within company. The gap is the sum of everything the numbers-only scorecard does not
     model: Moody's adjustments, the four qualitative factors, notching, committee judgement.
     It is not the qualitative grade and must not be read as one.
  2. Level calibration (Task A of the plan, numbers only): a monotone map from the
     quantitative aggregate to the assigned rating, fitted by isotonic regression and
     evaluated out-of-fold with whole companies held out (five folds, seed 20260911). Every
     reported prediction comes from a fit that never saw that company. Gold observations
     are excluded before any fitting, threshold selection, or descriptive analysis.
     Company folds are retrospective, not a rolling point-in-time forecast evaluation.
  3. Change detection (Task B, numbers only): from the persistence rating and the movement
     of the numbers, predict up, unchanged or down by one notch. Four signals: the change in
     the quantitative aggregate over the last quarter; the change since Moody's last rating
     action; the distance between the calibrated level and the current rating; and that
     distance anchored by the company's own past residual, which is the numbers-only version
     of the history pack. The alarm threshold is chosen on the training folds by overall MAE,
     never on the held-out fold. Metrics follow score_run.py: changed-subset lift over
     persistence, direction accuracy, false-alarm rate on unchanged quarters, recall, and
     the paired bootstrap on the notch-error difference against persistence.

Point-in-time rule: a fiscal year's figures are used at t only if the 10-K carrying them was
filed on or before t (fetch_xbrl.py keeps the earliest filing date per value and does not
apply restatements retroactively). Label and persistence come from observations.json: the
rating in effect at t and at the previous quarter end. In-scope companies only.

Outputs: evaluation/runs/calibration/rows.json (one record per observation, gitignored) and
evaluation/calibration-summary.md (generated tables, committed). The reading of the numbers
lives in notes/scorecard-calibration.md.

Run: python3 evaluation/pipeline/calibrate_scorecard.py
"""
import collections
import json
import os
import random
import statistics
import sys
from datetime import date

import numpy as np
from sklearn.isotonic import IsotonicRegression

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history_pack as hp   # noqa: E402
import scorecard as sc      # noqa: E402

COMPANIES = os.path.join(ROOT, "evaluation", "companies")
OUT_DIR = os.path.join(ROOT, "evaluation", "runs", "calibration")
SUMMARY = os.path.join(ROOT, "evaluation", "calibration-summary.md")
GOLD = os.path.join(ROOT, "evaluation", "goldset.json")
SEED = 20260911
FOLDS = 5
THETAS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 99.0]   # 99 = never alarm
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]
QEND = {3: "31", 6: "30", 9: "30", 12: "31"}


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def bucket(i):
    return SCALE[i].rstrip("123")


def prev_quarter_end(t):
    y, m = int(t[:4]), int(t[5:7]) - 3
    if m <= 0:
        y, m = y - 1, m + 12
    return f"{y}-{m:02d}-{QEND[m]}"


def quant_at(xbrl, t):
    """Quantitative-only aggregate at t from the latest fiscal year filed on or before t.
    Returns None unless all four quantitative subfactors are computable."""
    years = hp.fy_values(xbrl, t)
    if not years:
        return None
    fy = max(years)
    y = years[fy]
    s = hp.quant_contribution(hp.metrics_for(y))
    if len(s) < 4:
        return None
    q = sum(hp.QUANT_W[k] * v for k, v in s.items()) / 0.55   # quant scores carried to the full scale
    lease = any(k in y for k in ("operating_lease_current", "operating_lease_noncurrent"))
    return {"q": q, "fy": fy, "lease": lease, "scores": s}


def last_action_before(path, quarter_start):
    """Date of the last non-WR rating event strictly before the observation quarter."""
    ev = [e for e in path if e[0] < quarter_start and e[1] != "WR"]
    return ev[-1][0] if ev else None


def load_rows():
    gold = {(i["slug"], i["date"]) for i in json.load(open(GOLD))["items"]}
    rows, cov = [], collections.Counter()
    for slug in sorted(os.listdir(COMPANIES)):
        f = os.path.join(COMPANIES, slug, "observations.json")
        x = os.path.join(COMPANIES, slug, "xbrl.json")
        if not (os.path.exists(f) and os.path.exists(x)):
            continue
        o = json.load(open(f))
        if o.get("scope") != "in":
            cov["obs_out_of_scope"] += sum(1 for _ in o["observations"])
            continue
        xbrl = json.load(open(x))
        cov["invalid_fact_dates_quarantined"] += len(hp.invalid_fact_dates(xbrl))
        for ob in o["observations"]:
            cov["obs_in_scope"] += 1
            if (slug, ob["date"]) in gold:
                cov["gold_excluded"] += 1
                continue
            lab, per = notch(ob["label"]), notch(ob.get("persistence"))
            if lab is None or per is None or ob.get("changed") is None:
                cov["no_label_or_persistence"] += 1
                continue
            cov["changed_in_scope"] += bool(ob["changed"])
            t = ob["date"]
            now = quant_at(xbrl, t)
            if now is None:
                cov["no_full_quant"] += 1
                continue
            cov["covered"] += 1
            cov["covered_changed"] += bool(ob["changed"])
            prev = quant_at(xbrl, prev_quarter_end(t))
            a = last_action_before(ob.get("rating_path", []), hp.quarter_start(t))
            at_action = quant_at(xbrl, a) if a else None
            rows.append({
                "slug": slug, "t": t, "fy": now["fy"], "lease": now["lease"],
                "label": ob["label"], "lab": lab, "per": per,
                "changed": bool(ob["changed"]), "delta": lab - per,
                "q": now["q"], "raw": notch(sc.outcome(now["q"])),
                "q_prev": prev["q"] if prev else None,
                "q_action": at_action["q"] if at_action else None, "action_date": a,
                "gold": (slug, t) in gold,
            })
    return rows, cov


# ----------------------------------------------------------------------------- folds and fits

def folds_by_company(rows):
    slugs = sorted({r["slug"] for r in rows})
    random.Random(SEED).shuffle(slugs)
    fold_of = {s: i % FOLDS for i, s in enumerate(slugs)}
    return [fold_of[r["slug"]] for r in rows]


def fit_iso(train):
    if any(r.get("gold") for r in train):
        raise ValueError("Gold observations must never enter calibration fitting")
    iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
    iso.fit([r["q"] for r in train], [r["lab"] for r in train])
    return iso


def level_calibration(rows, fold):
    """Out-of-fold continuous calibrated level per row: pooled map and era-split map."""
    for k in range(FOLDS):
        train = [r for r, f in zip(rows, fold) if f != k]
        test = [r for r, f in zip(rows, fold) if f == k]
        pooled = fit_iso(train)
        by_era = {}
        for era in (True, False):
            sub = [r for r in train if r["lease"] == era]
            by_era[era] = fit_iso(sub) if len(sub) >= 30 else pooled
        prior = int(round(statistics.median(r["lab"] for r in train)))
        for r in test:
            r["f"] = float(pooled.predict([r["q"]])[0])
            r["f_era"] = float(by_era[r["lease"]].predict([r["q"]])[0])
            r["cal"] = int(round(r["f"]))
            r["cal_era"] = int(round(r["f_era"]))
            r["prior"] = prior
    # the company's own past residual against the calibrated level (numbers-only anchor),
    # strictly from observations before the quarter, at least four of them
    by = collections.defaultdict(list)
    for r in rows:
        by[r["slug"]].append(r)
    for slug, rs in by.items():
        rs.sort(key=lambda r: r["t"])
        for i, r in enumerate(rs):
            past = [p for p in rs[:i] if p["t"] < hp.quarter_start(r["t"])]
            r["rbar"] = statistics.mean(p["lab"] - p["f"] for p in past) if len(past) >= 4 else None
    for r in rows:
        r["s_q"] = None if r["q_prev"] is None else r["q"] - r["q_prev"]
        r["s_a"] = None if r["q_action"] is None else r["q"] - r["q_action"]
        r["s_lvl"] = r["f"] - r["per"]
        r["s_anch"] = None if r["rbar"] is None else r["f"] + r["rbar"] - r["per"]


# ----------------------------------------------------------------------------- metrics

def mae(v):
    v = [x for x in v if x is not None]
    return round(sum(v) / len(v), 3) if v else None


def spearman(xs, ys):
    from scipy.stats import spearmanr
    if len(xs) < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None                      # undefined for a constant channel (the sector prior)
    return round(float(spearmanr(xs, ys).statistic), 3)


def level_metrics(rows, key):
    e = [abs(r[key] - r["lab"]) for r in rows]
    return {"n": len(rows), "mae": mae(e), "exact": round(sum(x == 0 for x in e) / len(e), 3),
            "within_1": round(sum(x <= 1 for x in e) / len(e), 3),
            "spearman": spearman([r[key] for r in rows], [r["lab"] for r in rows]),
            "mean_signed": round(statistics.mean(r["lab"] - r[key] for r in rows), 2)}


def predict_change(r, signal, theta):
    s = r[signal]
    if s is None or abs(s) <= theta:
        return r["per"]
    return min(20, max(0, r["per"] + (1 if s > 0 else -1)))


def change_metrics(rows, pred_key):
    """The score_run.py definitions, applied to a numbers-only channel."""
    e = [abs(r[pred_key] - r["lab"]) for r in rows]
    ep = [abs(r["per"] - r["lab"]) for r in rows]
    ch = [r for r in rows if r["changed"]]
    un = [r for r in rows if not r["changed"]]
    dir_ok = sum(1 for r in ch if r[pred_key] != r["per"] and (r[pred_key] - r["per"]) * (r["lab"] - r["per"]) > 0)
    alarms = sum(1 for r in rows if r[pred_key] != r["per"])
    out = {"n": len(rows), "mae": mae(e), "mae_persistence": mae(ep),
           "exact": round(sum(x == 0 for x in e) / len(e), 3),
           "changed": {"n": len(ch), "mae": mae([abs(r[pred_key] - r["lab"]) for r in ch]),
                       "mae_persistence": mae([abs(r["per"] - r["lab"]) for r in ch]),
                       "moved_at_all_rate": round(sum(r[pred_key] != r["per"] for r in ch) / len(ch), 3) if ch else None,
                       "direction_correct_rate": round(dir_ok / len(ch), 3) if ch else None},
           "unchanged": {"n": len(un),
                         "false_alarm_rate": round(sum(r[pred_key] != r["per"] for r in un) / len(un), 3) if un else None},
           "alarms": alarms,
           "precision_of_alarm": round(dir_ok / alarms, 3) if alarms else None}
    out["changed"]["lift_notches"] = (round(out["changed"]["mae_persistence"] - out["changed"]["mae"], 3)
                                      if ch else None)
    rng = random.Random(17)
    deltas = []
    n = len(rows)
    for _ in range(10_000):
        idx = [rng.randrange(n) for _ in range(n)]
        deltas.append(sum(e[i] for i in idx) / n - sum(ep[i] for i in idx) / n)
    deltas.sort()
    out["bootstrap_err_minus_persistence"] = {"mean": round(sum(deltas) / len(deltas), 4),
                                              "ci95": [round(deltas[249], 4), round(deltas[9749], 4)],
                                              "p_system_beats_persistence": round(sum(d < 0 for d in deltas) / len(deltas), 3),
                                              "seed": 17}
    return out


def choose_theta(train, signal):
    """Threshold with the lowest overall MAE on the training rows; ties go to the larger one."""
    if any(r.get("gold") for r in train):
        raise ValueError("Gold observations must never enter threshold selection")
    best = None
    for th in THETAS:
        m = mae([abs(predict_change(r, signal, th) - r["lab"]) for r in train])
        if best is None or m < best[1] or (m == best[1] and th > best[0]):
            best = (th, m)
    return best[0]


def change_detection(rows, fold):
    signals = ["s_q", "s_a", "s_lvl", "s_anch"]
    chosen = {s: [] for s in signals}
    for k in range(FOLDS):
        # Build the training features using only the outer training companies. Reusing
        # their global out-of-fold features would let the outer test labels influence
        # the calibration maps used to select the threshold.
        train = [dict(r) for r, f in zip(rows, fold) if f != k]
        test = [r for r, f in zip(rows, fold) if f == k]
        level_calibration(train, folds_by_company(train))
        for s in signals:
            th = choose_theta(train, s)
            chosen[s].append(th)
            for r in test:
                r["pred_" + s] = predict_change(r, s, th)
    result = {}
    for s in signals:
        result[s] = change_metrics(rows, "pred_" + s)
        result[s]["theta_per_fold"] = chosen[s]
    # the threshold curve, in sample, for the reading of the tradeoff (not a result). An alarm
    # is "prediction != persistence"; its precision is the share of alarms that moved the
    # right way on a quarter that did change. With the one-notch rule a channel beats
    # persistence on MAE only if that precision exceeds one half.
    curve = {}
    for s in signals:
        curve[s] = []
        for th in THETAS:
            preds = [predict_change(r, s, th) for r in rows]
            ch = [(p, r) for p, r in zip(preds, rows) if r["changed"]]
            un = [(p, r) for p, r in zip(preds, rows) if not r["changed"]]
            dir_ok = sum(1 for p, r in ch if p != r["per"] and (p - r["per"]) * (r["lab"] - r["per"]) > 0)
            alarms = sum(p != r["per"] for p, r in zip(preds, rows))
            moved = round(sum(p != r["per"] for p, r in ch) / len(ch), 3) if ch else None
            fa = round(sum(p != r["per"] for p, r in un) / len(un), 3) if un else None
            curve[s].append({"theta": th, "mae": mae([abs(p - r["lab"]) for p, r in zip(preds, rows)]),
                             "recall_direction": round(dir_ok / len(ch), 3) if ch else None,
                             "moved_on_changed": moved, "false_alarm": fa,
                             "alarms": alarms, "precision": round(dir_ok / alarms, 3) if alarms else None,
                             "odds_vs_unchanged": round(moved / fa, 2) if moved and fa else None,
                             "n_signal": sum(r[s] is not None for r in rows)})
    return result, curve


def timing(rows):
    """Do rating changes cluster in quarters where new annual figures arrived? A numbers-only
    detector can only fire when the numbers move; this bounds what annual XBRL can time."""
    def share(sub, cond):
        return round(sum(cond(r) for r in sub) / len(sub), 3) if sub else None
    ch = [r for r in rows if r["changed"]]
    un = [r for r in rows if not r["changed"]]
    new_fy = lambda r: r["q_prev"] is not None and r["s_q"] not in (None, 0.0)
    fy_recent = lambda r: r["fy"] >= prev_quarter_end(prev_quarter_end(r["t"]))   # FY end within ~6 months
    return {"changed_n": len(ch), "unchanged_n": len(un),
            "new_annual_figures_this_quarter": {"changed": share(ch, new_fy), "unchanged": share(un, new_fy)},
            "fiscal_year_end_within_two_quarters": {"changed": share(ch, fy_recent), "unchanged": share(un, fy_recent)},
            "changed_by_size_of_move": dict(collections.Counter(abs(r["delta"]) for r in ch))}


# ----------------------------------------------------------------------------- report

def gap_tables(rows):
    res = [r["lab"] - r["raw"] for r in rows]
    by_bucket, by_era = {}, {}
    for b in ["Aaa", "Aa", "A", "Baa", "Ba", "B", "Caa", "Ca", "C"]:
        sub = [r["lab"] - r["raw"] for r in rows if bucket(r["lab"]) == b]
        if sub:
            by_bucket[b] = {"n": len(sub), "mean": round(statistics.mean(sub), 2),
                            "median": statistics.median(sub), "sd": round(statistics.pstdev(sub), 2)}
    for era, name in ((False, "no operating-lease tags"), (True, "operating-lease tags")):
        sub = [r["lab"] - r["raw"] for r in rows if r["lease"] == era]
        if sub:
            by_era[name] = {"n": len(sub), "mean": round(statistics.mean(sub), 2),
                            "median": statistics.median(sub), "sd": round(statistics.pstdev(sub), 2)}
    by = collections.defaultdict(list)
    for r in rows:
        by[r["slug"]].append(r["lab"] - r["raw"])
    means = {s: statistics.mean(v) for s, v in by.items()}
    within = [x - means[s] for s, v in by.items() for x in v]
    between = [means[r["slug"]] for r in rows]
    total_var = statistics.pvariance(res)
    return {"all": {"n": len(res), "mean": round(statistics.mean(res), 2), "median": statistics.median(res),
                    "sd": round(statistics.pstdev(res), 2),
                    "share_positive": round(sum(x > 0 for x in res) / len(res), 3),
                    "share_exact": round(sum(x == 0 for x in res) / len(res), 3),
                    "share_within_1": round(sum(abs(x) <= 1 for x in res) / len(res), 3)},
            "by_bucket": by_bucket, "by_era": by_era,
            "variance_split": {"between_company_share": round(statistics.pvariance(between) / total_var, 3),
                               "within_company_share": round(statistics.pvariance(within) / total_var, 3),
                               "median_within_company_sd": round(statistics.median(
                                   statistics.pstdev(v) for v in by.values() if len(v) >= 8), 2),
                               "companies": len(by)}}


def md_table(header, rows_):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows_:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def write_summary(cov, gap, level, change, curve, rows, tim):
    L = ["# Scorecard calibration summary",
         "",
         f"*Generated {date.today().isoformat()} by evaluation/pipeline/calibrate_scorecard.py; "
         "reviewed by Codex, directed by Robert Vetter. Verified against the local XBRL and "
         "observation records. Gold excluded before development analysis; threshold-feature "
         "fitting nested within outer training folds. No model calls. "
         f"Seed {SEED}, {FOLDS} folds by company. Retrospective cross-company validation, "
         "not a rolling forecast. Definitions and caveats in the script; study history in "
         "notes/scorecard-calibration.md.*",
         "",
         "## Coverage",
         "",
         md_table(["Item", "Count"], [(k, v) for k, v in sorted(cov.items())]),
         "",
         "## The gap: assigned rating minus quantitative-only scorecard outcome (notches; positive = Moody's rates worse than the numbers)",
         "",
         md_table(["Subset", "n", "mean", "median", "sd"],
                  [("all", gap["all"]["n"], gap["all"]["mean"], gap["all"]["median"], gap["all"]["sd"])] +
                  [(b, v["n"], v["mean"], v["median"], v["sd"]) for b, v in gap["by_bucket"].items()] +
                  [(e, v["n"], v["mean"], v["median"], v["sd"]) for e, v in gap["by_era"].items()]),
         "",
         f"Share of observations where the numbers-only outcome is too good: {gap['all']['share_positive']}; "
         f"exact: {gap['all']['share_exact']}; within one notch: {gap['all']['share_within_1']}.",
         "",
         f"Variance of the gap: between companies {gap['variance_split']['between_company_share']}, within "
         f"companies {gap['variance_split']['within_company_share']} (median within-company sd "
         f"{gap['variance_split']['median_within_company_sd']} notches over {gap['variance_split']['companies']} companies).",
         "",
         "## Level from numbers only (Task A), out-of-fold",
         "",
         md_table(["Channel", "subset", "n", "MAE", "exact", "within 1", "Spearman", "mean signed gap"],
                  [(ch, sub, m["n"], m["mae"], m["exact"], m["within_1"], m["spearman"], m["mean_signed"])
                   for ch, subs in level.items() for sub, m in subs.items()]),
         "",
         "## Change detection from numbers only (Task B), out-of-fold, one-notch rule",
         "",
         md_table(["Signal", "theta per fold", "n", "MAE", "MAE persistence", "changed n", "changed MAE",
                   "lift", "direction correct", "moved on changed", "false alarm on unchanged", "alarms",
                   "precision of alarm", "bootstrap p(beats persistence)"],
                  [(s, m["theta_per_fold"], m["n"], m["mae"], m["mae_persistence"], m["changed"]["n"],
                    m["changed"]["mae"], m["changed"]["lift_notches"], m["changed"]["direction_correct_rate"],
                    m["changed"]["moved_at_all_rate"], m["unchanged"]["false_alarm_rate"], m["alarms"],
                    m["precision_of_alarm"], m["bootstrap_err_minus_persistence"]["p_system_beats_persistence"])
                   for s, m in change.items()]),
         "",
         "Signals: s_q = change of the quantitative aggregate since the previous quarter end; s_a = change since "
         "Moody's last rating action; s_lvl = calibrated level minus current rating; s_anch = s_lvl plus the "
         "company's own mean past residual (needs four prior observations). Threshold theta chosen per fold on "
         "training rows by overall MAE; theta 99 means never alarm (equals persistence).",
         "",
         "## When do the numbers move relative to the rating? (timing bound for annual figures)",
         "",
         md_table(["Condition", "share of changed quarters", "share of unchanged quarters"],
                  [("new annual figures arrived this quarter", tim["new_annual_figures_this_quarter"]["changed"],
                    tim["new_annual_figures_this_quarter"]["unchanged"]),
                   ("latest fiscal year ended within two quarters", tim["fiscal_year_end_within_two_quarters"]["changed"],
                    tim["fiscal_year_end_within_two_quarters"]["unchanged"])]),
         "",
         f"Changed quarters by size of move (notches: count): {tim['changed_by_size_of_move']}.",
         "",
         "## Threshold curves (in sample, for reading the tradeoff only)",
         "",
         "An alarm is a prediction that differs from persistence. Precision = share of alarms that moved the right "
         "way on a quarter that did change; with the one-notch rule a channel beats persistence on MAE only above "
         "one half. Odds = alarm rate on changed quarters divided by alarm rate on unchanged quarters (1 = no signal).",
         ""]
    for s, pts in curve.items():
        L += [f"### {s} (signal available on {pts[0]['n_signal']} of {len(rows)} observations)", "",
              md_table(["theta", "MAE", "alarms", "precision", "odds", "direction-correct recall on changed",
                        "moved on changed", "false alarm on unchanged"],
                       [(p["theta"], p["mae"], p["alarms"], p["precision"], p["odds_vs_unchanged"],
                         p["recall_direction"], p["moved_on_changed"], p["false_alarm"]) for p in pts]),
              ""]
    open(SUMMARY, "w").write("\n".join(L))


def main():
    rows, cov = load_rows()
    fold = folds_by_company(rows)
    level_calibration(rows, fold)
    gap = gap_tables(rows)
    gold = [r for r in rows if r["gold"]]
    level = {}
    for ch, key in (("raw scorecard outcome", "raw"), ("calibrated (pooled)", "cal"),
                    ("calibrated (era-split)", "cal_era"), ("sector prior (train median)", "prior"),
                    ("persistence (context)", "per")):
        level[ch] = {"all": level_metrics(rows, key)}
        for name, subset in (("changed", [r for r in rows if r["changed"]]),
                             ("unchanged", [r for r in rows if not r["changed"]])):
            if subset:
                level[ch][name] = level_metrics(subset, key)
        if gold:
            level[ch]["gold"] = level_metrics(gold, key)
    change, curve = change_detection(rows, fold)
    tim = timing(rows)
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({"seed": SEED, "folds": FOLDS, "coverage": dict(cov), "gap": gap, "level": level,
               "change": change, "curve": curve, "timing": tim},
              open(os.path.join(OUT_DIR, "scores.json"), "w"), indent=1)
    json.dump(rows, open(os.path.join(OUT_DIR, "rows.json"), "w"))
    write_summary(cov, gap, level, change, curve, rows, tim)
    print(json.dumps({"coverage": dict(cov), "gap_all": gap["all"], "by_bucket": gap["by_bucket"],
                      "by_era": gap["by_era"], "variance": gap["variance_split"], "timing": tim}, indent=1))
    print(json.dumps(level, indent=1))
    for s, m in change.items():
        print(s, json.dumps({k: v for k, v in m.items() if k != "bootstrap_err_minus_persistence"}),
              "p_beats", m["bootstrap_err_minus_persistence"]["p_system_beats_persistence"])
    print(f"\ngeschrieben: {SUMMARY}, {OUT_DIR}/scores.json, {OUT_DIR}/rows.json")


if __name__ == "__main__":
    main()
