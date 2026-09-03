"""
Experiment 02 runner: probes + paired A/B with filing and history pack, via the Batch API.

Design: README.md and decisions.md (D1-D5). Ten gold observations (selection.json), one
batch of 30 requests: a contamination probe, variant A and variant B per observation.
Batch API = 50% price. Every request's full params (prompts verbatim, documents referenced
by file, pack text) are written to runs/<batch>/requests.json before submission - that file
IS the documentation of what the model saw.

    python3 experiments/02-relative-with-history/run_batch.py --dry      # build + count_tokens + cost, no spend
    python3 experiments/02-relative-with-history/run_batch.py --submit   # submit the batch, save its id
    python3 experiments/02-relative-with-history/run_batch.py --collect  # fetch results, score, write results.json
"""
import json
import os
import sys
import time

import anthropic
import httpx2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
import analyst, history_pack, redact, run_eval, scorecard   # noqa: E402,E401

MODEL = "claude-opus-4-5-20251101"      # decisions D3; training cutoff Aug 2025, 200K context
CONTEXT_GUARD = 170_000
RUNS = os.path.join(HERE, "runs")
SEL = json.load(open(os.path.join(HERE, "selection.json")))["items"]
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3", "Ba1", "Ba2",
         "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]

SYSTEM = ("You are a credit analyst working with Moody's Retail and Apparel rating methodology "
          "(September 2025). Use only the material provided in this conversation; ignore any "
          "recollection of this company's actual ratings. The task is relative: judge whether "
          "what is new justifies keeping or changing the rating in effect at quarter start.")

A_TASK = ("TASK A (grade-then-score). From the filing(s) above, report the ten scorecard "
          "figures for the most recent FULL fiscal year they contain (USD millions; the pack's "
          "XBRL figures are for cross-checking, the filing is the source). Then grade the four "
          "qualitative factors RELATIVE to the implied anchors in the history pack: for each, "
          "say in qualitative_rationale whether it is better, the same, or worse than the "
          "anchor and why. Give direct_rating as your overall judgement.")

B_SCHEMA = {"type": "object", "properties": {
    "rating": {"type": "string", "enum": SCALE},
    "vs_quarter_start": {"type": "string", "enum": ["upgrade", "unchanged", "downgrade"]},
    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    "key_drivers": {"type": "string"}},
    "required": ["rating", "vs_quarter_start", "confidence", "key_drivers"],
    "additionalProperties": False}
B_TASK = ("TASK B (direct). State the issuer's Moody's-style long-term rating as of the "
          "observation date, using the filing(s) and the history pack. Say explicitly whether "
          "this is an upgrade, unchanged, or a downgrade versus the rating in effect at quarter "
          "start, and name the drivers.")

PROBE_SYSTEM = ("You are being probed for what you know FROM MEMORY. Answer strictly from your "
                "training knowledge; if you do not specifically recall a value, return null. "
                "Honest 'I don't know' answers are the desired behavior.")
PROBE_SCHEMA = {"type": "object", "properties": {
    "claimed_rating_at_date": {"type": ["string", "null"]},
    "rating_confidence": {"type": "string", "enum": ["high", "medium", "low", "none"]},
    "claimed_rating_action_in_that_quarter": {"type": "string",
        "description": "any Moody's action on this issuer in the observation quarter you recall, else 'none known'"},
    "claimed_fy_revenue_usd_bn": {"type": ["number", "null"]},
    "notes": {"type": "string"}},
    "required": ["claimed_rating_at_date", "rating_confidence",
                 "claimed_rating_action_in_that_quarter", "claimed_fy_revenue_usd_bn", "notes"],
    "additionalProperties": False}


