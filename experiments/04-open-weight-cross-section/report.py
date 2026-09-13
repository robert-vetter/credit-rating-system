"""
Markdown tables for results.md from the scored run (runs/<run>/results/scores.json and the
ledger). Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-13. Offline.

    python3 experiments/04-open-weight-cross-section/report.py [run_dir]
"""
import json
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_openrouter as ro   # noqa: E402

RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "runs", "EXP04-ARM1-A1")


def pct(a, b):
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "n/a"


def channel_row(name, m, cohort_n):
    """One table row for a channel block from ro.metrics()."""
    mv = m["metrics_on_valid"]
    if not mv:
        return f"| {name} | 0/{cohort_n} | n/a | n/a | n/a |"
    return (f"| {name} | {m['n_valid']}/{cohort_n} | {pct(m['exact_over_planned'], cohort_n)} "
            f"| {pct(round(mv['within_1'] * mv['n']), mv['n'])} | {mv['mae']:.2f} |")


def persistence_row(p, cohort_n):
    return (f"| Persistence | {p['n']}/{cohort_n} | {pct(round(p['exact_rate'] * p['n']), p['n'])} "
            f"| {pct(round(p['within_1'] * p['n']), p['n'])} | {p['mae']:.2f} |")


def block(title, arm_scores, cohort, cohort_n):
    lines = [f"**{title}**", "", "| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) |",
             "|---|---|---|---|---|"]
    for k in ("r1", "r2", "r3"):
        m = arm_scores["replicates"][k][cohort]
        lines.append(channel_row(f"Scorecard, replicate {k[1]}", m["pred_scorecard"], cohort_n))
    lines.append(channel_row("Scorecard, consensus (median of 3)", arm_scores["consensus"][cohort]["pred_scorecard"], cohort_n))
    for k in ("r1", "r2", "r3"):
        m = arm_scores["replicates"][k][cohort]
        lines.append(channel_row(f"Judgement, replicate {k[1]}", m["pred_direct"], cohort_n))
    lines.append(channel_row("Judgement, consensus (median of 3)", arm_scores["consensus"][cohort]["pred_direct"], cohort_n))
    lines.append(persistence_row(arm_scores["replicates"]["r1"][cohort]["persistence_full_cohort"], cohort_n))
    return "\n".join(lines) + "\n"


def diagnostics(run, arm, ids, labels):
    """Changed and unchanged diagnostics per replicate and consensus, counted from the records."""
    reps = {f"replicate {k}": json.load(open(os.path.join(run, "results", f"results_{arm}_r{k}.json"))) for k in (1, 2, 3)}
    reps["consensus"] = json.load(open(os.path.join(run, "results", f"results_{arm}_consensus.json")))
    lines = ["| Channel | Changed valid | Changed exact | Direction correct | Unchanged valid | False alarms |", "|---|---|---|---|---|---|"]
    for ch, name in (("pred_scorecard", "Scorecard"), ("pred_direct", "Judgement")):
        for k, recs in reps.items():
            rows = [r for r in recs if r["id"] in ids and ro.notch(r[ch]) is not None]
            chg = [r for r in rows if r["changed"]]
            unc = [r for r in rows if not r["changed"]]
            exact = sum(ro.notch(r[ch]) == ro.notch(r["label"]) for r in chg)
            direction = sum((ro.notch(r[ch]) - ro.notch(r["persistence"])) * (ro.notch(r["label"]) - ro.notch(r["persistence"])) > 0 for r in chg)
            fa = sum(ro.notch(r[ch]) != ro.notch(r["persistence"]) for r in unc)
            lines.append(f"| {name}, {k} | {len(chg)} | {exact} | {direction} | {len(unc)} | {fa} |")
    return "\n".join(lines) + "\n"


def per_issuer(run, arm, ids, labels):
    reps = [json.load(open(os.path.join(run, "results", f"results_{arm}_r{k}.json"))) for k in (1, 2, 3)]
    cons = {c["id"]: c for c in json.load(open(os.path.join(run, "results", f"results_{arm}_consensus.json")))}
    lines = ["| ID | Issuer | Persistence | Label | Scorecard r1, r2, r3 | Scorecard consensus | Judgement r1, r2, r3 | Judgement consensus | FY label |",
             "|---|---|---|---|---|---|---|---|---|"]
    for xid in ids:
        rs = [next(r for r in rep if r["id"] == xid) for rep in reps]
        c = cons[xid]
        sc = ", ".join(str(r["pred_scorecard"] or ("fail" if r.get("scorecard_failure") else "none")) for r in rs)
        dj = ", ".join(str(r["pred_direct"] or "none") for r in rs)
        fy = sorted({str(r.get("fiscal_year_label")) for r in rs if r.get("fiscal_year_label")})
        lab = labels[xid]
        lines.append(f"| {xid} | {rs[0].get('slug', xid)} | {lab['persistence']} | {lab['label']}{' (changed)' if lab['changed'] else ''} "
                     f"| {sc} | {c['pred_scorecard'] or c.get('pred_scorecard_consensus')} | {dj} | {c['pred_direct'] or c.get('pred_direct_consensus')} | {'; '.join(fy)} |")
    return "\n".join(lines) + "\n"


