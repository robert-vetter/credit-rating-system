"""
Experiment 07: how often and how much Moody's Retail and Apparel ratings change, 2012 to 2025.

Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Implements section 8
(definitions) and section 9 (tables T1 to T8) of README.md in this folder. No model call, no
network, no spend.

Inputs: evaluation/companies/*/observations.json and ratings.json, read as built. The label
rule and rating lines are imported from evaluation/pipeline/build_observations.py so that the
study reads the files exactly as the labels were made.

Outputs, in a new folder that must not exist yet: experiments/07-rating-change-base-rates/runs/<run_id>/
    manifest.json   SHA-256 of every input file and of this script, the cohort, the seed
    results.json    every table as data
    tables.md       every table as Markdown, the source for results.md

Run from the repository root:
    python3 experiments/07-rating-change-base-rates/run_study.py R1-2026-09-26
    python3 experiments/07-rating-change-base-rates/run_study.py R2-2026-09-26 <withdrawn_dir>
The second form (amendment 0.3) adds the withdrawn-rating companies built by build_withdrawn.py;
the primary cohort is then every in-scope company, active or withdrawn.
"""
import hashlib
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
from build_observations import GRID, lines_of  # noqa: E402

COMPANIES = os.path.join(ROOT, "evaluation", "companies")
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260926
BOOT = 2000

SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]
CATS = ["Aaa", "Aa", "A", "Baa", "Ba", "B", "Caa", "Ca-C"]
QI = {t: i for i, t in enumerate(GRID)}


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def category(r):
    n = notch(r)
    if n is None:
        return None
    if n == 0:
        return "Aaa"
    if n >= 19:
        return "Ca-C"
    return CATS[(n - 1) // 3 + 1]


def investment_grade(r):
    n = notch(r)
    return None if n is None else n <= SCALE.index("Baa3")


# ----------------------------------------------------------------------------- per company

def label_actions(ent, sen, level, oi, start, end):
    """Distinct (date, rating) UP/DG actions in (start, end] on the line that carries the label."""
    lines = ent if level == "entity" else sen
    acts = set()
    for line in lines:
        if line["oi"] != oi:
            continue
        for r in line["recs"]:
            if r.get("RAC") in ("UP", "DG") and start < r["RAD"] <= end:
                acts.add((r["RAD"], r["R"]))
    return acts


def company_records(slug, obs_doc, ratings):
    """Quarterly records plus per-company facts, from one company's files."""
    obs = {o["date"]: o for o in obs_doc["observations"]}
    ent, sen = lines_of(ratings) if ratings else ([], [])
    quarters = []
    for t in GRID:
        o = obs.get(t)
        if not o or o["changed"] is None:
            continue
        prev = obs[GRID[QI[t] - 1]]
        a, b = notch(prev["label"]), notch(o["label"])
        delta = None if a is None or b is None else b - a
        acts = label_actions(ent, sen, o["label_level"], o["label_oi"], GRID[QI[t] - 1], t)
        quarters.append({
            "company": slug, "date": t, "year": int(t[:4]),
            "prev": prev["label"], "cur": o["label"],
            "changed": bool(o["changed"]), "delta": delta,
            "level_switch": o["label_level"] != prev["label_level"],
            "source_switch": o["label_oi"] != prev["label_oi"],
            "ambiguous": bool(o["label_ambiguous"] or prev["label_ambiguous"]),
            "actions": len(acts),
        })
    dates = sorted(obs)
    span = GRID[QI[dates[0]]:QI[dates[-1]] + 1] if dates else []
    gaps = [t for t in span if t not in obs]
    return {
        "slug": slug, "scope": obs_doc["scope"], "labelled": dates, "gaps": gaps,
        "ends_early": bool(dates) and dates[-1] < GRID[-1],
        "quarters": quarters,
    }


def forward_windows(c, width=4):
    """For each labelled quarter t: did the label change in the next `width` quarters?
    Only windows where all `width` following quarters are quarterly records are kept;
    the rest are censored (end of grid, gap, withdrawal)."""
    by_date = {q["date"]: q for q in c["quarters"]}
    out, censored = [], 0
    for t in c["labelled"]:
        i = QI[t]
        nxt = GRID[i + 1:i + 1 + width]
        if len(nxt) < width or any(d not in by_date for d in nxt):
            censored += 1
            continue
        qs = [by_date[d] for d in nxt]
        out.append({
            "company": c["slug"], "date": t, "label": None,
            "changed": any(q["changed"] for q in qs),
            "deltas": [q["delta"] for q in qs if q["changed"]],
            "level_switch": any(q["level_switch"] for q in qs),
            "ambiguous": any(q["ambiguous"] for q in qs),
        })
    return out, censored


def lag_pairs(c, obs_doc, lag, q4_only=False):
    """Label at t against the label `lag` quarters earlier, both labelled."""
    obs = {o["date"]: o for o in obs_doc["observations"]}
    out = []
    for t in c["labelled"]:
        if q4_only and not t.endswith("12-31"):
            continue
        i = QI[t] - lag
        if i < 0 or GRID[i] not in obs:
            continue
        p, o = obs[GRID[i]], obs[t]
        a, b = notch(p["label"]), notch(o["label"])
        out.append({
            "company": c["slug"], "date": t, "prev": p["label"], "cur": o["label"],
            "changed": p["label"] != o["label"],
            "delta": None if a is None or b is None else b - a,
            "level_switch": p["label_level"] != o["label_level"],
            "ambiguous": bool(p["label_ambiguous"] or o["label_ambiguous"]),
        })
    return out


# ----------------------------------------------------------------------------- statistics

def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - half, centre + half)