def build_requests(client=None):
    reqs, manifest = [], []
    for it in SEL:
        slug, t = it["slug"], it["date"]
        c = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug, "company.json")))
        manifest_f = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug,
                                                 "filings", "manifest.json")))["filings"]
        obs = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug, "observations.json")))
        o = next(x for x in obs["observations"] if x["date"] == t)
        pack, pack_log = history_pack.build(slug, t)
        config = "annual+q"
        for attempt in ("annual",):
            config = attempt
            chosen = run_eval.pick_documents(o, manifest_f, config)
            docs, doc_meta, n_red = "", [], 0
            for f in chosen:
                path, fn = run_eval.ensure_doc(slug, obs["cik"], f)
                clean, removed = redact.redact(run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore")))
                docs += f"<document name=\"{f['form']} filed {f['filingDate']}\">\n{clean}\n</document>\n"
                doc_meta.append({"form": f["form"], "filed": f["filingDate"], "file": fn, "redacted_lines": len(removed)})
                n_red += len(removed)
            if client is None or client.messages.count_tokens(
                    model=MODEL, system=SYSTEM,
                    messages=[{"role": "user", "content": docs + pack + A_TASK}]).input_tokens <= CONTEXT_GUARD:
                break
        # No cache_control in batch mode: requests run in parallel, so A and B both paid the
        # 1.25x cache-write premium with zero reads (measured: 1.57M cache-creation tokens,
        # 0 read) - which is what pushed the first run 21 cents over the cap.
        doc_block = {"type": "text", "text": docs}
        shared = [doc_block, {"type": "text", "text": pack}]
        probe_q = (f"As of {t}: what was the Moody's long-term credit rating of {c['edgar_name']} "
                   f"({it['group']})? Did Moody's take any rating action on it in the quarter ending "
                   f"{t}? What was its most recent full fiscal-year revenue known at that date?")
        reqs += [
            {"custom_id": f"probe-{it['id']}", "params": {
                "model": MODEL, "max_tokens": 1000, "system": PROBE_SYSTEM,
                "messages": [{"role": "user", "content": probe_q}],
                "output_config": {"format": {"type": "json_schema", "schema": PROBE_SCHEMA}}}},
            {"custom_id": f"a-{it['id']}", "params": {
                "model": MODEL, "max_tokens": 6000, "system": SYSTEM,
                "messages": [{"role": "user", "content": shared + [{"type": "text", "text": A_TASK}]}],
                "output_config": {"format": {"type": "json_schema", "schema": analyst.SCHEMA}}}},
            {"custom_id": f"b-{it['id']}", "params": {
                "model": MODEL, "max_tokens": 3000, "system": SYSTEM,
                "messages": [{"role": "user", "content": shared + [{"type": "text", "text": B_TASK}]}],
                "output_config": {"format": {"type": "json_schema", "schema": B_SCHEMA}}}},
        ]
        manifest.append({**it, "docs_config": config, "documents": doc_meta, "redacted_lines": n_red,
                         "pack_log": pack_log, "pack_text": pack, "probe_question": probe_q})
    return reqs, manifest


def dry(client):
    reqs, manifest = build_requests(client)
    total = 0
    for r in reqs:
        n = client.messages.count_tokens(model=MODEL, system=r["params"]["system"],
                                         messages=r["params"]["messages"]).input_tokens
        total += n
        print(f"  {r['custom_id']:<12} {n:>8,} Tokens")
    worst = (total * 5 / 1e6 + len(reqs) * 3000 * 25 / 1e6) * 0.5   # batch price, no caching
    print(f"\n{len(reqs)} Requests, {total:,} Input-Tokens gesamt. Worst-case Batch-Kosten ~${worst:.2f}")
    return reqs, manifest


def submit(client):
    reqs, manifest = build_requests(client)
    batch = client.messages.batches.create(requests=reqs)
    d = os.path.join(RUNS, batch.id)
    os.makedirs(d, exist_ok=True)
    json.dump({"batch_id": batch.id, "model": MODEL, "system_prompt": SYSTEM, "a_task": A_TASK,
               "b_task": B_TASK, "probe_system": PROBE_SYSTEM, "observations": manifest},
              open(os.path.join(d, "requests.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(reqs, open(os.path.join(d, "requests_raw.json"), "w"))
    open(os.path.join(HERE, "LAST_BATCH"), "w").write(batch.id)
    print(f"submitted {batch.id}: {batch.processing_status}")


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def collect(client):
    bid = open(os.path.join(HERE, "LAST_BATCH")).read().strip()
    st = client.messages.batches.retrieve(bid)
    if st.processing_status != "ended":
        print(f"{bid}: {st.processing_status} {st.request_counts}"); return
    d = os.path.join(RUNS, bid)
    outs, usage = {}, {"in": 0, "out": 0, "cw": 0, "cr": 0}
    for item in client.messages.batches.results(bid):
        if item.result.type != "succeeded":
            outs[item.custom_id] = {"error": item.result.type}; continue
        m = item.result.message
        text = next(b.text for b in m.content if b.type == "text")
        try:
            outs[item.custom_id] = json.loads(text[text.index("{"):text.rindex("}") + 1])
        except Exception:
            outs[item.custom_id] = {"parse_error": text[:400]}
        u = m.usage.model_dump()
        usage["in"] += u["input_tokens"]; usage["out"] += u["output_tokens"]
        usage["cw"] += u.get("cache_creation_input_tokens") or 0
        usage["cr"] += u.get("cache_read_input_tokens") or 0
    json.dump(outs, open(os.path.join(d, "raw_outputs.json"), "w"), indent=1, ensure_ascii=False)

    results = []
    for it in SEL:
        a, b, p = outs.get(f"a-{it['id']}", {}), outs.get(f"b-{it['id']}", {}), outs.get(f"probe-{it['id']}", {})
        pred_a = agg = None
        if "figures_usd_m" in a:
            fig = dict(a["figures_usd_m"]); fig["qualitative"] = a["qualitative"]; fig["label"] = it["id"]
            try:
                agg = round(scorecard.aggregate(scorecard.build(fig)), 3); pred_a = scorecard.outcome(agg)
            except Exception as exc:
                pred_a = f"scorecard error: {exc}"
        lab = notch(it["label"]); per = notch(it["persistence"])
        e = lambda pred: abs(notch(pred) - lab) if notch(pred) is not None and lab is not None else None
        claimed = p.get("claimed_rating_at_date")
        results.append({**it, "probe": p, "probe_flag": (
            "recalls_label" if claimed and notch(claimed) == lab and lab != per else
            "recalls_prior" if claimed and notch(claimed) == per else
            "wrong_or_none"),
            "A": {"pred": pred_a, "aggregate": agg, "direct": a.get("direct_rating"),
                  "qualitative": a.get("qualitative"), "figures": a.get("figures_usd_m"),
                  "figure_notes": a.get("figure_notes"), "rationale": a.get("qualitative_rationale")},
            "B": {"pred": b.get("rating"), "vs": b.get("vs_quarter_start"),
                  "confidence": b.get("confidence"), "drivers": b.get("key_drivers")},
            "err": {"A": e(pred_a), "A_direct": e(a.get("direct_rating")), "B": e(b.get("rating")),
                    "persistence": abs(per - lab) if per is not None and lab is not None else None}})
    cost = (usage["in"] * 5 + usage["out"] * 25 + usage["cw"] * 6.25 + usage["cr"] * 0.5) / 1e6 * 0.5
    json.dump({"batch_id": bid, "usage": usage, "cost_usd_batch": round(cost, 3), "results": results},
              open(os.path.join(d, "results.json"), "w"), indent=1, ensure_ascii=False)
    for r in results:
        print(f"  {r['id']} {r['slug']:<18} {r['date']} {r['persistence']:>4}->{r['label']:<4} "
              f"A={r['A']['pred']!s:<5} Ad={r['A']['direct']!s:<5} B={r['B']['pred']!s:<5}({r['B']['vs']}) "
              f"probe={r['probe_flag']}")
    for ch in ("A", "A_direct", "B", "persistence"):
        errs = [r["err"][ch] for r in results if r["err"][ch] is not None]
        print(f"  {ch:<12} exakt {sum(x == 0 for x in errs)}/{len(errs)}  MAE {sum(errs)/len(errs):.2f}")
    print(f"  Kosten (Batch): ${cost:.2f}   usage {usage}")


def make_client():
    # This machine has a dead IPv6 route while api.anthropic.com publishes an AAAA record,
    # and binding the local address did not stop the resolver from handing out v6 targets.
    # Filter IPv6 out at DNS level for this process, and retry generously on top.
    import socket
    _gai = socket.getaddrinfo
    def v4_only(*args, **kwargs):
        res = _gai(*args, **kwargs)
        v4 = [r for r in res if r[0] == socket.AF_INET]
        return v4 or res
    socket.getaddrinfo = v4_only
    return anthropic.Anthropic(max_retries=10, timeout=120.0,
                               http_client=anthropic.DefaultHttpxClient(
                                   transport=httpx2.HTTPTransport(retries=5)))


if __name__ == "__main__":
    client = make_client()
    {"--dry": dry, "--submit": submit, "--collect": collect}[sys.argv[1]](client)
