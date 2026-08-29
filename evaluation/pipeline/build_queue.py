"""
Builds and updates evaluation/mapping.json, the registry behind the manual mapping review.

Written by Claude (Opus 5), directed by Robert Vetter. See evaluation/README.md for the design.

One item per Moody's Retail/Apparel entity (from data/frame/retail_frame.json), keyed by the Moody's
entity id (OI), carrying the automatic EDGAR proposal (CIK) for Robert to confirm, correct or
reject in the review UI. Once the listed-universe SIC sweep has finished
(data/sic_sweep_listed.done exists), a second item kind is added: listed SEC companies with a
Retail/Apparel SIC code that no Moody's item points to, keyed by CIK, so the mapping is checked
from both directions.

Decided items are never modified here; re-running only adds missing items and refreshes
informational fields on still-pending ones. Also writes:
  data/moodys/derived/moodys_corporates.json  - all Corporate entities of both 17g-7 sets
                                 (gitignored, derived from the zips)
  evaluation/lists.md          - the two alphabetical name lists, for reading outside the UI

Run: python3 evaluation/pipeline/build_queue.py
"""
import html
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_frame as sc  # noqa: E402  (variants/norm, zip parsing, sector_bucket)

DATA = os.path.join(ROOT, "data")
EVAL = os.path.join(ROOT, "evaluation")
MAPPING = os.path.join(EVAL, "mapping.json")
FRAME = os.path.join(DATA, "frame", "retail_frame.json")
MOODYS_OUT = os.path.join(DATA, "moodys", "derived", "moodys_corporates.json")
SWEEP_DONE = os.path.join(DATA, "edgar", "sic_sweep_listed.done")


def cik_names(needed):
    """Official EDGAR names for a set of CIKs, from the cached cik-lookup file."""
    out = {}
    for line in open(os.path.join(DATA, "edgar", "cik-lookup-data.txt"), encoding="latin-1"):
        if line.count(":") < 2:
            continue
        name, cik = line.rsplit(":", 2)[0], line.rsplit(":", 2)[1]
        if cik.isdigit() and int(cik) in needed and int(cik) not in out:
            out[int(cik)] = name
    return out


def moodys_corporates():
    if os.path.exists(MOODYS_OUT):
        return json.load(open(MOODYS_OUT))
    ents = sc.load_corporates()
    out = [{"oi": e["oi"], "name": html.unescape(e["name"]), "lei": e.get("lei", "")}
           for e in ents.values()]
    out.sort(key=lambda e: e["name"].upper())
    json.dump(out, open(MOODYS_OUT, "w"), indent=0)
    return out


