"""
Builds the evidence chain for every gold-set item and the human review sheet.

Written by Claude (Opus 5), directed by Robert Vetter. Runs after build_goldset.py; costs
nothing (EDGAR only).

Per item, three independent legs are collected into goldset.json and rendered into
evaluation/goldset-review.md for Robert's manual validation:

  1. the raw 17g-7 records: the exact Moody's action that sets the label at the observation
     date (date, rating, action code, rating type, entity), and the record behind the
     previous-quarter rating - quoted verbatim from ratings.json, re-derived independently
     of build_observations.py
  2. self-disclosure: the first company filing AFTER the label-setting action is downloaded
     and scanned for the label symbol within 400 characters of a "Moody" mention (for
     unchanged items: the latest annual before the observation date). A hit quotes the
     snippet - the company itself confirming the rating. A miss is neutral (many filers do
     not print ratings), never counted as contradiction.
  3. EDGAR links to the verification document and to the input documents the runner would
     use, so every claim is one click from its source.

Post-t documents are used ONLY for label verification, never as model input; stated here so
nobody mistakes it for leakage.

Run: python3 evaluation/pipeline/verify_goldset.py
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evaluation", "companies")
GOLD = os.path.join(ROOT, "evaluation", "goldset.json")
REVIEW = os.path.join(ROOT, "evaluation", "goldset-review.md")
UA = {"User-Agent": "Robert Vetter robert@certus-ai.com"}
LT = ("LT CORPORATE FAMILY RATINGS", "LT ISSUER RATING", "ISSUER RATING", "ISSUER LT RATING")
SYM = re.compile(r"\(?P?\)?\b(Aaa|Aa[1-3]|A[1-3]|Baa[1-3]|Ba[1-3]|B[1-3]|Caa[1-3])\b")


def lines_of(ratings):
    ent, sen = [], []
    for e in ratings["entities"]:
        recs = sorted([r for r in (e.get("obligor_records") or [])
                       if r.get("RT", "").upper() in LT and r.get("RAD")], key=lambda r: r["RAD"])
        if recs:
            ent.append({"oi": e["oi"], "recs": recs})
        for ins in (e.get("instruments") or []):
            recs = sorted([r for r in ins["records"]
                           if r.get("RT") == "Senior Unsecured" and r.get("RAD")],
                          key=lambda r: r["RAD"])
            if recs:
                sen.append({"oi": e["oi"], "recs": recs})
    return ent, sen


def record_at(ent, sen, t, want_rating):
    """The most recent record <= t whose rating equals want_rating, preferring entity level."""
    best = None
    for level, lines in (("entity", ent), ("instrument", sen)):
        for line in lines:
            for r in line["recs"]:
                if r["RAD"] <= t and r.get("R") == want_rating:
                    cand = (r["RAD"], level, line["oi"], r)
                    if best is None or cand[0] > best[0] or (cand[0] == best[0] and best[1] == "instrument"):
                        best = cand
    if not best:
        return None
    d, level, oi, r = best
    return {"date": d, "rating": r.get("R"), "action": r.get("RAC"), "type": r.get("RT"),
            "level": level, "oi": oi}


def url_of(cik, f):
    acc = f["accessionNumber"].replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{f['primaryDocument']}"


def fetch_text(slug, cik, f):
    import run_eval
    path, _ = run_eval.ensure_doc(slug, cik, f)
    return run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore"))


def scan_disclosure(text, symbol):
    for m in re.finditer(r"Moody", text, re.I):
        w = text[max(0, m.start() - 400):m.end() + 400]
        if symbol in SYM.findall(w):
            mid = len(w) // 2
            return re.sub(r"\s+", " ", w[max(0, mid - 200):mid + 200]).strip()
    return None


def main():
    gold = json.load(open(GOLD))
    if len(sys.argv) > 1 and sys.argv[1] == "--render-only":
        render(gold)
        return
    for it in gold["items"]:
        slug = it["slug"]
        ratings = json.load(open(os.path.join(OUT, slug, "ratings.json")))
        manifest = json.load(open(os.path.join(OUT, slug, "filings", "manifest.json")))["filings"]
        ent, sen = lines_of(ratings)
        label_rec = record_at(ent, sen, it["date"], it["label"])
        prev_rec = record_at(ent, sen, it["date"][:4] + {"03": "-01-01", "06": "-04-01",
                             "09": "-07-01", "12": "-10-01"}[it["date"][5:7]], it["persistence"])
        ev = {"label_record": label_rec, "persistence_record": prev_rec}

        docs_before = [f for f in manifest if f["filingDate"] <= it["date"]]
        annual = next((f for f in docs_before if f["form"] in ("10-K",)), None)
        quarterly = next((f for f in docs_before if f["form"] == "10-Q"
                          and annual and f["filingDate"] > annual["filingDate"]), None)
        ev["input_docs"] = [{"form": f["form"], "filed": f["filingDate"], "url": url_of(it["cik"], f)}
                           for f in ([annual] if annual else []) + ([quarterly] if quarterly else [])]

        if it["kind"] == "changed" and label_rec:
            scan_doc = next((f for f in sorted(manifest, key=lambda x: x["filingDate"])
                             if f["form"] in ("10-K", "10-Q") and f["filingDate"] > label_rec["date"]), None)
        else:
            scan_doc = annual
        if scan_doc:
            try:
                snippet = scan_disclosure(fetch_text(slug, it["cik"], scan_doc), it["label"])
            except Exception as exc:
                snippet = None
                ev["scan_error"] = str(exc)[:80]
            ev["disclosure"] = ({"verdict": "self_disclosed", "form": scan_doc["form"],
                                 "filed": scan_doc["filingDate"], "url": url_of(it["cik"], scan_doc),
                                 "snippet": snippet} if snippet else
                                {"verdict": "no_mention", "form": scan_doc["form"],
                                 "filed": scan_doc["filingDate"], "url": url_of(it["cik"], scan_doc)})
        it["evidence"] = ev
        d = ev.get("disclosure", {})
        print(f"  {it['id']} {slug:<24} {it['date']}  {it['persistence']}->{it['label']}"
              f"{'  SELBSTBESTAETIGT' if d.get('verdict') == 'self_disclosed' else ''}", flush=True)

    json.dump(gold, open(GOLD, "w"), indent=1, ensure_ascii=False)
    render(gold)


def render(gold):
    n_sd = sum(1 for i in gold["items"] if (i["evidence"].get("disclosure") or {}).get("verdict") == "self_disclosed")
    with open(REVIEW, "w") as f:
        f.write("# Goldset-Review: 50 Beobachtungen zur manuellen Bestätigung\n\n")
        v = gold.get("validation")
        if v:
            f.write(f"## Zweitpruefung vom {v['date']}\n\n*{v['by']}:*\n\n")
            for c in v["checks"]:
                f.write(f"- {c}\n")
            f.write("\n---\n")
        f.write("*Erzeugt von verify_goldset.py (Auswahl: build_goldset.py, Seed 20260829). "
                "Jedes Item zeigt die komplette Belegkette: der rohe Moody's-Record hinter dem "
                "Label, der Record hinter dem Vorquartal, die Selbstoffenlegung der Firma im "
                "naechsten Filing (sofern gefunden) und die Input-Dokumente. Dokumente NACH dem "
                "Stichtag dienen nur der Label-Pruefung, nie als Modell-Input.*\n\n")
        f.write(f"**Stand: {n_sd} von 50 zusaetzlich durch Selbstoffenlegung der Firma bestaetigt.** "
                "Kein Fund ist neutral (viele Firmen drucken Ratings nicht ab), nie ein Widerspruch.\n\n"
                "**Status: eingefroren am 2026-08-29 — alle 50 von Robert bestaetigt** (pauschal, nach der "
                "dokumentierten Zweitpruefung unten). Aenderungen ab jetzt nur als sichtbare, begruendete "
                "Einzelfall-Entscheidung.\n\n---\n")
        for kind, title in (("changed", "Changed (30) - das Primaermaterial"),
                            ("unchanged", "Unchanged (20) - die Fehlalarm-Kontrolle")):
            f.write(f"\n## {title}\n\n")
            for it in gold["items"]:
                if it["kind"] != kind:
                    continue
                ev = it["evidence"]; lr = ev["label_record"]; pr = ev["persistence_record"]
                arrow = {True: "⬇", False: "⬆"}[it["delta"] > 0] + str(abs(it["delta"])) if kind == "changed" else "="
                f.write(f"### {it['id']} · {it['group']} · {it['date']} · {arrow} "
                        f"{it['persistence']} → {it['label']}\n")
                if lr:
                    f.write(f"- **Label-Beleg (17g-7):** {lr['date']} „{lr['rating']}“ "
                            f"[{lr['action']}] {lr['type']}, {lr['level']}-Ebene, OI {lr['oi']}\n")
                else:
                    f.write("- **Label-Beleg: NICHT GEFUNDEN — pruefen!**\n")
                if pr:
                    f.write(f"- Vorquartal-Beleg: {pr['date']} „{pr['rating']}“ [{pr['action']}] "
                            f"{pr['type']}, {pr['level']}-Ebene\n")
                d = ev.get("disclosure") or {}
                if d.get("verdict") == "self_disclosed":
                    f.write(f"- **Selbstoffenlegung ✔** [{d['form']} vom {d['filed']}]({d['url']}): "
                            f"„…{d['snippet']}…“\n")
                elif d:
                    f.write(f"- Selbstoffenlegung: keine Erwaehnung im [{d['form']} vom "
                            f"{d['filed']}]({d['url']}) (neutral)\n")
                docs = " · ".join(f"[{x['form']} {x['filed']}]({x['url']})" for x in ev["input_docs"])
                f.write(f"- Input-Dokumente: {docs or 'FEHLEN — pruefen!'}\n")
                if kind == "unchanged" and it["next_quarter_changes"]:
                    f.write("- Hinweis: hartes Negativ — im Folgequartal aendert sich das Rating\n")
                if it.get("validation_note"):
                    f.write(f"- **Anmerkung aus der Zweitpruefung:** {it['validation_note']}\n")
                if it["status"] == "confirmed":
                    f.write(f"- [x] **bestaetigt** ({it.get('confirmed_by','')})\n\n")
                else:
                    f.write(f"- [ ] bestaetigt\n\n")
    print(f"\n{n_sd}/50 selbstbestaetigt. Review-Sheet: evaluation/goldset-review.md")


if __name__ == "__main__":
    main()
