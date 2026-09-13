"""
Experiment 04, Arm 1 runner: guarded submission to OpenRouter, resumable collection, scoring.

Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-12. Implements the twelve
acceptance gates of review-codex-2026-09-12.md. Every model request is priced, reserved and
recorded in one authorization-wide ledger before it leaves this machine; nothing is dispatched
without the authorization file, a matching manifest, a live price at or below the approved
ceilings, a reviewed memory probe for the issuer, and room under the cap for the worst case.

    python3 experiments/04-open-weight-cross-section/run_openrouter.py prepare
    python3 experiments/04-open-weight-cross-section/run_openrouter.py gates
    python3 experiments/04-open-weight-cross-section/run_openrouter.py price-check
    python3 experiments/04-open-weight-cross-section/run_openrouter.py submit --pilot-probe
    python3 experiments/04-open-weight-cross-section/run_openrouter.py submit --pilot-document
    python3 experiments/04-open-weight-cross-section/run_openrouter.py submit --probes
    python3 experiments/04-open-weight-cross-section/run_openrouter.py submit --documents
    python3 experiments/04-open-weight-cross-section/run_openrouter.py status
    python3 experiments/04-open-weight-cross-section/run_openrouter.py score

Files under the run directory (gitignored): manifest.json and bodies/ from prepare_inputs.py;
ledger.jsonl (append-only, fsynced), responses/<attempt>.json (raw bytes, saved before any
parsing), probe_review.json and pilot_review.json (written by the reviewer), halts cleared by
`clear-halt` with a recorded note, results/ from `score`.

Attempt lifecycle, as recorded in the ledger: reserve -> dispatch -> one of
  reconcile (charge known, reservation released; then valid | invalid | suspect)
  failed_not_billed (an explicit provider error, reservation released)
  unresolved (no readable outcome: the reservation stays charged and a halt is recorded)
A halt blocks every further dispatch until cleared with a note. Retries: at most two attempts
per request and at most ten attempts beyond the plan, never automatic after an unresolved one.
A parse or schema failure of an otherwise complete response is recorded as invalid with its
charge and does not halt by itself. Repairs after the 2026-09-13 audit: an error response that
carries usage or an id is never released (its charge is reconciled and the run halts, or it
stays unresolved); a 5xx or unreadable outcome stays unresolved; a charge above its reservation
or an exposure above the cap halts; a live price check is required in every process; the raw
generation payloads are archived next to the responses.
"""
import datetime
import fcntl
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from decimal import Decimal, ROUND_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "system"), os.path.join(ROOT, "evaluation", "pipeline"), HERE]
import scorecard      # noqa: E402
import score_run      # noqa: E402

AUTH_FILE = os.path.join(HERE, "authorization.json")
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
GEN_URL = "https://openrouter.ai/api/v1/generation"
ENDPOINTS_URL = "https://openrouter.ai/api/v1/models/qwen/qwen3-235b-a22b-2507/endpoints"
SCALE = score_run.SCALE
ALLOWED_BODY_KEYS = {"model", "messages", "temperature", "seed", "max_tokens", "response_format",
                     "provider", "transforms", "stream"}
FIGURES = ("revenue", "operating_income", "d_and_a", "capex", "interest", "cash", "dividends", "cfo",
           "wc_swing", "debt")


class Refusal(Exception):
    """A guard refused before anything was dispatched."""


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    return sha256_bytes(open(path, "rb").read())


def notch(r):
    return score_run.notch(r)


