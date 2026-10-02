"""
The all-sector universe: quarterly Moody's labels for every corporate issuer, and a proposed
Moody's-to-SEC mapping for the issuers rated in the 2025 window, for Robert's spot check.

Written 2026-10-01 by Claude (Opus 5.5), directed by Robert Vetter. Separate from the Retail and
Apparel universe (data/frame/, evaluation/mapping.json, evaluation/companies/), which it does not touch.
Reuses the label rule of build_observations.py and the name matcher of
experiments/10-all-sector-next-quarter/sizing.py.

Writes (data/ is gitignored, evaluation/all-sectors/ is committed):
    data/all-sectors/moodys-quarterly-labels.json   every corporate issuer: name, LEI, quarterly labels 2012-09-30 to 2025-06-30
    data/all-sectors/sec-submissions/CIK*.json      SEC submissions of matched companies and of ambiguous candidates
    evaluation/all-sectors/proposed-mapping.json    one entry per issuer rated in the window: rule, proposed CIK, evidence, status
    evaluation/all-sectors/spot-check-<date>.md     a seeded random sample of proposed matches for Robert's check

Mapping rules (proposals, not decisions; Robert's decisions go to evaluation/all-sectors/decisions.jsonl):
    A  unique name     the cleaned Moody's name matches exactly one SEC registrant
    B  10-K tie-break  several registrants share the cleaned name and exactly one filed a 10-K within
                       450 days before 2024-12-31 or 2025-03-31
    conflict           several of them filed such a 10-K: dropped (Robert, 2026-10-01)
    unmapped           no registrant, or none of several files 10-Ks
    LEI                where SEC lists an LEI and Moody's has one: equal confirms, different rejects

    python3 evaluation/pipeline/map_all_sectors.py labels | fetch | propose | spotcheck
"""
import collections
import datetime as dt
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments", "10-all-sector-next-quarter"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "07-rating-change-base-rates"))
import sizing as Z  # noqa: E402
from build_withdrawn import quarterly_labels  # noqa: E402
from fetch_xbrl import UA  # noqa: E402

DATA = os.path.join(ROOT, "data", "all-sectors")
SUBS = os.path.join(DATA, "sec-submissions")
LABELS = os.path.join(DATA, "moodys-quarterly-labels.json")
EVAL = os.path.join(ROOT, "evaluation", "all-sectors")
PROPOSED = os.path.join(EVAL, "proposed-mapping.json")
WINDOW = ("2024-12-31", "2025-03-31", "2025-06-30")
TEST_DATES = ("2024-12-31", "2025-03-31")
SEED, SPOT_N, SPOT_MIN_B = 20261001, 30, 8


def labels():
    os.makedirs(DATA, exist_ok=True)
    zob, zis = zipfile.ZipFile(Z.OB_ZIP), zipfile.ZipFile(Z.IS_ZIP)
    ob, isn = Z.corporate_members(zob, "Obligor"), Z.corporate_members(zis, "Issuer")
    out = {}
    for oi in sorted(set(ob) | set(isn)):
        h = Z.history(oi, zob, zis, ob, isn)
        obs = quarterly_labels({"entities": [h]})
        out[oi] = {"name": h["name"], "lei": h["lei"] or None,
                   "sets": [s for s, m in (("obligor", ob), ("issuer", isn)) if oi in m],
                   "observations": [[o["date"], o["label"], o["label_level"], o["label_ambiguous"],
                                     o["persistence"], o["changed"]] for o in obs]}
    json.dump({"source": "Moody's 17g-7 archives dated 2026-08-11, all issuers of sector class Corporate",
               "built": dt.date.today().isoformat(), "rule": "build_observations.py label rule",
               "fields": ["date", "label", "level", "ambiguous", "persistence", "changed"], "issuers": out},
              open(LABELS, "w"))
    print(f"{len(out)} corporate issuers written to {os.path.relpath(LABELS, ROOT)}")


def window_issuers():
    lab = json.load(open(LABELS))["issuers"]
    return {oi: v for oi, v in lab.items() if any(o[0] in WINDOW for o in v["observations"])}


def ensure(cik):
    path = os.path.join(SUBS, f"CIK{cik:010d}.json")
    if os.path.exists(path):
        return False
    try:
        body = urllib.request.urlopen(urllib.request.Request(
            f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA), timeout=60).read()
    except urllib.error.HTTPError as exc:
        body = json.dumps({"error": f"HTTP {exc.code}"}).encode()
    open(path, "wb").write(body)
    time.sleep(0.15)
    return True


def fetch():
    os.makedirs(SUBS, exist_ok=True)
    idx = Z.sec_names()
    got = 0
    for oi, v in window_issuers().items():
        cik, kind, cands = Z.propose(v["name"], idx)
        for c in ([cik] if kind == "unique" else cands if kind == "ambiguous" else []):
            got += ensure(c)
    print(f"downloaded {got} SEC submissions into {os.path.relpath(SUBS, ROOT)}")


