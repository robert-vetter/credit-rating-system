"""
Experiment 07, amendment 0.3: rebuild the confirmed groups that compile_folders.py skipped
because none of their members had an active rating at the file end (the withdrawn-rating
companies), so that run R2 is not limited to survivors.

Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Reads evaluation/mapping.json
(read only) and the two Moody's 17g-7 archives under data/moodys/ through compile_folders.entity_history;
applies the label rule of build_observations.py (label_at, lines_of) with the same quarterly loop.
Filings are not needed for this study and are not fetched.

Writes, into a folder that must not exist yet:
    <out>/<slug>/company.json        group, scope, member OIs, origin "withdrawn"
    <out>/<slug>/ratings.json        raw rating history, as compile_folders.py writes it
    <out>/<slug>/observations.json   quarterly labels in the same fields run_study.py reads
Never writes into evaluation/companies/. A group whose slug equals an active folder is skipped
and listed in <out>/_skipped.json.

    python3 experiments/07-rating-change-base-rates/build_withdrawn.py <out_dir>
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
from build_observations import GRID, label_at, lines_of  # noqa: E402
from compile_folders import entity_history, slug  # noqa: E402


def quarterly_labels(ratings):
    """The label part of build_observations.main, field for field."""
    ent, sen = lines_of(ratings)
    obs, prev = [], None
    for t in GRID:
        label, level, oi, amb = label_at(ent, sen, t)
        if label is None:
            prev = None
            continue
        obs.append({"date": t, "quarter": "Q" + str((int(t[5:7]) + 2) // 3),
                    "label": label, "label_level": level, "label_oi": oi,
                    "label_ambiguous": amb, "persistence": prev,
                    "changed": (label != prev) if prev else None})
        prev = label
    return obs


def skipped_groups(items):
    confirmed = [i for i in items if i["kind"] == "moodys" and i["status"] == "confirmed"]
    groups = {}
    for it in confirmed:
        groups.setdefault(it["group"], []).append(it)
    return {g: ms for g, ms in groups.items() if not any(m.get("current") for m in ms)}


def main(out):
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")
    items = json.load(open(os.path.join(ROOT, "evaluation", "mapping.json")))
    active_slugs = set(os.listdir(os.path.join(ROOT, "evaluation", "companies")))
    groups = skipped_groups(items)
    os.makedirs(out)
    written, skipped = 0, []
    for g, members in sorted(groups.items()):
        s = slug(g)
        if s in active_slugs:
            # an earlier Moody's entity of a company that already has an active folder
            # (CDW CORPORATION next to cdw); counting it again would count the company twice
            skipped.append({"group": g, "slug": s, "reason": "slug of an active folder"})
            continue
        ratings = {"source": "SEC 17g-7(b) disclosure, Moody's, file date 2026-08-11",
                   "entities": [entity_history(m["oi"]) for m in members]}
        scope = max(members, key=lambda m: bool(m.get("current"))).get("scope")
        d = os.path.join(out, s)
        os.makedirs(d)
        json.dump({"group": g, "scope": scope, "origin": "withdrawn",
                   "members": [{"moodys_name": m["moodys_name"], "oi": m["oi"],
                                "decided_cik": m["decided_cik"]} for m in members]},
                  open(os.path.join(d, "company.json"), "w"), indent=1)
        json.dump(ratings, open(os.path.join(d, "ratings.json"), "w"), indent=1)
        json.dump({"group": g, "scope": scope, "origin": "withdrawn",
                   "design": "experiments/07-rating-change-base-rates/build_withdrawn.py",
                   "observations": quarterly_labels(ratings)},
                  open(os.path.join(d, "observations.json"), "w"), indent=1)
        written += 1
    json.dump(skipped, open(os.path.join(out, "_skipped.json"), "w"), indent=1)
    print(f"{written} withdrawn-rating groups written to {out}; skipped {len(skipped)}: "
          f"{', '.join(x['group'] for x in skipped)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
