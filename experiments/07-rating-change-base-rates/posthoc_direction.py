"""
Experiment 07, post-hoc diagnostic added 2026-09-26 after reading run R1 (not in the
specification). Question: how many quarterly changes point in a different direction from every
rating action on the label line that quarter, or have no action at all? Found by inspecting
Albertsons 2015, where the label moved between Albertsons and Safeway bonds.

Written by Claude (Opus 5.5), directed by Robert Vetter. Reads the same inputs as run_study.py;
writes runs/<run_id>/posthoc_direction.json and prints a table. Refuses to overwrite.
    python3 experiments/07-rating-change-base-rates/posthoc_direction.py R1-2026-09-26
    python3 experiments/07-rating-change-base-rates/posthoc_direction.py R2-2026-09-26 <withdrawn_dir>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_study as S  # noqa: E402
from build_observations import GRID, lines_of  # noqa: E402


def classify(companies):
    rows = []
    for slug, doc, ratings, _, _ in companies:
        if doc["scope"] != "in":
            continue
        ent, sen = lines_of(ratings) if ratings else ([], [])
        c = S.company_records(slug, doc, ratings)
        obs = {o["date"]: o for o in doc["observations"]}
        for q in c["quarters"]:
            if not q["changed"]:
                continue
            o = obs[q["date"]]
            prev_t = GRID[S.QI[q["date"]] - 1]
            lines = ent if o["label_level"] == "entity" else sen
            racs = {r["RAC"] for line in lines if line["oi"] == o["label_oi"]
                    for r in line["recs"] if r.get("RAC") in ("UP", "DG") and prev_t < r["RAD"] <= q["date"]}
            grid = "DG" if q["delta"] > 0 else "UP"
            if not racs:
                kind = "no action on the label line"
            elif racs == {grid}:
                kind = "agrees with the action"
            elif grid in racs:
                kind = "mixed actions"
            else:
                kind = "contradicts the action"
            rows.append({"company": slug, "date": q["date"], "prev": q["prev"], "cur": q["cur"],
                         "delta": q["delta"], "actions": sorted(racs), "kind": kind,
                         "level_switch": q["level_switch"], "source_switch": q["source_switch"]})
    return rows


def main(run_id, extra_dir=None):
    out = os.path.join(S.HERE, "runs", run_id, "posthoc_direction.json")
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")
    rows = classify(S.load(extra_dir))
    json.dump(rows, open(out, "w"), indent=1)
    kinds = {}
    for r in rows:
        kinds.setdefault(r["kind"], []).append(r)
    print("| Kind | Changes | Upgrades | Downgrades | With a level or source switch |")
    print("|---|---|---|---|---|")
    for k, rs in sorted(kinds.items()):
        print(f"| {k} | {len(rs)} | {sum(r['delta'] < 0 for r in rs)} | {sum(r['delta'] > 0 for r in rs)} | "
              f"{sum(r['level_switch'] or r['source_switch'] for r in rs)} |")
    for r in rows:
        if r["kind"] != "agrees with the action":
            print(r["company"], r["date"], r["prev"], "->", r["cur"], r["actions"], r["kind"],
                  "switch" if r["level_switch"] or r["source_switch"] else "")


if __name__ == "__main__":
    main(sys.argv[1], os.path.abspath(sys.argv[2]) if len(sys.argv) == 3 else None)
