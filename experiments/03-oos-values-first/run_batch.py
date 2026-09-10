"""
Experiment 03 runner: probes + values-first extraction on the post-cutoff cross-section.

Design and decisions: README.md, decisions.md (D1-D9). Model claude-opus-4-6 (training data
cutoff Aug 2025, verified: https://platform.claude.com/docs/en/models/opus-4-6/overview).
Boundary B = 2025-09-30; every input document must satisfy filingDate > B, every pack and
peer fact filed <= as_of; the checks are asserted here and written to runs/<batch>/audit.json.
One batch: per candidate a memory probe (no documents) and one values-first request
(documents + history pack + peer table). No tools, no cache_control (Exp 02 lesson), adaptive
thinking with effort high, structured output. Hard cap from decisions D9.

    python3 experiments/03-oos-values-first/run_batch.py --dry      # build, count_tokens, cost; no spend
    python3 experiments/03-oos-values-first/run_batch.py --submit   # submit within the cap
    python3 experiments/03-oos-values-first/run_batch.py --collect  # fetch, score, results.json
"""
import json
import os
import sys

import anthropic
import httpx2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
import history_pack, redact, run_eval, scorecard   # noqa: E402,E401

MODEL = "claude-opus-4-6"
B = "2025-09-30"
AS_OF = "2026-08-29"
HISTORY_END = "2025-08-28"          # latest action date in the 17g-7 file (measured), content end
CAP_USD = 9.60                      # decision D9: $10 balance minus pre-flight and margin
CAP_RERUN = 1.60                    # remaining budget after the first batch ($2.47), with margin
# max_tokens is the ceiling for thinking AND answer together. At effort=high on Opus 4.6 the
# successful runs spent 6.6k-8.6k output tokens, so the original 9000 was borderline and 11 of
# 16 requests hit the ceiling inside the thinking block and returned no answer (2026-09-10).
VF_MAX_TOKENS, PROBE_MAX_TOKENS = 24000, 1200
PRICE_IN, PRICE_OUT = 5 / 1e6, 25 / 1e6
RUNS = os.path.join(HERE, "runs")
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3", "Ba1", "Ba2",
         "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]

SYSTEM = open(os.path.join(HERE, "prompts", "system.txt")).read().strip()
TASK = open(os.path.join(HERE, "prompts", "task_values_first.txt")).read().strip()
SCHEMA = json.load(open(os.path.join(HERE, "prompts", "schema_values_first.json")))
PROBE_SYSTEM, PROBE_USER = [p.split(":", 1)[1].strip() for p in
                            open(os.path.join(HERE, "prompts", "probe.txt")).read().strip().split("\n\n")]
PROBE_SCHEMA = {"type": "object", "properties": {
    "claimed_moodys_rating": {"type": ["string", "null"]},
    "rating_confidence": {"type": "string", "enum": ["high", "medium", "low", "none"]},
    "claimed_debt_ebitda": {"type": ["number", "null"]},
    "claimed_latest_fy_revenue_usd_bn": {"type": ["number", "null"]},
    "claimed_fy_end": {"type": ["string", "null"]},
    "claimed_recent_rating_actions": {"type": "string"},
    "notes": {"type": "string"}},
    "required": ["claimed_moodys_rating", "rating_confidence", "claimed_debt_ebitda",
                 "claimed_latest_fy_revenue_usd_bn", "claimed_fy_end",
                 "claimed_recent_rating_actions", "notes"], "additionalProperties": False}


def candidates():
    return json.load(open(os.path.join(HERE, "candidates.json")))


def pick_documents(manifest):
    """Latest 10-K with filingDate > B, then every 10-Q filed after it up to AS_OF (decision D2)."""
    post = [f for f in manifest if B < f["filingDate"] <= AS_OF]
    ks = sorted([f for f in post if f["form"] == "10-K"], key=lambda f: f["filingDate"])
    if not ks:
        return []
    k = ks[-1]
    qs = sorted([f for f in post if f["form"] == "10-Q" and f["filingDate"] > k["filingDate"]],
                key=lambda f: f["filingDate"])
    return [k] + qs


