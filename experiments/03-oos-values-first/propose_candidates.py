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

HERE = os.path.dirname(os.path.abspath(__file__))
B, AS_OF = "2025-09-30", "2026-08-29"
h = json.load(open(os.path.join(HERE, "harvest.json")))

items, review = [], []
for slug, v in sorted(h.items()):
    stmts = [x for x in v["hits"] if "symbols" in x and x["class"] == "statement" and len(x["symbols"]) == 1
             and B < x["filed"] <= AS_OF]
    others = [x for x in v["hits"] if "symbols" in x and x not in stmts]
    if stmts:
        s = max(stmts, key=lambda x: x["filed"])
        label = s["symbols"][0]
        items.append({"id": f"X{len(items) + 1:02d}", "slug": slug, "group": v["group"], "cik": v["cik"],
                      "label": label, "persistence": v["persistence_file_end"],
                      "changed": bool(v["persistence_file_end"]) and label != v["persistence_file_end"],
                      "label_evidence": {"form": s["form"], "filed": s["filed"],
                                         "url": f"https://www.sec.gov/Archives/edgar/data/{v['cik']}/"
                                                f"{s['accession'].replace('-', '')}/{s['primaryDocument']}",
                                         "snippet": s["snippet"], "class": "statement"},
                      "n_statements_in_window": len(stmts), "status": "proposed"})
    review.append({"slug": slug, "n_statement": len(stmts), "n_other": len(others)})

json.dump({"boundary_B": B, "as_of": AS_OF, "model": "claude-opus-4-6",
           "rule": "latest single-symbol statement-class self-disclosure after B; human-confirmed before use",
           "items": items}, open(os.path.join(HERE, "candidates.json"), "w"), indent=1, ensure_ascii=False)
ch = [i for i in items if i["changed"]]
print(f"{len(items)} vorgeschlagene Kandidaten, davon {len(ch)} mit Aenderung vs Datei-Ende:")
for i in ch:
    print(f"   {i['slug']:<24} {i['persistence']} -> {i['label']}  ({i['label_evidence']['form']} {i['label_evidence']['filed']})")
print("Firmen ohne statement-Treffer:", [r["slug"] for r in review if r["n_statement"] == 0 and r["n_other"] > 0][:20])