def api_key():
    key = os.environ.get("OPEN_ROUTER_API_KEY")
    if not key:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith("OPEN_ROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise Refusal("OPEN_ROUTER_API_KEY not available")
    return key


# ----------------------------------------------------------------------------- strict parsing

def parse_strict_json(text):
    """Objects only; duplicate keys, NaN and Infinity are rejected rather than coerced."""
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError(f"duplicate key {k!r}")
            d[k] = v
        return d

    def constant(name):
        raise ValueError(f"non-finite constant {name}")
    obj = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(obj, dict):
        raise ValueError("top-level JSON is not an object")
    return obj


def validate_schema(obj, schema):
    import jsonschema
    cls = jsonschema.validators.validator_for(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in cls(schema).iter_errors(obj)]


def finite_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def evaluate_document_output(obj, schema):
    """Validation before arithmetic; each channel fails independently and visibly."""
    out = {"schema_errors": validate_schema(obj, schema), "pred_scorecard": None, "scorecard_failure": None,
           "aggregate": None, "pred_direct": None, "direct_failure": None}
    if out["schema_errors"]:
        return out
    fig = obj.get("figures_usd_m") or {}
    bad = [k for k in FIGURES if not finite_number(fig.get(k))]
    if bad:
        out["scorecard_failure"] = f"non-finite or non-numeric figures: {bad}"
    else:
        try:
            rows = scorecard.build({**{k: fig[k] for k in FIGURES}, "qualitative": obj["qualitative"]})
            agg = scorecard.aggregate(rows)
            out["aggregate"] = agg
            out["pred_scorecard"] = scorecard.outcome(agg)
        except (ValueError, KeyError, TypeError) as exc:
            out["scorecard_failure"] = f"scorecard: {exc}"
    d = obj.get("direct_rating")
    if notch(d) is None:
        out["direct_failure"] = f"direct rating not on the scale: {d!r}"
    else:
        out["pred_direct"] = d.replace("(P)", "").strip()
    out["figures"] = fig
    out["qualitative"] = obj.get("qualitative")
    out["vs_last_known"] = obj.get("vs_last_known")
    out["fiscal_year_label"] = obj.get("fiscal_year_label")
    return out


# ----------------------------------------------------------------------------- ledger

class Ledger:
    """Append-only JSON lines, fsynced per event, replayed into a state on every read."""

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def append(self, event):
        events = self.events()
        event = {"seq": len(events) + 1, "ts": now(), **event}
        with open(self.path, "a") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return event

    def events(self):
        if not os.path.exists(self.path):
            return []
        return [json.loads(l) for l in open(self.path) if l.strip()]

    def state(self):
        st = {"committed": Decimal("0"), "unresolved": Decimal("0"), "open": {}, "attempts": {},
              "halts": {}, "dispatches": 0, "dispatched_requests": set(), "price_checks": [],
              "authorization_id": None}
        for e in self.events():
            ev, aid, rid = e.get("event"), e.get("attempt_id"), e.get("request_id")
            if ev == "open":
                st["authorization_id"] = e["authorization_id"]
            elif ev == "price_check":
                st["price_checks"].append(e)
            elif ev == "reserve":
                st["open"][aid] = Decimal(e["reservation_usd"])
                st["attempts"].setdefault(rid, []).append({"attempt_id": aid, "status": "reserved",
                                                           "reservation_usd": e["reservation_usd"]})
            elif ev == "dispatch":
                st["dispatches"] += 1
                st["dispatched_requests"].add(rid)
                self._att(st, aid)["status"] = "dispatched"
            elif ev == "failed_not_billed":
                st["open"].pop(aid, None)
                a = self._att(st, aid)
                a.update(status="failed_not_billed", reason=e.get("reason"))
            elif ev == "unresolved":
                st["unresolved"] += st["open"].pop(aid, Decimal("0"))
                a = self._att(st, aid)
                a.update(status="unresolved", reason=e.get("reason"))
            elif ev == "reconcile":
                st["open"].pop(aid, None)
                st["committed"] += Decimal(e["charge_usd"])
                a = self._att(st, aid)
                a.update(status="reconciled", charge_usd=e["charge_usd"], generation_id=e.get("generation_id"))
            elif ev in ("valid", "invalid", "suspect"):
                a = self._att(st, aid)
                a.update(status=ev, reason=e.get("reason"), response_ts=e.get("ts"))
            elif ev == "halt":
                st["halts"][e["halt_id"]] = e
            elif ev == "clear_halt":
                st["halts"].pop(e["halt_id"], None)
        st["completed"] = {rid for rid, atts in st["attempts"].items() if any(a["status"] == "valid" for a in atts)}
        st["extra_attempts"] = st["dispatches"] - len(st["dispatched_requests"])
        return st

    @staticmethod
    def _att(st, aid):
        for atts in st["attempts"].values():
            for a in atts:
                if a["attempt_id"] == aid:
                    return a
        raise KeyError(aid)


# ----------------------------------------------------------------------------- transport

class Response:
    def __init__(self, status, body, error=None):
        self.status, self.body, self.error = status, body, error


class HttpxTransport:
    """The only network path. No automatic retries; timeouts surface as transport errors."""

    def __init__(self, key):
        import httpx
        self.client = httpx.Client(timeout=httpx.Timeout(connect=30.0, read=900.0, write=120.0, pool=30.0),
                                   headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                            "HTTP-Referer": "https://github.com/robert-vetter/credit-rating-system",
                                            "X-Title": "credit-rating-system experiment 04"},
                                   transport=httpx.HTTPTransport(retries=0))

    def _do(self, method, url, content=None):
        import httpx
        try:
            r = self.client.request(method, url, content=content)
            return Response(r.status_code, r.content)
        except httpx.HTTPError as exc:
            return Response(None, b"", f"{type(exc).__name__}: {exc}")

    def send(self, body):
        return self._do("POST", CHAT_URL, body)

    def generation(self, gen_id):
        return self._do("GET", f"{GEN_URL}?id={gen_id}")

    def endpoints(self):
        return self._do("GET", ENDPOINTS_URL)


# ----------------------------------------------------------------------------- runner

