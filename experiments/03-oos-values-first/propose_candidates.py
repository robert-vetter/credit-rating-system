"""
Turns harvest.json into a PROPOSED candidates.json for human validation.

Rule (README §2/§3): per company, the latest post-B filing whose Moody's mention is a
single-symbol *statement* of the current rating. Threshold/grid language and multi-symbol
windows are never auto-accepted; they are listed separately for hand reading. The proposal
is marked status "proposed" and becomes usable only after Robert confirms in chat; the
confirmation is then written into candidates.json (status "confirmed", by, date).

Run: python3 experiments/03-oos-values-first/propose_candidates.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
import history_pack  # noqa: E402

B, AS_OF = "2025-09-30", "2026-08-29"
HISTORY_END = "2025-08-28"   # latest action date in the 17g-7 file (measured), not the file date minus a year
h = json.load(open(os.path.join(HERE, "harvest.json")))

# Hand-read additions (2026-08-31): companies whose disclosure is a multi-symbol table or a
# narrative, resolved by the label rule (corporate family rating for speculative grade).
HAND = {
    "bath-body-works":   ("Ba2",  "10-Q", "2026-08-26", "table as of Aug 1, 2026: Moody's Corporate Ba2 (senior unsecured w/ guarantee Ba2, senior unsecured B1)"),
    "victoria-s-secret": ("Ba3",  "10-Q", "2026-06-05", "table as of May 2, 2026: Moody's Corporate Ba3 (senior secured Ba2, senior unsecured B1)"),
    "leslie-s-poolmart": ("Caa3", "10-K", "2025-12-18", "narrative: 'received downgraded credit ratings from Moody's to (Caa3 from Caa1)' during quarter ended Oct 4, 2025; file shows the CFR action on 2025-08-13, i.e. before B -> unchanged vs file end"),
    "qurate-qvc":        ("Caa3", "10-Q", "2025-11-05", "narrative: 'during October 2025 ... downgraded LI LLC's corporate family rating from Caa1 to Caa3 and its senior unsecured rating from Caa3 to C'; October 2025 > B -> genuine out-of-sample change; no later filing discloses a further action"),
}


def persistence_at_file_end(slug):
    r = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug, "ratings.json")))
    return history_pack.rating_at(r, HISTORY_END)

items, review = [], []
for slug, v in sorted(h.items()):
    stmts = [x for x in v["hits"] if "symbols" in x and x["class"] == "statement" and len(x["symbols"]) == 1
             and B < x["filed"] <= AS_OF]
    others = [x for x in v["hits"] if "symbols" in x and x not in stmts]
    pers = persistence_at_file_end(slug)
    if slug in HAND:
        label, form, filed, note = HAND[slug]
        hit = next(x for x in v["hits"] if x.get("form") == form and x.get("filed") == filed)
        items.append({"id": f"X{len(items) + 1:02d}", "slug": slug, "group": v["group"], "cik": v["cik"],
                      "label": label, "persistence": pers, "changed": bool(pers) and label != pers,
                      "label_evidence": {"form": form, "filed": filed,
                                         "url": f"https://www.sec.gov/Archives/edgar/data/{v['cik']}/"
                                                f"{hit['accession'].replace('-', '')}/{hit['primaryDocument']}",
                                         "snippet": hit["snippet"], "class": "hand-read", "note": note},
                      "n_statements_in_window": len(stmts), "status": "proposed"})
    elif stmts:
        s = max(stmts, key=lambda x: x["filed"])
        label = s["symbols"][0]
        items.append({"id": f"X{len(items) + 1:02d}", "slug": slug, "group": v["group"], "cik": v["cik"],
                      "label": label, "persistence": pers, "changed": bool(pers) and label != pers,
                      "label_evidence": {"form": s["form"], "filed": s["filed"],
                                         "url": f"https://www.sec.gov/Archives/edgar/data/{v['cik']}/"
                                                f"{s['accession'].replace('-', '')}/{s['primaryDocument']}",
                                         "snippet": s["snippet"], "class": "statement"},
                      "n_statements_in_window": len(stmts), "status": "proposed"})
    review.append({"slug": slug, "n_statement": len(stmts), "n_other": len(others)})

json.dump({"boundary_B": B, "as_of": AS_OF, "history_end": HISTORY_END, "model": "claude-opus-4-6",
           "rule": "latest single-symbol statement-class self-disclosure after B; human-confirmed before use",
           "items": items}, open(os.path.join(HERE, "candidates.json"), "w"), indent=1, ensure_ascii=False)
ch = [i for i in items if i["changed"]]
print(f"{len(items)} vorgeschlagene Kandidaten, davon {len(ch)} mit Aenderung vs Datei-Ende:")
for i in ch:
    print(f"   {i['slug']:<24} {i['persistence']} -> {i['label']}  ({i['label_evidence']['form']} {i['label_evidence']['filed']})")
print("Firmen ohne statement-Treffer:", [r["slug"] for r in review if r["n_statement"] == 0 and r["n_other"] > 0][:20])
