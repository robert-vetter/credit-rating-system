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
    Added 2026-10-01 after the first spot check found Six Flags matched to its pre-merger registration:
    /OLD               an SEC registrant whose current name is marked "/OLD" is never a candidate;
                       a "/NEW" or "/OLD" suffix is ignored when names are compared
    GLEIF              where Moody's has an LEI, GLEIF's legal name or other names must agree with the
                       SEC company's current or former names; otherwise the proposal is dropped

    python3 evaluation/pipeline/map_all_sectors.py labels | fetch | gleif | propose | spotcheck [seed]
"""
import collections
import datetime as dt
import json
import os
import random
import re
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
GLEIF = os.path.join(DATA, "gleif-lei-records.json")


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
    idx, old = sec_index()
    got = 0
    for oi, v in window_issuers().items():
        cik, kind, cands = propose_name(v["name"], idx, old)
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


def sec_index():
    """SEC names with the /OLD rule: registrants currently marked /OLD are excluded; /NEW and /OLD
    suffixes are ignored when names are compared (rule of 2026-10-01)."""
    idx = Z.sec_names()
    clean = collections.defaultdict(set)
    old = set()
    for line in open(os.path.join(ROOT, "data", "edgar", "cik-lookup-data.txt"), encoding="latin-1"):
        parts = line.rstrip("\n").rsplit(":", 2)
        if len(parts) >= 3 and parts[1].isdigit() and "/OLD" in parts[0].upper():
            old.add(int(parts[1]))
    for k, ciks in idx.items():
        k2 = " ".join(t for t in k.split() if t not in ("NEW", "OLD"))
        clean[k2] |= ciks
    return clean, old


def propose_name(name, idx, old):
    k = " ".join(t for t in Z.norm(name).split() if t not in ("NEW", "OLD"))
    cands = sorted(c for c in idx.get(k, set()) if c not in old and not is_old(c))
    if len(cands) == 1:
        return cands[0], "unique", cands
    if len(cands) > 1:
        return None, "ambiguous", cands[:10]
    return None, "none", []


def is_old(cik):
    r = sec_record(cik)
    return bool(r and "error" not in r and "/OLD" in (r.get("name") or "").upper())


def gleif():
    """GLEIF records for the Moody's LEIs of all issuers rated in the window (public API, batches of 100)."""
    leis = sorted({v["lei"] for v in window_issuers().values() if v["lei"]})
    have = json.load(open(GLEIF)) if os.path.exists(GLEIF) else {}
    todo = [x for x in leis if x not in have]
    for i in range(0, len(todo), 100):
        batch = todo[i:i + 100]
        url = ("https://api.gleif.org/api/v1/lei-records?page[size]=100&filter[lei]=" + ",".join(batch))
        d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/vnd.api+json"}),
                                              timeout=60).read())
        for rec in d.get("data", []):
            a = rec["attributes"]["entity"]
            have[rec["id"]] = {"legal_name": a["legalName"]["name"],
                               "other_names": [n["name"] for n in a.get("otherNames", [])],
                               "transliterated": [n["name"] for n in a.get("transliteratedOtherNames", [])],
                               "country": a["legalAddress"].get("country"), "region": a["legalAddress"].get("region"),
                               "status": a.get("status")}
        for x in batch:
            have.setdefault(x, {"not_found": True})
        time.sleep(1.0)
    json.dump(have, open(GLEIF, "w"), indent=0)
    print(f"GLEIF records: {sum(1 for v in have.values() if 'legal_name' in v)} of {len(leis)} LEIs")


FOREIGN_FORMS = {"NEW", "OLD", "SPA", "SOCIETA", "PER", "AZIONI", "KOMMANDITGESELLSCHAFT", "AUF", "AKTIEN", "KGAA",
                 "AKTIEBOLAGET", "AB", "SAB", "CV", "SRL", "GMBH", "BV", "ASA", "OYJ", "LTEE", "LTDA", "SAS",
                 "AKTIENGESELLSCHAFT", "PUBLIC", "HOLDING", "HOLDINGS", "GROUP", "GRUPO", "SOCIETE", "ANONYME"}


def clean_name(n):
    import unicodedata
    n = re.sub("[\u00b4\u2019\u2018`']", "", n or "")          # apostrophes first, before accent folding
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return " ".join(t for t in Z.norm(n).split() if t not in FOREIGN_FORMS)