class Runner:
    def __init__(self, run_dir, transport, auth_path=AUTH_FILE, sleep=time.sleep):
        self.run_dir = run_dir
        self.transport = transport
        self.sleep = sleep
        if not os.path.exists(auth_path):
            raise Refusal("no authorization file")
        self.auth = json.load(open(auth_path))
        self.manifest_path = os.path.join(run_dir, "manifest.json")
        if not os.path.exists(self.manifest_path):
            raise Refusal("no manifest in the run directory")
        self.manifest = json.load(open(self.manifest_path))
        self.req = {r["request_id"]: r for r in self.manifest["requests"]}
        # the ledger location follows the authorization, never the run directory
        self.ledger = Ledger(os.path.join(HERE, self.auth["ledger_path"]))
        self.cap = Decimal(self.auth["cap_usd"])
        self.lock = None
        self.price_checked = False      # a live price check is required in every process, not once per ledger

    # ---- locking ----
    def __enter__(self):
        os.makedirs(os.path.dirname(self.ledger.path), exist_ok=True)
        self.lock = open(os.path.join(os.path.dirname(self.ledger.path), ".lock"), "w")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise Refusal("another process holds the ledger lock")
        return self

    def __exit__(self, *exc):
        if self.lock:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
            self.lock = None

    # ---- G1 to G3 ----
    def preflight_checks(self):
        a, m = self.auth, self.manifest
        msha = sha256_file(self.manifest_path)
        if a.get("manifest_sha256") != msha:
            raise Refusal(f"manifest {msha[:12]} is not the authorized manifest {str(a.get('manifest_sha256'))[:12]}")
        if a.get("authorization_id") != a.get("ledger_path", "").split("/")[1]:
            raise Refusal("ledger path is not bound to the authorization id")
        for k in ("model",):
            if a[k] != m[k]:
                raise Refusal(f"authorization {k} differs from manifest")
        if a["endpoint_slug"] != m["endpoint"]["slug"] or a["provider_name"] != m["endpoint"]["provider_name"]:
            raise Refusal("authorized endpoint differs from manifest")
        if a["price_ceilings_usd_per_mtok"] != m["price_ceilings_usd_per_mtok"]:
            raise Refusal("price ceilings differ")
        if a["cohort_ids"] != m["cohort"]["ids"] or a["saved_arm_ids"] != m["cohort"]["saved_arm_ids"] \
                or a["diagnostic_ids"] != m["cohort"]["diagnostic_ids"]:
            raise Refusal("cohort differs from the authorization")
        if a["replicates"] != m["config"]["replicates"] or a["retry_allowance"] != m["config"]["retry_allowance_total"]:
            raise Refusal("replicates or retry allowance differ")
        if a["pilot"] != m["pilot"]:
            raise Refusal("pilot selection differs")
        if Decimal(m["plan_totals"]["conservative_total_usd"]) > self.cap:
            raise Refusal("conservative plan total exceeds the cap")
        ids = m["cohort"]["ids"]
        expect = {f"probe-{x}" for x in ids} | {f"doc-current-{x}-r{r}" for x in ids for r in (1, 2, 3)} | \
                 {f"doc-saved-{x}-r{r}" for x in m["cohort"]["saved_arm_ids"] for r in (1, 2, 3)}
        rids = [r["request_id"] for r in m["requests"]]
        if len(rids) != len(set(rids)) or set(rids) != expect:
            raise Refusal("request set is not the exact authorized plan")
        if ids != [f"X{i:02d}" for i in range(1, 21)]:
            raise Refusal("cohort is not the 20 confirmed candidates")
        hashes = json.load(open(os.path.join(self.run_dir, m["hashes_file"])))
        if sha256_file(os.path.join(self.run_dir, m["hashes_file"])) != m["hashes_sha256"]:
            raise Refusal("hashes file changed after preparation")
        for f, h in hashes["code_and_prompts"].items():
            if sha256_file(os.path.join(ROOT, f)) != h:
                raise Refusal(f"{f} changed after preparation")
        for f, h in hashes["primary_documents"].items():
            if sha256_file(os.path.join(ROOT, "evaluation", "companies", f)) != h:
                raise Refusal(f"document {f} changed after preparation")
        for r in m["requests"]:
            body = open(os.path.join(self.run_dir, r["body_file"]), "rb").read()
            if sha256_bytes(body) != r["body_sha256"]:
                raise Refusal(f"body of {r['request_id']} changed after preparation")
            obj = json.loads(body)
            if set(obj) - ALLOWED_BODY_KEYS or "tools" in obj or "plugins" in obj:
                raise Refusal(f"body of {r['request_id']} carries a field outside the allowlist")
            if obj["provider"]["order"] != [a["endpoint_slug"]] or obj["provider"]["allow_fallbacks"] is not False:
                raise Refusal(f"body of {r['request_id']} is not pinned to the authorized endpoint")
            if r["input_bound_tokens"] + r["max_tokens"] > m["endpoint"]["context_length"]:
                raise Refusal(f"{r['request_id']} exceeds the context allowance")
        st = self.ledger.state()
        if st["authorization_id"] not in (None, a["authorization_id"]):
            raise Refusal("ledger belongs to another authorization")
        if st["authorization_id"] is None:
            self.ledger.append({"event": "open", "authorization_id": a["authorization_id"], "manifest_sha256": msha,
                                "cap_usd": a["cap_usd"]})
        return True

    # ---- G7 live price ----
    def live_price_check(self):
        r = self.transport.endpoints()
        if r.error or r.status != 200:
            raise Refusal(f"endpoint listing unavailable: {r.error or r.status}")
        try:
            data = json.loads(r.body)["data"]
            ep = next(e for e in data["endpoints"] if e.get("tag") == self.auth["endpoint_slug"])
            p_in = Decimal(str(ep["pricing"]["prompt"])) * Decimal(10 ** 6)
            p_out = Decimal(str(ep["pricing"]["completion"])) * Decimal(10 ** 6)
        except (KeyError, StopIteration, ValueError, TypeError) as exc:
            raise Refusal(f"authorized endpoint or its prices missing from the live listing: {exc}")
        if not (p_in.is_finite() and p_out.is_finite()) or p_in < 0 or p_out < 0:
            raise Refusal("invalid live prices")
        ceil = self.auth["price_ceilings_usd_per_mtok"]
        if p_in > Decimal(ceil["prompt"]) or p_out > Decimal(ceil["completion"]):
            raise Refusal(f"live price {p_in}/{p_out} per MTok exceeds the ceilings {ceil}")
        need = max(r_["input_bound_tokens"] + r_["max_tokens"] for r_ in self.manifest["requests"])
        if int(ep.get("context_length") or 0) < need:
            raise Refusal("live context length below the largest request")
        if int(ep.get("max_completion_tokens") or 0) < max(r_["max_tokens"] for r_ in self.manifest["requests"]):
            raise Refusal("live completion limit below max_tokens")
        if ep.get("quantization") not in ("fp8",):
            raise Refusal(f"live quantization {ep.get('quantization')} is not fp8")
        self.ledger.append({"event": "price_check", "prompt_per_mtok": str(p_in), "completion_per_mtok": str(p_out),
                            "context_length": ep.get("context_length"), "provider_name": ep.get("provider_name"),
                            "quantization": ep.get("quantization"), "endpoint_name": ep.get("name")})
        self.price_checked = True
        return {"prompt": p_in, "completion": p_out}

    # ---- G10, G12 and the other pre-dispatch guards ----
    def _reviewed_probe(self, issuer):
        path = os.path.join(self.run_dir, "probe_review.json")
        rev = json.load(open(path)).get(issuer) if os.path.exists(path) else None
        st = self.ledger.state()
        valid = [a for a in st["attempts"].get(f"probe-{issuer}", []) if a["status"] == "valid"]
        if not valid:
            return False, "probe not completed"
        if not rev or not rev.get("reviewed_at"):
            return False, "probe not reviewed"
        if rev.get("probe_attempt_id") != valid[-1]["attempt_id"] or rev["reviewed_at"] < valid[-1]["response_ts"]:
            return False, "probe review does not refer to the completed probe response"
        return True, None

    def _pilot_passed(self):
        path = os.path.join(self.run_dir, "pilot_review.json")
        if not os.path.exists(path):
            return False
        rev = json.load(open(path))
        st = self.ledger.state()
        pair = (self.manifest["pilot"]["probe"], self.manifest["pilot"]["document"])
        return rev.get("verdict") == "pass" and all(p in st["completed"] for p in pair) \
            and rev.get("document_attempt_id") in {a["attempt_id"] for a in st["attempts"].get(pair[1], [])}

    def guards(self, request_id, retry_unresolved=False):
        st = self.ledger.state()
        if st["authorization_id"] != self.auth["authorization_id"]:
            raise Refusal("ledger not opened under this authorization (run preflight_checks)")
        if not self.price_checked:
            raise Refusal("no live price check in this process (a recorded check from an earlier process does not count)")
        if request_id not in self.req:
            raise Refusal(f"{request_id} is not in the plan")
        if st["halts"]:
            raise Refusal("halted: " + "; ".join(f"{h['halt_id']}: {h['reason']}" for h in st["halts"].values()))
        if request_id in st["completed"]:
            raise Refusal(f"{request_id} already has a valid response")
        atts = st["attempts"].get(request_id, [])
        if any(a["status"] in ("reserved", "dispatched") for a in atts):
            raise Refusal(f"{request_id} has an attempt in flight or unreconciled")
        if any(a["status"] == "unresolved" for a in atts) and not retry_unresolved:
            raise Refusal(f"{request_id} has an unresolved attempt; a retry needs an explicit decision")
        if len(atts) >= self.manifest["config"]["max_attempts_per_request"]:
            raise Refusal(f"{request_id} reached the per-request attempt limit")
        if atts and st["extra_attempts"] >= self.manifest["config"]["retry_allowance_total"]:
            raise Refusal("the pooled retry allowance is exhausted")
        req = self.req[request_id]
        pair = (self.manifest["pilot"]["probe"], self.manifest["pilot"]["document"])
        if request_id not in pair and not self._pilot_passed():
            raise Refusal("the inspected pilot has not passed; only the pilot pair may run")
        if req["kind"] == "document":
            ok, why = self._reviewed_probe(req["issuer_id"])
            if not ok:
                raise Refusal(f"{request_id}: {why}")
        res = Decimal(req["reservation_usd"])
        if st["committed"] + st["unresolved"] + sum(st["open"].values(), Decimal("0")) + res > self.cap:
            raise Refusal(f"cap: committed {st['committed']} + unresolved {st['unresolved']} + reservation {res} > {self.cap}")
        return req, res

    # ---- the dispatch path ----
    def dispatch(self, request_id, retry_unresolved=False):
        req, res = self.guards(request_id, retry_unresolved)
        body = open(os.path.join(self.run_dir, req["body_file"]), "rb").read()
        if sha256_bytes(body) != req["body_sha256"]:
            raise Refusal("body hash mismatch at dispatch")
        st = self.ledger.state()
        aid = f"{request_id}#a{len(st['attempts'].get(request_id, [])) + 1}"
        self.ledger.append({"event": "reserve", "attempt_id": aid, "request_id": request_id, "reservation_usd": str(res)})
        self.ledger.append({"event": "dispatch", "attempt_id": aid, "request_id": request_id,
                            "body_sha256": req["body_sha256"]})
        r = self.transport.send(body)
        if r.error is not None:
            self.ledger.append({"event": "unresolved", "attempt_id": aid, "request_id": request_id,
                                "reason": f"no HTTP response: {r.error}"})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                "reason": "transport failure without a response; billing unknown"})
            return {"attempt_id": aid, "status": "unresolved"}
        os.makedirs(os.path.join(self.run_dir, "responses"), exist_ok=True)
        with open(os.path.join(self.run_dir, "responses", f"{aid}.json"), "wb") as f:
            f.write(json.dumps({"attempt_id": aid, "request_id": request_id, "status": r.status, "received_at": now(),
                                "body_utf8": r.body.decode("utf-8", "replace")}).encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())
        return self._settle(aid, request_id, req, r)

    def _settle(self, aid, request_id, req, r):
        try:
            obj = json.loads(r.body)
        except ValueError:
            obj = None
        is_error = r.status != 200 or not isinstance(obj, dict) or "error" in obj or not obj.get("choices")
        if is_error:
            msg = (obj or {}).get("error") if isinstance(obj, dict) else r.body[:200].decode("utf-8", "replace")
            evidence = isinstance(obj, dict) and (bool(obj.get("usage")) or bool(obj.get("id")))
            if isinstance(obj, dict) and r.status is not None and 400 <= r.status < 500 and not evidence:
                # an explicit client-side rejection without any billing evidence: not billed
                self.ledger.append({"event": "failed_not_billed", "attempt_id": aid, "request_id": request_id,
                                    "reason": f"HTTP {r.status}: {json.dumps(msg)[:300]}"})
                if r.status in (400, 401, 402, 403, 422):
                    self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                        "reason": f"request rejected with HTTP {r.status}; protocol review needed"})
                return {"attempt_id": aid, "status": "failed_not_billed"}
            # ambiguous (a 5xx, an unreadable body, or an error that carries usage or an id): never release
            gen = self._generation(obj.get("id"), aid) if isinstance(obj, dict) and obj.get("id") else None
            usage = (obj.get("usage") if isinstance(obj, dict) else None) or {}
            charges = [Decimal(str(c)) for c in (usage.get("cost"), (gen or {}).get("total_cost"))
                       if isinstance(c, (int, float)) and not isinstance(c, bool) and math.isfinite(c) and c >= 0]
            if charges:
                charge = max(charges).quantize(Decimal("0.000001"), rounding=ROUND_UP)
                self.ledger.append({"event": "reconcile", "attempt_id": aid, "request_id": request_id,
                                    "charge_usd": str(charge), "usage_cost": usage.get("cost"),
                                    "generation_total_cost": (gen or {}).get("total_cost"), "generation_id": obj.get("id"),
                                    "error_response": True})
                self.ledger.append({"event": "invalid", "attempt_id": aid, "request_id": request_id,
                                    "reason": f"error response with a charge, HTTP {r.status}: {json.dumps(msg)[:200]}"})
                self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                    "reason": "an error response carried a charge; review before continuing"})
                return {"attempt_id": aid, "status": "invalid"}
            self.ledger.append({"event": "unresolved", "attempt_id": aid, "request_id": request_id,
                                "reason": f"ambiguous outcome, HTTP {r.status}: {json.dumps(msg)[:200]}"})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                "reason": "ambiguous error outcome; billing unknown"})
            return {"attempt_id": aid, "status": "unresolved"}
        usage = obj.get("usage") or {}
        gen_id = obj.get("id")
        cost = usage.get("cost")
        gen = self._generation(gen_id, aid) if gen_id else None
        charges = [Decimal(str(c)) for c in (cost, (gen or {}).get("total_cost")) if isinstance(c, (int, float))
                   and not isinstance(c, bool) and math.isfinite(c) and c >= 0]
        if not charges:
            self.ledger.append({"event": "unresolved", "attempt_id": aid, "request_id": request_id,
                                "reason": "no readable charge in the response or the generation record"})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid, "reason": "billing unknown"})
            return {"attempt_id": aid, "status": "unresolved"}
        charge = max(charges).quantize(Decimal("0.000001"), rounding=ROUND_UP)
        choice = (obj.get("choices") or [{}])[0]
        self.ledger.append({"event": "reconcile", "attempt_id": aid, "request_id": request_id, "charge_usd": str(charge),
                            "usage_cost": cost, "generation_total_cost": (gen or {}).get("total_cost"),
                            "generation_id": gen_id, "prompt_tokens": usage.get("prompt_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "native_prompt_tokens": (gen or {}).get("native_tokens_prompt"),
                            "native_completion_tokens": (gen or {}).get("native_tokens_completion"),
                            "model": obj.get("model"), "provider": obj.get("provider") or (gen or {}).get("provider_name"),
                            "finish_reason": choice.get("finish_reason"),
                            "native_finish_reason": choice.get("native_finish_reason")})
        # the actual charge against its reservation and the cap (audit of 2026-09-13)
        st_now = self.ledger.state()
        exposure = st_now["committed"] + st_now["unresolved"] + sum(st_now["open"].values(), Decimal("0"))
        if charge > Decimal(req["reservation_usd"]) or exposure > self.cap:
            why = (f"charge {charge} above its reservation {req['reservation_usd']}" if charge > Decimal(req["reservation_usd"])
                   else f"exposure {exposure} above the cap {self.cap}")
            self.ledger.append({"event": "suspect", "attempt_id": aid, "request_id": request_id, "reason": why})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid, "reason": why})
            return {"attempt_id": aid, "status": "suspect"}
        # provenance
        provider = obj.get("provider") or (gen or {}).get("provider_name")
        if obj.get("model") != self.auth["model"] or (provider or "").lower() != self.auth["provider_name"].lower():
            self.ledger.append({"event": "suspect", "attempt_id": aid, "request_id": request_id,
                                "reason": f"provenance: model {obj.get('model')!r} provider {provider!r}"})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                "reason": "served model or provider is not the authorized one"})
            return {"attempt_id": aid, "status": "suspect"}
        # token accounting
        pt = usage.get("prompt_tokens")
        lo, hi = req["expected_prompt_tokens"]
        if not isinstance(pt, int) or isinstance(pt, bool) or pt < lo or pt > hi:
            kind = "suspected truncation" if isinstance(pt, int) and pt < lo else "unexplained prompt token count"
            self.ledger.append({"event": "suspect", "attempt_id": aid, "request_id": request_id,
                                "reason": f"{kind}: reported {pt}, expected {lo} to {hi}"})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                "reason": f"{kind} on {request_id}"})
            return {"attempt_id": aid, "status": "suspect"}
        if choice.get("finish_reason") != "stop":
            self.ledger.append({"event": "invalid", "attempt_id": aid, "request_id": request_id,
                                "reason": f"finish_reason {choice.get('finish_reason')!r}"})
            self.ledger.append({"event": "halt", "halt_id": f"halt-{aid}", "attempt_id": aid,
                                "reason": f"output did not finish with stop on {request_id}"})
            return {"attempt_id": aid, "status": "invalid"}
        content = (choice.get("message") or {}).get("content")
        try:
            parsed = parse_strict_json(content if isinstance(content, str) else "")
        except ValueError as exc:
            self.ledger.append({"event": "invalid", "attempt_id": aid, "request_id": request_id, "reason": f"parse: {exc}"})
            return {"attempt_id": aid, "status": "invalid"}
        schema = json.loads(open(os.path.join(self.run_dir, req["body_file"]), "rb").read())["response_format"]["json_schema"]["schema"]
        if req["kind"] == "document":
            ev = evaluate_document_output(parsed, schema)
            if ev["schema_errors"]:
                self.ledger.append({"event": "invalid", "attempt_id": aid, "request_id": request_id,
                                    "reason": f"schema: {ev['schema_errors'][:3]}"})
                return {"attempt_id": aid, "status": "invalid"}
            self.ledger.append({"event": "valid", "attempt_id": aid, "request_id": request_id,
                                "pred_scorecard": ev["pred_scorecard"], "scorecard_failure": ev["scorecard_failure"],
                                "aggregate": ev["aggregate"], "pred_direct": ev["pred_direct"],
                                "direct_failure": ev["direct_failure"]})
            return {"attempt_id": aid, "status": "valid", **ev}
        errs = validate_schema(parsed, schema)
        if errs:
            self.ledger.append({"event": "invalid", "attempt_id": aid, "request_id": request_id, "reason": f"schema: {errs[:3]}"})
            return {"attempt_id": aid, "status": "invalid"}
        self.ledger.append({"event": "valid", "attempt_id": aid, "request_id": request_id,
                            "claimed_moodys_rating": parsed.get("claimed_moodys_rating")})
        return {"attempt_id": aid, "status": "valid", "parsed": parsed}

    def _generation(self, gen_id, aid=None):
        for _ in range(6):
            r = self.transport.generation(gen_id)
            if r.error is None and r.status == 200:
                if aid:      # archive the raw generation payload next to the response (audit of 2026-09-13)
                    os.makedirs(os.path.join(self.run_dir, "responses"), exist_ok=True)
                    with open(os.path.join(self.run_dir, "responses", f"{aid}.generation.json"), "wb") as f:
                        f.write(r.body)
                        f.flush()
                        os.fsync(f.fileno())
                try:
                    return json.loads(r.body).get("data") or {}
                except ValueError:
                    return None
            if r.status in (404,):
                self.sleep(2)
                continue
            break
        return None

    def clear_halt(self, halt_id, note):
        st = self.ledger.state()
        if halt_id not in st["halts"]:
            raise Refusal(f"{halt_id} is not an active halt")
        self.ledger.append({"event": "clear_halt", "halt_id": halt_id, "note": note})


