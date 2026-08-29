"""
Selects the gold set: the fixed, hand-validated evaluation set everything will be measured on.

Written by Claude (Opus 5), directed by Robert Vetter, who validates every member by hand
(that is the point: the measuring stick gets human eyes, the measurements then don't need
re-litigating).

Design:
  50 observations, 30 changed / 20 unchanged, drawn ONLY from clean material: scope "in",
  US 10-K filers (foreign 20-F/40-F filers excluded for document homogeneity), unambiguous
  label, an annual report no older than 455 days at the observation date (the general
  has_recent_annual flag tolerates two years, which lets post-acquisition zombies like Whole
  Foods 2019 through - too stale for gold), and a defined previous-quarter rating. Stratified so no single company, era, direction or rating region dominates:

  changed (the primary experiment's material):
    - direction mix (downgrades and upgrades), multi-notch cases and investment-grade
      boundary crossings explicitly represented
    - eras spread: 2012-2016, 2017-2019, 2020-2021 (COVID), 2022-2025
    - at most 2 changed observations per company
  unchanged (the false-alarm control):
    - stratified over rating buckets (Aa/A, Baa, Ba, B, Caa) and the same eras
    - at most 1 per company, companies not already in the changed half preferred
    - whether the NEXT quarter brings a change is recorded (hard-negative flag), but not
      selected on

  Selection is deterministic: fixed seed 20260829, sorted iteration, committed code. Re-runs
  reproduce the identical set; the set only changes if this file changes, visibly in git.

Status lifecycle in evaluation/goldset.json: "proposed" (this script) -> "confirmed" /
"rejected" (Robert, via the review sheet). The gold set is a HOLDOUT: day-to-day system
iteration uses non-gold observations; gold runs are for milestone claims.

Run: python3 evaluation/pipeline/build_goldset.py
"""
import datetime
import json
import os
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "evaluation", "companies")
GOLD = os.path.join(ROOT, "evaluation", "goldset.json")
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]
SEED = 20260829


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def era(date):
    y = int(date[:4])
    if y <= 2016: return "2012-2016"
    if y <= 2019: return "2017-2019"
    if y <= 2021: return "2020-2021"
    return "2022-2025"


def bucket(label):
    n = notch(label)
    if n <= 6: return "Aa/A"
    if n <= 9: return "Baa"
    if n <= 12: return "Ba"
    if n <= 15: return "B"
    return "Caa+"


def load_eligible():
    ch, un = [], []
    for slug in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, slug, "observations.json")
        cj = os.path.join(OUT, slug, "company.json")
        if not os.path.exists(p):
            continue
        c = json.load(open(cj))
        if c.get("scope") != "in":
            continue
        blob = json.load(open(p))
        obs = blob["observations"]
        for i, o in enumerate(obs):
            if (o["persistence"] is None or o["label_ambiguous"] or not o["has_recent_annual"]
                    or notch(o["label"]) is None or notch(o["persistence"]) is None
                    or not o["latest_annual"] or o["latest_annual"]["form"] != "10-K"):
                continue
            t = datetime.date(*map(int, o["date"].split("-")))
            filed = datetime.date(*map(int, o["latest_annual"]["filingDate"].split("-")))
            if (t - filed).days > 455:
                continue
            nxt = obs[i + 1]["changed"] if i + 1 < len(obs) else None
            item = {"slug": slug, "group": c["group"], "cik": c["cik"], "date": o["date"],
                    "label": o["label"], "label_level": o["label_level"], "label_oi": o["label_oi"],
                    "persistence": o["persistence"],
                    "delta": notch(o["label"]) - notch(o["persistence"]),
                    "era": era(o["date"]), "bucket": bucket(o["label"]),
                    "boundary_cross": (notch(o["label"]) <= 9) != (notch(o["persistence"]) <= 9),
                    "next_quarter_changes": nxt}
            (ch if o["changed"] else un).append(item)
    return ch, un


