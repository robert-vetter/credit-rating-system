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

Run: python3 evaluation/compile_folders.py
"""
import html
import json
import os
import re
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
EVAL = os.path.join(ROOT, "evaluation")
OUT = os.path.join(EVAL, "companies")
OB_ZIP = os.path.join(DATA, "xbrl100-obligor-2026-08-11.zip")
IS_ZIP = os.path.join(DATA, "xbrl100-issuer-2026-08-11.zip")
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


def main():
    items = json.load(open(os.path.join(EVAL, "mapping.json")))
    confirmed = [i for i in items if i["kind"] == "moodys" and i["status"] == "confirmed"]
    if not confirmed:
        print("no confirmed mappings yet; decide items in the review UI first "
              "(python3 evaluation/review_server.py)")
        return
    groups = {}
    for it in confirmed:
        groups.setdefault(it["group"], []).append(it)

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for gname, members in sorted(groups.items()):
        ciks = sorted({m["decided_cik"] for m in members})
        if len(ciks) > 1:
            print(f"  WARNING {gname}: members map to multiple CIKs {ciks}")
        d = os.path.join(OUT, slug(gname))
        os.makedirs(d, exist_ok=True)
        company = {
            "group": gname,
            "cik": ciks[0],
            "edgar_name": members[0]["decided_edgar_name"],
            "scope": members[0].get("scope"),
            "current_rating_at_file_date": members[0].get("current"),
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
    print(f"{len(groups)} company folders written to evaluation/companies/ "
          f"({len(confirmed)} confirmed entities; {n_skipped} decided as no-SEC-filer, no folder)")


if __name__ == "__main__":
    main()