def gleif_agrees(g, rec):
    """True if a Latin-script GLEIF name and an SEC name agree after cleaning (equal, one contains the
    other, or at least half their words shared); None if GLEIF offers no Latin-script name to compare."""
    if not g or "legal_name" not in g or not rec or "error" in rec:
        return None
    gn = {clean_name(n) for n in [g["legal_name"]] + g.get("other_names", []) + g.get("transliterated", []) if n}
    gn = {x for x in gn if x}
    if not gn:
        return None
    sn = {clean_name(n) for n in [rec["name"]] + rec["former_names"] + former_all(rec["cik"]) if n}
    sn = {x for x in sn if x}

    def close(a, b):
        A, B = set(a.split()), set(b.split())
        a2, b2 = a.replace(" ", ""), b.replace(" ", "")
        return a == b or a in b or b in a or a2 == b2 or len(A & B) / len(A | B) >= 0.5
    return any(close(a, b) for a in gn for b in sn)


def former_all(cik):
    path = os.path.join(SUBS, f"CIK{cik:010d}.json")
    j = json.load(open(path)) if os.path.exists(path) else {}
    return [f.get("name") for f in (j.get("formerNames") or []) if f.get("name")]


def propose():
    os.makedirs(EVAL, exist_ok=True)
    idx, old = sec_index()
    gl = json.load(open(GLEIF)) if os.path.exists(GLEIF) else {}
    out, counts = {}, collections.Counter()
    for oi, v in sorted(window_issuers().items()):
        cik, kind, cands = propose_name(v["name"], idx, old)
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
        g = gl.get(v["lei"]) if v["lei"] else None
        gleif_check = gleif_agrees(g, rec) if rec else None
        entry["gleif"] = ({"legal_name": g.get("legal_name"), "other_names": g.get("other_names"), "agrees": gleif_check}
                          if g and "legal_name" in g else None)
        status = ("dropped: conflict (Robert, 2026-10-01)" if rule == "conflict" else
                  "unmapped" if rule == "unmapped" else
                  "dropped: LEI differs" if lei_check == "different" else
                  "dropped: GLEIF name differs" if gleif_check is False else "proposed")
        entry.update({"rule": rule, "proposed_cik": chosen, "lei_check": lei_check, "status": status,
                      "sec": rec, "files_10k_at": {t: files_10k_by(rec, t) for t in TEST_DATES} if rec else {}})
        out[oi] = entry
        counts[status if status != "proposed" else f"proposed, {rule}"] += 1
    json.dump({"built": dt.date.today().isoformat(), "by": "Claude (Opus 5.5), evaluation/pipeline/map_all_sectors.py",
               "status_note": "machine proposals; nothing here is a decision until recorded in decisions.jsonl",
               "counts": dict(counts), "issuers": out}, open(PROPOSED, "w"), indent=1)
    print(json.dumps(dict(counts), indent=1))


def spotcheck(seed=SEED):
    p = json.load(open(PROPOSED))["issuers"]
    usable = [(oi, e) for oi, e in sorted(p.items()) if e["status"] == "proposed" and any(e["files_10k_at"].values())]
    rng = random.Random(seed)
    b = [x for x in usable if x[1]["rule"].startswith("B")]
    a = [x for x in usable if x[1]["rule"].startswith("A")]
    pick = rng.sample(b, min(SPOT_MIN_B, len(b)))
    pick += rng.sample(a, SPOT_N - len(pick))
    pick.sort(key=lambda x: x[1]["moodys_name"])
    date = dt.date.today().isoformat()
    L = [f"# Spot check of the proposed all-sector mapping, {date}",
         "",
         f"*Prepared by Claude (Opus 5.5) for Robert Vetter. {SPOT_N} proposals drawn at random (seed {seed}) from the "
         f"{len(usable)} proposed matches that file 10-Ks in the window ({len(a)} by rule A, unique name; {len(b)} by rule B, "
         f"10-K tie-break; at least {SPOT_MIN_B} of the sample from rule B). Source: `proposed-mapping.json`. "
         "Mark each line right or wrong in the last column. If all are right, the rules are accepted as Robert's "
         "decision for every proposed match; if any is wrong, the rules are tightened and a new sample is drawn.*",
         "",
         "| # | Moody's issuer | Rule | SEC company (CIK) | Earlier SEC names | Industry | State | GLEIF legal name (from Moody's LEI) | Right or wrong |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, (oi, e) in enumerate(pick, 1):
        s = e["sec"]
        L.append(f"| {i} | {e['moodys_name']} | {e['rule'][0]} | {s['name']} ({s['cik']}) | "
                 f"{'; '.join(n for n in s['former_names'] if n) or ''} | {s.get('industry') or ''} | "
                 f"{s.get('state') or ''} | {(e.get('gleif') or {}).get('legal_name') or 'no LEI at Moody' + chr(39) + 's'} | |")
    path = os.path.join(EVAL, f"spot-check-{date}-seed{seed}.md")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(path, ROOT)}: {len(a)} usable by rule A, {len(b)} by rule B")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "spotcheck" and len(sys.argv) > 2:
        spotcheck(int(sys.argv[2]))
    else:
        {"labels": labels, "fetch": fetch, "gleif": gleif, "propose": propose, "spotcheck": spotcheck}[cmd]()
