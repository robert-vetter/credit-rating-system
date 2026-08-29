"""
Sector count and sample frame: which Moody's-rated issuers are Retail and Apparel SEC filers.

Written by Claude (Opus 5) as part of the rating-history work described in rating-history-file.md.

Pipeline: read both 17g-7 zip archives from data/, take the union of Corporate entities from the
obligor set (entity-level ratings) and the issuer set (instrument-level ratings), match names to
EDGAR CIKs in two tiers (listed companies, then all SEC filers), fetch each match's SIC industry
code from the SEC submissions API (cached in data/sic_cache.json), filter to Retail and Apparel
codes, and determine each issuer's current rating using the methodology's label rule: entity-level
rating where an active one exists, otherwise the most senior active instrument-level rating.

Sector definition, deliberately transparent so it can be argued with: retail is SIC 5200-5999
excluding 5810-5819 (eating and drinking places have their own methodology); apparel manufacturing 2300-2399;
footwear and leather 3021 and 3100-3199; apparel wholesale 5136-5137.

Requires network for the EDGAR lists and any uncached SIC lookups. SEC fair-use: identify yourself
via the UA constant and stay under 10 requests per second.

Run: python3 notes/sector_count.py
"""

import collections
import json
import os
import queue
import re
import threading
import time
import urllib.request
import zipfile

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
UA = {"User-Agent": "Robert Vetter robert@certus-ai.com"}
OBLIGOR_ZIP = os.path.join(DATA, "xbrl100-obligor-2026-08-11.zip")
ISSUER_ZIP = os.path.join(DATA, "xbrl100-issuer-2026-08-11.zip")
SIC_CACHE = os.path.join(DATA, "sic_cache.json")
FRAME_OUT = os.path.join(DATA, "retail_frame.json")

LT_TYPES = ("LT CORPORATE FAMILY RATINGS", "LT ISSUER RATING", "ISSUER RATING", "ISSUER LT RATING")
HDR = re.compile(r"<(OSC|OBNAME|SSC|ISSNAME|LEI|OI|ISI)\b[^>]*>([^<]*)</\1>")
FLD = re.compile(r"<(R|RAD|RAC|RT)\b[^>]*>([^<]*)</\1>")
SUFFIX = re.compile(r"\b(INCORPORATED|INC|CORPORATION|CORP|COMPANY|CO|LIMITED|LTD|LLC|L L C|LP|L P|PLC|SA|NV|AG|SE)\b\.?$")


def _base(name):
    n = name.upper().replace("&AMP;", "&")
    n = re.sub(r"/[A-Z ]{0,6}/?\s*$", "", n)  # EDGAR suffixes like /NEW/ /DE/
    n = re.sub(r"\(THE\)\s*$", "", n)
    n = re.sub(r"^THE\s+", "", n)
    return n


def _tidy(n):
    n = re.sub(r"\s+", " ", n).strip()
    prev = None
    while prev != n:
        prev = n
        n = SUFFIX.sub("", n).strip()
    return n


def variants(name):
    """Two normalisations, because a period means different things in the two sources.

    Moody's writes AMAZON.COM and V.F. CORPORATION; EDGAR writes AMAZON COM and V F CORP.
    Deleting periods gives AMAZONCOM and never matches; turning them into spaces gives
    AMAZON COM and does. But deleting is right for CO., INC. style abbreviations.

    Same story for apostrophes and hyphens (O'REILLY vs O REILLY, G-III vs G III) and for
    "AND" versus "&" (PETCO HEALTH AND WELLNESS): each class found as a real miss by the
    reverse completeness check.

    Returns [delete-periods, periods-to-spaces, all-to-spaces] in that fixed order. The forms
    index separately and are never pooled: pooling them into one index turns names that were
    previously unique into collisions and loses more matches than it gains.
    """
    n = _base(name)
    n = re.sub(r"\bAND\b", "&", n)  # PETCO HEALTH AND WELLNESS vs ... & WELLNESS
    a = re.sub(r"[.,\'’`\"]", "", n)
    a = re.sub(r"[/\\]", " ", a)
    b = re.sub(r"[\'’`\"]", "", n)
    b = re.sub(r"[.,/\\]", " ", b)
    c = re.sub(r"[.,\'’`\"\-]", " ", n)  # O'REILLY vs O REILLY, G-III vs G III
    return [_tidy(a), _tidy(b), _tidy(c)]  # ordered, never a set: set order varies per run