def build_requests(only=None, include_probes=True):
    cand = candidates()
    reqs, audit = [], []
    for it in cand["items"]:
        if not it.get("in_run", True) or it.get("status") != "confirmed":
            continue
        if only and it["id"] not in only:
            continue
        slug = it["slug"]
        cdir = os.path.join(ROOT, "evaluation", "companies", slug)
        c = json.load(open(os.path.join(cdir, "company.json")))
        manifest = json.load(open(os.path.join(cdir, "filings", "manifest.json")))["filings"]
        chosen = pick_documents(manifest)
        checks = {"documents_after_B": all(f["filingDate"] > B for f in chosen) and bool(chosen),
                  "documents_before_as_of": all(f["filingDate"] <= AS_OF for f in chosen),
                  "label_evidence_after_B": it["label_evidence"]["filed"] > B,
                  "label_evidence_before_as_of": it["label_evidence"]["filed"] <= AS_OF}
        if not all(checks.values()):
            audit.append({"id": it["id"], "slug": slug, "skipped": True, "checks": checks})
            print(f"  SKIP {it['id']} {slug}: {checks}")
            continue
        docs, doc_meta = "", []
        for f in chosen:
            path, fn = run_eval.ensure_doc(slug, c["cik"], f)
            clean, removed = redact.redact(run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore")))
            docs += f"<document name=\"{f['form']} filed {f['filingDate']}\">\n{clean}\n</document>\n"
            doc_meta.append({"form": f["form"], "filed": f["filingDate"], "file": fn,
                             "redacted_lines": len(removed)})
        pack, pack_log = history_pack.build(slug, AS_OF, history_end=HISTORY_END)
        # every dated fact in the pack must be filed <= AS_OF; the builder filters, we assert
        assert HISTORY_END in pack
        body = [{"type": "text", "text": docs}, {"type": "text", "text": pack},
                {"type": "text", "text": f"As-of date: {AS_OF}.\n\n{TASK}"}]
        probe_q = PROBE_USER.replace("{as_of}", AS_OF).replace("{edgar_name}", c["edgar_name"])
        probe_req = [
            {"custom_id": f"probe-{it['id']}", "params": {
                "model": MODEL, "max_tokens": PROBE_MAX_TOKENS, "system": PROBE_SYSTEM,
                "thinking": {"type": "adaptive"},
                "messages": [{"role": "user", "content": probe_q}],
                "output_config": {"format": {"type": "json_schema", "schema": PROBE_SCHEMA},
                                  "effort": "low"}}}]
        vf_req = [
            {"custom_id": f"vf-{it['id']}", "params": {
                "model": MODEL, "max_tokens": VF_MAX_TOKENS, "system": SYSTEM,   # thinking + answer headroom
                "thinking": {"type": "adaptive"},
                "messages": [{"role": "user", "content": body}],
                "output_config": {"format": {"type": "json_schema", "schema": SCHEMA},
                                  "effort": "high"}}}]
        reqs += (probe_req if include_probes else []) + vf_req
        audit.append({"id": it["id"], "slug": slug, "skipped": False, "checks": checks,
                      "documents": doc_meta, "pack_quarterly_rows": pack_log.get("quarterly_rows"),
                      "pack_text": pack, "probe_question": probe_q,
                      "label": it["label"], "label_evidence": it["label_evidence"],
                      "persistence": it["persistence"], "changed": it["changed"]})
    return reqs, audit


def worst_case(reqs, per):
    """Exact ceiling at batch prices: counted input + max_tokens of every request as output."""
    inp = sum(per[r["custom_id"]] for r in reqs)
    out = sum(r["params"]["max_tokens"] for r in reqs)
    return (inp * PRICE_IN + out * PRICE_OUT) * 0.5


def dry(client, quiet=False, only=None, include_probes=True, cap=None):
    cap = CAP_USD if cap is None else cap
    reqs, audit = build_requests(only, include_probes)
    per = {}
    for r in reqs:
        per[r["custom_id"]] = client.messages.count_tokens(
            model=MODEL, system=r["params"]["system"], messages=r["params"]["messages"]).input_tokens
        if not quiet:
            print(f"  {r['custom_id']:<12} {per[r['custom_id']]:>9,} Tokens")
    # D9 auto-trim: while over the cap, drop the most expensive UNCHANGED observation (both requests)
    cand = {it["id"]: it for it in candidates()["items"]}
    dropped = []
    while worst_case(reqs, per) > cap:
        unch = [r for r in reqs if r["custom_id"].startswith("vf-") and not cand[r["custom_id"][3:]]["changed"]]
        if not unch:
            break
        victim = max(unch, key=lambda r: per[r["custom_id"]])["custom_id"][3:]
        reqs = [r for r in reqs if not r["custom_id"].endswith(f"-{victim}")]
        audit = [a for a in audit if a["id"] != victim] + [{"id": victim, "slug": cand[victim]["slug"],
                                                            "skipped": True, "reason": "D9 cost trim"}]
        dropped.append(victim)
    worst = worst_case(reqs, per)
    n_vf = sum(1 for r in reqs if r["custom_id"].startswith("vf-"))
    print(f"\n{len(reqs)} Requests ({n_vf} Beobachtungen), {sum(per[r['custom_id']] for r in reqs):,} Input-Tokens. "
          f"Exakter Worst Case ${worst:.2f} (Cap {cap}){'; D9-Trim: ' + ', '.join(dropped) if dropped else ''}")
    return reqs, audit, per, worst


def submit(client, only=None, include_probes=True, cap=None, tag=""):
    cap = CAP_USD if cap is None else cap
    reqs, audit, per, worst = dry(client, quiet=True, only=only, include_probes=include_probes, cap=cap)
    if worst > cap:
        print(f"ABBRUCH: worst case ${worst:.2f} > Cap ${cap}. Kandidaten reduzieren (Regel D9)."); return
    batch = client.messages.batches.create(requests=reqs)
    d = os.path.join(RUNS, batch.id); os.makedirs(d, exist_ok=True)
    json.dump({"batch_id": batch.id, "model": MODEL, "boundary_B": B, "as_of": AS_OF,
               "history_end": HISTORY_END, "system_prompt": SYSTEM, "task": TASK,
               "probe_system": PROBE_SYSTEM, "token_counts": per, "worst_case_usd": worst,
               "observations": audit}, open(os.path.join(d, "audit.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(reqs, open(os.path.join(d, "requests_raw.json"), "w"))
    open(os.path.join(HERE, "LAST_BATCH" + tag), "w").write(batch.id)
    print(f"submitted {batch.id}: {batch.processing_status} ({len(reqs)} requests, worst case ${worst:.2f})")


def notch(r):
    r = (r or "").replace("(P)", "").strip()
    return SCALE.index(r) if r in SCALE else None


def collect(client, tag=""):
    bid = open(os.path.join(HERE, "LAST_BATCH" + tag)).read().strip()
    st = client.messages.batches.retrieve(bid)
    if st.processing_status != "ended":
        print(f"{bid}: {st.processing_status} {st.request_counts}"); return
    d = os.path.join(RUNS, bid)
    outs, usage, models = {}, {"in": 0, "out": 0}, {}
    for item in client.messages.batches.results(bid):
        if item.result.type != "succeeded":
            outs[item.custom_id] = {"error": item.result.type}; continue
        m = item.result.message
        models[item.custom_id] = m.model            # run-time provenance of the exact model served
        u = m.usage.model_dump(); usage["in"] += u["input_tokens"]; usage["out"] += u["output_tokens"]
        text = next((b.text for b in m.content if b.type == "text"), None)
        if text is None or m.stop_reason == "max_tokens":
            # max_tokens is the ceiling for thinking AND answer; when thinking exhausts it the
            # response carries no (complete) answer. Recorded as a failed observation, not scored.
            outs[item.custom_id] = {"failed": True, "reason": "no_text_or_truncated",
                                    "stop_reason": m.stop_reason,
                                    "block_types": [b.type for b in m.content], "usage": u}
            continue
        try:
            outs[item.custom_id] = json.loads(text[text.index("{"):text.rindex("}") + 1])
        except Exception:
            outs[item.custom_id] = {"parse_error": text[:400], "stop_reason": m.stop_reason}
    json.dump(outs, open(os.path.join(d, "raw_outputs.json"), "w"), indent=1, ensure_ascii=False)

    results = []
    for it in candidates()["items"]:
        if not it.get("in_run", True):
            continue
        v, p = outs.get(f"vf-{it['id']}", {}), outs.get(f"probe-{it['id']}", {})
        if not v or "figures_usd_m" not in v:
            continue
        fig = dict(v["figures_usd_m"]); fig["qualitative"] = v["qualitative"]; fig["label"] = it["id"]
        try:
            agg = round(scorecard.aggregate(scorecard.build(fig)), 3); pred = scorecard.outcome(agg)
        except Exception as exc:
            agg, pred = None, f"error: {exc}"
        lab, per = notch(it["label"]), notch(it["persistence"])
        e = lambda x: abs(notch(x) - lab) if notch(x) is not None and lab is not None else None
        claimed = p.get("claimed_moodys_rating")
        results.append({**it, "probe": p,
                        "probe_flag": ("recalls_label" if claimed and notch(claimed) == lab and lab != per else
                                       "recalls_prior" if claimed and notch(claimed) == per else "wrong_or_none"),
                        "scorecard": {"pred": pred, "aggregate": agg},
                        "direct": {"pred": v.get("direct_rating"), "vs_last_known": v.get("vs_last_known")},
                        "extraction": {"figures": v.get("figures_usd_m"), "figure_notes": v.get("figure_notes"),
                                       "qualitative": v.get("qualitative"),
                                       "qualitative_relative": v.get("qualitative_relative"),
                                       "rationale": v.get("qualitative_rationale")},
                        "err": {"scorecard": e(pred), "direct": e(v.get("direct_rating")),
                                "persistence": abs(per - lab) if per is not None and lab is not None else None}})
    cost = (usage["in"] * PRICE_IN + usage["out"] * PRICE_OUT) * 0.5
    json.dump({"batch_id": bid, "models_served": sorted(set(models.values())), "usage": usage,
               "cost_usd_batch": round(cost, 3), "results": results},
              open(os.path.join(d, "results.json"), "w"), indent=1, ensure_ascii=False)
    for r in results:
        print(f"  {r['id']} {r['slug']:<22} {r['persistence']:>4}->{r['label']:<4} "
              f"scorecard={r['scorecard']['pred']!s:<5} direct={r['direct']['pred']!s:<5}"
              f"({r['direct']['vs_last_known']}) probe={r['probe_flag']}")
    for ch in ("scorecard", "direct", "persistence"):
        errs = [r["err"][ch] for r in results if r["err"][ch] is not None]
        if errs:
            print(f"  {ch:<12} exakt {sum(x == 0 for x in errs)}/{len(errs)}  MAE {sum(errs)/len(errs):.2f}")
    print(f"  Kosten (Batch): ${cost:.2f}   usage {usage}")


def make_client():
    import socket
    _gai = socket.getaddrinfo
    def v4_only(*a, **k):
        res = _gai(*a, **k); v4 = [r for r in res if r[0] == socket.AF_INET]; return v4 or res
    socket.getaddrinfo = v4_only
    return anthropic.Anthropic(max_retries=10, timeout=120.0,
                               http_client=anthropic.DefaultHttpxClient(transport=httpx2.HTTPTransport(retries=5)))


def rerun(client):
    """Re-run named observations (vf only; probes already succeeded) under the remaining budget."""
    ids = sys.argv[2].split(",")
    submit(client, only=ids, include_probes=False, cap=CAP_RERUN, tag="_RERUN")


if __name__ == "__main__":
    c = make_client()
    if sys.argv[1] == "--rerun":
        rerun(c)
    elif sys.argv[1] == "--collect-rerun":
        collect(c, tag="_RERUN")
    else:
        {"--dry": dry, "--submit": submit, "--collect": collect}[sys.argv[1]](c)