# ----------------------------------------------------------------------------- scoring

def load_valid_attempts(run_dir, ledger):
    st = ledger.state()
    manifest = json.load(open(os.path.join(run_dir, "manifest.json")))
    req = {r["request_id"]: r for r in manifest["requests"]}
    rows = []
    for rid, atts in st["attempts"].items():
        r = req[rid]
        for a in atts:
            rec = {"request_id": rid, "attempt_id": a["attempt_id"], "kind": r["kind"], "arm": r["arm"],
                   "issuer_id": r["issuer_id"], "slug": r["slug"], "replicate": r["replicate"],
                   "status": a["status"], "reason": a.get("reason"), "charge_usd": a.get("charge_usd")}
            if a["status"] == "valid":
                raw = json.load(open(os.path.join(run_dir, "responses", f"{a['attempt_id']}.json")))
                obj = json.loads(raw["body_utf8"])
                content = obj["choices"][0]["message"]["content"]
                parsed = parse_strict_json(content)
                if r["kind"] == "document":
                    schema = json.loads(open(os.path.join(run_dir, r["body_file"]), "rb").read())["response_format"]["json_schema"]["schema"]
                    rec.update(evaluate_document_output(parsed, schema))
                    rec["parsed"] = parsed
                else:
                    rec["parsed"] = parsed
                rec["usage"] = obj.get("usage")
            rows.append(rec)
    return manifest, rows, st


