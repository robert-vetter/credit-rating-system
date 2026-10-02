"""
Experiment 10, design stage: sizing. How many next-quarter rating changes in the GPT-5.1 window
(outcome quarters 2025 Q1 and Q2) could be tested across all corporate sectors, and what would it take?

Written 2026-10-01 by Claude (Opus 5.5), directed by Robert Vetter (decision 0 in decisions.md). No model
call. Reads the two Moody's 17g-7 archives (data/moodys/), the SEC name list (data/edgar/cik-lookup-data.txt),
the confirmed mapping (evaluation/mapping.json, read only, used as the answer key for the matcher), and
downloads SEC submissions JSON for matched companies (Robert's approval of 2026-10-01) into the shared
cache data/all-sectors/sec-submissions/.

Steps, each writing into runs/sizing/ (gitignored):
    labels     quarterly labels of every corporate issuer, the label rule of build_observations.py
    match      proposed Moody's-to-SEC matches by normalised name; matcher scored against mapping.json
    fetch      SEC submissions for matched issuers with a label in the window (changes: all; stable: a seeded sample)
    summary    the sizing tables -> runs/sizing/sizing.json and printed Markdown

    python3 experiments/10-all-sector-next-quarter/sizing.py labels|match|fetch|summary
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "07-rating-change-base-rates"))
from build_withdrawn import quarterly_labels  # noqa: E402
from compile_folders import IND_META, ORD_FLD, STAMP  # noqa: E402
from fetch_xbrl import UA  # noqa: E402

OUT = os.path.join(HERE, "runs", "sizing")
SUBS = os.path.join(ROOT, "data", "all-sectors", "sec-submissions")   # shared cache since 2026-10-01
OB_ZIP = os.path.join(ROOT, "data", "moodys", "xbrl100-obligor-2026-08-11.zip")
IS_ZIP = os.path.join(ROOT, "data", "moodys", "xbrl100-issuer-2026-08-11.zip")
PRED = ("2024-12-31", "2025-03-31")
NEXT = {"2024-12-31": "2025-03-31", "2025-03-31": "2025-06-30"}
SEED, STABLE_SAMPLE = 20261001, 400
ELIGIBLE_DAYS = 450
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def category(r):
    n = notch(r)
    if n is None:
        return None
    return ["Aaa", "Aa", "Aa", "Aa", "A", "A", "A", "Baa", "Baa", "Baa", "Ba", "Ba", "Ba",
            "B", "B", "B", "Caa", "Caa", "Caa", "Ca-C", "Ca-C"][n]


# ----------------------------------------------------------------------------- labels

def corporate_members(z, kind):
    """{oi: member name} for files whose sector class is Corporate."""
    out = {}
    for n in z.namelist():
        m = re.search(rf"NRSRO-(\d+)-{kind}-", n)
        if not m:
            continue
        head = z.read(n)[:4000].decode("utf-8", "ignore")
        if re.search(r"<(?:OSC|SSC)[^>]*>Corporate</(?:OSC|SSC)>", head):
            out[m.group(1)] = n
    return out


def history(oi, zob, zis, ob_names, is_names):
    """The structure compile_folders.entity_history writes, from open archives."""
    hist = {"oi": oi, "obligor_records": None, "instruments": None, "name": None, "lei": None}
    if oi in ob_names:
        d = zob.read(ob_names[oi]).decode("utf-8", "ignore")
        hist["obligor_records"] = [dict((x.group(1), x.group(2)) for x in ORD_FLD.finditer(m.group(1)))
                                   for m in re.finditer(r"<ORD>(.*?)</ORD>", d, re.S)]
        hist["name"] = (re.search(r"<OBNAME[^>]*>([^<]*)</OBNAME>", d) or [None, None])[1]
        hist["lei"] = (re.search(r"<LEI[^>]*>([^<]*)</LEI>", d) or [None, None])[1]
    if oi in is_names:
        d = zis.read(is_names[oi]).decode("utf-8", "ignore")
        ins = []
        for im in re.finditer(r"<IND>(.*?)</IND>", d, re.S):
            meta = dict((x.group(1), x.group(2)) for x in IND_META.finditer(im.group(1)))
            recs = [dict((x.group(1), x.group(2)) for x in ORD_FLD.finditer(m.group(1)))
                    for m in re.finditer(r"<INRD>(.*?)</INRD>", im.group(1), re.S)]
            ins.append({"meta": meta, "records": recs})
        hist["instruments"] = ins
        if not hist["name"]:
            hist["name"] = (re.search(r"<(?:OBNAME|ISSNAME)[^>]*>([^<]*)</", d) or [None, None])[1]
    return hist


def labels():
    os.makedirs(OUT, exist_ok=True)
    zob, zis = zipfile.ZipFile(OB_ZIP), zipfile.ZipFile(IS_ZIP)
    ob_names, is_names = corporate_members(zob, "Obligor"), corporate_members(zis, "Issuer")
    ois = sorted(set(ob_names) | set(is_names))
    rows = []
    for i, oi in enumerate(ois):
        h = history(oi, zob, zis, ob_names, is_names)
        obs = {o["date"]: o for o in quarterly_labels({"entities": [h]})}
        for t in PRED:
            a, b = obs.get(t), obs.get(NEXT[t])
            if not a or not b or b.get("persistence") != a["label"]:
                continue
            na, nb = notch(a["label"]), notch(b["label"])
            rows.append({"oi": oi, "name": h["name"], "lei": h["lei"], "t": t, "rating_t": a["label"],
                         "level": a["label_level"], "next": b["label"],
                         "move": "unchanged" if a["label"] == b["label"] else
                         ("down" if (na is not None and nb is not None and nb > na) else "up"),
                         "level_switch": a["label_level"] != b["label_level"]})
        if i % 2000 == 0:
            print(f"  {i} of {len(ois)} issuers", flush=True)
    json.dump({"file_date": STAMP, "corporate_issuers": len(ois), "rows": rows},
              open(os.path.join(OUT, "labels.json"), "w"))
    c = collections.Counter(r["move"] for r in rows)
    print(f"{len(ois)} corporate issuers; window company-quarters {len(rows)}: {dict(c)}")


# ----------------------------------------------------------------------------- matching

LEGAL = {"INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LLC", "LC", "LP", "LTD", "LIMITED",
         "PLC", "SA", "NV", "AG", "SE", "THE", "DE", "OF", "AND"}


def norm(name):
    s = re.sub(r"\([^)]*\)", " ", (name or "").upper())
    s = s.replace("&", " AND ")
    s = re.sub(r"['’`.]", "", s)                 # KOHL'S -> KOHLS, L.L.C. -> LLC (fix of 2026-10-01)
    s = re.sub(r"\bL\.?\s?L\.?\s?C\b", "LLC", s)
    s = re.sub(r"\bL\.?\s?P\b", "LP", s)
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    toks = [t for t in s.split() if t not in LEGAL]
    return " ".join(toks)


def sec_names():
    idx = collections.defaultdict(set)
    for line in open(os.path.join(ROOT, "data", "edgar", "cik-lookup-data.txt"), encoding="latin-1"):
        parts = line.rstrip("\n").rsplit(":", 2)
        if len(parts) < 3 or not parts[1].isdigit():
            continue
        k = norm(parts[0])
        if k:
            idx[k].add(int(parts[1]))
    return idx


def propose(name, idx):
    cands = idx.get(norm(name), set())
    if len(cands) == 1:
        return next(iter(cands)), "unique", sorted(cands)
    if len(cands) > 1:
        return None, "ambiguous", sorted(cands)[:10]
    return None, "none", []


def match():
    lab = json.load(open(os.path.join(OUT, "labels.json")))
    idx = sec_names()
    # matcher scored on the 186 confirmed retail decisions (the answer key)
    items = [i for i in json.load(open(os.path.join(ROOT, "evaluation", "mapping.json")))
             if i["kind"] == "moodys" and i["status"] == "confirmed"]
    score = collections.Counter()
    for it in items:
        cik, kind, _ = propose(it["moodys_name"], idx)
        truth = int(it["decided_cik"]) if it.get("decided_cik") else None
        score[(kind, "right" if cik == truth else "wrong" if cik else "-")] += 1
    names = {r["oi"]: r["name"] for r in lab["rows"]}
    proposals = {oi: dict(zip(("cik", "kind", "candidates"), propose(n, idx))) for oi, n in names.items()}
    json.dump({"answer_key_score": {f"{k[0]}|{k[1]}": v for k, v in score.items()}, "proposals": proposals},
              open(os.path.join(OUT, "matches.json"), "w"), indent=0)
    print("matcher on the 186 confirmed retail decisions:", dict(score))
    print("window issuers:", collections.Counter(p["kind"] for p in proposals.values()))


# ----------------------------------------------------------------------------- SEC submissions

def fetch():
    lab = json.load(open(os.path.join(OUT, "labels.json")))
    mt = json.load(open(os.path.join(OUT, "matches.json")))["proposals"]
    rows = [r for r in lab["rows"] if mt[r["oi"]]["kind"] == "unique"]
    changed = {mt[r["oi"]]["cik"] for r in rows if r["move"] != "unchanged"}
    stable_ois = sorted({r["oi"] for r in rows if r["move"] == "unchanged"})
    rng = random.Random(SEED)
    sample = set(rng.sample(stable_ois, min(STABLE_SAMPLE, len(stable_ois))))
    ciks = sorted(changed | {mt[o]["cik"] for o in sample})
    d = SUBS
    os.makedirs(d, exist_ok=True)
    json.dump({"stable_sample_ois": sorted(sample), "seed": SEED}, open(os.path.join(OUT, "stable_sample.json"), "w"))
    got = 0
    for cik in ciks:
        path = os.path.join(d, f"CIK{cik:010d}.json")
        if os.path.exists(path):
            continue
        try:
            body = urllib.request.urlopen(urllib.request.Request(
                f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA), timeout=60).read()
        except urllib.error.HTTPError as exc:
            body = json.dumps({"error": f"HTTP {exc.code}"}).encode()
        open(path, "wb").write(body)
        got += 1
        time.sleep(0.15)
    print(f"submissions: {len(ciks)} CIKs ({len(changed)} with a change, {len(sample)} stable issuers sampled); downloaded {got}")


def filings_of(cik):
    path = os.path.join(SUBS, f"CIK{cik:010d}.json")
    if not os.path.exists(path):
        return None
    j = json.load(open(path))
    if "error" in j:
        return {"error": j["error"]}
    r = j.get("filings", {}).get("recent", {})
    fl = [{"form": f, "date": dte} for f, dte in zip(r.get("form", []), r.get("filingDate", []))]
    return {"sic": j.get("sic"), "sic_desc": j.get("sicDescription"), "state": (j.get("addresses", {}).get("business") or {}).get("stateOrCountry"),
            "filings": fl, "name": j.get("name")}


def eligible(f, t):
    if not f or "error" in f:
        return False, "no SEC record"
    ks = [x["date"] for x in f["filings"] if x["form"] in ("10-K", "10-K405") and x["date"] <= t]
    if not ks:
        return False, "no 10-K by t"
    age = (dt.date.fromisoformat(t) - dt.date.fromisoformat(max(ks))).days
    return (age <= ELIGIBLE_DAYS), (None if age <= ELIGIBLE_DAYS else f"latest 10-K {age} days old")


SIC_DIVISION = [(100, 999, "Agriculture"), (1000, 1499, "Mining and energy"), (1500, 1799, "Construction"),
                (2000, 3999, "Manufacturing"), (4000, 4999, "Transport, communications, utilities"),
                (5000, 5199, "Wholesale"), (5200, 5999, "Retail"), (6000, 6799, "Finance and real estate"),
                (7000, 8999, "Services"), (9100, 9999, "Public administration and other")]


def division(sic):
    try:
        s = int(sic)
    except (TypeError, ValueError):
        return "unknown"
    return next((n for a, b, n in SIC_DIVISION if a <= s <= b), "unknown")


def summary():
    lab = json.load(open(os.path.join(OUT, "labels.json")))
    m = json.load(open(os.path.join(OUT, "matches.json")))
    mt, key = m["proposals"], m["answer_key_score"]
    sample = set(json.load(open(os.path.join(OUT, "stable_sample.json")))["stable_sample_ois"])
    rows = lab["rows"]
    res = {"corporate_issuers": lab["corporate_issuers"], "answer_key_score": key}
    funnel = collections.OrderedDict()
    ch = [r for r in rows if r["move"] != "unchanged"]
    st = [r for r in rows if r["move"] == "unchanged"]
    funnel["window company-quarters with a label at t and t+1"] = (len(ch), len(st))
    ch_m = [r for r in ch if mt[r["oi"]]["kind"] == "unique"]
    st_m = [r for r in st if mt[r["oi"]]["kind"] == "unique"]
    funnel["unique SEC name match"] = (len(ch_m), len(st_m))
    ch_e, reasons = [], collections.Counter()
    for r in ch_m:
        ok, why = eligible(filings_of(mt[r["oi"]]["cik"]), r["t"])
        if ok:
            ch_e.append(r)
        else:
            reasons[why] += 1
    st_s = [r for r in st_m if r["oi"] in sample]
    st_e = [r for r in st_s if eligible(filings_of(mt[r["oi"]]["cik"]), r["t"])[0]]
    rate = len(st_e) / len(st_s) if st_s else None
    funnel["10-K within 450 days before t (stable: estimated from the sample)"] = (len(ch_e), round(len(st_m) * rate) if rate else None)
    res["funnel"] = funnel
    res["changed_not_eligible_reasons"] = dict(reasons)
    res["stable_sample"] = {"rows": len(st_s), "eligible": len(st_e), "rate": rate}
    res["eligible_changes"] = {"by_move": dict(collections.Counter(r["move"] for r in ch_e)),
                               "by_date": dict(collections.Counter(r["t"] for r in ch_e)),
                               "by_category": dict(collections.Counter(category(r["rating_t"]) for r in ch_e)),
                               "by_division": dict(collections.Counter(division((filings_of(mt[r["oi"]]["cik"]) or {}).get("sic")) for r in ch_e)),
                               "level_switches": sum(r["level_switch"] for r in ch_e),
                               "companies": len({r["oi"] for r in ch_e})}
    res["window_all_issuers"] = {"changes": len(ch), "by_move": dict(collections.Counter(r["move"] for r in ch)),
                                 "match_kinds_changed": dict(collections.Counter(mt[r["oi"]]["kind"] for r in ch))}
    json.dump(res, open(os.path.join(OUT, "sizing.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"labels": labels, "match": match, "fetch": fetch, "summary": summary}[sys.argv[1]]()
