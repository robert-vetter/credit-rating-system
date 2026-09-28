"""
Experiment 09: select the window rows, fetch their filings, and build every request body offline.

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. Implements sections 3, 6 and 7
of README.md (version 0.2).

    python3 experiments/09-gpt51-next-quarter/inputs.py fetch            # downloads (decision 2)
    python3 experiments/09-gpt51-next-quarter/inputs.py prepare R1       # offline; refuses to overwrite
    python3 experiments/09-gpt51-next-quarter/inputs.py prepare R2 --openai   # direct OpenAI flex (decision 10)

fetch: for every one of the 147 window rows of Experiment 08, reads the company's SEC filing
manifest (fetched from EDGAR for withdrawn-rating companies that have none), picks the latest 10-K
filed on or before t and every 10-Q filed after it and on or before t, and downloads missing primary
documents from EDGAR with the project's SEC User-Agent (evaluation/pipeline/run_eval.py).

prepare: builds, for every row, the forecast request (documents arm for eligible rows, rating-
history-only arm for the others) and one memory probe per company; text from run_eval.to_text,
redaction by system/redact.redact_v2 with the fragment scan that must return nothing; tokens counted
with tiktoken o200k_base; reservations priced at the approved ceilings; everything hashed into
runs/<run_id>/manifest.json with the bodies under runs/<run_id>/bodies/.
"""
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.request
from decimal import Decimal, ROUND_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
sys.path.insert(0, os.path.join(ROOT, "system"))
import history_pack as hp  # noqa: E402
import redact  # noqa: E402
import run_eval  # noqa: E402

E08_RUN = os.path.join(ROOT, "experiments", "08-next-quarter-baselines", "runs", "R1-2026-09-27")
E07_WITHDRAWN = os.path.join(ROOT, "experiments", "07-rating-change-base-rates", "runs", "R2-inputs-withdrawn")
COMPANIES = os.path.join(ROOT, "evaluation", "companies")
EXTRA = os.path.join(HERE, "runs", "inputs")            # manifests and filings of withdrawn-rating companies

TARGET = "openai" if "--openai" in sys.argv else "openrouter"
MODEL = "openai/gpt-5.1"
OPENAI_MODEL = "gpt-5.1-2025-11-13"
EXPECTED_SNAPSHOT = "gpt-5.1-20251113"
PROVIDER_SLUG = "openai/flex"
PRICE_IN, PRICE_OUT = Decimal("0.625"), Decimal("5")     # USD per million tokens, approved ceilings
CUTOFF, BOUNDARY = "2024-09-30", "2024-10-31"
REASONING = "medium"
MAX_TOKENS_FORECAST, MAX_TOKENS_PROBE = 32000, 6000
CONTEXT, INPUT_LIMIT, TOKEN_MARGIN = 400000, 272000, 1.03   # OpenAI: 272,000 input + 128,000 output
ELIGIBLE_DAYS = 450
PERIOD = {"2024-12-31": ("2025-01-01", "2025-03-31"), "2025-03-31": ("2025-04-01", "2025-06-30")}

SYSTEM = open(os.path.join(HERE, "prompts", "system.txt")).read().strip()
TASK = open(os.path.join(HERE, "prompts", "task.txt")).read()
PROBE = open(os.path.join(HERE, "prompts", "probe.txt")).read()
SCHEMA = json.load(open(os.path.join(HERE, "prompts", "schema_forecast.json")))
PROBE_SCHEMA = json.load(open(os.path.join(HERE, "prompts", "schema_probe.json")))
PROBE_SYSTEM = "You answer questions from your own knowledge. Say plainly when you do not know."

