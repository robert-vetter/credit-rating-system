"""
Source-date evidence for the saved-input control of Experiment 04 (decision D12, option c).

Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-12. Offline; no network.

The seven Opus successes of Experiment 03 are re-run on Qwen with exactly the inputs Opus saw.
Those inputs are saved verbatim (requests_raw.json of the two batches), but the history packs
in them were built by the 2026-09-10 builder without per-fact provenance, and the builder and
the XBRL extraction changed afterwards. This module recovers the evidence without changing the
supplied text: it re-runs the vendored 2026-09-10 code (legacy_builders/) on the raw SEC
companyfacts cache (data/edgar/companyfacts/, fetched 2026-09-11) inside a temporary mirror of
the company folders, checks that the result is byte-identical to the saved pack, and then
records, for every figure the saved pack shows, the raw record it came from with its period
end, filing date, tag and form, asserting end <= filed <= as_of. Rating events are checked
against the history end. Nothing under evaluation/companies/ is written.

Inputs: saved audit.json/requests of Experiment 03, data/edgar/companyfacts/, company folders.
Output: one sidecar dict per issuer (written by prepare_inputs.py to audit/legacy/<id>.json).
"""
import hashlib
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "legacy_builders"))
sys.path.insert(0, os.path.join(ROOT, "system"))
import fetch_xbrl_20260910 as fx          # noqa: E402
import history_pack_20260910 as ohp       # noqa: E402
import peer_table_20260910 as opt         # noqa: E402

COMPANIES = os.path.join(ROOT, "evaluation", "companies")
RAW = os.path.join(ROOT, "data", "edgar", "companyfacts")
E03 = os.path.join(ROOT, "experiments", "03-oos-values-first")
AS_OF, HISTORY_END = "2026-08-29", "2025-08-28"
ALLOWED_XBRL_FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "40-F"}


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def old_extract(raw):
    """The 2026-09-10 extraction (fetch_xbrl.py main loop at fe4613c), in memory."""
    gaap = raw.get("facts", {}).get("us-gaap", {})
    fields = {}
    for canon, tags in fx.CONCEPTS.items():
        merged, merged_q = {}, {}
        for tag in tags:
            units = gaap.get(tag, {}).get("units", {}).get("USD", [])
            for v in fx.annual_values(units, canon in fx.INSTANT):
                if v["end"] not in merged:
                    merged[v["end"]] = {**v, "tag": tag}
            for v in fx.quarterly_values(units, canon in fx.INSTANT):
                if v["end"] not in merged_q:
                    merged_q[v["end"]] = {**v, "tag": tag}
        if merged or merged_q:
            fields[canon] = {"annual": sorted(merged.values(), key=lambda x: x["end"]),
                             "quarterly": sorted(merged_q.values(), key=lambda x: x["end"])}
    return fields


