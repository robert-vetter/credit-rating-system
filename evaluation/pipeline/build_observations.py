"""
The observation builder ("Tripel-Builder"): turns each company folder into evaluation samples.

Written by Claude (Opus 5), directed by Robert Vetter. See evaluation/README.md.

One observation is the unit the evaluation runs on:

    (company, observation date t) ->
        label_at_t          the Moody's rating in effect at t, derived from ratings.json:
                            entity-level long-term rating (CFR / issuer rating) where one is
                            alive, otherwise the freshest senior unsecured instrument rating.
                            The level actually used is recorded per observation, plus
                            ambiguity flags when group members disagree
        rating_path         the last up-to-12 rating events (date, rating, action, level) up
                            to and including t - the Task B input
        documents           references (form, date, accession, primary document) of all SEC
                            filings from the manifest with filingDate <= t: the latest annual
                            report plus everything filed in the 365 days before t. References
                            only; the runner downloads what it needs
        persistence         the label at the previous grid date - the baseline prediction
        changed             label_at_t != persistence (None on the first observation)
        delta_notches       signed rating change vs persistence on the 21-notch scale

Grid: calendar quarter ends from 2012-09-30 (first full quarter after the 17g-7 history start)
through 2025-06-30, the last quarter end safely inside the embargoed file window (file dated
2026-08-11, content through August 2025). Quarterly is the finest grid the labels support;
an annual evaluation filters to one quarter per year downstream ("quarter" field). Observation
dates beyond 2025-06-30 require post-embargo labels from the lab's dataset.

Writes observations.json into every company folder and evaluation/observations-summary.md.

Run after compile_folders.py and fetch_filings.py:
    python3 evaluation/pipeline/build_observations.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "evaluation", "companies")
LT = ("LT CORPORATE FAMILY RATINGS", "LT ISSUER RATING", "ISSUER RATING", "ISSUER LT RATING")
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]
ANNUAL = ("10-K", "20-F", "40-F")
GRID = [f"{y}-{md}" for y in range(2012, 2026) for md in ("03-31", "06-30", "09-30", "12-31")]
GRID = [d for d in GRID if "2012-09-30" <= d <= "2025-06-30"]


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def lines_of(ratings):
    """Entity-level and senior-unsecured event lines, each sorted by action date."""
    ent, sen = [], []
    for e in ratings["entities"]:
        recs = sorted([r for r in (e.get("obligor_records") or [])
                       if r.get("RT", "").upper() in LT and r.get("RAD")],
                      key=lambda r: r["RAD"])
        if recs:
            ent.append({"oi": e["oi"], "recs": recs})
        for ins in (e.get("instruments") or []):
            recs = sorted([r for r in ins["records"]
                           if r.get("RT") == "Senior Unsecured" and r.get("RAD")],
                          key=lambda r: r["RAD"])
            if recs:
                sen.append({"oi": e["oi"], "recs": recs})
    return ent, sen


def in_effect(line, t):
    last = None
    for r in line["recs"]:
        if r["RAD"] <= t:
            last = r
        else:
            break
    if last and last.get("R") and last["R"] != "WR":
        return last
    return None


def label_at(ent, sen, t):
    """(rating, level, oi, ambiguous) per the documented label rule."""
    live = [(line, in_effect(line, t)) for line in ent]
    live = [(l, r) for l, r in live if r]
    if live:
        l, r = max(live, key=lambda lr: lr[1]["RAD"])
        distinct = {r2["R"] for _, r2 in live}
        return r["R"], "entity", l["oi"], len(distinct) > 1
    live = [(line, in_effect(line, t)) for line in sen]
    live = [(l, r) for l, r in live if r]
    if live:
        l, r = max(live, key=lambda lr: lr[1]["RAD"])
        distinct = {r2["R"] for _, r2 in live}
        return r["R"], "instrument", l["oi"], len(distinct) > 1
    return None, None, None, False


def path_to(ent, sen, t):
    ev = set()
    for level, lines in (("entity", ent), ("instrument", sen)):
        for line in lines:
            for r in line["recs"]:
                if r["RAD"] <= t and r.get("R"):
                    ev.add((r["RAD"], r["R"], r.get("RAC", ""), level))
    return [list(e) for e in sorted(ev)[-12:]]


def main():
    total = changed_n = 0
    rows = []
    for slug in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, slug)
        cj = os.path.join(d, "company.json")
        if not os.path.exists(cj):
            continue
        c = json.load(open(cj))
        ratings = json.load(open(os.path.join(d, "ratings.json")))
        mpath = os.path.join(d, "filings", "manifest.json")
        manifest = json.load(open(mpath))["filings"] if os.path.exists(mpath) else []
        ent, sen = lines_of(ratings)
        obs = []
        prev_label = None
        for t in GRID:
            label, level, oi, amb = label_at(ent, sen, t)
            if label is None:
                prev_label = None
                continue
            docs = [f for f in manifest if f["filingDate"] <= t]
            annual = next((f for f in docs if f["form"] in ANNUAL), None)  # docs sorted desc
            year_ago = f"{int(t[:4]) - 1}{t[4:]}"
            recent = [{k: f[k] for k in ("form", "filingDate", "accessionNumber", "primaryDocument")}
                      for f in docs if f["filingDate"] > year_ago]
            ch = (label != prev_label) if prev_label else None
            dn = None
            if ch and notch(label) is not None and notch(prev_label) is not None:
                dn = notch(label) - notch(prev_label)
            obs.append({
                "date": t, "quarter": "Q" + str((int(t[5:7]) + 2) // 3),
                "label": label, "label_level": level, "label_oi": oi,
                "label_ambiguous": amb,
                "persistence": prev_label, "changed": ch, "delta_notches": dn,
                "rating_path": path_to(ent, sen, t),
                "latest_annual": ({k: annual[k] for k in
                                   ("form", "filingDate", "accessionNumber", "primaryDocument")}
                                  if annual else None),
                "has_recent_annual": bool(annual) and annual["filingDate"] > f"{int(t[:4]) - 2}{t[4:]}",
                "documents_365d": recent,
            })
            prev_label = label
            total += 1
            changed_n += 1 if ch else 0
        json.dump({"group": c["group"], "cik": c["cik"], "scope": c.get("scope"),
                   "filing_status": c.get("filing_status"),
                   "design": "see evaluation/pipeline/build_observations.py",
                   "observations": obs},
                  open(os.path.join(d, "observations.json"), "w"), indent=1, ensure_ascii=False)
        n_ch = sum(1 for o in obs if o["changed"])
        rows.append((slug, c.get("scope"), c.get("filing_status") or "-", len(obs), n_ch,
                     obs[0]["date"] if obs else "-", obs[-1]["label"] if obs else "-"))
        print(f"  {slug:<30} {len(obs):>3} Obs, {n_ch:>2} changed")

    with open(os.path.join(ROOT, "evaluation", "observations-summary.md"), "w") as f:
        f.write("# Observation build summary\n\n")
        f.write("*Generated by evaluation/pipeline/build_observations.py; design and field "
                "reference in its docstring. Grid: calendar quarter ends 2012-09-30 through "
                "2025-06-30 (the embargoed label horizon).*\n\n")
        f.write(f"**{total} observations across {len(rows)} companies, "
                f"{changed_n} with a rating change against the previous quarter "
                f"({100 * changed_n / total:.1f}%).** The changed subset is the primary "
                "experiment's sample; the unchanged rest is what the persistence baseline "
                "gets right for free.\n\n")
        f.write("| Company | Scope | Filing status | Obs | Changed | First obs | Label at end |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| " + " | ".join(str(x) for x in r) + " |\n")
    print(f"\n{total} Beobachtungen, davon {changed_n} changed ({100 * changed_n / total:.1f}%)")


if __name__ == "__main__":
    main()