def flat_records(manifest, rows, arm, replicate):
    labels = manifest["cohort"]["labels"]
    out = []
    for xid in manifest["cohort"]["ids"] if arm == "current" else manifest["cohort"]["saved_arm_ids"]:
        lab = labels[xid]
        valid = [r for r in rows if r["arm"] == arm and r["issuer_id"] == xid and r["replicate"] == replicate
                 and r["status"] == "valid"]
        rec = {"id": xid, "arm": arm, "replicate": replicate, "label": lab["label"], "persistence": lab["persistence"],
               "changed": lab["changed"], "pred_scorecard": None, "pred_direct": None, "attempted": bool(
                   [r for r in rows if r["arm"] == arm and r["issuer_id"] == xid and r["replicate"] == replicate])}
        if valid:
            v = valid[-1]
            rec.update(pred_scorecard=v["pred_scorecard"], pred_direct=v["pred_direct"],
                       scorecard_failure=v["scorecard_failure"], direct_failure=v["direct_failure"],
                       aggregate=v["aggregate"], figures=v["figures"], qualitative=v["qualitative"],
                       fiscal_year_label=v["fiscal_year_label"], vs_last_known=v["vs_last_known"])
        out.append(rec)
    return out


def consensus(records_by_rep, ids):
    """Median notch across three valid ratings per channel; fewer than three is incomplete."""
    out = []
    for xid in ids:
        recs = [next(r for r in reps if r["id"] == xid) for reps in records_by_rep]
        base = {k: recs[0][k] for k in ("id", "arm", "label", "persistence", "changed")}
        base["replicate"] = "consensus"
        for ch in ("pred_scorecard", "pred_direct"):
            ns = [notch(r[ch]) for r in recs if notch(r[ch]) is not None]
            if len(ns) == len(records_by_rep) == 3:
                base[ch] = SCALE[int(statistics.median(ns))]
                base[ch + "_spread"] = max(ns) - min(ns)
            else:
                base[ch] = None
                base[ch + "_consensus"] = f"incomplete: {len(ns)} of 3 valid"
        out.append(base)
    return out


