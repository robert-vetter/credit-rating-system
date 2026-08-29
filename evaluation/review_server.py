"""
Local review UI for the manual Moody's-to-EDGAR mapping.

Written by Claude (Opus 5), directed by Robert Vetter. See evaluation/README.md.

Serves a single page on http://localhost:8531 showing every item from evaluation/mapping.json
alphabetically. Each decision is written immediately to two places: appended as one line to
evaluation/decisions.jsonl (the append-only audit log, never rewritten) and folded into
evaluation/mapping.json (the current state). No decision is ever lost by re-running any script;
re-deciding an item appends a new log line and the latest decision wins.

Search boxes query the full cached EDGAR name list (data/cik-lookup-data.txt, ~900k names) or
the full Moody's Corporate universe (data/moodys_corporates.json), so a wrong proposal can be
replaced by any company from either source, not just the automatic candidates.

Run: python3 evaluation/review_server.py   (stdlib only, no dependencies)
"""
import datetime
import json
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
EVAL = os.path.join(ROOT, "evaluation")
MAPPING = os.path.join(EVAL, "mapping.json")
LOG = os.path.join(EVAL, "decisions.jsonl")
PORT = 8531

print("loading EDGAR name list ...", flush=True)
EDGAR = []  # (name, cik)
for line in open(os.path.join(DATA, "cik-lookup-data.txt"), encoding="latin-1"):
    if line.count(":") < 2:
        continue
    name, cik = line.rsplit(":", 2)[0], line.rsplit(":", 2)[1]
    if cik.isdigit():
        EDGAR.append((name, int(cik)))
MOODYS = json.load(open(os.path.join(DATA, "moodys_corporates.json")))
ITEMS = json.load(open(MAPPING))
BY_KEY = {it["key"]: it for it in ITEMS}
print(f"{len(EDGAR)} EDGAR names, {len(MOODYS)} Moody's corporates, {len(ITEMS)} items", flush=True)


def save_items():
    tmp = MAPPING + ".tmp"
    json.dump(ITEMS, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, MAPPING)


def decide(payload):
    it = BY_KEY[payload["key"]]
    entry = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "key": payload["key"],
        "action": payload["action"],
        "by": payload.get("by") or "Robert Vetter",
        "note": payload.get("note", ""),
    }
    if payload["action"] == "pending":  # undo
        it["status"] = "pending"
        it["decided_by"] = it["decided_at"] = None
        if it["kind"] == "moodys":
            it["decided_cik"] = it["decided_edgar_name"] = None
        else:
            it["decided_oi"] = it["decided_moodys_name"] = None
    elif it["kind"] == "moodys":
        if payload["action"] == "confirm":
            it["decided_cik"] = it["proposed_cik"]
            it["decided_edgar_name"] = it.get("proposed_edgar_name", "")
            it["status"] = "confirmed"
        elif payload["action"] == "set":
            it["decided_cik"] = int(payload["cik"])
            it["decided_edgar_name"] = payload.get("name", "")
            it["status"] = "confirmed"
        elif payload["action"] == "no_sec_filer":
            it["decided_cik"] = None
            it["decided_edgar_name"] = None
            it["status"] = "no_sec_filer"
        entry["cik"] = it["decided_cik"]
        entry["edgar_name"] = it["decided_edgar_name"]
    else:  # kind == edgar (reverse item): question is "does Moody's rate this?"
        if payload["action"] == "set":
            it["decided_oi"] = payload["oi"]
            it["decided_moodys_name"] = payload.get("name", "")
            it["status"] = "confirmed"
        elif payload["action"] == "not_rated":
            it["decided_oi"] = None
            it["decided_moodys_name"] = None
            it["status"] = "not_rated"
        entry["oi"] = it.get("decided_oi")
        entry["moodys_name"] = it.get("decided_moodys_name")
    if payload["action"] != "pending":
        it["decided_by"] = entry["by"]
        it["decided_at"] = entry["ts"]
    if payload.get("note"):
        it["note"] = payload["note"]
    with open(LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    save_items()
    return it


def search(side, q):
    q = q.strip().upper()
    if len(q) < 2:
        return []
    toks = q.split()
    out = []
    if side == "edgar":
        for name, cik in EDGAR:
            u = name.upper()
            if all(t in u for t in toks):
                out.append({"name": name, "cik": cik})
                if len(out) >= 60:
                    break
    else:
        for e in MOODYS:
            u = e["name"].upper()
            if all(t in u for t in toks):
                out.append({"name": e["name"], "oi": e["oi"]})
                if len(out) >= 60:
                    break
    return out


PAGE = open(os.path.join(EVAL, "review_ui.html"), "rb").read()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(PAGE)))
            self.end_headers()
            self.wfile.write(PAGE)
        elif u.path == "/api/state":
            self._json(ITEMS)
        elif u.path == "/api/search":
            qs = urllib.parse.parse_qs(u.query)
            self._json(search(qs.get("side", ["edgar"])[0], qs.get("q", [""])[0]))
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/decide":
            return self._json({"error": "not found"}, 404)
        n = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(n))
            self._json(decide(payload))
        except Exception as exc:
            self._json({"error": str(exc)}, 400)


if __name__ == "__main__":
    print(f"http://localhost:{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