class Mirror:
    """Temporary copy of evaluation/companies/ with 2026-09-10-style xbrl.json per company."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="exp04-legacy-")
        self.xbrl, self.raw_sha, self.companies = {}, {}, {}
        for slug in sorted(os.listdir(COMPANIES)):
            d = os.path.join(COMPANIES, slug)
            if not os.path.exists(os.path.join(d, "company.json")):
                continue
            os.makedirs(os.path.join(self.dir, slug))
            for f in ("company.json", "ratings.json", "observations.json"):
                if os.path.exists(os.path.join(d, f)):
                    os.symlink(os.path.join(d, f), os.path.join(self.dir, slug, f))
            self.companies[slug] = json.load(open(os.path.join(d, "company.json")))
            rp = os.path.join(RAW, slug + ".json")
            record = {"cik": self.companies[slug]["cik"], "fields": {}}
            if os.path.exists(rp):
                self.raw_sha[slug] = sha256_file(rp)
                raw = json.load(open(rp))
                if "error" not in raw:
                    record = {"cik": raw.get("cik"), "entity": raw.get("entityName", ""),
                              "source": "2026-09-10 extraction re-run on the raw companyfacts cache",
                              "fields": old_extract(raw)}
            self.xbrl[slug] = record
            json.dump(record, open(os.path.join(self.dir, slug, "xbrl.json"), "w"))
        ohp.OUT = self.dir
        opt.OUT = self.dir

    def reconstruct(self, slug):
        return ohp.build(slug, AS_OF, history_end=HISTORY_END)


def _dated(rec):
    return bool(rec.get("filed")) and bool(rec.get("end")) and rec["end"] <= rec["filed"] <= AS_OF


def provenance(mirror, slug, saved_text):
    """Per-figure source records for one saved pack, with the identity proof."""
    text, log = mirror.reconstruct(slug)
    identical = text == saved_text
    xbrl = mirror.xbrl[slug]
    fields = xbrl.get("fields", {})
    problems = []
    # Fiscal-year rows: the old fy_values (filed <= as_of), one record per (end, field).
    years = ohp.fy_values(xbrl, AS_OF)
    ends = sorted(years)
    shown_ends = re.findall(r"^  FY ending (\d{4}-\d{2}-\d{2})", saved_text, flags=re.M)
    annual = {}
    for end in shown_ends:
        annual[end] = {}
        for field, blob in fields.items():
            recs = [v for v in blob.get("annual", []) if v["end"] == end and v.get("filed", "9999") <= AS_OF]
            if recs:
                rec = recs[-1]
                annual[end][field] = {k: rec.get(k) for k in ("end", "filed", "tag", "form", "val")}
                if not _dated(rec) or rec.get("form") not in ALLOWED_XBRL_FORMS:
                    problems.append(f"annual {end} {field}: {rec}")
        if end not in years:
            problems.append(f"shown FY {end} not in fy_values")
    # Quarterly rows.
    shown_q = re.findall(r"^  quarter ending (\d{4}-\d{2}-\d{2})", saved_text, flags=re.M)
    quarterly = {}
    for end in shown_q:
        quarterly[end] = {}
        for field, blob in fields.items():
            recs = [v for v in blob.get("quarterly", []) if v["end"] == end and v.get("filed", "9999") <= AS_OF]
            if recs:
                rec = recs[-1]
                quarterly[end][field] = {k: rec.get(k) for k in ("end", "filed", "tag", "form", "fp", "val")}
                if not _dated(rec) or rec.get("form") not in ALLOWED_XBRL_FORMS:
                    problems.append(f"quarterly {end} {field}: {rec}")
    # Peer rows: the old _latest picks, per field, the last annual record with end <= t, filed <= t.
    peers = {}
    for pslug in sorted(mirror.companies):
        c = mirror.companies[pslug]
        if pslug == slug or c.get("scope") != "in":
            continue
        pf = mirror.xbrl.get(pslug, {}).get("fields", {})
        if not pf:
            continue
        if opt._latest(pf.get("revenue", {}), AS_OF) is None:
            continue
        row = {}
        for field, blob in pf.items():
            vals = [v for v in blob.get("annual", []) if v["end"] <= AS_OF and v.get("filed", "9") <= AS_OF]
            if vals:
                rec = vals[-1]
                assert rec["val"] == opt._latest(blob, AS_OF)
                row[field] = {k: rec.get(k) for k in ("end", "filed", "tag", "form", "val")}
                if not _dated(rec) or rec.get("form") not in ALLOWED_XBRL_FORMS:
                    problems.append(f"peer {pslug} {field}: {rec}")
        peers[pslug] = {"group": c["group"], "printed_name": c["group"][:27], "fields": row,
                        "fiscal_ends": sorted({r["end"] for r in row.values()}),
                        "mixed_periods": len({r["end"] for r in row.values()}) > 1}
    printed_peers = re.findall(r"^(\S.{0,26}?)\s{2,}", saved_text.split("<peer_table>")[1], flags=re.M)
    printed_peers = [p for p in printed_peers if p not in ("Rated", "Figures", "debt", "company")]
    # Rating events: the old path is the latest observation's rating_path (built from ratings.json
    # on 2026-08-29) filtered to the history end; check dates and completeness against raw records.
    obs = json.load(open(os.path.join(COMPANIES, slug, "observations.json")))["observations"]
    path = [e for e in obs[-1]["rating_path"] if e[0] <= HISTORY_END]
    ratings = json.load(open(os.path.join(COMPANIES, slug, "ratings.json")))
    sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
    import history_pack as current_hp   # the repaired builder, for typed_events
    raw_events = current_hp.typed_events(ratings, HISTORY_END)
    omitted_after_grid = [e for e in raw_events if e[0] > obs[-1]["date"]]
    event_dates_ok = all(e[0] <= HISTORY_END for e in path)
    terminal = ohp.rating_at(ratings, HISTORY_END)
    if omitted_after_grid:
        problems.append(f"raw events after the observation grid omitted from the saved path: {omitted_after_grid}")
    return {"slug": slug, "identical_to_saved": identical,
            "saved_sha256": hashlib.sha256(saved_text.encode()).hexdigest(),
            "reconstructed_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "raw_companyfacts_sha256": mirror.raw_sha.get(slug),
            "as_of": AS_OF, "history_end": HISTORY_END,
            "annual_sources": annual, "quarterly_sources": quarterly,
            "peer_sources": peers, "peers_printed": len(printed_peers), "peers_traced": len(peers),
            "rating_path_source": "observations.json rating_path derived from ratings.json (2026-08-29), filtered to the history end",
            "rating_path": path, "rating_event_dates_ok": event_dates_ok,
            "raw_events_after_grid_omitted": [list(e) for e in omitted_after_grid],
            "terminal_rating_2026_09_10_selector": terminal,
            "counts": {"annual_records": sum(len(v) for v in annual.values()),
                       "quarterly_records": sum(len(v) for v in quarterly.values()),
                       "peer_records": sum(len(p["fields"]) for p in peers.values())},
            "problems": problems,
            "all_dated_and_eligible": identical and not problems and event_dates_ok}


if __name__ == "__main__":
    a1 = json.load(open(os.path.join(E03, "runs", "msgbatch_01EwnHhsKjahuwhmL8S5h2Sx", "audit.json")))
    saved = {it["id"]: it for it in a1["observations"] if not it.get("skipped")}
    m = Mirror()
    for xid in sys.argv[1:] or sorted(saved):
        p = provenance(m, saved[xid]["slug"], saved[xid]["pack_text"])
        print(xid, p["slug"], "identical" if p["identical_to_saved"] else "DIFFERS", p["counts"],
              "peers printed/traced", p["peers_printed"], p["peers_traced"], "ok" if p["all_dated_and_eligible"] else p["problems"][:3])
