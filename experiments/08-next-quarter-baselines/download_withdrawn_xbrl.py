"""
Experiment 08: download SEC companyfacts for the in-scope withdrawn-rating companies.

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter (decision 3 in decisions.md).
Reads the company.json files that experiments/07-rating-change-base-rates/build_withdrawn.py wrote
for run R2 and downloads https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json for every
distinct member CIK of an in-scope group. Uses the project's SEC User-Agent from fetch_xbrl.py and
waits 0.25 s between requests (SEC asks for at most 10 per second).

Writes into data/edgar/companyfacts-withdrawn/ (gitignored under data/):
    CIK##########.json   the raw response, verbatim; an {"error": ...} stub on HTTP errors
    _manifest.json       per CIK: group slug, fetch date, status, bytes
Existing files are kept, never re-downloaded.

    python3 experiments/08-next-quarter-baselines/download_withdrawn_xbrl.py
"""
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
from fetch_xbrl import UA  # noqa: E402

WITHDRAWN = os.path.join(ROOT, "experiments", "07-rating-change-base-rates", "runs", "R2-inputs-withdrawn")
OUT = os.path.join(ROOT, "data", "edgar", "companyfacts-withdrawn")


def targets():
    out = []
    for slug in sorted(os.listdir(WITHDRAWN)):
        cj = os.path.join(WITHDRAWN, slug, "company.json")
        if not os.path.exists(cj):
            continue
        c = json.load(open(cj))
        if c["scope"] != "in":
            continue
        for cik in sorted({m["decided_cik"] for m in c["members"] if m.get("decided_cik")}):
            out.append((slug, int(cik)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(OUT, "_manifest.json")
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    today = datetime.date.today().isoformat()
    for slug, cik in targets():
        name = f"CIK{cik:010d}.json"
        path = os.path.join(OUT, name)
        if os.path.exists(path):
            continue
        url = f"https://data.sec.gov/api/xbrl/companyfacts/{name}"
        try:
            body = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            json.loads(body)
            open(path, "wb").write(body)
            status = "ok"
        except urllib.error.HTTPError as exc:
            body = json.dumps({"error": f"HTTP Error {exc.code}"}).encode()
            open(path, "wb").write(body)
            status = f"HTTP {exc.code}"
        manifest[name] = {"group": slug, "cik": cik, "fetched": today, "status": status, "bytes": len(body)}
        json.dump(manifest, open(mpath, "w"), indent=1)
        print(f"  {slug:<45} {name}  {status}  {len(body) / 1e6:.1f} MB", flush=True)
        time.sleep(0.25)
    ok = sum(1 for v in manifest.values() if v["status"] == "ok")
    print(f"{ok} of {len(manifest)} CIKs with companyfacts; "
          f"{sum(v['bytes'] for v in manifest.values()) / 1e6:.0f} MB in {OUT}")


if __name__ == "__main__":
    main()