def bootstrap_by_company(rows, rng):
    """Pooled change rate, companies resampled with replacement."""
    groups = defaultdict(lambda: [0, 0])
    for r in rows:
        groups[r["company"]][0] += r["changed"]
        groups[r["company"]][1] += 1
    keys = sorted(groups)
    if not keys:
        return (None, None)
    rates = []
    for _ in range(BOOT):
        k = n = 0
        for _ in keys:
            g = groups[rng.choice(keys)]
            k += g[0]
            n += g[1]
        rates.append(k / n if n else 0.0)
    rates.sort()
    return (rates[int(0.025 * BOOT)], rates[int(0.975 * BOOT) - 1])


def rate_row(name, rows, direction_from="delta"):
    n = len(rows)
    k = sum(r["changed"] for r in rows)
    if direction_from == "delta":
        up = sum(1 for r in rows if r["changed"] and r["delta"] is not None and r["delta"] < 0)
        down = sum(1 for r in rows if r["changed"] and r["delta"] is not None and r["delta"] > 0)
    else:
        up = sum(1 for r in rows if r["changed"] and any(d is not None and d < 0 for d in r["deltas"]))
        down = sum(1 for r in rows if r["changed"] and any(d is not None and d > 0 for d in r["deltas"]))
    lo, hi = wilson(k, n)
    return {"row": name, "n": n, "changed": k, "rate": k / n if n else None,
            "wilson_lo": lo, "wilson_hi": hi, "upgrades": up, "downgrades": down}


def precision(base, sens, spec):
    tp = sens * base
    fp = (1 - spec) * (1 - base)
    return tp / (tp + fp) if tp + fp else None


# ----------------------------------------------------------------------------- the study

def load(extra_dir=None):
    companies = []
    for base, origin in ((COMPANIES, "active"), (extra_dir, "withdrawn")):
        if not base:
            continue
        for slug in sorted(os.listdir(base)):
            op = os.path.join(base, slug, "observations.json")
            rp = os.path.join(base, slug, "ratings.json")
            if not os.path.exists(op):
                continue
            obs_doc = json.load(open(op))
            obs_doc["origin"] = origin
            ratings = json.load(open(rp)) if os.path.exists(rp) else None
            companies.append((slug, obs_doc, ratings, op, rp))
    return companies