def main():
    frame = json.load(open(FRAME))
    existing = {}
    if os.path.exists(MAPPING):
        existing = {it["key"]: it for it in json.load(open(MAPPING))}

    needed_ciks = {e.get("filing_cik") or e.get("cik") for e in frame if e.get("cik")}
    names = cik_names({c for c in needed_ciks if c})

    items = []
    for e in sorted(frame, key=lambda x: html.unescape(x["name"]).upper()):
        key = f"oi-{e['oi']}"
        prop_cik = e.get("filing_cik") or e.get("cik")
        info = {
            "key": key, "kind": "moodys",
            "moodys_name": html.unescape(e["name"]), "oi": e["oi"], "lei": e.get("lei", ""),
            "group": html.unescape(e.get("group") or e["name"]),
            "own_cik": e.get("cik"), "proposed_cik": prop_cik,
            "proposed_edgar_name": names.get(prop_cik, ""),
            "scope": e.get("scope"), "scope_reason": e.get("scope_reason"),
            "bucket": e.get("bucket"), "sic": e.get("sic"),
            "sic_desc": html.unescape(html.unescape(e.get("sic_desc") or "")),
            "current": e.get("current"), "filing_status": e.get("filing_status"),
        }
        if key in existing:
            it = existing.pop(key)
            if it.get("status") == "pending":
                it.update(info)  # refresh informational fields, keep any note
            items.append(it)
        else:
            items.append({**info, "status": "pending", "decided_cik": None,
                          "decided_edgar_name": None, "decided_by": None,
                          "decided_at": None, "note": ""})

    # Reverse direction, once the sweep is complete
    if os.path.exists(SWEEP_DONE):
        cache = json.load(open(os.path.join(DATA, "edgar", "sic_cache.json")))
        tickers = json.load(open(os.path.join(DATA, "edgar", "company_tickers.json")))
        listed = {}
        for v in tickers.values():
            listed.setdefault(int(v["cik_str"]), v["title"])
        covered = set()
        for it in items:
            for c in (it.get("proposed_cik"), it.get("own_cik"), it.get("decided_cik")):
                if c:
                    covered.add(c)
        for cik, title in sorted(listed.items(), key=lambda kv: kv[1].upper()):
            sic = cache.get(str(cik), ["", ""])[0]
            if not sc.sector_bucket(sic) or cik in covered:
                continue
            key = f"cik-{cik}"
            if key in existing:
                items.append(existing.pop(key))
            else:
                items.append({
                    "key": key, "kind": "edgar", "edgar_name": title, "cik": cik,
                    "sic": sic, "sic_desc": cache.get(str(cik), ["", ""])[1],
                    "status": "pending", "decided_oi": None, "decided_moodys_name": None,
                    "decided_by": None, "decided_at": None, "note": "",
                })

    # carry over decided items that no longer regenerate; drop only still-pending reverse
    # items whose CIK a confirmed mapping now covers (their question got answered elsewhere)
    covered_now = set()
    for it in items:
        for c in (it.get("proposed_cik"), it.get("own_cik"), it.get("decided_cik")):
            if c:
                covered_now.add(c)
    for it in existing.values():
        if it["kind"] == "edgar" and it["status"] == "pending" and it["cik"] in covered_now:
            continue
        items.append(it)

    tmp = MAPPING + ".tmp"
    json.dump(items, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, MAPPING)

    corps = moodys_corporates()

    # the two alphabetical lists as a plain document
    with open(os.path.join(EVAL, "lists.md"), "w") as f:
        f.write("# The two name lists behind the mapping\n\n")
        f.write("*Generated by evaluation/build_queue.py; do not edit, re-run instead. "
                "The mapping decisions themselves live in mapping.json / decisions.jsonl.*\n\n")
        f.write("## Moody's side: Retail and Apparel entities from the 17g-7 files "
                f"({len([i for i in items if i['kind']=='moodys'])}, alphabetical)\n\n")
        f.write("| Moody's name | OI | rating | scope | EDGAR proposal |\n|---|---|---|---|---|\n")
        for it in items:
            if it["kind"] != "moodys":
                continue
            cur = it.get("current") or {}
            f.write(f"| {it['moodys_name']} | {it['oi']} | {cur.get('rating','—')} "
                    f"| {it['scope']} | {it.get('proposed_edgar_name','')} "
                    f"(CIK {it.get('proposed_cik','—')}) |\n")
        rev = [i for i in items if i["kind"] == "edgar"]
        f.write(f"\n## EDGAR side: listed companies with Retail/Apparel SIC and no Moody's "
                f"item ({len(rev)}, alphabetical)\n\n")
        if rev:
            f.write("| EDGAR name | CIK | SIC |\n|---|---|---|\n")
            for it in rev:
                f.write(f"| {it['edgar_name']} | {it['cik']} | {it['sic']} {it['sic_desc']} |\n")
        else:
            f.write("*Not generated yet: appears after the listed-universe SIC sweep "
                    "(evaluation/sic_sweep_listed.py) has finished and build_queue.py is re-run.*\n")
        f.write(f"\nMoody's Corporate universe for the search box: {len(corps)} entities "
                f"in data/moodys_corporates.json.\n")

    n_m = len([i for i in items if i["kind"] == "moodys"])
    n_e = len([i for i in items if i["kind"] == "edgar"])
    n_p = len([i for i in items if i["status"] == "pending"])
    print(f"mapping.json: {n_m} Moody's items, {n_e} EDGAR reverse items, {n_p} pending")


if __name__ == "__main__":
    main()
