"""Acceptance tests for the Experiment 04 runner: the twelve gates of review-codex-2026-09-12.md.

Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-12. Every test drives the
production dispatch path (Runner.dispatch) with a fake transport that records what would have
been sent; blocking tests assert zero sends. No network, no model call.

Run from this folder: python3 -m unittest -v test_runner
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "system"), os.path.join(ROOT, "evaluation", "pipeline")]
import run_openrouter as ro   # noqa: E402
import scorecard              # noqa: E402

MODEL = "qwen/qwen3-235b-a22b-2507"
SCHEMA = json.load(open(os.path.join(ROOT, "experiments", "03-oos-values-first", "prompts", "schema_values_first.json")))
PROBE_SCHEMA = {"type": "object", "properties": {"claimed_moodys_rating": {"type": ["string", "null"]},
                "notes": {"type": "string"}}, "required": ["claimed_moodys_rating", "notes"], "additionalProperties": False}
GOOD_FIGURES = {k: scorecard.WALMART[k] for k in ro.FIGURES}
GOOD_OUTPUT = {"fiscal_year_label": "FY2026", "figures_usd_m": GOOD_FIGURES, "figure_notes": "n",
               "qualitative": scorecard.WALMART["qualitative"],
               "qualitative_rationale": "r",
               "direct_rating": "Aa2", "direct_rationale": "d",
               "qualitative_relative": {k: "same" for k in scorecard.WALMART["qualitative"]},
               "vs_last_known": "unchanged"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def body(system, user, schema, max_tokens):
    return {"model": MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0, "seed": 20260912, "max_tokens": max_tokens,
            "response_format": {"type": "json_schema", "json_schema": {"name": "x", "strict": True, "schema": schema}},
            "provider": {"order": ["deepinfra/fp8"], "allow_fallbacks": False, "require_parameters": True,
                         "quantizations": ["fp8"], "max_price": {"prompt": 0.09, "completion": 0.55}},
            "transforms": [], "stream": False}


def make_fixture(base, cap="3.00", saved_ids=("X12",), n_ids=20):
    """A miniature run: the real 20-issuer id set, tiny bodies, consistent hashes."""
    run = os.path.join(base, "runs", "TEST-AUTH")
    for sub in ("bodies", "audit/current", "audit/legacy"):
        os.makedirs(os.path.join(run, sub), exist_ok=True)
    ids = [f"X{i:02d}" for i in range(1, n_ids + 1)]
    labels = {x: {"label": "A2", "persistence": "A2", "changed": False} for x in ids}
    labels["X12"] = {"label": "A2", "persistence": "A1", "changed": True}
    reqs = []

    def add(rid, kind, arm, xid, rep, b, max_tokens):
        raw = canonical(b)
        open(os.path.join(run, "bodies", f"{rid}.json"), "wb").write(raw)
        rendered = 1000 if kind == "document" else 150
        bound = rendered + 2 * 100 + 512
        res = ((Decimal(bound) * Decimal("0.09") + Decimal(max_tokens) * Decimal("0.55")) / Decimal(10 ** 6)).quantize(Decimal("0.000001"), rounding="ROUND_UP")
        reqs.append({"request_id": rid, "kind": kind, "arm": arm, "issuer_id": xid, "slug": xid.lower(), "replicate": rep,
                     "body_file": f"bodies/{rid}.json", "body_sha256": sha(raw), "rendered_tokens": rendered,
                     "schema_tokens": 100, "input_bound_tokens": bound, "max_tokens": max_tokens,
                     "expected_prompt_tokens": [max(0, rendered - 256), bound], "reservation_usd": str(res)})
    for x in ids:
        for r in (1, 2, 3):
            add(f"doc-current-{x}-r{r}", "document", "current", x, r, body("s", f"doc {x}", SCHEMA, 8192), 8192)
        if x in saved_ids:
            for r in (1, 2, 3):
                add(f"doc-saved-{x}-r{r}", "document", "saved", x, r, body("s", f"saved {x}", SCHEMA, 8192), 8192)
        add(f"probe-{x}", "probe", "probe", x, 1, body("p", f"probe {x}", PROBE_SCHEMA, 1200), 1200)
    for x in ids:
        json.dump({"pack_checks": "all passed"}, open(os.path.join(run, "audit", "current", f"{x}.json"), "w"))
    for x in saved_ids:
        json.dump({"all_dated_and_eligible": True}, open(os.path.join(run, "audit", "legacy", f"{x}.json"), "w"))
    code = ["experiments/04-open-weight-cross-section/run_openrouter.py", "system/scorecard.py"]
    hashes = {"code_and_prompts": {f: ro.sha256_file(os.path.join(ROOT, f)) for f in code}, "primary_documents": {}}
    hp = os.path.join(run, "audit", "hashes.json")
    json.dump(hashes, open(hp, "w"))
    docs = [r for r in reqs if r["kind"] == "document"]
    sum_res = sum(Decimal(r["reservation_usd"]) for r in reqs)
    max_doc = max(Decimal(r["reservation_usd"]) for r in docs)
    manifest = {"model": MODEL, "endpoint": {"slug": "deepinfra/fp8", "provider_name": "DeepInfra", "context_length": 262144,
                                             "max_completion_tokens": 16384},
                "price_ceilings_usd_per_mtok": {"prompt": "0.09", "completion": "0.55"},
                "cohort": {"ids": ids, "primary_ids": [x for x in ids if x != "X14"], "diagnostic_ids": ["X14"],
                           "saved_arm_ids": list(saved_ids), "labels": labels},
                "config": {"replicates": 3, "retry_allowance_total": 10, "max_attempts_per_request": 2},
                "requests": reqs,
                "plan_totals": {"n_probes": n_ids, "n_documents_current": 3 * n_ids, "n_documents_saved": 3 * len(saved_ids),
                                "sum_reservations_usd": str(sum_res), "max_document_reservation_usd": str(max_doc),
                                "conservative_total_usd": str(sum_res + 10 * max_doc)},
                "pilot": {"probe": "probe-X12", "document": "doc-saved-X12-r1"},
                "hashes_file": "audit/hashes.json", "hashes_sha256": ro.sha256_file(hp)}
    mp = os.path.join(run, "manifest.json")
    open(mp, "w").write(json.dumps(manifest, indent=1))
    auth = {"authorization_id": "TEST-AUTH", "cap_usd": cap, "model": MODEL, "endpoint_slug": "deepinfra/fp8",
            "provider_name": "DeepInfra", "price_ceilings_usd_per_mtok": {"prompt": "0.09", "completion": "0.55"},
            "replicates": 3, "retry_allowance": 10, "cohort_ids": ids, "saved_arm_ids": list(saved_ids),
            "diagnostic_ids": ["X14"], "pilot": manifest["pilot"], "manifest_sha256": ro.sha256_file(mp),
            "ledger_path": "runs/TEST-AUTH/ledger.jsonl"}
    ap = os.path.join(base, "authorization.json")
    json.dump(auth, open(ap, "w"))
    return run, ap, manifest


ENDPOINTS_OK = {"data": {"endpoints": [{"tag": "deepinfra/fp8", "provider_name": "DeepInfra", "name": "DeepInfra | x",
                                        "context_length": 262144, "max_completion_tokens": 16384, "quantization": "fp8",
                                        "pricing": {"prompt": "0.00000009", "completion": "0.00000055"}}]}}


def completion(content, prompt_tokens=1000, cost=0.0005, model=MODEL, provider="DeepInfra", finish="stop",
               gen_id="gen-1", usage=True):
    o = {"id": gen_id, "model": model, "provider": provider,
         "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": finish}]}
    if usage:
        o["usage"] = {"prompt_tokens": prompt_tokens, "completion_tokens": 50, "cost": cost}
    return o


class Fake:
    """Records sends; serves scripted responses; can crash at chosen points."""

    def __init__(self, responses=None, endpoints=ENDPOINTS_OK, gen=None, crash=None):
        self.sends, self.responses, self.endpoints_obj = [], list(responses or []), endpoints
        self.gen, self.crash = gen, crash

    def endpoints(self):
        if self.endpoints_obj is None:
            return ro.Response(500, b"")
        return ro.Response(200, json.dumps(self.endpoints_obj).encode())

    def send(self, body):
        if self.crash == "before_send":
            raise RuntimeError("crash before send")
        self.sends.append(body)
        if self.crash == "after_send":
            raise RuntimeError("crash after send, before response")
        r = self.responses.pop(0)
        if isinstance(r, ro.Response):
            return r
        return ro.Response(200, json.dumps(r).encode())

    def generation(self, gen_id):
        if self.gen is None:
            return ro.Response(404, b"")
        return ro.Response(200, json.dumps({"data": self.gen}).encode())


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="exp04-test-")
        self.run, self.auth_path, self.manifest = make_fixture(self.tmp)
        self.orig_here = ro.HERE
        ro.HERE = self.tmp            # ledgers live under <HERE>/runs/<auth>/

    def tearDown(self):
        ro.HERE = self.orig_here
        shutil.rmtree(self.tmp, ignore_errors=True)

    def runner(self, fake, run_dir=None):
        r = ro.Runner(run_dir or self.run, fake, auth_path=self.auth_path, sleep=lambda s: None)
        r.__enter__()
        self.addCleanup(r.__exit__, None, None, None)
        return r

    def ready(self, fake, run_dir=None):
        r = self.runner(fake, run_dir)
        r.preflight_checks()
        r.live_price_check()
        return r

    def review_probe(self, r, xid):
        out = r.dispatch(f"probe-{xid}")
        self.assertEqual(out["status"], "valid")
        st = r.ledger.state()
        att = st["attempts"][f"probe-{xid}"][-1]
        path = os.path.join(self.run, "probe_review.json")
        rev = json.load(open(path)) if os.path.exists(path) else {}
        rev[xid] = {"reviewed_at": ro.now(), "probe_attempt_id": att["attempt_id"], "flags": [], "notes": "test"}
        json.dump(rev, open(path, "w"))

    def pass_pilot(self, r):
        self.review_probe(r, "X12")
        out = r.dispatch("doc-saved-X12-r1")
        self.assertEqual(out["status"], "valid")
        json.dump({"verdict": "pass", "document_attempt_id": out["attempt_id"], "reviewed_at": ro.now()},
                  open(os.path.join(self.run, "pilot_review.json"), "w"))


PROBE_OK = json.dumps({"claimed_moodys_rating": "A1", "notes": "n"})
DOC_OK = json.dumps(GOOD_OUTPUT)


class G1Authorization(Base):
    def test_missing_authorization_blocks(self):
        os.remove(self.auth_path)
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            ro.Runner(self.run, fake, auth_path=self.auth_path)
        self.assertEqual(fake.sends, [])

    def test_wrong_cap_or_cohort_blocks(self):
        a = json.load(open(self.auth_path))
        a["cohort_ids"] = a["cohort_ids"][:19]
        json.dump(a, open(self.auth_path, "w"))
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            self.runner(fake).preflight_checks()
        self.assertEqual(fake.sends, [])


class G2Cohort(Base):
    def test_incomplete_or_duplicated_plan_blocks(self):
        m = json.load(open(os.path.join(self.run, "manifest.json")))
        m["requests"].append(copy.deepcopy(m["requests"][0]))
        open(os.path.join(self.run, "manifest.json"), "w").write(json.dumps(m, indent=1))
        a = json.load(open(self.auth_path))
        a["manifest_sha256"] = ro.sha256_file(os.path.join(self.run, "manifest.json"))
        json.dump(a, open(self.auth_path, "w"))
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            self.runner(fake).preflight_checks()
        self.assertEqual(fake.sends, [])

    def test_old_in_run_flags_do_not_shrink_the_cohort(self):
        cand = json.load(open(os.path.join(ROOT, "experiments", "03-oos-values-first", "candidates.json")))
        self.assertEqual(sum(not it.get("in_run", True) for it in cand["items"]), 4)
        self.assertEqual(self.manifest["cohort"]["ids"], [it["id"] for it in cand["items"] if it["status"] == "confirmed"])
        self.assertEqual(len({r["request_id"] for r in self.manifest["requests"]}), len(self.manifest["requests"]))

    def test_attempt_limits(self):
        fake = Fake(responses=[completion(PROBE_OK, 150), completion(DOC_OK), completion("not json"), completion("not json")])
        r = self.ready(fake)
        self.pass_pilot(r)
        self.review_probe(r, "X12") if False else None
        self.assertEqual(r.dispatch("doc-current-X12-r1")["status"], "invalid")
        self.assertEqual(r.dispatch("doc-current-X12-r1")["status"], "invalid")
        with self.assertRaises(ro.Refusal):
            r.dispatch("doc-current-X12-r1")
        self.assertEqual(len(fake.sends), 4)


class G3FrozenBytes(Base):
    def test_changed_body_blocks(self):
        p = os.path.join(self.run, "bodies", "doc-current-X01-r1.json")
        open(p, "ab").write(b" ")
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            self.runner(fake).preflight_checks()
        self.assertEqual(fake.sends, [])

    def test_changed_code_blocks(self):
        hp = os.path.join(self.run, "audit", "hashes.json")
        h = json.load(open(hp))
        h["code_and_prompts"]["system/scorecard.py"] = "0" * 64
        json.dump(h, open(hp, "w"))
        m = json.load(open(os.path.join(self.run, "manifest.json")))
        m["hashes_sha256"] = ro.sha256_file(hp)
        open(os.path.join(self.run, "manifest.json"), "w").write(json.dumps(m, indent=1))
        a = json.load(open(self.auth_path))
        a["manifest_sha256"] = ro.sha256_file(os.path.join(self.run, "manifest.json"))
        json.dump(a, open(self.auth_path, "w"))
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            self.runner(fake).preflight_checks()
        self.assertEqual(fake.sends, [])

    def test_manifest_edit_after_authorization_blocks(self):
        m = json.load(open(os.path.join(self.run, "manifest.json")))
        m["config"]["replicates"] = 4
        open(os.path.join(self.run, "manifest.json"), "w").write(json.dumps(m, indent=1))
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            self.runner(fake).preflight_checks()
        self.assertEqual(fake.sends, [])


class G5InputIsolation(Base):
    def test_disallowed_field_blocks(self):
        rid = "doc-current-X01-r1"
        p = os.path.join(self.run, "bodies", f"{rid}.json")
        b = json.loads(open(p, "rb").read())
        b["tools"] = []
        raw = canonical(b)
        open(p, "wb").write(raw)
        m = json.load(open(os.path.join(self.run, "manifest.json")))
        next(r for r in m["requests"] if r["request_id"] == rid)["body_sha256"] = sha(raw)
        open(os.path.join(self.run, "manifest.json"), "w").write(json.dumps(m, indent=1))
        a = json.load(open(self.auth_path))
        a["manifest_sha256"] = ro.sha256_file(os.path.join(self.run, "manifest.json"))
        json.dump(a, open(self.auth_path, "w"))
        fake = Fake()
        with self.assertRaises(ro.Refusal):
            self.runner(fake).preflight_checks()
        self.assertEqual(fake.sends, [])

    def test_real_bodies_if_prepared(self):
        run = os.path.join(self.orig_here, "runs", "EXP04-ARM1-A1")
        if not os.path.exists(os.path.join(run, "manifest.json")):
            self.skipTest("real manifest not prepared")
        m = json.load(open(os.path.join(run, "manifest.json")))
        for r in m["requests"]:
            b = json.loads(open(os.path.join(run, r["body_file"]), "rb").read())
            self.assertEqual(set(b) - ro.ALLOWED_BODY_KEYS, set())
            user = b["messages"][1]["content"]
            self.assertNotIn("label_evidence", user)
            self.assertNotIn("claimed_moodys_rating", user)
            if r["kind"] == "document":
                # every line the redactor removed stays out of the body
                suffix = "-saved" if r["arm"] == "saved" else ""
                removed = json.load(open(os.path.join(run, "audit", "removed_lines", f"{r['issuer_id']}{suffix}.json")))
                for lines in removed.values():
                    for line in lines:
                        if len(line.strip()) >= 40:
                            self.assertNotIn(line, user, f"{r['request_id']}: a removed line is in the body")


class G6Tokens(Base):
    def test_prompt_token_discrepancy_halts(self):
        fake = Fake(responses=[completion(PROBE_OK, 150), completion(DOC_OK, prompt_tokens=500), completion(DOC_OK)])
        r = self.ready(fake)
        self.review_probe(r, "X12")
        out = r.dispatch("doc-saved-X12-r1")
        self.assertEqual(out["status"], "suspect")
        with self.assertRaises(ro.Refusal):
            r.dispatch("doc-saved-X12-r1")
        self.assertEqual(len(fake.sends), 2)
        st = r.ledger.state()
        self.assertEqual(st["committed"], Decimal("0.001"))     # both charges kept, the suspect one included


class G7Prices(Base):
    def test_live_price_increase_blocks(self):
        ep = copy.deepcopy(ENDPOINTS_OK)
        ep["data"]["endpoints"][0]["pricing"]["prompt"] = "0.00000036"
        fake = Fake(endpoints=ep)
        r = self.runner(fake)
        r.preflight_checks()
        with self.assertRaises(ro.Refusal):
            r.live_price_check()
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X12")
        self.assertEqual(fake.sends, [])

    def test_missing_price_blocks(self):
        fake = Fake(endpoints={"data": {"endpoints": []}})
        r = self.runner(fake)
        r.preflight_checks()
        with self.assertRaises(ro.Refusal):
            r.live_price_check()
        self.assertEqual(fake.sends, [])

    def test_exact_cap_arithmetic(self):
        fake = Fake(responses=[completion(PROBE_OK, 150)])
        r = self.ready(fake)
        res = Decimal(r.req["probe-X12"]["reservation_usd"])
        r.ledger.append({"event": "reserve", "attempt_id": "x#a1", "request_id": "doc-current-X01-r1",
                         "reservation_usd": str(r.cap - res)})
        r.ledger.append({"event": "dispatch", "attempt_id": "x#a1", "request_id": "doc-current-X01-r1"})
        r.ledger.append({"event": "reconcile", "attempt_id": "x#a1", "request_id": "doc-current-X01-r1",
                         "charge_usd": str(r.cap - res + Decimal("0.000001"))})
        r.ledger.append({"event": "valid", "attempt_id": "x#a1", "request_id": "doc-current-X01-r1"})
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X12")
        self.assertEqual(fake.sends, [])

    def test_invalid_cost_value_is_unresolved(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, cost=-1)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "unresolved")
        st = r.ledger.state()
        self.assertEqual(st["unresolved"], Decimal(r.req["probe-X12"]["reservation_usd"]))
        self.assertTrue(st["halts"])

    def test_reservation_uses_ceilings_exactly(self):
        r = self.manifest["requests"][0]
        expect = ((Decimal(r["input_bound_tokens"]) * Decimal("0.09") + Decimal(r["max_tokens"]) * Decimal("0.55"))
                  / Decimal(10 ** 6)).quantize(Decimal("0.000001"), rounding="ROUND_UP")
        self.assertEqual(Decimal(r["reservation_usd"]), expect)


class G8CrashResume(Base):
    def test_crash_before_send_reserves_nothing_dispatched(self):
        fake = Fake(crash="before_send")
        r = self.ready(fake)
        with self.assertRaises(RuntimeError):
            r.dispatch("probe-X12")
        st = r.ledger.state()
        self.assertEqual(fake.sends, [])
        self.assertEqual(st["attempts"]["probe-X12"][0]["status"], "dispatched")   # reserved and recorded before the crash
        r.__exit__(None, None, None)                                # the crashed process is gone
        fake2 = Fake(responses=[completion(PROBE_OK, 150)])
        r2 = self.ready(fake2, run_dir=self.run)
        with self.assertRaises(ro.Refusal):                       # an attempt in flight blocks a duplicate
            r2.dispatch("probe-X12")
        self.assertEqual(fake2.sends, [])

    def test_crash_after_send_keeps_reservation_and_blocks_duplicate(self):
        fake = Fake(crash="after_send")
        r = self.ready(fake)
        with self.assertRaises(RuntimeError):
            r.dispatch("probe-X12")
        self.assertEqual(len(fake.sends), 1)
        r.__exit__(None, None, None)
        other = os.path.join(self.tmp, "runs", "OTHER-DIR")
        shutil.copytree(self.run, other)
        fake2 = Fake(responses=[completion(PROBE_OK, 150)])
        r2 = self.ready(fake2, run_dir=other)
        st = r2.ledger.state()
        self.assertEqual(sum(st["open"].values(), Decimal("0")), Decimal(r2.req["probe-X12"]["reservation_usd"]))
        with self.assertRaises(ro.Refusal):
            r2.dispatch("probe-X12")
        self.assertEqual(fake2.sends, [])

    def test_transport_failure_is_unresolved_and_halts(self):
        fake = Fake(responses=[ro.Response(None, b"", "ReadTimeout: x"), completion(PROBE_OK, 150)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "unresolved")
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X12", retry_unresolved=True)          # halted until cleared
        st = r.ledger.state()
        hid = next(iter(st["halts"]))
        r.clear_halt(hid, "reviewed: no generation id, charge kept as unresolved")
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X12")                                  # still needs the explicit decision
        self.assertEqual(r.dispatch("probe-X12", retry_unresolved=True)["status"], "valid")
        st = r.ledger.state()
        self.assertEqual(st["unresolved"], Decimal(r.req["probe-X12"]["reservation_usd"]))
        self.assertEqual(st["extra_attempts"], 1)

    def test_duplicate_completed_request_blocks(self):
        fake = Fake(responses=[completion(PROBE_OK, 150), completion(PROBE_OK, 150)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "valid")
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X12")
        self.assertEqual(len(fake.sends), 1)

    def test_second_process_blocks(self):
        fake = Fake()
        self.runner(fake)
        with self.assertRaises(ro.Refusal):
            self.runner(Fake())
        self.assertEqual(fake.sends, [])

    def test_new_directory_shares_the_cap(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, cost=2.5)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "suspect")   # a charge above its reservation halts
        r.__exit__(None, None, None)
        other = os.path.join(self.tmp, "runs", "NEW-DIR")
        shutil.copytree(self.run, other)
        fake2 = Fake(responses=[completion(DOC_OK)])
        r2 = self.ready(fake2, run_dir=other)
        self.assertEqual(r2.ledger.state()["committed"], Decimal("2.5"))
        st = r2.ledger.state()
        self.assertGreater(st["committed"] + Decimal(r2.req["doc-saved-X12-r1"]["reservation_usd"]), Decimal("2.5"))


class G9Provenance(Base):
    def test_wrong_model_halts_but_charge_is_kept(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, model="other/model", cost=0.003)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "suspect")
        st = r.ledger.state()
        self.assertEqual(st["committed"], Decimal("0.003"))
        self.assertTrue(st["halts"])

    def test_wrong_provider_halts(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, provider="GMICloud")])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "suspect")

    def test_missing_usage_and_generation_is_unresolved(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, usage=False)], gen=None)
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "unresolved")

    def test_missing_usage_reconciled_from_generation(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, usage=False)], gen={"total_cost": 0.0007, "provider_name": "DeepInfra"})
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "suspect")   # no prompt_tokens to check
        self.assertEqual(r.ledger.state()["committed"], Decimal("0.0007"))

    def test_http_error_not_billed_and_retry_once(self):
        fake = Fake(responses=[ro.Response(429, json.dumps({"error": {"message": "rate"}}).encode()), completion(PROBE_OK, 150)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "failed_not_billed")
        st = r.ledger.state()
        self.assertEqual(st["committed"] + st["unresolved"] + sum(st["open"].values(), Decimal("0")), Decimal("0"))
        self.assertEqual(r.dispatch("probe-X12")["status"], "valid")

    def test_length_finish_is_failed_and_halts(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, finish="length")])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "invalid")
        self.assertTrue(r.ledger.state()["halts"])

    def test_malformed_outputs(self):
        for text in ('{"a": 1', '{"claimed_moodys_rating": "A1", "claimed_moodys_rating": "A2", "notes": ""}',
                     '{"claimed_moodys_rating": NaN, "notes": ""}', '{"claimed_moodys_rating": 1, "notes": ""}'):
            fake = Fake(responses=[completion(text, 150, cost=0.0005)])
            with tempfile.TemporaryDirectory() as t2:
                pass
            r = self.ready(fake)
            self.assertEqual(r.dispatch("probe-X12")["status"], "invalid")
            self.assertEqual(r.ledger.state()["committed"], Decimal("0.0005"))
            r.__exit__(None, None, None)
            os.remove(r.ledger.path)

    def test_raw_response_saved_before_parsing(self):
        fake = Fake(responses=[completion("garbage", 150)])
        r = self.ready(fake)
        out = r.dispatch("probe-X12")
        self.assertTrue(os.path.exists(os.path.join(self.run, "responses", f"{out['attempt_id']}.json")))

    def test_document_validation_channels(self):
        bad_bool = copy.deepcopy(GOOD_OUTPUT); bad_bool["figures_usd_m"]["revenue"] = True
        undefined = copy.deepcopy(GOOD_OUTPUT); undefined["figures_usd_m"]["interest"] = 0
        bad_direct = copy.deepcopy(GOOD_OUTPUT); bad_direct["direct_rating"] = "AA"
        ev = ro.evaluate_document_output(bad_bool, SCHEMA)
        self.assertTrue(ev["schema_errors"])
        ev = ro.evaluate_document_output(undefined, SCHEMA)
        self.assertIsNone(ev["pred_scorecard"]); self.assertIn("Undefined", ev["scorecard_failure"]); self.assertEqual(ev["pred_direct"], "Aa2")
        ev = ro.evaluate_document_output(bad_direct, SCHEMA)
        self.assertTrue(ev["schema_errors"])   # enum
        ev = ro.evaluate_document_output(GOOD_OUTPUT, SCHEMA)
        self.assertEqual(ev["pred_scorecard"], scorecard.outcome(scorecard.aggregate(scorecard.build(scorecard.WALMART))))


class G10ProbeSequencing(Base):
    def test_document_blocked_until_probe_reviewed(self):
        fake = Fake(responses=[completion(PROBE_OK, 150), completion(DOC_OK)])
        r = self.ready(fake)
        with self.assertRaises(ro.Refusal):
            r.dispatch("doc-saved-X12-r1")
        self.assertEqual(fake.sends, [])
        self.assertEqual(r.dispatch("probe-X12")["status"], "valid")
        with self.assertRaises(ro.Refusal):                         # completed but not reviewed
            r.dispatch("doc-saved-X12-r1")
        json.dump({"X12": {"reviewed_at": "2000-01-01T00:00:00.000+00:00", "probe_attempt_id": "probe-X12#a1"}},
                  open(os.path.join(self.run, "probe_review.json"), "w"))
        with self.assertRaises(ro.Refusal):                         # review dated before the response
            r.dispatch("doc-saved-X12-r1")
        json.dump({"X12": {"reviewed_at": ro.now(), "probe_attempt_id": "probe-X12#a1"}},
                  open(os.path.join(self.run, "probe_review.json"), "w"))
        self.assertEqual(r.dispatch("doc-saved-X12-r1")["status"], "valid")
        self.assertEqual(len(fake.sends), 2)

    def test_probe_answers_never_enter_bodies(self):
        for r in self.manifest["requests"]:
            b = json.loads(open(os.path.join(self.run, r["body_file"]), "rb").read())
            self.assertNotIn("claimed_moodys_rating", b["messages"][1]["content"])


class G11Reporting(unittest.TestCase):
    def test_golden_experiment03_conversion(self):
        recs = ro.experiment03_records()
        m = ro.metrics(recs, [r["id"] for r in recs])
        sc, d = m["pred_scorecard"]["metrics_on_valid"], m["pred_direct"]["metrics_on_valid"]
        self.assertEqual((sc["n"], sc["exact_rate"], sc["within_1"], sc["mae"]), (7, 0.429, 0.857, 1.143))
        self.assertEqual((d["exact_rate"], d["within_1"], d["mae"]), (0.571, 0.857, 0.571))
        self.assertEqual(sc["mae_persistence"], 0.429)

    def test_persistence_baseline_on_frozen_candidates(self):
        cand = json.load(open(os.path.join(ROOT, "experiments", "03-oos-values-first", "candidates.json")))
        recs = [{"id": it["id"], "label": it["label"], "persistence": it["persistence"], "changed": it["changed"],
                 "pred_scorecard": None, "pred_direct": None} for it in cand["items"]]
        m = ro.metrics(recs, [r["id"] for r in recs])
        p = m["persistence_full_cohort"]
        self.assertEqual((p["n"], p["exact_rate"], p["mae"]), (20, 0.9, 0.15))
        self.assertEqual(m["pred_direct"]["n_valid"], 0)
        p19 = ro.metrics(recs, [r["id"] for r in recs if r["id"] != "X14"])["persistence_full_cohort"]
        self.assertEqual((p19["n"], p19["mae"]), (19, round(1 / 19, 3)))

    def test_direct_only_null_and_failed_rows(self):
        recs = [{"id": "X01", "label": "A2", "persistence": "A2", "changed": False, "pred_scorecard": None, "pred_direct": "A2"},
                {"id": "X02", "label": "A2", "persistence": "A2", "changed": False, "pred_scorecard": None, "pred_direct": None}]
        m = ro.metrics(recs, ["X01", "X02"])
        self.assertEqual(m["pred_direct"]["n_valid"], 1)
        self.assertEqual(m["pred_direct"]["exact_over_planned"], 1)
        self.assertEqual(m["n_planned"], 2)
        self.assertIsNone(m["pred_scorecard"]["metrics_on_valid"])
        self.assertEqual(m["persistence_full_cohort"]["n"], 2)

    def test_consensus_incomplete_and_spread(self):
        mk = lambda sc, d: {"id": "X01", "arm": "current", "label": "A2", "persistence": "A2", "changed": False,
                            "pred_scorecard": sc, "pred_direct": d}
        c = ro.consensus([[mk("A1", "A2")], [mk("A3", "A2")], [mk("A2", "A1")]], ["X01"])[0]
        self.assertEqual((c["pred_scorecard"], c["pred_scorecard_spread"], c["pred_direct"]), ("A2", 2, "A2"))
        c = ro.consensus([[mk("A1", "A2")], [mk(None, "A2")], [mk("A2", "A1")]], ["X01"])[0]
        self.assertIsNone(c["pred_scorecard"]); self.assertIn("incomplete", c["pred_scorecard_consensus"])

    def test_changed_flag_consistency(self):
        cand = json.load(open(os.path.join(ROOT, "experiments", "03-oos-values-first", "candidates.json")))
        for it in cand["items"]:
            self.assertEqual(it["changed"], it["label"] != it["persistence"])


class G12Rollout(Base):
    def test_non_pilot_blocked_before_pilot_verdict(self):
        fake = Fake(responses=[completion(PROBE_OK, 150), completion(DOC_OK), completion(PROBE_OK, 150)])
        r = self.ready(fake)
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X01")
        self.assertEqual(fake.sends, [])
        self.review_probe(r, "X12")
        out = r.dispatch("doc-saved-X12-r1")
        self.assertEqual(out["status"], "valid")
        with self.assertRaises(ro.Refusal):                         # pause after the pair
            r.dispatch("probe-X01")
        json.dump({"verdict": "pass", "document_attempt_id": out["attempt_id"]}, open(os.path.join(self.run, "pilot_review.json"), "w"))
        self.assertEqual(r.dispatch("probe-X01")["status"], "valid")

    def test_plan_fits_cap(self):
        self.assertLessEqual(Decimal(self.manifest["plan_totals"]["conservative_total_usd"]), Decimal("3.00"))


if __name__ == "__main__":
    unittest.main()


class G7SettlementRepairs(Base):
    """Repairs after the 2026-09-13 audit: error responses carrying billing evidence are never
    released, charges above the reservation or the cap halt, and every process checks the price."""

    def test_error_response_with_charge_is_not_released(self):
        body = json.dumps({"error": {"message": "upstream"}, "id": "gen-e", "usage": {"prompt_tokens": 150, "completion_tokens": 10, "cost": 0.01}}).encode()
        fake = Fake(responses=[ro.Response(500, body)], gen={"total_cost": 0.01, "provider_name": "DeepInfra"})
        r = self.ready(fake)
        out = r.dispatch("probe-X12")
        st = r.ledger.state()
        self.assertEqual(out["status"], "invalid")
        self.assertEqual(st["committed"], Decimal("0.01"))
        self.assertEqual(sum(st["open"].values(), Decimal("0")), Decimal("0"))
        self.assertTrue(st["halts"])

    def test_5xx_without_billing_evidence_stays_unresolved(self):
        fake = Fake(responses=[ro.Response(502, json.dumps({"error": {"message": "bad gateway"}}).encode())])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "unresolved")
        st = r.ledger.state()
        self.assertEqual(st["unresolved"], Decimal(r.req["probe-X12"]["reservation_usd"]))
        self.assertTrue(st["halts"])

    def test_4xx_without_billing_evidence_is_released(self):
        fake = Fake(responses=[ro.Response(429, json.dumps({"error": {"message": "rate"}}).encode())])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "failed_not_billed")
        st = r.ledger.state()
        self.assertEqual(st["committed"] + st["unresolved"] + sum(st["open"].values(), Decimal("0")), Decimal("0"))

    def test_charge_above_reservation_halts_but_is_committed(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, cost=0.05)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "suspect")
        st = r.ledger.state()
        self.assertEqual(st["committed"], Decimal("0.05"))
        self.assertTrue(st["halts"])
        with self.assertRaises(ro.Refusal):
            r.dispatch("probe-X01")

    def test_charge_above_cap_halts(self):
        fake = Fake(responses=[completion(PROBE_OK, 150, cost=3.5)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "suspect")
        st = r.ledger.state()
        self.assertEqual(st["committed"], Decimal("3.5"))
        self.assertTrue(st["halts"])

    def test_price_check_required_in_every_process(self):
        fake = Fake(responses=[completion(PROBE_OK, 150)])
        r = self.ready(fake)
        self.assertEqual(r.dispatch("probe-X12")["status"], "valid")
        r.__exit__(None, None, None)
        fake2 = Fake(responses=[completion(PROBE_OK, 150)])
        r2 = self.runner(fake2)
        r2.preflight_checks()                      # no live_price_check in this process
        self.assertTrue(r2.ledger.state()["price_checks"])
        with self.assertRaises(ro.Refusal):
            r2.dispatch("probe-X01")
        self.assertEqual(fake2.sends, [])

    def test_generation_payload_archived(self):
        fake = Fake(responses=[completion(PROBE_OK, 150)], gen={"total_cost": 0.0007, "provider_name": "DeepInfra"})
        r = self.ready(fake)
        out = r.dispatch("probe-X12")
        self.assertTrue(os.path.exists(os.path.join(self.run, "responses", f"{out['attempt_id']}.generation.json")))


class RedactionV2(unittest.TestCase):
    """The Kohl's and Dollar General table cells that survived the original redactor."""

    KOHLS = ("Our financing strategy is to ensure adequate liquidity.\n"
             "As of January 31, 2026, our corporate credit ratings and outlook were as follows:\n"
             "Moody\u2019s\nS&P\nFitch\nCorporate credit\nB2\nB+\nBB-\nOutlook\nStable\nNegative\nNegative\n"
             "The majority of our financing activities generally include proceeds from borrowings.")
    DG = ("Our current credit ratings, as well as future rating agency actions, could affect our cost.\n"
          "\u200b\nRating Agency\n\u200b\nSenior unsecured debt rating\n\u200b\nCommercial paper rating\n\u200b\nOutlook\n"
          "Moody\u2019s\n\u200b\nBaa3\n\u200b\nP-3\n\u200b\nStable outlook\nStandard & Poor\u2019s\n\u200b\nBBB\n\u200b\nA-2\n\u200b\nStable outlook\n\u200b\n"
          "Changes in Cash Flows\nUnless otherwise noted, all references to the 2026 and 2025 periods are to fiscal periods.")

    def test_original_redactor_leaves_the_cells(self):
        import redact
        clean, _ = redact.redact(self.KOHLS)
        self.assertIn("\nB2\n", clean)
        self.assertTrue(redact.rating_fragments(clean))

    def test_v2_removes_the_table_cells_and_keeps_the_prose(self):
        import redact
        for text, cells in ((self.KOHLS, ("B2", "B+", "BB-", "Stable", "Negative", "Corporate credit")),
                            (self.DG, ("Baa3", "P-3", "A-2", "BBB", "Stable outlook", "Commercial paper rating"))):
            clean, removed = redact.redact_v2(text)
            for c in cells:
                self.assertNotIn("\n" + c + "\n", "\n" + clean + "\n", c)
            self.assertEqual(redact.rating_fragments(clean), [])
        clean, _ = redact.redact_v2(self.KOHLS)
        self.assertIn("The majority of our financing activities", clean)
        clean, _ = redact.redact_v2(self.DG)
        self.assertIn("Unless otherwise noted", clean)

    def test_v2_keeps_single_letter_section_labels_and_prose_symbols(self):
        import redact
        text = "Item 1A. Risk Factors\nA\nB\nC\nOur Series A preferred stock and our B2B channel grew.\nWe operate 1,200 stores."
        clean, removed = redact.redact_v2(text)
        self.assertEqual(clean, text)
        self.assertEqual(removed, [])

    def test_cached_filings_of_the_run_have_no_fragments_after_v2(self):
        import redact, run_eval
        run = os.path.join(HERE, "runs", "EXP04-ARM1-A1")
        if not os.path.exists(os.path.join(run, "audit", "hashes.json")):
            self.skipTest("run records not present")
        hashes = json.load(open(os.path.join(run, "audit", "hashes.json")))
        left = {}
        for rel in hashes["primary_documents"]:
            path = os.path.join(ROOT, "evaluation", "companies", rel)
            if not os.path.exists(path):
                self.skipTest("cached filings not present")
            text = run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore"))
            clean, _ = redact.redact_v2(text)
            frags = redact.rating_fragments(clean)
            if frags:
                left[rel] = frags[:2]
        self.assertEqual(left, {})