def metrics(records, ids):
    """Per channel: coverage and score_run metrics on the valid subset, with persistence on the
    full cohort and on the same subset. No answer never becomes persistence."""
    rows = [r for r in records if r["id"] in ids]
    out = {"n_planned": len(rows), "n_attempted": sum(r.get("attempted", True) for r in rows)}
    for ch in ("pred_scorecard", "pred_direct"):
        valid = [r for r in rows if notch(r[ch]) is not None]
        out[ch] = {"n_valid": len(valid), "exact_over_planned": sum(notch(r[ch]) == notch(r["label"]) for r in valid),
                   "error_sum": sum(abs(notch(r[ch]) - notch(r["label"])) for r in valid),
                   "persistence_on_valid": {"exact": sum(notch(r["persistence"]) == notch(r["label"]) for r in valid),
                                            "error_sum": sum(abs(notch(r["persistence"]) - notch(r["label"])) for r in valid)},
                   "metrics_on_valid": score_run.score_channel(valid, ch) if valid else None}
    pers = [{**r, "pred_persistence": r["persistence"]} for r in rows]
    out["persistence_full_cohort"] = score_run.score_channel(pers, "pred_persistence")
    out["persistence_full_cohort"]["error_sum"] = sum(abs(notch(r["persistence"]) - notch(r["label"])) for r in rows)
    return out


