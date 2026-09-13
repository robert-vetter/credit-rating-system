"""
Experiment 04, Arm 1: offline preparation of every request, frozen into a manifest.

Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-12. No network, no model
call, no download: documents come from the local cache, the tokenizer from the Hugging Face
cache (HF_HUB_OFFLINE), provider facts from the endpoint snapshot under evidence/.

What it produces under runs/<run>/ (gitignored):
  manifest.json          cohort, configuration, every request with body hash, rendered token
                         count, input bound, reservation, the plan totals and the pilot choice
  bodies/<request>.json  the exact bytes the runner sends (replicates share identical bytes)
  audit/current/<id>.json   documents (hashes, redaction counts), pack provenance and checks
  audit/legacy/<id>.json    saved-input control: identity proof and per-figure source dates
  audit/removed_lines/<id>.json   what the redactor cut, never part of any body
  audit/probes.json, audit/residual_scan.json, audit/hashes.json, audit/environment.json
  preflight.txt          the free pre-flight table

Design (RUN-SPEC.md, review-codex-2026-09-12.md, decisions D5 to D12):
  current arm   20 confirmed issuers, current repaired packs (typed history from raw rating
                records, 24-month peer policy), oldest-10-Q trim only where the finalized
                package exceeds the context allowance, three replicates
  saved arm     the seven Opus successes on the exact saved Experiment 03 inputs, untrimmed,
                three replicates, with legacy_provenance.py evidence
  probes        one memory probe per issuer, the Experiment 03 probe prompt and schema
Bodies carry only model input: no labels, evidence, flags, probe answers or audit data.

Run from the repository root: python3 experiments/04-open-weight-cross-section/prepare_inputs.py
"""
import datetime
import hashlib
import json
import os
import re
import sys
from decimal import Decimal, ROUND_UP

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "system"), os.path.join(ROOT, "evaluation", "pipeline"),
                os.path.join(ROOT, "experiments", "03-oos-values-first"), HERE]
import history_pack   # noqa: E402
import redact         # noqa: E402
import run_eval       # noqa: E402
import run_batch      # noqa: E402  (prompts, probe schema; its paid guard is untouched)
import legacy_provenance   # noqa: E402

E03 = os.path.join(ROOT, "experiments", "03-oos-values-first")
COMPANIES = os.path.join(ROOT, "evaluation", "companies")
RUN_NAME = "EXP04-ARM1-A1"
RUN_DIR = os.path.join(HERE, "runs", RUN_NAME)