def analyse(companies, cohort_filter):
    rng = random.Random(SEED)
    cs, docs = [], {}
    for slug, obs_doc, ratings, _, _ in companies:
        if not cohort_filter(obs_doc):
            continue
        c = company_records(slug, obs_doc, ratings)
        cs.append(c)
        docs[slug] = obs_doc
    Q = [q for c in cs for q in c["quarters"]]
    F, censored = [], 0
    for c in cs:
        f, k = forward_windows(c)
        F += f
        censored += k
    A = [p for c in cs for p in lag_pairs(c, docs[c["slug"]], 4, q4_only=True)]
    T3y = [p for c in cs for p in lag_pairs(c, docs[c["slug"]], 12)]

    t1 = [rate_row("quarter", Q), rate_row("year (Q4 to Q4)", A),
          rate_row("within the next 12 months", F, "deltas"), rate_row("three years", T3y)]
    t1[0]["boot_lo"], t1[0]["boot_hi"] = bootstrap_by_company(Q, rng)
    t1[2]["boot_lo"], t1[2]["boot_hi"] = bootstrap_by_company(F, rng)
    t1[2]["censored"] = censored

    sens = {
        "level switches excluded, quarter": rate_row("quarter", [q for q in Q if not q["level_switch"]]),
        "ambiguous excluded, quarter": rate_row("quarter", [q for q in Q if not q["ambiguous"]]),
        "level switches excluded, 12 months": rate_row("12 months", [f for f in F if not f["level_switch"]], "deltas"),
        "ambiguous excluded, 12 months": rate_row("12 months", [f for f in F if not f["ambiguous"]], "deltas"),
    }

    ch = [q for q in Q if q["changed"]]
    size = Counter()
    for q in ch:
        d = q["delta"]
        if d is None or d == 0:
            size[("unknown or zero", "")] += 1
        else:
            size[("3+" if abs(d) >= 3 else str(abs(d)), "down" if d > 0 else "up")] += 1
    t2 = {"counts": {f"{k[0]}|{k[1]}": v for k, v in sorted(size.items())},
          "mean_abs_notches": (sum(abs(q["delta"]) for q in ch if q["delta"]) /
                               max(1, sum(1 for q in ch if q["delta"])))}

    by_cat = defaultdict(list)
    for q in Q:
        by_cat[category(q["prev"])].append(q)
    fwd_cat = defaultdict(list)
    lab = {(c["slug"], o["date"]): o["label"] for c in cs for o in docs[c["slug"]]["observations"]}
    for f in F:
        fwd_cat[category(lab[(f["company"], f["date"])])].append(f)
    t3 = [dict(rate_row(cat, by_cat[cat]),
               fwd12=rate_row(cat, fwd_cat[cat], "deltas")) for cat in CATS if by_cat.get(cat)]
    ig = [q for q in Q if investment_grade(q["prev"])]
    sg = [q for q in Q if investment_grade(q["prev"]) is False]
    t3_grade = [rate_row("investment grade", ig), rate_row("speculative grade", sg)]
    fig = [f for f in F if investment_grade(lab[(f["company"], f["date"])])]
    fsg = [f for f in F if investment_grade(lab[(f["company"], f["date"])]) is False]
    t3_grade_fwd = [rate_row("investment grade", fig, "deltas"), rate_row("speculative grade", fsg, "deltas")]
    matrix = defaultdict(Counter)
    for p in A:
        matrix[category(p["prev"])][category(p["cur"])] += 1
    t3_matrix = {r: dict(matrix[r]) for r in CATS if matrix.get(r)}

    t4 = []
    for c in cs:
        qs = c["quarters"]
        chs = [q for q in qs if q["changed"]]
        t4.append({"company": c["slug"], "scope": c["scope"], "quarters": len(qs),
                   "changes": len(chs),
                   "upgrades": sum(1 for q in chs if q["delta"] is not None and q["delta"] < 0),
                   "downgrades": sum(1 for q in chs if q["delta"] is not None and q["delta"] > 0),
                   "largest_move": max((abs(q["delta"]) for q in chs if q["delta"]), default=0)})
    t4.sort(key=lambda r: (-r["changes"], r["company"]))
    total_changes = sum(r["changes"] for r in t4)
    with_quarters = [r for r in t4 if r["quarters"] > 0]
    never = sorted(r["company"] for r in with_quarters if r["changes"] == 0)
    top10 = sum(r["changes"] for r in t4[:10])
    active = sorted((r["changes"] / r["quarters"] for r in with_quarters))
    t4_summary = {"companies_with_quarters": len(with_quarters), "never_changed": never,
                  "top10_share": top10 / total_changes if total_changes else None,
                  "companies_with_any_change": sum(1 for r in with_quarters if r["changes"]),
                  "median_company_rate": active[len(active) // 2] if active else None}

    by_year = defaultdict(list)
    for q in Q:
        by_year[q["year"]].append(q)
    t5 = [rate_row(str(y), by_year[y]) for y in sorted(by_year)]

    fq = {(q["company"], q["date"]): q for q in Q}
    after_change, after_none = [], []
    for q in Q:
        nxt = GRID[QI[q["date"]] + 1:QI[q["date"]] + 5]
        if len(nxt) < 4 or any((q["company"], d) not in fq for d in nxt):
            continue
        later = [fq[(q["company"], d)] for d in nxt if fq[(q["company"], d)]["changed"]]
        rec = {"company": q["company"], "changed": bool(later), "delta": None}
        if q["changed"] and q["delta"]:
            sign = 1 if q["delta"] > 0 else -1
            rec["same"] = any(l["delta"] and (l["delta"] > 0) == (sign > 0) for l in later)
            rec["reverse"] = any(l["delta"] and (l["delta"] > 0) != (sign > 0) for l in later)
            after_change.append(rec)
        elif not q["changed"]:
            after_none.append(rec)
    t6 = {"after_change": rate_row("after a change", after_change),
          "after_change_same_direction": sum(r["same"] for r in after_change),
          "after_change_reversal": sum(r["reverse"] for r in after_change),
          "after_no_change": rate_row("after no change", after_none)}
    for key in ("after_change", "after_no_change"):
        t6[key].pop("upgrades"), t6[key].pop("downgrades")

    t7 = {
        "quarterly_records": len(Q),
        "level_switches": sum(q["level_switch"] for q in Q),
        "level_switches_with_change": sum(q["level_switch"] and q["changed"] for q in Q),
        "source_switches": sum(q["source_switch"] for q in Q),
        "source_switches_with_change": sum(q["source_switch"] and q["changed"] for q in Q),
        "ambiguous_records": sum(q["ambiguous"] for q in Q),
        "changes_with_unknown_or_zero_size": sum(1 for q in ch if not q["delta"]),
        "gap_quarters": sum(len(c["gaps"]) for c in cs),
        "companies_label_ends_before_grid_end": sum(c["ends_early"] for c in cs),
        "rating_actions_on_label_line": sum(q["actions"] for q in Q),
        "quarters_with_action_but_no_grid_change": sum(1 for q in Q if q["actions"] and not q["changed"]),
        "quarters_with_2plus_actions": sum(1 for q in Q if q["actions"] >= 2),
        "grid_changes_without_action_on_label_line": sum(1 for q in ch if not q["actions"]),
        "grid_changes_without_action_and_no_switch": sum(1 for q in ch if not q["actions"]
                                                         and not q["level_switch"] and not q["source_switch"]),
        "censored_forward_windows": censored,
    }

    t8 = {"changed_quarters": len(ch),
          "companies_with_a_change": t4_summary["companies_with_any_change"],
          "positive_12m_windows": sum(f["changed"] for f in F),
          "negative_12m_windows": sum(not f["changed"] for f in F),
          "precision_examples": [
              {"base": name, "rate": row["rate"], "sensitivity": s, "specificity": sp,
               "precision": precision(row["rate"], s, sp)}
              for name, row in (("quarter", t1[0]), ("within 12 months", t1[2]))
              for s, sp in ((0.9, 0.9), (0.8, 0.95))]}

    ended = []
    for c in cs:
        if not c["ends_early"]:
            continue
        last = docs[c["slug"]]["observations"][-1]
        before = [q for q in c["quarters"] if GRID[QI[last["date"]] - 4] < q["date"] <= last["date"]]
        ended.append({"company": c["slug"], "last_date": last["date"], "last_label": last["label"],
                      "category": category(last["label"]),
                      "downgrades_4q_before": sum(1 for q in before if q["changed"] and (q["delta"] or 0) > 0),
                      "upgrades_4q_before": sum(1 for q in before if q["changed"] and (q["delta"] or 0) < 0)})
    t9 = {"companies": ended,
          "by_category": dict(Counter(e["category"] for e in ended)),
          "by_year": dict(sorted(Counter(e["last_date"][:4] for e in ended).items()))}

    return {"companies": len(cs), "T9": t9, "T1": t1, "sensitivities": sens, "T2": t2, "T3": t3,
            "T3_grade": t3_grade, "T3_grade_fwd12": t3_grade_fwd, "T3_matrix": t3_matrix,
            "T4": t4, "T4_summary": t4_summary, "T5": t5, "T6": t6, "T7": t7, "T8": t8}


# ----------------------------------------------------------------------------- output

def pct(x):
    return "" if x is None else f"{100 * x:.1f}%"


def ci(r, lo="wilson_lo", hi="wilson_hi"):
    return "" if r.get(lo) is None else f"{pct(r[lo])} to {pct(r[hi])}"


def to_markdown(res, comparisons):
    L = []
    w = L.append
    w("## T1 Base rate by horizon (primary: in-scope companies)\n")
    w("| Horizon | n | Changed | Rate | 95% Wilson | 95% company bootstrap | Upgrades | Downgrades |")
    w("|---|---|---|---|---|---|---|---|")
    for r in res["T1"]:
        w(f"| {r['row']} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {ci(r)} | "
          f"{ci(r, 'boot_lo', 'boot_hi')} | {r['upgrades']} | {r['downgrades']} |")
    w(f"\nForward 12-month windows censored (end of grid, gap or withdrawal): {res['T1'][2]['censored']}.\n")
    w("### Sensitivities\n")
    w("| Variant | n | Changed | Rate | 95% Wilson |")
    w("|---|---|---|---|---|")
    for k, r in res["sensitivities"].items():
        w(f"| {k} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {ci(r)} |")
    for name, alt in comparisons:
        for r in alt["T1"]:
            w(f"| {name}, {r['row']} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {ci(r)} |")
    w("\n## T2 Size of quarterly changes\n")
    w("| Notches | Direction | Changes |")
    w("|---|---|---|")
    for k, v in res["T2"]["counts"].items():
        a, b = k.split("|")
        w(f"| {a} | {b} | {v} |")
    w(f"\nMean absolute size: {res['T2']['mean_abs_notches']:.2f} notches.\n")
    w("## T3 By rating category at the start of the quarter\n")
    w("| Category | Quarters | Changed | Quarterly rate | Upgrades | Downgrades | 12-month windows | 12-month rate |")
    w("|---|---|---|---|---|---|---|---|")
    for r in res["T3"]:
        f = r["fwd12"]
        w(f"| {r['row']} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {r['upgrades']} | "
          f"{r['downgrades']} | {f['n']} | {pct(f['rate'])} |")
    for r, f in zip(res["T3_grade"], res["T3_grade_fwd12"]):
        w(f"| {r['row']} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {r['upgrades']} | "
          f"{r['downgrades']} | {f['n']} | {pct(f['rate'])} |")
    w("\n### One-year transitions between categories (Q4 to Q4, counts)\n")
    cols = [c for c in CATS if any(c in row for row in res["T3_matrix"].values())]
    w("| From \\ to | " + " | ".join(cols) + " |")
    w("|---|" + "---|" * len(cols))
    for r, row in res["T3_matrix"].items():
        w(f"| {r} | " + " | ".join(str(row.get(c, "")) for c in cols) + " |")
    s = res["T4_summary"]
    w("\n## T4 By company\n")
    w(f"Companies with quarterly records: {s['companies_with_quarters']}. With at least one change: "
      f"{s['companies_with_any_change']}. Never changed: {len(s['never_changed'])} "
      f"({', '.join(s['never_changed'])}). Share of all changes from the ten most active companies: "
      f"{pct(s['top10_share'])}. Median company change rate per quarter: {pct(s['median_company_rate'])}.\n")
    w("| Company | Scope | Quarters | Changes | Upgrades | Downgrades | Largest move |")
    w("|---|---|---|---|---|---|---|")
    for r in res["T4"]:
        w(f"| {r['company']} | {r['scope']} | {r['quarters']} | {r['changes']} | {r['upgrades']} | "
          f"{r['downgrades']} | {r['largest_move']} |")
    w("\n## T5 By year\n")
    w("| Year | Quarters | Changed | Rate | Upgrades | Downgrades |")
    w("|---|---|---|---|---|---|")
    for r in res["T5"]:
        w(f"| {r['row']} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {r['upgrades']} | {r['downgrades']} |")
    t6 = res["T6"]
    w("\n## T6 Follow-on changes within four quarters\n")
    w("| Starting quarter | n | Change in the next 4 quarters | Rate | 95% Wilson |")
    w("|---|---|---|---|---|")
    for k in ("after_change", "after_no_change"):
        r = t6[k]
        w(f"| {r['row']} | {r['n']} | {r['changed']} | {pct(r['rate'])} | {ci(r)} |")
    w(f"\nAfter a change: same direction again {t6['after_change_same_direction']}, "
      f"reversal {t6['after_change_reversal']}.\n")
    w("## T7 Data artefacts\n")
    w("| Item | Count |")
    w("|---|---|")
    for k, v in res["T7"].items():
        w(f"| {k.replace('_', ' ')} | {v} |")
    t8 = res["T8"]
    w("\n## T8 What this means for a balanced test set\n")
    w("| Item | Value |")
    w("|---|---|")
    for k in ("changed_quarters", "companies_with_a_change", "positive_12m_windows", "negative_12m_windows"):
        w(f"| {k.replace('_', ' ')} | {t8[k]} |")
    w("\n| Base rate | Rate | Sensitivity | Specificity | Precision of an alarm |")
    w("|---|---|---|---|---|")
    for e in t8["precision_examples"]:
        w(f"| {e['base']} | {pct(e['rate'])} | {e['sensitivity']:.0%} | {e['specificity']:.0%} | {pct(e['precision'])} |")
    t9 = res.get("T9")
    if t9 is not None:
        w("\n## T9 Companies whose label ends before 2025-06-30\n")
        w(f"Companies: {len(t9['companies'])}.\n")
        w("| Last rating category | Companies |")
        w("|---|---|")
        for k in CATS:
            if k in t9["by_category"]:
                w(f"| {k} | {t9['by_category'][k]} |")
        w("\n| Year the label ends | Companies |")
        w("|---|---|")
        for k, v in t9["by_year"].items():
            w(f"| {k} | {v} |")
        w("\n| Company | Last labelled quarter | Last rating | Downgrades in the 4 quarters before | Upgrades |")
        w("|---|---|---|---|---|")
        for e in sorted(t9["companies"], key=lambda e: e["last_date"]):
            w(f"| {e['company']} | {e['last_date']} | {e['last_label']} | {e['downgrades_4q_before']} | {e['upgrades_4q_before']} |")
    return "\n".join(L) + "\n"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(run_id, extra_dir=None):
    out = os.path.join(HERE, "runs", run_id)
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")
    companies = load(extra_dir)
    primary = analyse(companies, lambda d: d["scope"] == "in")
    if extra_dir:
        comparisons = [
            ("survivors only (R1 cohort)", analyse(companies, lambda d: d["scope"] == "in" and d["origin"] == "active")),
            ("withdrawn-rating companies only", analyse(companies, lambda d: d["scope"] == "in" and d["origin"] == "withdrawn")),
            ("all groups regardless of scope", analyse(companies, lambda d: True)),
        ]
    else:
        comparisons = [("all 86 companies", analyse(companies, lambda d: True))]
    os.makedirs(out)
    manifest = {
        "run_id": run_id, "seed": SEED, "bootstrap": BOOT,
        "script_sha256": sha(os.path.abspath(__file__)),
        "builder_sha256": sha(os.path.join(ROOT, "evaluation", "pipeline", "build_observations.py")),
        "cohort_primary": sorted(s for s, d, *_ in companies if d["scope"] == "in"),
        "cohort_all": sorted(s for s, *_ in companies),
        "inputs": {os.path.relpath(p, ROOT): sha(p) for _, _, _, op, rp in companies
                   for p in (op, rp) if os.path.exists(p)},
    }
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    manifest["extra_dir"] = os.path.relpath(extra_dir, ROOT) if extra_dir else None
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    json.dump({"primary_in_scope": primary, **{n: r for n, r in comparisons}},
              open(os.path.join(out, "results.json"), "w"), indent=1)
    open(os.path.join(out, "tables.md"), "w").write(to_markdown(primary, comparisons))
    print(f"wrote {out}: {len(manifest['inputs'])} input files hashed")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(sys.argv[1], os.path.abspath(sys.argv[2]) if len(sys.argv) == 3 else None)