def norm(name):
    """Single canonical form, for index keys where one string is needed."""
    return _tidy(re.sub(r"[/\\]", " ", re.sub(r"[.,\'’`\"]", "", _base(name))))


def sector_bucket(sic):
    if not sic or not sic.isdigit():
        return None
    s = int(sic)
    if 5810 <= s <= 5819:
        return None  # eating and drinking places, own methodology; 5810 itself occurs (Starbucks)
    if 5200 <= s <= 5999:
        return "retail"
    if 2300 <= s <= 2399:
        return "apparel_mfg"
    if s == 3021 or 3100 <= s <= 3199:
        return "footwear_leather"
    if s in (5136, 5137):
        return "apparel_wholesale"
    return None


def header_meta(text):
    """First occurrence of each header tag. Some files carry a long namespace preamble, so a
    fixed byte window silently misses the entity id (101 issuer-set Corporates, e.g. Heineken,
    plus 295 files whose class tag sat outside the window too); parse the full text instead."""
    meta = {}
    for m in HDR.finditer(text):
        meta.setdefault(m.group(1), m.group(2))
    return meta


def load_corporates():
    """Union of Corporate entities from both zips, keyed by Moody's entity id."""
    entities = {}
    with zipfile.ZipFile(OBLIGOR_ZIP) as z:
        for zn in z.namelist():
            if not zn.endswith(".xml"):
                continue
            d = z.read(zn).decode("utf-8", "ignore")
            meta = header_meta(d)
            if meta.get("OSC") != "Corporate":
                continue
            recs = []
            for m in re.finditer(r"<ORD>(.*?)</ORD>", d, re.S):
                recs.append(dict((f.group(1), f.group(2)) for f in FLD.finditer(m.group(1))))
            entities[meta.get("OI", "")] = {
                "name": meta.get("OBNAME", ""), "lei": meta.get("LEI", ""),
                "oi": meta.get("OI", ""), "obligor_records": recs,
            }
    with zipfile.ZipFile(ISSUER_ZIP) as z:
        for zn in z.namelist():
            if not zn.endswith(".xml"):
                continue
            head = z.read(zn)[:1600].decode("utf-8", "ignore")
            meta = header_meta(head)
            if meta.get("SSC") != "Corporate" or not meta.get("ISI"):
                meta = header_meta(z.read(zn).decode("utf-8", "ignore"))
            if meta.get("SSC") != "Corporate":
                continue
            oi = meta.get("ISI", "")
            if not oi:
                raise ValueError(f"{zn}: Corporate issuer file with no ISI anywhere")
            if oi not in entities:
                entities[oi] = {"name": meta.get("ISSNAME", ""), "lei": meta.get("LEI", ""),
                                "oi": oi, "obligor_records": []}
    return entities


def match_to_edgar(entities):
    """Match Moody's entity names to EDGAR CIKs.

    Two index tiers (listed companies, then all SEC filers) crossed with two name
    normalisations, tried in a fixed order: the strict form against both tiers first, then
    the period-splitting form. A name is only accepted when the index it hits holds exactly
    one CIK, so an ambiguous fallback never overrides a clean strict match.
    """
    tickers = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://www.sec.gov/files/company_tickers.json", headers=UA)))
    tier1 = [collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)]
    for v in tickers.values():
        for i, key in enumerate(variants(v["title"])):
            if key:
                tier1[i][key].add(int(v["cik_str"]))
    tier2 = [collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)]
    lookup = urllib.request.urlopen(urllib.request.Request(
        "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt", headers=UA)).read().decode("latin-1")
    for line in lookup.split("\n"):
        if line.count(":") < 2:
            continue
        name, cik = line.rsplit(":", 2)[0], line.rsplit(":", 2)[1]
        if cik.isdigit():
            for i, key in enumerate(variants(name)):
                if key:
                    tier2[i][key].add(int(cik))
    matched = []
    for e in entities.values():
        keys = variants(e["name"])
        forms = ["strict", "period-split", "all-split"]
        for fi in (0, 1, 2):
            hit = None
            for tier in (tier1, tier2):
                ciks = tier[fi].get(keys[fi]) if keys[fi] else None
                if ciks and len(ciks) == 1:
                    hit = next(iter(ciks))
                    break
            if hit is not None:
                e["cik"] = hit
                e["match_form"] = forms[fi]
                matched.append(e)
                break
    return matched


