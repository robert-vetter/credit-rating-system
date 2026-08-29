"""
Bulk acceptance of the automatic mapping proposals.

Written by Claude (Opus 5), directed by Robert Vetter.

On 2026-08-29 Robert decided in chat to accept all automatic Moody's-to-EDGAR proposals
wholesale instead of confirming each pair in the review UI. This script records that decision
honestly: every pending Moody's-side item with a proposal becomes "confirmed", each with a note
stating it was a bulk decision, not an individual review. The append-only log keeps one line
per item so downstream tooling sees a uniform schema. Items without a proposal stay pending.

The review UI remains the tool for revisiting any single pair (decisions are reversible) and
for the reverse-direction items once the listed-universe sweep lands.

Run: python3 evaluation/pipeline/bulk_accept.py
"""
import datetime
import json
import os

EVAL = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAPPING = os.path.join(EVAL, "mapping.json")
LOG = os.path.join(EVAL, "decisions.jsonl")
NOTE = ("Sammelentscheidung: automatischen Vorschlag pauschal akzeptiert "
        "(Robert im Chat, 2026-08-29), nicht einzeln geprueft")

def main():
    items = json.load(open(MAPPING))
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    n = 0
    with open(LOG, "a") as log:
        for it in items:
            if it["kind"] != "moodys" or it["status"] != "pending":
                continue
            if not it.get("proposed_cik"):
                print(f"  bleibt offen (kein Vorschlag): {it['moodys_name']}")
                continue
            it["status"] = "confirmed"
            it["decided_cik"] = it["proposed_cik"]
            it["decided_edgar_name"] = it.get("proposed_edgar_name", "")
            it["decided_by"] = "Robert Vetter"
            it["decided_at"] = ts
            it["note"] = NOTE
            log.write(json.dumps({"ts": ts, "key": it["key"], "action": "confirm",
                                  "by": "Robert Vetter", "note": NOTE,
                                  "cik": it["decided_cik"],
                                  "edgar_name": it["decided_edgar_name"]},
                                 ensure_ascii=False) + "\n")
            n += 1
    tmp = MAPPING + ".tmp"
    json.dump(items, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, MAPPING)
    print(f"{n} Mappings als Sammelentscheidung bestaetigt")


if __name__ == "__main__":
    main()