def sec_record(cik):
    path = os.path.join(SUBS, f"CIK{cik:010d}.json")
    if not os.path.exists(path):
        return None
    j = json.load(open(path))
    if "error" in j:
        return {"error": j["error"]}
    r = j.get("filings", {}).get("recent", {})
    tenk = sorted(d for f, d in zip(r.get("form", []), r.get("filingDate", [])) if f in ("10-K", "10-K405"))
    return {"cik": cik, "name": j.get("name"), "former_names": [f.get("name") for f in (j.get("formerNames") or [])][:3],
            "sic": j.get("sic"), "industry": j.get("sicDescription"), "lei": j.get("lei"),
            "state": (j.get("addresses", {}).get("business") or {}).get("stateOrCountry"),
            "incorporated": j.get("stateOfIncorporation"), "entity_type": j.get("entityType"),
            "tenk_dates": tenk}


def files_10k_by(rec, t):
    if not rec or "error" in rec:
        return False
    ks = [d for d in rec["tenk_dates"] if d <= t]
    return bool(ks) and (dt.date.fromisoformat(t) - dt.date.fromisoformat(max(ks))).days <= Z.ELIGIBLE_DAYS


def propose():
    os.makedirs(EVAL, exist_ok=True)
    idx = Z.sec_names()
    out, counts = {}, collections.Counter()
    for oi, v in sorted(window_issuers().items()):
        cik, kind, cands = Z.propose(v["name"], idx)
        entry = {"moodys_name": v["name"], "moodys_lei": v["lei"], "name_match": kind, "candidates": cands}
        if kind == "unique":
            rule, chosen = "A unique name", cik
        elif kind == "ambiguous":
            active = [c for c in cands if any(files_10k_by(sec_record(c), t) for t in TEST_DATES)]
            rule, chosen = (("B 10-K tie-break", active[0]) if len(active) == 1 else
                            ("conflict", None) if len(active) > 1 else ("unmapped", None))
            entry["candidates_filing_10k"] = active
        else:
            rule, chosen = "unmapped", None
        rec = sec_record(chosen) if chosen else None
        lei_check = None
        if rec and "error" not in rec and rec.get("lei") and v["lei"]:
            lei_check = "equal" if rec["lei"] == v["lei"] else "different"
        status = ("dropped: conflict (Robert, 2026-10-01)" if rule == "conflict" else
                  "unmapped" if rule == "unmapped" else
                  "dropped: LEI differs" if lei_check == "different" else "proposed")
        entry.update({"rule": rule, "proposed_cik": chosen, "lei_check": lei_check, "status": status,
                      "sec": rec, "files_10k_at": {t: files_10k_by(rec, t) for t in TEST_DATES} if rec else {}})
        out[oi] = entry
        counts[status if status != "proposed" else f"proposed, {rule}"] += 1
    json.dump({"built": dt.date.today().isoformat(), "by": "Claude (Opus 5.5), evaluation/pipeline/map_all_sectors.py",
               "status_note": "machine proposals; nothing here is a decision until recorded in decisions.jsonl",
               "counts": dict(counts), "issuers": out}, open(PROPOSED, "w"), indent=1)
    print(json.dumps(dict(counts), indent=1))


def spotcheck():
    p = json.load(open(PROPOSED))["issuers"]
    usable = [(oi, e) for oi, e in sorted(p.items()) if e["status"] == "proposed" and any(e["files_10k_at"].values())]
    rng = random.Random(SEED)
    b = [x for x in usable if x[1]["rule"].startswith("B")]
    a = [x for x in usable if x[1]["rule"].startswith("A")]
    pick = rng.sample(b, min(SPOT_MIN_B, len(b)))
    pick += rng.sample(a, SPOT_N - len(pick))
    pick.sort(key=lambda x: x[1]["moodys_name"])
    date = dt.date.today().isoformat()
    L = [f"# Spot check of the proposed all-sector mapping, {date}",
         "",
         f"*Prepared by Claude (Opus 5.5) for Robert Vetter. {SPOT_N} proposals drawn at random (seed {SEED}) from the "
         f"{len(usable)} proposed matches that file 10-Ks in the window ({len(a)} by rule A, unique name; {len(b)} by rule B, "
         f"10-K tie-break; at least {SPOT_MIN_B} of the sample from rule B). Source: `proposed-mapping.json`. "
         "Mark each line right or wrong in the last column. If all are right, the rules are accepted as Robert's "
         "decision for every proposed match; if any is wrong, the rules are tightened and a new sample is drawn.*",
         "",
         "| # | Moody's issuer | Rule | SEC company (CIK) | Earlier SEC names | Industry | State | LEI | Right or wrong |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, (oi, e) in enumerate(pick, 1):
        s = e["sec"]
        L.append(f"| {i} | {e['moodys_name']} | {e['rule'][0]} | {s['name']} ({s['cik']}) | "
                 f"{'; '.join(n for n in s['former_names'] if n) or ''} | {s.get('industry') or ''} | "
                 f"{s.get('state') or ''} | {e['lei_check'] or 'not listed by SEC'} | |")
    path = os.path.join(EVAL, f"spot-check-{date}.md")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(path, ROOT)}: {len(a)} usable by rule A, {len(b)} by rule B")


if __name__ == "__main__":
    {"labels": labels, "fetch": fetch, "propose": propose, "spotcheck": spotcheck}[sys.argv[1]]()