def pick_changed(pool, rng, n=30):
    rng.shuffle(pool)
    picked, per_company = [], {}

    def take(pred, k):
        got = 0
        for it in pool:
            if got >= k:
                break
            if it in picked or per_company.get(it["slug"], 0) >= 2 or not pred(it):
                continue
            picked.append(it)
            per_company[it["slug"]] = per_company.get(it["slug"], 0) + 1
            got += 1

    take(lambda i: i["boundary_cross"], 5)
    take(lambda i: abs(i["delta"]) >= 2, 5)
    for e in ("2012-2016", "2017-2019", "2020-2021", "2022-2025"):
        need = 5 - sum(1 for i in picked if i["era"] == e)
        take(lambda i, e=e: i["era"] == e, max(0, need))
    need_up = 10 - sum(1 for i in picked if i["delta"] < 0)
    take(lambda i: i["delta"] < 0, max(0, need_up))
    take(lambda i: True, n - len(picked))
    return picked[:n]


def pick_unchanged(pool, rng, used_companies, n=20):
    rng.shuffle(pool)
    pool.sort(key=lambda i: i["slug"] in used_companies)  # fresh companies first, stable
    picked, seen = [], set()
    targets = [("Aa/A", 4), ("Baa", 4), ("Ba", 5), ("B", 4), ("Caa+", 3)]
    eras = ["2012-2016", "2017-2019", "2020-2021", "2022-2025"]
    for b, k in targets:
        got = 0
        for pass_eras in (eras, [None]):        # first pass: one per era; second: fill freely
            for e in pass_eras:
                if got >= k:
                    break
                for it in pool:
                    if got >= k:
                        break
                    if (it["bucket"] == b and it["slug"] not in seen
                            and (e is None or it["era"] == e)):
                        picked.append(it); seen.add(it["slug"]); got += 1
                        break
    for it in pool:  # fill any stratum shortfall
        if len(picked) >= n:
            break
        if it["slug"] not in seen:
            picked.append(it); seen.add(it["slug"])
    return picked[:n]


def main():
    ch, un = load_eligible()
    print(f"eligible: {len(ch)} changed, {len(un)} unchanged")
    rng = random.Random(SEED)
    picked_ch = pick_changed(ch, rng, 30)
    picked_un = pick_unchanged(un, rng, {i["slug"] for i in picked_ch}, 20)
    items = []
    for kind, arr in (("changed", picked_ch), ("unchanged", picked_un)):
        arr.sort(key=lambda i: (i["slug"], i["date"]))
        for it in arr:
            items.append({**it, "kind": kind, "status": "proposed", "evidence": None})
    for i, it in enumerate(items, 1):
        it["id"] = f"G{i:02d}"
    json.dump({"seed": SEED, "design": "see evaluation/pipeline/build_goldset.py",
               "items": items}, open(GOLD, "w"), indent=1, ensure_ascii=False)

    import collections
    chp = [i for i in items if i["kind"] == "changed"]
    print(f"\ngewaehlt: {len(chp)} changed / {len(items)-len(chp)} unchanged, "
          f"{len({i['slug'] for i in items})} Firmen")
    print("  changed  Richtung:", dict(collections.Counter("down" if i["delta"] > 0 else "up" for i in chp)))
    print("  changed  |delta|>=2:", sum(1 for i in chp if abs(i["delta"]) >= 2),
          " Boundary-Cross:", sum(1 for i in chp if i["boundary_cross"]))
    print("  changed  Aeren:", dict(collections.Counter(i["era"] for i in chp)))
    print("  unchanged Buckets:", dict(collections.Counter(i["bucket"] for i in items if i["kind"] == "unchanged")))
    print("  unchanged Aeren:", dict(collections.Counter(i["era"] for i in items if i["kind"] == "unchanged")))
    print("  unchanged hart (naechstes Q aendert sich):", sum(1 for i in items if i["kind"] == "unchanged" and i["next_quarter_changes"]))


if __name__ == "__main__":
    main()