def spread_table(records_by_rep, ids):
    out = {}
    for xid in ids:
        recs = [next(r for r in reps if r["id"] == xid) for reps in records_by_rep]
        entry = {}
        for ch in ("pred_scorecard", "pred_direct"):
            vals = [r[ch] for r in recs]
            ns = [notch(v) for v in vals if notch(v) is not None]
            entry[ch] = {"ratings": vals, "spread_notches": (max(ns) - min(ns)) if ns else None}
        figs = [r.get("figures") or {} for r in recs]
        entry["figure_ranges"] = {k: [min(f[k] for f in figs if finite_number(f.get(k))), max(f[k] for f in figs if finite_number(f.get(k)))]
                                  for k in FIGURES if any(finite_number(f.get(k)) for f in figs)}
        entry["fiscal_year_labels"] = [r.get("fiscal_year_label") for r in recs]
        quals = [r.get("qualitative") for r in recs if r.get("qualitative")]
        entry["qualitative_identical"] = len(quals) == 3 and all(q == quals[0] for q in quals)
        out[xid] = entry
    return out


def experiment03_records():
    """The corrected Opus outputs converted to the flat shape (offline review rows)."""
    audit = json.load(open(os.path.join(ROOT, "experiments", "03-oos-values-first", "runs",
                                        "offline-review-2026-09-12", "audit.json")))
    return [{"id": r["id"], "arm": "opus46-saved", "replicate": 1, "label": r["label"], "persistence": r["persistence"],
             "changed": r["changed"], "pred_scorecard": r["corrected_scorecard"], "pred_direct": r["direct"],
             "attempted": True} for r in audit["rows"]]


def score(run_dir):
    ledger = Ledger(os.path.join(HERE, json.load(open(AUTH_FILE))["ledger_path"]))
    manifest, rows, st = load_valid_attempts(run_dir, ledger)
    out_dir = os.path.join(run_dir, "results")
    os.makedirs(out_dir, exist_ok=True)
    json.dump(rows, open(os.path.join(out_dir, "attempts.json"), "w"), indent=1, ensure_ascii=False)
    ids = manifest["cohort"]["ids"]
    primary, saved = manifest["cohort"]["primary_ids"], manifest["cohort"]["saved_arm_ids"]
    diag = manifest["cohort"]["diagnostic_ids"]
    result = {"spend": {"committed_usd": str(st["committed"]), "unresolved_usd": str(st["unresolved"]),
                        "dispatches": st["dispatches"], "extra_attempts": st["extra_attempts"]},
              "attempt_status_counts": {}, "arms": {}}
    for r in rows:
        result["attempt_status_counts"][r["status"]] = result["attempt_status_counts"].get(r["status"], 0) + 1
    for arm, arm_ids in (("current", ids), ("saved", saved)):
        reps = [flat_records(manifest, rows, arm, k) for k in (1, 2, 3)]
        for k, recs in enumerate(reps, 1):
            json.dump(recs, open(os.path.join(out_dir, f"results_{arm}_r{k}.json"), "w"), indent=1)
        cons = consensus(reps, arm_ids)
        json.dump(cons, open(os.path.join(out_dir, f"results_{arm}_consensus.json"), "w"), indent=1)
        cohorts = {"all": arm_ids, "primary_without_diagnostic": [x for x in arm_ids if x not in diag]}
        if arm == "current":
            # post-hoc sensitivities from the 2026-09-13 audit: Kohl's (X07) carried its disclosed
            # rating table; Dollar General (X04) carried its short-term rating and outlook cells
            cohorts["post_hoc_without_X07"] = [x for x in arm_ids if x not in diag and x != "X07"]
            cohorts["post_hoc_without_X07_X04"] = [x for x in arm_ids if x not in diag and x not in ("X07", "X04")]
        result["arms"][arm] = {"replicates": {f"r{k}": {c: metrics(recs, cids) for c, cids in cohorts.items()}
                                              for k, recs in enumerate(reps, 1)},
                               "consensus": {c: metrics(cons, cids) for c, cids in cohorts.items()},
                               "spread": spread_table(reps, arm_ids)}
    opus = experiment03_records()
    result["opus46_corrected_saved_inputs"] = {c: metrics(opus, cids) for c, cids in
                                               (("seven", saved), ("six_without_diagnostic", [x for x in saved if x not in diag]))}
    json.dump(result, open(os.path.join(out_dir, "scores.json"), "w"), indent=1, default=str)
    print(json.dumps({"spend": result["spend"], "attempt_status_counts": result["attempt_status_counts"]}, indent=1))
    return result


# ----------------------------------------------------------------------------- gates