RATING_TYPE = {"LT Corporate Family Ratings": "long-term corporate family rating",
               "LT Issuer Rating": "long-term issuer rating", "Issuer Rating": "issuer rating",
               "Senior Unsecured": "senior unsecured rating"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(body):
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ----------------------------------------------------------------------------- rows and companies

def window_rows():
    rows = json.load(open(os.path.join(E08_RUN, "predictions.json")))["experiment_09_window"]
    return sorted(rows, key=lambda r: (r["company"], r["t"]))


def company(slug):
    active = os.path.join(COMPANIES, slug, "company.json")
    if os.path.exists(active):
        c = json.load(open(active))
        return {"slug": slug, "origin": "active", "name": c.get("edgar_name") or c["group"],
                "ciks": [int(c["cik"])], "ratings": json.load(open(os.path.join(COMPANIES, slug, "ratings.json"))),
                "filings_dir": os.path.join(COMPANIES, slug, "filings")}
    c = json.load(open(os.path.join(E07_WITHDRAWN, slug, "company.json")))
    return {"slug": slug, "origin": "withdrawn", "name": c["group"],
            "ciks": sorted({int(m["decided_cik"]) for m in c["members"] if m.get("decided_cik")}),
            "ratings": json.load(open(os.path.join(E07_WITHDRAWN, slug, "ratings.json"))),
            "filings_dir": os.path.join(EXTRA, "filings", slug)}


def filing_manifest(c, fetch=False):
    """(cik, filings) for the company; withdrawn-rating companies get an EDGAR manifest on fetch."""
    if c["origin"] == "active":
        m = json.load(open(os.path.join(c["filings_dir"], "manifest.json")))
        return c["ciks"][0], m["filings"]
    best = (None, [])
    for cik in c["ciks"]:
        path = os.path.join(EXTRA, "manifests", f"CIK{cik:010d}.json")
        if not os.path.exists(path):
            if not fetch:
                continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                import fetch_filings
                name, fl = fetch_filings.manifest(cik)
                json.dump({"cik": cik, "edgar_name": name, "fetched": dt.date.today().isoformat(), "filings": fl},
                          open(path, "w"), indent=0)
            except Exception as exc:                                   # noqa: BLE001
                json.dump({"cik": cik, "error": f"{type(exc).__name__}: {exc}", "filings": []}, open(path, "w"))
        fl = json.load(open(path)).get("filings", [])
        if len(fl) > len(best[1]):
            best = (cik, fl)
    return best


def choose_documents(filings, t):
    """Latest 10-K filed on or before t, then every 10-Q filed after it and on or before t.
    Returns (documents, eligible, reason)."""
    ks = sorted([f for f in filings if f["form"] == "10-K" and f["filingDate"] <= t], key=lambda f: f["filingDate"])
    if not ks:
        return [], False, "no 10-K on or before t"
    k = ks[-1]
    age = (dt.date.fromisoformat(t) - dt.date.fromisoformat(k["filingDate"])).days
    if age > ELIGIBLE_DAYS:
        return [], False, f"latest 10-K filed {k['filingDate']}, {age} days before t"
    qs = sorted([f for f in filings if f["form"] == "10-Q" and k["filingDate"] < f["filingDate"] <= t],
                key=lambda f: f["filingDate"])
    return [k] + qs, True, None


def doc_path(c, f):
    acc = f["accessionNumber"].replace("-", "")
    return os.path.join(c["filings_dir"], f"{f['filingDate']}_{f['form'].replace('/', '')}_{acc}.htm")


def fetch():
    done = got = 0
    for r in window_rows():
        c = company(r["company"])
        cik, filings = filing_manifest(c, fetch=True)
        docs, ok, why = choose_documents(filings, r["t"])
        for f in docs:
            path = doc_path(c, f)
            if os.path.exists(path):
                done += 1
                continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{f['accessionNumber'].replace('-', '')}/{f['primaryDocument']}"
            time.sleep(0.25)
            body = urllib.request.urlopen(urllib.request.Request(url, headers=run_eval.UA), timeout=120).read()
            open(path, "wb").write(body)
            got += 1
            print(f"  {c['slug']:<32} {f['form']} {f['filingDate']}  {len(body) / 1e6:.1f} MB", flush=True)
    print(f"documents already cached: {done}; downloaded: {got}")


# ----------------------------------------------------------------------------- bodies

def provider():
    return {"order": [PROVIDER_SLUG], "allow_fallbacks": False, "require_parameters": True,
            "max_price": {"prompt": float(PRICE_IN), "completion": float(PRICE_OUT)}}


def forecast_body(user_text):
    if TARGET == "openai":
        return {"model": OPENAI_MODEL,
                "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_text}],
                "reasoning_effort": REASONING, "max_completion_tokens": MAX_TOKENS_FORECAST,
                "response_format": {"type": "json_schema", "json_schema": {"name": "rating_forecast", "strict": True,
                                                                           "schema": SCHEMA}},
                "service_tier": "flex", "store": False}
    return {"model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_text}],
            "reasoning": {"effort": REASONING}, "max_tokens": MAX_TOKENS_FORECAST,
            "response_format": {"type": "json_schema", "json_schema": {"name": "rating_forecast", "strict": True,
                                                                       "schema": SCHEMA}},
            "provider": provider(), "usage": {"include": True}, "transforms": [], "stream": False}


def probe_body(question):
    if TARGET == "openai":
        return {"model": OPENAI_MODEL,
                "messages": [{"role": "system", "content": PROBE_SYSTEM}, {"role": "user", "content": question}],
                "reasoning_effort": REASONING, "max_completion_tokens": MAX_TOKENS_PROBE,
                "response_format": {"type": "json_schema", "json_schema": {"name": "memory_probe", "strict": True,
                                                                           "schema": PROBE_SCHEMA}},
                "service_tier": "flex", "store": False}
    return {"model": MODEL,
            "messages": [{"role": "system", "content": PROBE_SYSTEM}, {"role": "user", "content": question}],
            "reasoning": {"effort": REASONING}, "max_tokens": MAX_TOKENS_PROBE,
            "response_format": {"type": "json_schema", "json_schema": {"name": "memory_probe", "strict": True,
                                                                       "schema": PROBE_SCHEMA}},
            "provider": provider(), "usage": {"include": True}, "transforms": [], "stream": False}


def reservation(input_tokens, max_tokens):
    usd = (Decimal(input_tokens) * PRICE_IN + Decimal(max_tokens) * PRICE_OUT) / Decimal(10 ** 6)
    return str(usd.quantize(Decimal("0.000001"), rounding=ROUND_UP))


def rating_state(c, t, expected):
    st = hp.rating_state_at(c["ratings"], t)["selected"]
    if not st or st["rating"].replace("(P)", "").strip() != expected:
        raise AssertionError(f"{c['slug']} {t}: rating state {st} does not match the label {expected}")
    return st


def assemble(c, docs):
    text, meta, removed = "", [], {}
    for f in docs:
        path = doc_path(c, f)
        raw = open(path, "rb").read()
        clean, cut = redact.redact_v2(run_eval.to_text(raw.decode("utf-8", "ignore")))
        # Final pass (added 2026-09-27 before any request, after Best Buy's 2024 10-K kept two
        # orphaned "Stable" outlook cells): remove exactly the lines the fragment scan flags, log
        # them, rescan. The scan must end empty or the build stops.
        fragment_pass = []
        for _ in range(5):
            frags = redact.rating_fragments(clean)
            if not frags:
                break
            drop = {f["line"] for f in frags}
            lines = clean.split("\n")
            fragment_pass += [lines[i] for i in sorted(drop)]
            clean = "\n".join(line for i, line in enumerate(lines) if i not in drop)
        frags = redact.rating_fragments(clean)
        if frags:
            raise AssertionError(f"{c['slug']} {os.path.basename(path)}: rating fragments survived: {frags[:3]}")
        cut = cut + [f"[fragment pass] {x}" for x in fragment_pass]
        name = f"{f['form']} filed {f['filingDate']}"
        text += f'<document name="{name}">\n{clean}\n</document>\n'
        meta.append({"name": name, "form": f["form"], "filed": f["filingDate"], "report_date": f.get("reportDate"),
                     "accession": f["accessionNumber"], "file": os.path.relpath(path, ROOT),
                     "source_sha256": sha(raw), "text_sha256": sha(clean.encode()), "chars": len(clean),
                     "redacted_lines": len(cut), "fragment_pass_lines": len(fragment_pass)})
        removed[name] = cut
    return text, meta, removed


def prepare(run_id):
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    out = os.path.join(HERE, "runs", run_id)
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")
    os.makedirs(os.path.join(out, "bodies"))
    os.makedirs(os.path.join(out, "audit"))
    requests, probes_done = [], set()
    schema_tokens = len(enc.encode(json.dumps(SCHEMA)))
    for r in window_rows():
        c = company(r["company"])
        t = r["t"]
        assert BOUNDARY < t, f"prediction date {t} not after the boundary"
        cik, filings = filing_manifest(c)
        docs, eligible, why = choose_documents(filings, t)
        st = rating_state(c, t, r["rating_t"])
        events = hp.typed_events(c["ratings"], t)
        assert all(e[0] <= t for e in events)
        history = "\n".join(hp.typed_history_lines(events, t, per_level=12))
        if eligible:
            for f in docs:
                assert f["filingDate"] <= t and f["form"] in ("10-K", "10-Q")
            documents, meta, removed = assemble(c, docs)
            header = "Filings (the latest 10-K and the 10-Qs filed after it, on or before the as-of date; text converted from HTML):"
        else:
            documents, meta, removed = "", [], {}
            header = "Filings: none are supplied for this company."
        p0, p1 = PERIOD[t]
        rt = RATING_TYPE.get(st["rating_type"], st["rating_type"])
        user = TASK.format(as_of=t, company=c["name"], rating_type=rt, rating=r["rating_t"],
                           period_start=p0, period_end=p1, history=history,
                           documents_header=header, documents=documents)
        tokens = len(enc.encode(SYSTEM)) + len(enc.encode(user)) + schema_tokens
        bound = int(tokens * TOKEN_MARGIN) + 200
        dropped = []
        while eligible and bound > INPUT_LIMIT and len(docs) > 1:
            dropped.append(docs.pop(1)["filingDate"])             # the oldest 10-Q goes first
            documents, meta, removed = assemble(c, docs)
            user = TASK.format(as_of=t, company=c["name"], rating_type=rt, rating=r["rating_t"],
                               period_start=p0, period_end=p1, history=history,
                               documents_header=header, documents=documents)
            tokens = len(enc.encode(SYSTEM)) + len(enc.encode(user)) + schema_tokens
            bound = int(tokens * TOKEN_MARGIN) + 200
        assert bound <= INPUT_LIMIT and bound + MAX_TOKENS_FORECAST <= CONTEXT, f"{c['slug']} {t}: {bound} tokens do not fit"
        rid = f"F-{c['slug']}-{t}"
        body = forecast_body(user)
        raw = canonical(body)
        open(os.path.join(out, "bodies", f"{rid}.json"), "wb").write(raw)
        json.dump({"documents": meta, "removed_lines": removed, "rating_state": st, "dropped_10q": dropped,
                   "eligibility": why or "eligible"}, open(os.path.join(out, "audit", f"{rid}.json"), "w"), indent=1)
        requests.append({"request_id": rid, "kind": "forecast", "arm": "documents" if eligible else "history_only",
                         "company": c["slug"], "t": t, "rating_t": r["rating_t"], "target": r["target"],
                         "gold": r["gold"], "input_tokens": tokens, "input_bound": bound,
                         "max_tokens": MAX_TOKENS_FORECAST, "reservation_usd": reservation(bound, MAX_TOKENS_FORECAST),
                         "body_sha256": sha(raw), "documents": len(meta), "dropped_10q": dropped,
                         "probe_id": f"P-{c['slug']}"})
        if c["slug"] not in probes_done:
            probes_done.add(c["slug"])
            q = PROBE.format(company=c["name"], rating_type=rt)
            pbody = probe_body(q)
            praw = canonical(pbody)
            open(os.path.join(out, "bodies", f"P-{c['slug']}.json"), "wb").write(praw)
            ptok = len(enc.encode(PROBE_SYSTEM)) + len(enc.encode(q)) + len(enc.encode(json.dumps(PROBE_SCHEMA)))
            pbound = int(ptok * TOKEN_MARGIN) + 200
            requests.append({"request_id": f"P-{c['slug']}", "kind": "probe", "company": c["slug"],
                             "input_tokens": ptok, "input_bound": pbound, "max_tokens": MAX_TOKENS_PROBE,
                             "reservation_usd": reservation(pbound, MAX_TOKENS_PROBE), "body_sha256": sha(praw)})
    worst = sum(Decimal(x["reservation_usd"]) for x in requests)
    expected_in = sum(x["input_tokens"] for x in requests)
    manifest = {"created": dt.datetime.now(dt.timezone.utc).isoformat(), "api": TARGET,
                "model": OPENAI_MODEL if TARGET == "openai" else MODEL,
                "expected_snapshot": OPENAI_MODEL if TARGET == "openai" else EXPECTED_SNAPSHOT,
                "provider_slug": "openai service_tier flex" if TARGET == "openai" else PROVIDER_SLUG,
                "price_ceiling_per_million": {"input": str(PRICE_IN), "output": str(PRICE_OUT)},
                "cutoff": CUTOFF, "boundary": BOUNDARY, "reasoning_effort": REASONING,
                "tokenizer": "tiktoken " + tiktoken.__version__ + " o200k_base", "token_margin": TOKEN_MARGIN,
                "prompts_sha256": {n: sha(open(os.path.join(HERE, "prompts", n), "rb").read())
                                   for n in sorted(os.listdir(os.path.join(HERE, "prompts")))},
                "requests": requests,
                "totals": {"forecast_documents": sum(1 for x in requests if x.get("arm") == "documents"),
                           "forecast_history_only": sum(1 for x in requests if x.get("arm") == "history_only"),
                           "probes": sum(1 for x in requests if x["kind"] == "probe"),
                           "input_tokens": expected_in,
                           "worst_case_usd": str(worst),
                           "input_only_usd": str((Decimal(expected_in) * PRICE_IN / Decimal(10 ** 6)).quantize(Decimal("0.01")))}}
    raw = json.dumps(manifest, indent=1, sort_keys=True).encode()
    open(os.path.join(out, "manifest.json"), "wb").write(raw)
    open(os.path.join(out, "manifest.sha256"), "w").write(sha(raw) + "\n")
    print(json.dumps(manifest["totals"], indent=1))
    return manifest


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "fetch":
        fetch()
    elif len(sys.argv) in (3, 4) and sys.argv[1] == "prepare":
        prepare(sys.argv[2])
    else:
        sys.exit(__doc__)