MODEL = "qwen/qwen3-235b-a22b-2507"
ENDPOINT_SLUG, PROVIDER_NAME = "deepinfra/fp8", "DeepInfra"
TOKENIZER = "Qwen/Qwen3-235B-A22B-Instruct-2507"
PRICE_IN, PRICE_OUT = Decimal("0.09"), Decimal("0.55")       # USD per million tokens, ceilings (D6)
B, AS_OF, HISTORY_END = "2025-09-30", "2026-08-29", "2025-08-28"
MODEL_RELEASE_BOUND = "2025-07-21"
MAX_TOKENS_DOC, MAX_TOKENS_PROBE = 8192, 1200
REPLICATES, SEED, TEMPERATURE = 3, 20260912, 0
PEER_MAX_AGE_MONTHS = 24
RETRY_ALLOWANCE = 10
SAVED_ARM_IDS = ["X12", "X14", "X15", "X16", "X17", "X19", "X20"]      # the seven Opus successes
SUCCESS_BATCH = {"X12": "msgbatch_01QsBQnMF1itHj1Ysz3jguKZ", "X14": "msgbatch_01QsBQnMF1itHj1Ysz3jguKZ"}
FIRST_BATCH = "msgbatch_01EwnHhsKjahuwhmL8S5h2Sx"
DIAGNOSTIC_IDS = ["X14"]                                                # D8: executed, not primary
ALLOWED_PRIMARY_FORMS = ("10-K", "10-Q")
ALLOWED_XBRL_FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "40-F"}
SYSTEM, TASK, SCHEMA = run_batch.SYSTEM, run_batch.TASK, run_batch.SCHEMA
PROBE_SYSTEM, PROBE_USER, PROBE_SCHEMA = run_batch.PROBE_SYSTEM, run_batch.PROBE_USER, run_batch.PROBE_SCHEMA
JOIN_RULE = "user message = documents + '\\n' + history pack + '\\n\\n' + 'As-of date: <as_of>.' + '\\n\\n' + task"
CODE_FILES = ["experiments/04-open-weight-cross-section/prepare_inputs.py",
              "experiments/04-open-weight-cross-section/run_openrouter.py",
              "experiments/04-open-weight-cross-section/legacy_provenance.py",
              "experiments/04-open-weight-cross-section/test_runner.py",
              "experiments/04-open-weight-cross-section/legacy_builders/history_pack_20260910.py",
              "experiments/04-open-weight-cross-section/legacy_builders/peer_table_20260910.py",
              "experiments/04-open-weight-cross-section/legacy_builders/fetch_xbrl_20260910.py",
              "evaluation/pipeline/history_pack.py", "evaluation/pipeline/peer_table.py",
              "evaluation/pipeline/run_eval.py", "evaluation/pipeline/score_run.py",
              "system/redact.py", "system/scorecard.py",
              "experiments/03-oos-values-first/run_batch.py",
              "experiments/03-oos-values-first/prompts/system.txt",
              "experiments/03-oos-values-first/prompts/task_values_first.txt",
              "experiments/03-oos-values-first/prompts/schema_values_first.json",
              "experiments/03-oos-values-first/prompts/probe.txt",
              "experiments/03-oos-values-first/candidates.json"]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    return sha256_bytes(open(path, "rb").read())


def canonical(body):
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def reservation_usd(input_bound, max_tokens):
    usd = (Decimal(input_bound) * PRICE_IN + Decimal(max_tokens) * PRICE_OUT) / Decimal(10 ** 6)
    return str(usd.quantize(Decimal("0.000001"), rounding=ROUND_UP))


def provider_block():
    return {"order": [ENDPOINT_SLUG], "allow_fallbacks": False, "require_parameters": True,
            "quantizations": ["fp8"],
            "max_price": {"prompt": float(PRICE_IN), "completion": float(PRICE_OUT)}}


def doc_body(user_text):
    return {"model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_text}],
            "temperature": TEMPERATURE, "seed": SEED, "max_tokens": MAX_TOKENS_DOC,
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "scorecard_inputs", "strict": True, "schema": SCHEMA}},
            "provider": provider_block(), "transforms": [], "stream": False}


def probe_body(question):
    return {"model": MODEL,
            "messages": [{"role": "system", "content": PROBE_SYSTEM}, {"role": "user", "content": question}],
            "temperature": TEMPERATURE, "seed": SEED, "max_tokens": MAX_TOKENS_PROBE,
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "memory_probe", "strict": True, "schema": PROBE_SCHEMA}},
            "provider": provider_block(), "transforms": [], "stream": False}


def pick_documents(manifest):
    """Experiment 03 rule (run_batch.pick_documents): latest 10-K after B, then every later 10-Q up to as_of."""
    post = [f for f in manifest if B < f["filingDate"] <= AS_OF]
    ks = sorted([f for f in post if f["form"] == "10-K"], key=lambda f: f["filingDate"])
    if not ks:
        return []
    k = ks[-1]
    return [k] + sorted([f for f in post if f["form"] == "10-Q" and f["filingDate"] > k["filingDate"]],
                        key=lambda f: f["filingDate"])


def cached_document(slug, filing):
    """The cached primary document, never downloaded here."""
    acc = filing["accessionNumber"].replace("-", "")
    fn = f"{filing['filingDate']}_{filing['form'].replace('/', '')}_{acc}.htm"
    path = os.path.join(COMPANIES, slug, "filings", fn)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{slug}: {fn} is not cached; preparation never downloads")
    return path, fn


