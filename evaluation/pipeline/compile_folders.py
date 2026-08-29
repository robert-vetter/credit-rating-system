"""
Compiles confirmed mapping decisions into per-company evaluation folders.

Written by Claude (Opus 5), directed by Robert Vetter. See evaluation/README.md.

Reads evaluation/mapping.json, takes every item Robert has decided, groups the Moody's-side
items by corporate group (bond-issuing subsidiaries fold into their filing parent), and writes
one folder per group under evaluation/companies/:

  companies/<slug>/company.json   identity and provenance: Moody's OIs, LEIs, the confirmed
                                  CIK, who decided the mapping and when, scope, current rating
  companies/<slug>/ratings.json   the full raw Moody's rating history for every member entity,
                                  entity-level (ORD) and instrument-level (IND/INRD), extracted
                                  verbatim from the 17g-7 archives

The label at an observation date is derived from ratings.json later, by the documented label
rule; this file deliberately stores the raw records so that derivation stays checkable.

Folders are regenerated deterministically from mapping.json plus the archives: delete and
re-run at will, decisions are never stored here. The companies/ tree is gitignored because it
contains bulk Moody's rating data (terms-of-use question still open); mapping.json and
decisions.jsonl are the durable, committed record.

Run after the mapping decisions: python3 evaluation/pipeline/compile_folders.py
"""
import html
import json
import os
import re
import shutil
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
EVAL = os.path.join(ROOT, "evaluation")
OUT = os.path.join(EVAL, "companies")
OB_ZIP = os.path.join(DATA, "moodys", "xbrl100-obligor-2026-08-11.zip")
IS_ZIP = os.path.join(DATA, "moodys", "xbrl100-issuer-2026-08-11.zip")
STAMP = "2026-08-11"

ORD_FLD = re.compile(r"<(R|RAD|RAC|RT|RST|RTM)\b[^>]*>([^<]*)</\1>")
IND_META = re.compile(r"<(CUSIP|ISIN|CR|MD|PV|OBT)\b[^>]*>([^<]*)</\1>")


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-(inc|corp|corporation|company|co|llc|lp|plc|ltd|sa|nv)$", "", s).strip("-")


def entity_history(oi):
    hist = {"oi": oi, "obligor_records": None, "instruments": None}
    with zipfile.ZipFile(OB_ZIP) as z:
        try:
            d = z.read(f"Moodys-NRSRO-{oi}-Obligor-{STAMP}.xml").decode("utf-8", "ignore")
            hist["obligor_records"] = [
                dict((x.group(1), x.group(2)) for x in ORD_FLD.finditer(m.group(1)))
                for m in re.finditer(r"<ORD>(.*?)</ORD>", d, re.S)]
        except KeyError:
            pass
    with zipfile.ZipFile(IS_ZIP) as z:
        try:
            d = z.read(f"Moodys-NRSRO-{oi}-Issuer-{STAMP}.xml").decode("utf-8", "ignore")
        except KeyError:
            return hist
    instruments = []
    for im in re.finditer(r"<IND>(.*?)</IND>", d, re.S):
        meta = dict((x.group(1), x.group(2)) for x in IND_META.finditer(im.group(1)))
        recs = [dict((x.group(1), x.group(2)) for x in ORD_FLD.finditer(m.group(1)))
                for m in re.finditer(r"<INRD>(.*?)</INRD>", im.group(1), re.S)]
        instruments.append({"meta": meta, "records": recs})
    hist["instruments"] = instruments
    return hist


def current_titles():
    """Current listed names by CIK; the cik-lookup list often leads with historical aliases."""
    t = json.load(open(os.path.join(DATA, "edgar", "company_tickers.json")))
    out = {}
    for v in t.values():
        out.setdefault(int(v["cik_str"]), v["title"])
    return out