def gates(run_dir):
    """Runs the acceptance tests against the production dispatch path and the manifest checks,
    and records the evidence next to the manifest."""
    test = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_runner"], cwd=HERE,
                          capture_output=True, text=True)
    manifest = json.load(open(os.path.join(run_dir, "manifest.json")))
    checks = {}
    tot = manifest["plan_totals"]
    checks["G2_counts"] = (tot["n_probes"], tot["n_documents_current"], tot["n_documents_saved"]) == (20, 60, 21)
    checks["G6_context"] = all(r["input_bound_tokens"] + r["max_tokens"] <= manifest["endpoint"]["context_length"]
                               for r in manifest["requests"])
    checks["G7_reservations_exact"] = all(Decimal(r["reservation_usd"]) == (
        (Decimal(r["input_bound_tokens"]) * Decimal(manifest["price_ceilings_usd_per_mtok"]["prompt"])
         + Decimal(r["max_tokens"]) * Decimal(manifest["price_ceilings_usd_per_mtok"]["completion"])) / Decimal(10 ** 6)
    ).quantize(Decimal("0.000001"), rounding=ROUND_UP) for r in manifest["requests"])
    checks["G12_plan_fits_cap"] = os.path.exists(AUTH_FILE) and Decimal(tot["conservative_total_usd"]) <= Decimal(
        json.load(open(AUTH_FILE))["cap_usd"])
    checks["G3_bodies_match_manifest"] = all(sha256_file(os.path.join(run_dir, r["body_file"])) == r["body_sha256"]
                                             for r in manifest["requests"])
    checks["G5_body_allowlist"] = all(set(json.loads(open(os.path.join(run_dir, r["body_file"]), "rb").read()))
                                      <= ALLOWED_BODY_KEYS for r in manifest["requests"])
    checks["G4_current_pack_checks"] = all(json.load(open(os.path.join(run_dir, "audit", "current", f"{x}.json")))["pack_checks"] == "all passed"
                                           for x in manifest["cohort"]["ids"])
    checks["G4_legacy_provenance"] = all(json.load(open(os.path.join(run_dir, "audit", "legacy", f"{x}.json")))["all_dated_and_eligible"]
                                         for x in manifest["cohort"]["saved_arm_ids"])
    checks["tests_passed"] = test.returncode == 0
    evidence = {"checked_at": now(), "manifest_sha256": sha256_file(os.path.join(run_dir, "manifest.json")),
                "checks": checks, "all_passed": all(checks.values()),
                "unittest_returncode": test.returncode, "unittest_output_tail": test.stderr[-6000:]}
    os.makedirs(os.path.join(run_dir, "gates"), exist_ok=True)
    json.dump(evidence, open(os.path.join(run_dir, "gates", "gates.json"), "w"), indent=1)
    open(os.path.join(run_dir, "gates", "unittest_output.txt"), "w").write(test.stderr + test.stdout)
    print(json.dumps({k: v for k, v in evidence.items() if k != "unittest_output_tail"}, indent=1))
    return evidence["all_passed"]


# ----------------------------------------------------------------------------- CLI

def selection(manifest, args):
    ids = manifest["cohort"]["ids"]
    if args.pilot_probe:
        return [manifest["pilot"]["probe"]]
    if args.pilot_document:
        return [manifest["pilot"]["document"]]
    if args.request:
        return [args.request]
    if args.probes:
        return [f"probe-{x}" for x in ids]
    if args.documents:
        order = []
        for x in ids:
            order += [f"doc-current-{x}-r{r}" for r in (1, 2, 3)]
            if x in manifest["cohort"]["saved_arm_ids"]:
                order += [f"doc-saved-{x}-r{r}" for r in (1, 2, 3)]
        return order
    raise SystemExit("choose --pilot-probe, --pilot-document, --probes, --documents or --request")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["prepare", "gates", "price-check", "submit", "status", "score", "clear-halt"])
    ap.add_argument("--run-dir", default=os.path.join(HERE, "runs", "EXP04-ARM1-A1"))
    ap.add_argument("--pilot-probe", action="store_true")
    ap.add_argument("--pilot-document", action="store_true")
    ap.add_argument("--probes", action="store_true")
    ap.add_argument("--documents", action="store_true")
    ap.add_argument("--request")
    ap.add_argument("--retry-unresolved", action="store_true")
    ap.add_argument("--halt-id")
    ap.add_argument("--note")
    args = ap.parse_args()
    if args.command == "prepare":
        import prepare_inputs
        prepare_inputs.prepare(args.run_dir)
        return
    if args.command == "gates":
        raise SystemExit(0 if gates(args.run_dir) else 1)
    if args.command == "score":
        score(args.run_dir)
        return
    transport = None if args.command == "status" else HttpxTransport(api_key())
    with Runner(args.run_dir, transport) as run:
        if args.command == "status":
            st = run.ledger.state()
            print(json.dumps({"committed_usd": str(st["committed"]), "unresolved_usd": str(st["unresolved"]),
                              "open_reservations": {k: str(v) for k, v in st["open"].items()},
                              "completed": len(st["completed"]), "dispatches": st["dispatches"],
                              "extra_attempts": st["extra_attempts"], "halts": list(st["halts"].values())}, indent=1))
            return
        if args.command == "clear-halt":
            run.preflight_checks()
            run.clear_halt(args.halt_id, args.note or "")
            return
        run.preflight_checks()
        price = run.live_price_check()
        print(f"live price {price['prompt']}/{price['completion']} per MTok within the ceilings")
        if args.command == "price-check":
            return
        for rid in selection(run.manifest, args):
            st = run.ledger.state()
            if rid in st["completed"]:
                continue
            try:
                out = run.dispatch(rid, retry_unresolved=args.retry_unresolved)
            except Refusal as exc:
                print(f"REFUSED {rid}: {exc}")
                break
            st = run.ledger.state()
            print(f"{now()} {rid} -> {out['status']} {out.get('pred_scorecard') or ''} {out.get('pred_direct') or ''} "
                  f"committed ${st['committed']} unresolved ${st['unresolved']}", flush=True)
            if out["status"] in ("unresolved", "suspect") or st["halts"]:
                print("halted; inspect the ledger before continuing")
                break


if __name__ == "__main__":
    main()