def assemble_documents(slug, chosen):
    docs, meta, removed_all = "", [], {}
    for f in chosen:
        assert f["form"] in ALLOWED_PRIMARY_FORMS and B < f["filingDate"] <= AS_OF
        path, fn = cached_document(slug, f)
        raw = open(path, "rb").read()
        clean, removed = redact.redact_v2(run_eval.to_text(raw.decode("utf-8", "ignore")))
        fragments = redact.rating_fragments(clean)
        assert not fragments, f"{slug} {fn}: rating fragments survived redaction: {fragments[:3]}"
        text = f'<document name="{f["form"]} filed {f["filingDate"]}">\n{clean}\n</document>\n'
        docs += text
        meta.append({"form": f["form"], "filed": f["filingDate"], "file": fn,
                     "accession": f["accessionNumber"], "primary_document": f["primaryDocument"],
                     "source_sha256": sha256_bytes(raw), "redacted_text_sha256": sha256_bytes(clean.encode()),
                     "chars": len(clean), "redacted_lines": len(removed), "redactor": "redact_v2",
                     "rating_fragments_after_redaction": 0})
        removed_all[fn] = removed
    return docs, meta, removed_all


def assemble_documents_v1(slug, chosen):
    """The Experiment 03 assembly with the original redactor, used only to verify that a saved
    input replays byte for byte; the saved arm sends the saved text, never a re-redacted one."""
    docs, meta, removed_all = "", [], {}
    for f in chosen:
        path, fn = cached_document(slug, f)
        raw = open(path, "rb").read()
        clean, removed = redact.redact(run_eval.to_text(raw.decode("utf-8", "ignore")))
        docs += f'<document name="{f["form"]} filed {f["filingDate"]}">\n{clean}\n</document>\n'
        meta.append({"form": f["form"], "filed": f["filingDate"], "file": fn, "accession": f["accessionNumber"],
                     "primary_document": f["primaryDocument"], "source_sha256": sha256_bytes(raw),
                     "redacted_text_sha256": sha256_bytes(clean.encode()), "chars": len(clean),
                     "redacted_lines": len(removed), "redactor": "redact (2026-08-29), as in Experiment 03",
                     "rating_fragments_after_redaction": len(redact.rating_fragments(clean))})
        removed_all[fn] = removed
    return docs, meta, removed_all


RESIDUAL = re.compile(r"(?i)moody")
SYMBOL = re.compile(r"\b(Aaa|Aa[123]|A[123]|Baa[123]|Ba[123]|B[123]|Caa[123]|Ca)\b")
ACTION = re.compile(r"(?i)\b(downgrad|upgrad)\w*")


def residual_scan(clean_text):
    """Counts of what the heuristic redactor may have left: a Moody's mention within 200
    characters of a rating symbol or of upgrade/downgrade language. Counts only."""
    hits_symbol = hits_action = 0
    for m in RESIDUAL.finditer(clean_text):
        window = clean_text[max(0, m.start() - 200): m.end() + 200]
        hits_symbol += bool(SYMBOL.search(window))
        hits_action += bool(ACTION.search(window))
    return {"moodys_mentions": len(RESIDUAL.findall(clean_text)),
            "mentions_near_rating_symbol": hits_symbol, "mentions_near_action_word": hits_action,
            "action_words_total": len(ACTION.findall(clean_text))}


def load_tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(TOKENIZER)


def rendered_tokens(tok, system, user):
    ids = tok.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": user}],
                                  tokenize=True, add_generation_prompt=True)
    return len(ids)


def count(tok, text):
    return len(tok(text, add_special_tokens=False)["input_ids"])


def tokenizer_identity():
    hub = os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-235B-A22B-Instruct-2507")
    rev = open(os.path.join(hub, "refs", "main")).read().strip()
    snap = os.path.join(hub, "snapshots", rev)
    return {"name": TOKENIZER, "revision": rev,
            "files": {f: sha256_file(os.path.join(snap, f)) for f in sorted(os.listdir(snap))}}


