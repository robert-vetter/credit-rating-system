"""
SIC sweep over the full listed universe, for the reverse completeness check of the
Moody's-to-EDGAR mapping (see evaluation/README.md).

Written by Claude (Opus 5), directed by Robert Vetter.

The forward direction (Moody's name -> EDGAR name) can silently miss companies whose names
differ too much between the two sources. The reverse check needs the SIC industry code of
every listed SEC company, so that "listed retailer with no confirmed Moody's mapping" becomes
a computable list instead of a hope. This script fills data/edgar/sic_cache.json for all CIKs in
company_tickers.json, throttled well under the SEC's 10 requests/second fair-use limit,
and writes data/edgar/sic_sweep_listed.done when finished.

Run: python3 evaluation/pipeline/sic_sweep_listed.py
"""
import json, os, queue, re, threading, time, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
UA = {"User-Agent": "Robert Vetter robert@certus-ai.com"}
CACHE = os.path.join(DATA, "edgar", "sic_cache.json")
DONE = os.path.join(DATA, "edgar", "sic_sweep_listed.done")
SIC_RE = re.compile(r'"sic":"(\d*)","sicDescription":"([^"]*)"')

def save(cache):
    tmp = CACHE + ".tmp"
    json.dump(cache, open(tmp, "w"))
    os.replace(tmp, CACHE)

def main():
    tickers = json.load(open(os.path.join(DATA, "edgar", "company_tickers.json")))
    ciks = sorted({int(v["cik_str"]) for v in tickers.values()})
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [c for c in ciks if str(c) not in cache]
    print(f"{len(ciks)} listed CIKs, {len(todo)} to fetch", flush=True)
    q = queue.Queue()
    for c in todo:
        q.put(c)
    lock = threading.Lock()
    done_n = [0]

    def worker():
        while True:
            try:
                cik = q.get_nowait()
            except queue.Empty:
                return
            time.sleep(0.35)  # 3 workers x ~1/0.35s = well under 10 req/s
            try:
                req = urllib.request.Request(
                    f"https://data.sec.gov/submissions/CIK{cik:010d}.json",
                    headers={**UA, "Range": "bytes=0-900"})
                d = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
                m = SIC_RE.search(d)
                val = [m.group(1), m.group(2)] if m else ["", ""]
            except Exception as exc:
                val = ["ERR", str(exc)[:40]]
            with lock:
                cache[str(cik)] = val
                done_n[0] += 1
                if done_n[0] % 400 == 0:
                    save(cache)
                    print(f"  {done_n[0]}/{len(todo)}", flush=True)

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join()
    # one retry round for transient errors
    errs = [int(k) for k in cache if cache[k][0] == "ERR"]
    for cik in errs:
        time.sleep(0.35)
        try:
            req = urllib.request.Request(
                f"https://data.sec.gov/submissions/CIK{cik:010d}.json",
                headers={**UA, "Range": "bytes=0-900"})
            d = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
            m = SIC_RE.search(d)
            cache[str(cik)] = [m.group(1), m.group(2)] if m else ["", ""]
        except Exception:
            pass
    save(cache)
    remaining = sum(1 for k in cache if cache[k][0] == "ERR")
    open(DONE, "w").write(json.dumps({"listed": len(ciks), "fetched": len(todo), "errors_left": remaining}))
    print(f"done, {remaining} unresolved errors", flush=True)

if __name__ == "__main__":
    main()