def main():
    items = json.load(open(os.path.join(EVAL, "mapping.json")))
    titles = current_titles()
    frame = {e["oi"]: e for e in json.load(open(os.path.join(DATA, "frame", "retail_frame.json")))}
    confirmed = [i for i in items if i["kind"] == "moodys" and i["status"] == "confirmed"]
    n_all = len(confirmed)
    if not confirmed:
        print("no confirmed mappings yet; decide items in the review UI first "
              "(python3 evaluation/review_server.py)")
        return
    groups = {}
    for it in confirmed:
        groups.setdefault(it["group"], []).append(it)
    # Folders exist to be evaluated against a label; groups with no actively rated member have
    # none. Their mappings stay recorded in mapping.json, they just get no folder.
    inactive = sorted(g for g, ms in groups.items() if not any(m.get("current") for m in ms))
    groups = {g: ms for g, ms in groups.items() if any(m.get("current") for m in ms)}

    # Never wipe the tree: folders accumulate fetched filings and verification results.
    # Only company.json and ratings.json are (re)written; stale folders are reported, not deleted.
    os.makedirs(OUT, exist_ok=True)
    expected = {slug(g) for g in groups}
    stale = [x for x in sorted(os.listdir(OUT))
             if os.path.isdir(os.path.join(OUT, x)) and x not in expected]
    if stale:
        print(f"  note: {len(stale)} folders no longer in the confirmed active set "
              f"(kept, delete by hand if wanted): {', '.join(stale[:8])}{' ...' if len(stale) > 8 else ''}")
    for gname, members in sorted(groups.items()):
        ciks = sorted({m["decided_cik"] for m in members})
        # Primary filer for the evaluation: bond-issuing subsidiaries and predecessor entities
        # keep their own historical CIK in the mapping, but documents come from whichever group
        # member still files. Pick by (currently filing, latest annual filing date).
        def filer_rank(m):
            fr = frame.get(m["oi"], {})
            return (fr.get("filing_status") == "aktueller Filer", fr.get("last_annual") or "")
        primary = max(members, key=filer_rank)
        primary_cik = primary["decided_cik"]
        d = os.path.join(OUT, slug(gname))
        os.makedirs(d, exist_ok=True)
        company = {
            "group": gname,
            "cik": primary_cik,
            "cik_note": (None if len(ciks) == 1 else
                         "group members map to multiple CIKs; primary is the current filer, "
                         "see members[].decided_cik for the others"),
            "all_ciks": ciks,
            "edgar_name": titles.get(primary_cik, primary["decided_edgar_name"]),
            "scope": max(members, key=lambda m: bool(m.get("current"))).get("scope"),
            "current_rating_at_file_date": max(members, key=lambda m: bool(m.get("current"))).get("current"),
            "filing_status": frame.get(primary["oi"], {}).get("filing_status"),
            "last_annual": frame.get(primary["oi"], {}).get("last_annual"),
            "rating_file_date": STAMP,
            "members": [{
                "moodys_name": m["moodys_name"], "oi": m["oi"], "lei": m.get("lei", ""),
                "decided_cik": m["decided_cik"], "decided_edgar_name": m["decided_edgar_name"],
                "decided_by": m["decided_by"], "decided_at": m["decided_at"],
                "note": m.get("note", ""),
            } for m in members],
        }
        json.dump(company, open(os.path.join(d, "company.json"), "w"),
                  indent=1, ensure_ascii=False)
        ratings = {"source": f"SEC 17g-7(b) disclosure, Moody's, file date {STAMP}",
                   "entities": [entity_history(m["oi"]) for m in members]}
        json.dump(ratings, open(os.path.join(d, "ratings.json"), "w"),
                  indent=1, ensure_ascii=False)
    n_skipped = len([i for i in items if i["kind"] == "moodys"
                     and i["status"] in ("no_sec_filer",)])
    import collections
    sc = collections.Counter()
    fs = collections.Counter()
    for x in os.listdir(OUT):
        cj = os.path.join(OUT, x, "company.json")
        if os.path.exists(cj):
            c = json.load(open(cj))
            sc[c["scope"]] += 1
            fs["aktuell" if c.get("filing_status") == "aktueller Filer" else "nur historisch"] += 1
    print(f"{len(groups)} company folders written to evaluation/companies/ "
          f"(from {n_all} confirmed entities; {len(inactive)} groups without an active rating "
          f"skipped; {n_skipped} decided no-SEC-filer)")
    print(f"  scope: {dict(sc)}   filings: {dict(fs)}")


if __name__ == "__main__":
    main()