def endpoint_snapshot():
    ep = json.load(open(os.path.join(HERE, "evidence", "endpoints-2026-09-12", "ep_qwen_qwen3-235b-a22b-2507.json")))
    e = next(x for x in ep["data"]["endpoints"] if x["tag"] == ENDPOINT_SLUG)
    return {"slug": ENDPOINT_SLUG, "provider_name": e["provider_name"], "context_length": e["context_length"],
            "max_completion_tokens": e["max_completion_tokens"], "quantization": e["quantization"],
            "snapshot_prices_per_token": e["pricing"], "supported_parameters": e["supported_parameters"],
            "snapshot_file": "evidence/endpoints-2026-09-12/ep_qwen_qwen3-235b-a22b-2507.json",
            "model_created_unix": ep["data"]["created"]}


def pack_checks(log, persistence):
    """G4 assertions on one current pack's provenance log."""
    problems = []
    for kind in ("annual_sources", "quarterly_sources"):
        for end, fields in log.get(kind, {}).items():
            for field, src in fields.items():
                if not (src.get("end") and src.get("filed") and src["end"] <= src["filed"] <= AS_OF):
                    problems.append(f"{kind} {end} {field} {src}")
                if src.get("form") not in ALLOWED_XBRL_FORMS:
                    problems.append(f"{kind} {end} {field} form {src.get('form')}")
    for pslug, p in log.get("peers", {}).items():
        if pslug.startswith("_"):
            continue
        ends = set()
        for field, src in p["sources"].items():
            ends.add(src.get("end"))
            if not (src.get("end") and src.get("filed") and src["end"] <= src["filed"] <= AS_OF):
                problems.append(f"peer {pslug} {field} {src}")
            if src.get("form") not in ALLOWED_XBRL_FORMS:
                problems.append(f"peer {pslug} {field} form {src.get('form')}")
        if len(ends) > 1:
            problems.append(f"peer {pslug} mixes fiscal periods {sorted(ends)}")
    if any(e[0] > HISTORY_END for e in log.get("path_events", [])):
        problems.append("rating event after the history end")
    for end, y in log.get("years", {}).items():
        if y.get("anchor") and end > HISTORY_END:
            problems.append(f"anchor for FY {end} after the history end")
    sel = (log.get("terminal_state") or {}).get("selected") or {}
    if sel.get("rating") != persistence:
        problems.append(f"terminal rating {sel.get('rating')} differs from the frozen persistence {persistence}")
    return problems