def fetch_sics(matched):
    cache = json.load(open(SIC_CACHE)) if os.path.exists(SIC_CACHE) else {}
    todo = list({e["cik"] for e in matched if str(e["cik"]) not in cache})
    if todo:
        sic_re = re.compile(r'"sic":"(\d*)","sicDescription":"([^"]*)"')
        q = queue.Queue()
        for c in todo:
            q.put(c)
        lock = threading.Lock()

        def worker():
            while True:
                try:
                    cik = q.get_nowait()
                except queue.Empty:
                    return
                try:
                    req = urllib.request.Request(
                        f"https://data.sec.gov/submissions/CIK{cik:010d}.json",
                        headers={**UA, "Range": "bytes=0-900"})
                    d = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
                    m = sic_re.search(d)
                    val = [m.group(1), m.group(2)] if m else ["", ""]
                except Exception as exc:
                    val = ["ERR", str(exc)[:40]]
                with lock:
                    cache[str(cik)] = val
                time.sleep(0.75)  # 6 workers x 0.75s keeps us under the SEC rate limit

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        json.dump(cache, open(SIC_CACHE, "w"))
    return cache


def current_rating(entity, issuer_zip):
    """Label rule: active entity-level LT rating first, else most senior active instrument rating."""
    recs = [r for r in entity["obligor_records"] if r.get("RT", "").upper() in LT_TYPES]
    last = max(recs, key=lambda r: r.get("RAD", ""), default=None)
    if last and last.get("R") != "WR":
        return {"rating": last["R"], "date": last["RAD"], "type": last["RT"], "level": "obligor"}
    # No directory prefix inside the archive: the XML files sit at the root.
    zn = f"Moodys-NRSRO-{entity['oi']}-Issuer-2026-08-11.xml"
    try:
        d = issuer_zip.read(zn).decode("utf-8", "ignore")
    except KeyError:
        return None
    best = None
    for im in re.finditer(r"<IND>(.*?)</IND>", d, re.S):
        recs = []
        for m in re.finditer(r"<INRD>(.*?)</INRD>", im.group(1), re.S):
            f = dict((x.group(1), x.group(2)) for x in FLD.finditer(m.group(1)))
            recs.append((f.get("RAD", ""), f.get("R", ""), f.get("RT", "")))
        if not recs:
            continue
        last = max(recs)
        if last[1] == "WR" or last[2] == "Commercial Paper":
            continue
        rank = {"Senior Unsecured": 3, "Senior Unsec. Shelf": 2}.get(last[2], 1)
        if best is None or (rank, last[0]) > best[0]:
            best = ((rank, last[0]),
                    {"rating": last[1], "date": last[0], "type": last[2], "level": "instrument"})
    return best[1] if best else None


if __name__ == "__main__":
    entities = load_corporates()
    print(f"Corporate entities in the union of both sets: {len(entities):,}")
    matched = match_to_edgar(entities)
    print(f"uniquely matched to an EDGAR CIK: {len(matched):,}")
    cache = fetch_sics(matched)
    frame = []
    with zipfile.ZipFile(ISSUER_ZIP) as iz:
        for e in matched:
            sic, desc = cache.get(str(e["cik"]), ["", ""])
            bucket = sector_bucket(sic)
            if not bucket:
                continue
            frame.append({"name": e["name"], "cik": e["cik"], "oi": e["oi"], "lei": e["lei"],
                          "sic": sic, "sic_desc": desc, "bucket": bucket,
                          "current": current_rating(e, iz)})
    active = [f for f in frame if f["current"]]
    order = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
             "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]
    by_r = collections.Counter(f["current"]["rating"] for f in active)
    ig = sum(v for k, v in by_r.items() if k in order and order.index(k) <= 9)
    print(f"\nRetail and Apparel frame: {len(frame)} issuers, {len(active)} actively rated")
    print(f"  investment grade {ig}, speculative {len(active) - ig}")
    for r in order:
        if by_r.get(r):
            print(f"  {r:<5} {'#' * by_r[r]} {by_r[r]}")
    json.dump(frame, open(FRAME_OUT, "w"), indent=1)
    print(f"\nframe written to {FRAME_OUT}")