def main():
    s = json.load(open(os.path.join(RUN, "results", "scores.json")))
    manifest = json.load(open(os.path.join(RUN, "manifest.json")))
    attempts = json.load(open(os.path.join(RUN, "results", "attempts.json")))
    labels = manifest["cohort"]["labels"]
    ids, primary, saved = manifest["cohort"]["ids"], manifest["cohort"]["primary_ids"], manifest["cohort"]["saved_arm_ids"]
    six = [x for x in saved if x not in manifest["cohort"]["diagnostic_ids"]]
    slug = {r["issuer_id"]: r["slug"] for r in manifest["requests"]}
    for arm in ("current", "saved"):
        for k in (1, 2, 3):
            p = os.path.join(RUN, "results", f"results_{arm}_r{k}.json")
            recs = json.load(open(p))
            for r in recs:
                r["slug"] = slug[r["id"]]
            json.dump(recs, open(p, "w"), indent=1)
    out = []
    out.append("## Attempts and spend\n")
    counts = s["attempt_status_counts"]
    out.append(f"Dispatches {s['spend']['dispatches']} (planned 101, extra attempts {s['spend']['extra_attempts']}); "
               f"status counts {json.dumps(counts)}; committed ${s['spend']['committed_usd']}, unresolved ${s['spend']['unresolved_usd']}.\n")
    bad = [a for a in attempts if a["status"] != "valid"]
    if bad:
        out.append("| Attempt | Status | Reason | Charge |\n|---|---|---|---|")
        for a in bad:
            out.append(f"| {a['attempt_id']} | {a['status']} | {a.get('reason')} | {a.get('charge_usd')} |")
        out.append("")
    out.append("## Current inputs, all 20 issuers (legacy sensitivity including Qurate)\n")
    out.append(block("All 20", s["arms"]["current"], "all", 20))
    out.append("## Current inputs, primary cohort of 19 (Qurate excluded)\n")
    out.append(block("19 primary", s["arms"]["current"], "primary_without_diagnostic", 19))
    out.append("## Saved Experiment 03 inputs, the seven Opus successes\n")
    out.append(block("Seven", s["arms"]["saved"], "all", 7))
    out.append(block("Six without Qurate", s["arms"]["saved"], "primary_without_diagnostic", 6))
    o7, o6 = s["opus46_corrected_saved_inputs"]["seven"], s["opus46_corrected_saved_inputs"]["six_without_diagnostic"]
    out.append("**Opus 4.6 on the same saved inputs (Experiment 03, corrected arithmetic, one response each)**\n")
    out.append("| Channel | Valid / planned | Exact | Within one | MAE |\n|---|---|---|---|---|")
    out.append(channel_row("Scorecard, seven", o7["pred_scorecard"], 7))
    out.append(channel_row("Judgement, seven", o7["pred_direct"], 7))
    out.append(persistence_row(o7["persistence_full_cohort"], 7))
    out.append(channel_row("Scorecard, six", o6["pred_scorecard"], 6))
    out.append(channel_row("Judgement, six", o6["pred_direct"], 6))
    out.append(persistence_row(o6["persistence_full_cohort"], 6) + "\n")
    out.append("## Changed and unchanged diagnostics, current inputs, 19 primary\n")
    out.append(diagnostics(RUN, "current", primary, labels))
    out.append("## Changed and unchanged diagnostics, current inputs, all 20\n")
    out.append(diagnostics(RUN, "current", ids, labels))
    out.append("## Changed and unchanged diagnostics, saved inputs, seven\n")
    out.append(diagnostics(RUN, "saved", saved, labels))
    out.append("## Per issuer, current inputs\n")
    out.append(per_issuer(RUN, "current", ids, labels))
    out.append("## Per issuer, saved inputs\n")
    out.append(per_issuer(RUN, "saved", saved, labels))
    out.append("## Replicate spread\n")
    for arm in ("current", "saved"):
        sp = s["arms"][arm]["spread"]
        for ch in ("pred_scorecard", "pred_direct"):
            vals = [v[ch]["spread_notches"] for v in sp.values()]
            n0 = sum(v == 0 for v in vals); n1 = sum(v == 1 for v in vals); nm = sum((v or 0) > 1 for v in vals); nn = sum(v is None for v in vals)
            out.append(f"- {arm} inputs, {'scorecard' if ch == 'pred_scorecard' else 'judgement'}: spread 0 on {n0}, 1 on {n1}, more than 1 on {nm}, undefined on {nn} of {len(vals)} issuers.")
        same_q = sum(v["qualitative_identical"] for v in sp.values())
        out.append(f"- {arm} inputs: qualitative grades identical across the three replicates on {same_q} of {len(sp)} issuers.")
    out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    main()