def prepare(run_dir=RUN_DIR):
    for sub in ("bodies", "audit/current", "audit/legacy", "audit/removed_lines"):
        os.makedirs(os.path.join(run_dir, sub), exist_ok=True)
    tok = load_tokenizer()
    schema_tokens = count(tok, json.dumps(SCHEMA, separators=(",", ":")))
    probe_schema_tokens = count(tok, json.dumps(PROBE_SCHEMA, separators=(",", ":")))
    ep = endpoint_snapshot()
    context = ep["context_length"]
    assert ep["max_completion_tokens"] >= MAX_TOKENS_DOC
    cand = json.load(open(os.path.join(E03, "candidates.json")))
    items = [it for it in cand["items"] if it.get("status") == "confirmed"]
    ids = [it["id"] for it in items]
    assert ids == [f"X{i:02d}" for i in range(1, 21)], ids
    for it in items:
        assert it["changed"] == (it["label"] != it["persistence"]), it["id"]
    by_id = {it["id"]: it for it in items}
    requests, audit_docs, hashes_docs, scan = [], {}, {}, {}

    def allowance(st):
        return 2 * st + 512

    # ---- current arm ----
    for it in items:
        slug, xid = it["slug"], it["id"]
        c = json.load(open(os.path.join(COMPANIES, slug, "company.json")))
        manifest = json.load(open(os.path.join(COMPANIES, slug, "filings", "manifest.json")))["filings"]
        chosen = pick_documents(manifest)
        assert chosen, xid
        pack, plog = history_pack.build(slug, AS_OF, history_end=HISTORY_END,
                                        peer_max_age_months=PEER_MAX_AGE_MONTHS)
        problems = pack_checks(plog, it["persistence"])
        assert not problems, (xid, problems)
        trimmed, dropped = False, None
        while True:
            docs, meta, removed = assemble_documents(slug, chosen)
            user = docs + "\n" + pack + "\n\n" + f"As-of date: {AS_OF}.\n\n{TASK}"
            rendered = rendered_tokens(tok, SYSTEM, user)
            if rendered + allowance(schema_tokens) + MAX_TOKENS_DOC <= context:
                break
            qs = [f for f in chosen if f["form"] == "10-Q"]
            assert qs, f"{xid}: over the context allowance with no 10-Q left to drop"
            drop = min(qs, key=lambda f: f["filingDate"])
            chosen = [f for f in chosen if f is not drop]
            trimmed, dropped = True, f"{drop['form']} {drop['filingDate']}"
        body = doc_body(user)
        raw = canonical(body)
        for m in meta:
            hashes_docs[f"{slug}/filings/{m['file']}"] = m["source_sha256"]
        scan[xid] = {m["file"]: residual_scan(t) for m, t in zip(meta, re.findall(
            r'<document name="[^"]+">\n(.*?)\n</document>\n', docs, flags=re.S))}
        json.dump(removed, open(os.path.join(run_dir, "audit", "removed_lines", f"{xid}.json"), "w"), indent=0)
        for r in range(1, REPLICATES + 1):
            rid = f"doc-current-{xid}-r{r}"
            open(os.path.join(run_dir, "bodies", f"{rid}.json"), "wb").write(raw)
            requests.append({"request_id": rid, "kind": "document", "arm": "current", "issuer_id": xid,
                             "slug": slug, "replicate": r, "body_file": f"bodies/{rid}.json",
                             "body_sha256": sha256_bytes(raw), "rendered_tokens": rendered,
                             "schema_tokens": schema_tokens, "input_bound_tokens": rendered + allowance(schema_tokens),
                             "max_tokens": MAX_TOKENS_DOC,
                             "expected_prompt_tokens": [max(0, rendered - 256), rendered + allowance(schema_tokens)],
                             "reservation_usd": reservation_usd(rendered + allowance(schema_tokens), MAX_TOKENS_DOC)})
        audit_docs[xid] = {"id": xid, "slug": slug, "arm": "current", "documents": meta,
                           "documents_selected": [f"{m['form']} {m['filed']}" for m in meta],
                           "trimmed": trimmed, "dropped_document": dropped,
                           "pack_sha256": sha256_bytes(pack.encode()), "pack_tokens": count(tok, pack),
                           "documents_tokens": count(tok, docs),
                           "pack_log": plog, "pack_checks": "all passed", "body_sha256": sha256_bytes(raw),
                           "reference": {"label_source": "candidates.json (frozen, not in the body)",
                                         "persistence": it["persistence"], "changed": it["changed"]}}
        json.dump(audit_docs[xid], open(os.path.join(run_dir, "audit", "current", f"{xid}.json"), "w"), indent=1)
        print(f"  current {xid} {slug:<22} rendered {rendered:>7,} {'trimmed: dropped ' + dropped if trimmed else ''}", flush=True)

    # ---- saved arm ----
    mirror = legacy_provenance.Mirror()
    batches = {}
    for bid in (FIRST_BATCH, SUCCESS_BATCH["X12"]):
        d = os.path.join(E03, "runs", bid)
        batches[bid] = {"requests": {r["custom_id"]: r["params"] for r in json.load(open(os.path.join(d, "requests_raw.json")))},
                        "audit": {it["id"]: it for it in json.load(open(os.path.join(d, "audit.json")))["observations"]}}
    task_block = f"As-of date: {AS_OF}.\n\n{TASK}"
    for xid in SAVED_ARM_IDS:
        it = by_id[xid]
        slug = it["slug"]
        bid = SUCCESS_BATCH.get(xid, FIRST_BATCH)
        params = batches[bid]["requests"][f"vf-{xid}"]
        blocks = [b["text"] for b in params["messages"][0]["content"]]
        assert len(blocks) == 3 and params["system"] == SYSTEM and blocks[2] == task_block
        assert params["output_config"]["format"]["schema"] == SCHEMA and "tools" not in params
        if bid != FIRST_BATCH:
            first = batches[FIRST_BATCH]["requests"][f"vf-{xid}"]
            assert [b["text"] for b in first["messages"][0]["content"]] == blocks, f"{xid}: rerun body differs"
        saved_audit = batches[bid]["audit"][xid]
        chosen_meta = saved_audit["documents"]
        manifest = json.load(open(os.path.join(COMPANIES, slug, "filings", "manifest.json")))["filings"]
        chosen = [next(f for f in manifest if f["accessionNumber"].replace("-", "") in m["file"]) for m in chosen_meta]
        docs, meta, removed = assemble_documents_v1(slug, chosen)
        assert docs == blocks[0], f"{xid}: documents do not replay from the cache"
        prov = legacy_provenance.provenance(mirror, slug, blocks[1])
        assert prov["all_dated_and_eligible"], (xid, prov["problems"])
        user = blocks[0] + "\n" + blocks[1] + "\n\n" + blocks[2]
        rendered = rendered_tokens(tok, SYSTEM, user)
        assert rendered + allowance(schema_tokens) + MAX_TOKENS_DOC <= context, f"{xid}: saved input exceeds the context allowance"
        body = doc_body(user)
        raw = canonical(body)
        for m in meta:
            hashes_docs[f"{slug}/filings/{m['file']}"] = m["source_sha256"]
        json.dump(removed, open(os.path.join(run_dir, "audit", "removed_lines", f"{xid}-saved.json"), "w"), indent=0)
        for r in range(1, REPLICATES + 1):
            rid = f"doc-saved-{xid}-r{r}"
            open(os.path.join(run_dir, "bodies", f"{rid}.json"), "wb").write(raw)
            requests.append({"request_id": rid, "kind": "document", "arm": "saved", "issuer_id": xid,
                             "slug": slug, "replicate": r, "body_file": f"bodies/{rid}.json",
                             "body_sha256": sha256_bytes(raw), "rendered_tokens": rendered,
                             "schema_tokens": schema_tokens, "input_bound_tokens": rendered + allowance(schema_tokens),
                             "max_tokens": MAX_TOKENS_DOC,
                             "expected_prompt_tokens": [max(0, rendered - 256), rendered + allowance(schema_tokens)],
                             "reservation_usd": reservation_usd(rendered + allowance(schema_tokens), MAX_TOKENS_DOC)})
        prov.update({"id": xid, "source_batch": bid, "documents": meta, "trimmed": False,
                     "saved_system_matches_prompt": True, "saved_task_matches_prompt": True,
                     "saved_schema_matches_prompt": True, "documents_replay_exactly": True,
                     "body_sha256": sha256_bytes(raw), "pack_tokens": count(tok, blocks[1])})
        json.dump(prov, open(os.path.join(run_dir, "audit", "legacy", f"{xid}.json"), "w"), indent=1)
        print(f"  saved   {xid} {slug:<22} rendered {rendered:>7,} identical pack, {prov['counts']}", flush=True)

    # ---- probes ----
    probes = {}
    for it in items:
        xid, slug = it["id"], it["slug"]
        c = json.load(open(os.path.join(COMPANIES, slug, "company.json")))
        q = PROBE_USER.replace("{as_of}", AS_OF).replace("{edgar_name}", c["edgar_name"])
        body = probe_body(q)
        raw = canonical(body)
        rendered = rendered_tokens(tok, PROBE_SYSTEM, q)
        rid = f"probe-{xid}"
        open(os.path.join(run_dir, "bodies", f"{rid}.json"), "wb").write(raw)
        requests.append({"request_id": rid, "kind": "probe", "arm": "probe", "issuer_id": xid, "slug": slug,
                         "replicate": 1, "body_file": f"bodies/{rid}.json", "body_sha256": sha256_bytes(raw),
                         "rendered_tokens": rendered, "schema_tokens": probe_schema_tokens,
                         "input_bound_tokens": rendered + allowance(probe_schema_tokens), "max_tokens": MAX_TOKENS_PROBE,
                         "expected_prompt_tokens": [max(0, rendered - 256), rendered + allowance(probe_schema_tokens)],
                         "reservation_usd": reservation_usd(rendered + allowance(probe_schema_tokens), MAX_TOKENS_PROBE)})
        probes[xid] = {"question": q, "edgar_name": c["edgar_name"], "rendered_tokens": rendered}
    json.dump(probes, open(os.path.join(run_dir, "audit", "probes.json"), "w"), indent=1)
    json.dump(scan, open(os.path.join(run_dir, "audit", "residual_scan.json"), "w"), indent=1)

    # ---- hashes and environment ----
    code = {f: sha256_file(os.path.join(ROOT, f)) for f in CODE_FILES if os.path.exists(os.path.join(ROOT, f))}
    raw_caches = {s: sha256_file(os.path.join(legacy_provenance.RAW, s)) for s in sorted(os.listdir(legacy_provenance.RAW))
                  if s.endswith(".json")}
    xbrl = {s: sha256_file(os.path.join(COMPANIES, s, "xbrl.json")) for s in sorted(os.listdir(COMPANIES))
            if os.path.exists(os.path.join(COMPANIES, s, "xbrl.json"))}
    ratings = {it["slug"]: sha256_file(os.path.join(COMPANIES, it["slug"], "ratings.json")) for it in items}
    observations = {by_id[x]["slug"]: sha256_file(os.path.join(COMPANIES, by_id[x]["slug"], "observations.json"))
                    for x in SAVED_ARM_IDS}
    hashes = {"code_and_prompts": code, "primary_documents": dict(sorted(hashes_docs.items())),
              "raw_companyfacts": raw_caches, "xbrl_json": xbrl, "ratings_json": ratings,
              "observations_json_saved_arm": observations,
              "saved_experiment03_requests": {bid: sha256_file(os.path.join(E03, "runs", bid, "requests_raw.json"))
                                              for bid in batches}}
    json.dump(hashes, open(os.path.join(run_dir, "audit", "hashes.json"), "w"), indent=1)
    import importlib.metadata as md
    env = {"python": sys.version, "packages": {p: md.version(p) for p in ("transformers", "tokenizers", "httpx", "jsonschema")},
           "tokenizer": tokenizer_identity(), "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE"),
           "prepared_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    json.dump(env, open(os.path.join(run_dir, "audit", "environment.json"), "w"), indent=1)

    # ---- plan totals and pilot ----
    docs_reqs = [r for r in requests if r["kind"] == "document"]
    sum_res = sum(Decimal(r["reservation_usd"]) for r in requests)
    max_doc = max(Decimal(r["reservation_usd"]) for r in docs_reqs)
    conservative_total = sum_res + RETRY_ALLOWANCE * max_doc
    pilot_doc = max(docs_reqs, key=lambda r: (r["rendered_tokens"], -ord(r["request_id"][4]), r["request_id"]))
    pilot_doc = sorted([r for r in docs_reqs if r["rendered_tokens"] == pilot_doc["rendered_tokens"]],
                       key=lambda r: r["request_id"])[0]
    manifest = {
        "experiment": "04-open-weight-cross-section", "arm": "Arm 1", "run_name": RUN_NAME,
        "description": "post-release, history-conditioned disclosure-label pilot on Qwen3-235B-A22B-Instruct-2507 through OpenRouter",
        "model": MODEL, "model_release_bound": MODEL_RELEASE_BOUND, "endpoint": ep,
        "price_ceilings_usd_per_mtok": {"prompt": str(PRICE_IN), "completion": str(PRICE_OUT)},
        "dates": {"boundary_B": B, "as_of": AS_OF, "history_end": HISTORY_END},
        "cohort": {"ids": ids, "primary_ids": [x for x in ids if x not in DIAGNOSTIC_IDS],
                   "diagnostic_ids": DIAGNOSTIC_IDS, "saved_arm_ids": SAVED_ARM_IDS,
                   "labels": {it["id"]: {"label": it["label"], "persistence": it["persistence"], "changed": it["changed"]}
                              for it in items},
                   "selection": "all 20 confirmed candidates, explicitly; Experiment 03's in_run flags are not inherited"},
        "config": {"temperature": TEMPERATURE, "seed": SEED, "max_tokens_document": MAX_TOKENS_DOC,
                   "max_tokens_probe": MAX_TOKENS_PROBE, "replicates": REPLICATES, "join_rule": JOIN_RULE,
                   "peer_max_age_months": PEER_MAX_AGE_MONTHS, "primary_document_forms": list(ALLOWED_PRIMARY_FORMS),
                   "xbrl_source_forms": sorted(ALLOWED_XBRL_FORMS),
                   "trim_rule": "drop the oldest 10-Q while rendered + schema allowance + max_tokens exceeds the context; current arm only",
                   "schema_allowance_rule": "2 x schema tokens + 512", "prompt_token_policy":
                   "reported prompt_tokens must lie in expected_prompt_tokens; below: suspected truncation; above: unexplained; either halts",
                   "body_field_allowlist": ["model", "messages", "temperature", "seed", "max_tokens", "response_format",
                                            "provider", "transforms", "stream"],
                   "retry_allowance_total": RETRY_ALLOWANCE, "max_attempts_per_request": 2},
        "requests": requests,
        "plan_totals": {"n_probes": sum(r["kind"] == "probe" for r in requests),
                        "n_documents_current": sum(r["arm"] == "current" for r in requests),
                        "n_documents_saved": sum(r["arm"] == "saved" for r in requests),
                        "sum_reservations_usd": str(sum_res), "max_document_reservation_usd": str(max_doc),
                        "retry_allowance": RETRY_ALLOWANCE, "conservative_total_usd": str(conservative_total)},
        "pilot": {"probe": f"probe-{pilot_doc['issuer_id']}", "document": pilot_doc["request_id"],
                  "rule": "largest rendered document request across the arms that run; ties by request_id"},
        "hashes_file": "audit/hashes.json", "hashes_sha256": sha256_file(os.path.join(run_dir, "audit", "hashes.json")),
        "environment": env, "manifest_version": 1}
    mp = os.path.join(run_dir, "manifest.json")
    open(mp, "w").write(json.dumps(manifest, indent=1, ensure_ascii=False))
    lines = [f"Free pre-flight, {RUN_NAME}, prepared {env['prepared_at']}",
             f"{'request':<24}{'rendered':>10}{'bound':>10}{'max_out':>8}{'reserve $':>11}"]
    for r in requests:
        lines.append(f"{r['request_id']:<24}{r['rendered_tokens']:>10,}{r['input_bound_tokens']:>10,}{r['max_tokens']:>8}{r['reservation_usd']:>11}")
    lines += [f"requests {len(requests)}: probes {manifest['plan_totals']['n_probes']}, current documents "
              f"{manifest['plan_totals']['n_documents_current']}, saved documents {manifest['plan_totals']['n_documents_saved']}",
              f"sum of reservations ${sum_res}; retry allowance {RETRY_ALLOWANCE} x ${max_doc} = ${RETRY_ALLOWANCE * max_doc}",
              f"conservative total ${conservative_total}", f"pilot: {manifest['pilot']}",
              f"manifest sha256 {sha256_file(mp)}"]
    open(os.path.join(run_dir, "preflight.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[-6:]))
    return manifest


if __name__ == "__main__":
    prepare()
