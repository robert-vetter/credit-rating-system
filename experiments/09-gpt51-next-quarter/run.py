"""
Experiment 09 runner: guarded requests to GPT-5.1 through OpenRouter, resumable, with scoring.

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. Keeps the safeguards of the
Experiment 04 runner (run_openrouter.py): nothing leaves this machine without an authorization bound
to the manifest hash, a live price check in this process at or below the approved ceilings, a
reviewed memory probe for the company (forecasts only), and room under the cap for the worst case of
every request in flight. Every attempt is recorded in an append-only ledger; raw responses are saved
before parsing; anything unexplained halts the run.

    python3 experiments/09-gpt51-next-quarter/run.py authorize R1      # binds Robert's $50 cap (decision 4)
    python3 experiments/09-gpt51-next-quarter/run.py status R1
    python3 experiments/09-gpt51-next-quarter/run.py submit R1 --ids P-kohl-s F-kohl-s-2024-12-31
    python3 experiments/09-gpt51-next-quarter/run.py submit R1 --probes [--workers 6]
    python3 experiments/09-gpt51-next-quarter/run.py submit R1 --forecasts [--workers 6]
    python3 experiments/09-gpt51-next-quarter/run.py probes R1         # prints probe answers for review
    python3 experiments/09-gpt51-next-quarter/run.py score R1

Ledger events: open, price_check, reserve, dispatch, then one of
  reconcile (charge known) followed by valid | invalid | suspect
  failed_not_billed (explicit error without an id or usage; reservation released)
  unresolved (no readable outcome, or a charge that cannot be established; reservation stays counted)
and halt / clear_halt. A halt blocks all dispatch. At most two attempts per request; a retry happens
only when submit is run again, never automatically. When the next reservation would exceed the cap,
submit stops and reports; it does not dispatch.
"""
import datetime as dt
import hashlib
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
GEN_URL = "https://openrouter.ai/api/v1/generation"
ENDPOINTS_URL = "https://openrouter.ai/api/v1/models/openai/gpt-5.1/endpoints"
PROVIDER_TAG = "openai/flex"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_SNAPSHOT = "gpt-5.1-2025-11-13"
# OpenAI pricing page, saved as evidence/openai-pricing-page-2026-09-28.html (USD per million tokens)
OPENAI_PRICE = {"flex": (Decimal("0.625"), Decimal("0.0625"), Decimal("5")),
                "default": (Decimal("1.25"), Decimal("0.125"), Decimal("10"))}
MAX_TOTAL_ATTEMPTS = 8
PRICE_IN, PRICE_OUT = Decimal("0.625"), Decimal("5")
MAX_ATTEMPTS = 2
SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]


class Refusal(Exception):
    pass


class StopAtCap(Exception):
    pass


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def openai_key():
    """The key file is named at run time (decision 9); the key is never written anywhere."""
    path = os.environ.get("EXP09_OPENAI_KEY_FILE")
    if not path or not os.path.exists(path):
        raise Refusal("EXP09_OPENAI_KEY_FILE not set or missing")
    for line in open(path):
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise Refusal("OPENAI_API_KEY not in the key file")


def openai_charge(usage, tier):
    p_in, p_cached, p_out = OPENAI_PRICE.get(tier, OPENAI_PRICE["default"])
    prompt = int(usage["prompt_tokens"])
    cached = int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
    out = int(usage["completion_tokens"])
    return ((prompt - cached) * p_in + cached * p_cached + out * p_out) / Decimal(10 ** 6)


def api_key():
    key = os.environ.get("OPEN_ROUTER_API_KEY")
    if not key:
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith("OPEN_ROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise Refusal("OPEN_ROUTER_API_KEY not available")
    return key


# ----------------------------------------------------------------------------- ledger

class Ledger:
    def __init__(self, path):
        self.path = path
        self.lock = threading.RLock()

    def append(self, event):
        with self.lock:
            n = len(self.events())
            event = {"seq": n + 1, "ts": now(), **event}
            with open(self.path, "a") as f:
                f.write(json.dumps(event, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            return event

    def events(self):
        if not os.path.exists(self.path):
            return []
        return [json.loads(line) for line in open(self.path) if line.strip()]

    def state(self):
        st = {"committed": Decimal("0"), "unresolved": Decimal("0"), "open": {}, "attempts": {},
              "halts": {}, "price_checks": []}
        for e in self.events():
            ev, aid, rid = e.get("event"), e.get("attempt_id"), e.get("request_id")
            if ev == "price_check":
                st["price_checks"].append(e)
            elif ev == "reserve":
                st["open"][aid] = Decimal(e["reservation_usd"])
                st["attempts"].setdefault(rid, []).append({"attempt_id": aid, "status": "reserved"})
            elif ev == "dispatch":
                self._att(st, rid, aid)["status"] = "dispatched"
            elif ev == "failed_not_billed":
                st["open"].pop(aid, None)
                self._att(st, rid, aid).update(status="failed_not_billed", reason=e.get("reason"))
            elif ev == "unresolved":
                st["unresolved"] += st["open"].pop(aid, Decimal("0"))
                self._att(st, rid, aid).update(status="unresolved", reason=e.get("reason"))
            elif ev == "reconcile":
                st["open"].pop(aid, None)
                st["committed"] += Decimal(e["charge_usd"])
                self._att(st, rid, aid).update(status="reconciled", charge_usd=e["charge_usd"])
            elif ev in ("valid", "invalid", "suspect"):
                self._att(st, rid, aid).update(status=ev, reason=e.get("reason"))
            elif ev == "halt":
                st["halts"][e["halt_id"]] = e
            elif ev == "clear_halt":
                st["halts"].pop(e["halt_id"], None)
        st["valid"] = {rid for rid, atts in st["attempts"].items() if any(a["status"] == "valid" for a in atts)}
        st["exposure"] = st["committed"] + st["unresolved"] + sum(st["open"].values(), Decimal("0"))
        return st

    @staticmethod
    def _att(st, rid, aid):
        for a in st["attempts"].get(rid, []):
            if a["attempt_id"] == aid:
                return a
        raise KeyError(aid)


# ----------------------------------------------------------------------------- transport

class Response:
    def __init__(self, status, body, error=None):
        self.status, self.body, self.error = status, body, error


class HttpxTransport:
    """The only network path. No automatic retries."""

    def __init__(self, key):
        import httpx
        self.client = httpx.Client(timeout=httpx.Timeout(connect=30.0, read=1800.0, write=120.0, pool=60.0),
                                   headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                            "HTTP-Referer": "https://github.com/robert-vetter/credit-rating-system",
                                            "X-Title": "credit-rating-system experiment 09"},
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


class OpenAITransport(HttpxTransport):
    """Direct OpenAI Chat Completions; same no-retry client."""

    def __init__(self, key):
        import httpx
        self.client = httpx.Client(timeout=httpx.Timeout(connect=30.0, read=1800.0, write=120.0, pool=60.0),
                                   headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                   transport=httpx.HTTPTransport(retries=0))

    def send(self, body):
        return self._do("POST", OPENAI_URL, body)


# ----------------------------------------------------------------------------- validation

def parse_json(text):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate keys")
        return dict(pairs)
    return json.loads(text, object_pairs_hook=no_dupes)


def check_forecast(obj):
    need = ["p_down", "p_unchanged", "p_up", "most_likely_rating_at_period_end", "size_if_change_notches",
            "reasons", "insufficient_information"]
    if set(obj) != set(need):
        return "keys differ from the schema"
    ps = [obj["p_down"], obj["p_unchanged"], obj["p_up"]]
    if not all(isinstance(p, (int, float)) and not isinstance(p, bool) and 0 <= p <= 1 for p in ps):
        return "probability outside [0, 1] or not a number"
    if abs(sum(ps) - 1) > 0.01:
        return f"probabilities sum to {sum(ps):.4f}"
    if obj["most_likely_rating_at_period_end"] not in SCALE:
        return "rating not on the scale"
    if not isinstance(obj["size_if_change_notches"], int) or isinstance(obj["size_if_change_notches"], bool):
        return "size not an integer"
    if not isinstance(obj["reasons"], list) or not all(
            isinstance(x, dict) and set(x) == {"reason", "quote", "source"} for x in obj["reasons"]):
        return "reasons malformed"
    if not isinstance(obj["insufficient_information"], bool):
        return "insufficient_information not a boolean"
    return None


def check_probe(obj):
    need = {"recalled_rating", "recalled_as_of", "actions_from_october_2024", "credit_situation_after_september_2024"}
    if set(obj) != need or not isinstance(obj["actions_from_october_2024"], list):
        return "probe keys differ from the schema"
    return None


# ----------------------------------------------------------------------------- runner

class Runner:
    def __init__(self, run_dir, transport, cap=None):
        self.dir = run_dir
        self.transport = transport
        self.ledger = Ledger(os.path.join(run_dir, "ledger.jsonl"))
        self.manifest_raw = open(os.path.join(run_dir, "manifest.json"), "rb").read()
        self.manifest = json.loads(self.manifest_raw)
        self.requests = {r["request_id"]: r for r in self.manifest["requests"]}
        self.auth = self._authorization()
        self.cap = Decimal(self.auth["cap_usd"])
        self.lock = threading.Lock()
        self.priced = False
        self.api = self.manifest.get("api", "openrouter")
        os.makedirs(os.path.join(run_dir, "responses"), exist_ok=True)

    def _authorization(self):
        path = os.path.join(self.dir, "authorization.json")
        if not os.path.exists(path):
            raise Refusal("no authorization.json: nothing may be sent")
        a = json.load(open(path))
        if a.get("manifest_sha256") != sha(self.manifest_raw):
            raise Refusal("authorization does not match the manifest")
        return a

    def price_check(self):
        if self.api == "openai":
            ev = os.path.join(HERE, "evidence", "openai-pricing-page-2026-09-28.html")
            if not os.path.exists(ev):
                raise Refusal("pricing evidence missing")
            p_in, p_cached, p_out = OPENAI_PRICE["flex"]
            ok = p_in <= PRICE_IN and p_out <= PRICE_OUT
            self.ledger.append({"event": "price_check", "api": "openai", "tier": "flex",
                                "input_per_million": str(p_in), "cached_input_per_million": str(p_cached),
                                "output_per_million": str(p_out), "source": os.path.basename(ev), "ok": ok})
            if not ok:
                raise Refusal("flex price above the ceilings")
            self.priced = True
            return
        r = self.transport.endpoints()
        if r.status != 200:
            raise Refusal(f"price check failed: HTTP {r.status} {r.error or ''}")
        eps = json.loads(r.body).get("data", {}).get("endpoints", [])
        ep = next((e for e in eps if e.get("tag") == PROVIDER_TAG), None)
        if ep is None:
            raise Refusal(f"endpoint {PROVIDER_TAG} not listed")
        p_in = Decimal(ep["pricing"]["prompt"]) * 10 ** 6
        p_out = Decimal(ep["pricing"]["completion"]) * 10 ** 6
        ok = p_in <= PRICE_IN and p_out <= PRICE_OUT
        self.ledger.append({"event": "price_check", "endpoint": ep.get("name"), "tag": PROVIDER_TAG,
                            "input_per_million": str(p_in), "output_per_million": str(p_out), "ok": ok})
        if not ok:
            raise Refusal(f"live price {p_in}/{p_out} above the ceilings {PRICE_IN}/{PRICE_OUT}")
        self.priced = True

    def reviewed_probes(self):
        path = os.path.join(self.dir, "probe_review.json")
        return set(json.load(open(path))["reviewed"]) if os.path.exists(path) else set()

    def _reserve(self, rid):
        """Checks and reservation under one lock, so parallel workers cannot overrun the cap."""
        with self.lock:
            st = self.ledger.state()
            if st["halts"]:
                raise Refusal(f"halted: {list(st['halts'])}")
            if not self.priced:
                raise Refusal("no live price check in this process")
            req = self.requests[rid]
            if rid in st["valid"]:
                return None
            atts = st["attempts"].get(rid, [])
            if any(a["status"] in ("reserved", "dispatched", "unresolved") for a in atts):
                raise Refusal(f"{rid}: an earlier attempt is still open or unresolved")
            counted = [a for a in atts if a["status"] != "failed_not_billed"]
            if len(counted) >= MAX_ATTEMPTS or len(atts) >= MAX_TOTAL_ATTEMPTS:
                return None
            if req["kind"] == "forecast":
                if req["probe_id"] not in st["valid"] or req["company"] not in self.reviewed_probes():
                    raise Refusal(f"{rid}: memory probe not answered and reviewed")
            res = Decimal(req["reservation_usd"])
            if st["exposure"] + res > self.cap:
                raise StopAtCap(f"{rid}: exposure {st['exposure']} + {res} would exceed the cap {self.cap}")
            body = open(os.path.join(self.dir, "bodies", f"{rid}.json"), "rb").read()
            if sha(body) != req["body_sha256"]:
                raise Refusal(f"{rid}: body hash changed")
            aid = f"{rid}#{len(atts) + 1}"
            self.ledger.append({"event": "reserve", "request_id": rid, "attempt_id": aid,
                                "reservation_usd": str(res)})
            return aid, body, res

    def _halt(self, rid, aid, reason):
        self.ledger.append({"event": "halt", "halt_id": f"H-{aid}", "request_id": rid, "attempt_id": aid,
                            "reason": reason})

    def _charge(self, body_json):
        usage = body_json.get("usage") or {}
        if usage.get("cost") is not None:
            return Decimal(str(usage["cost"])), None
        gid = body_json.get("id")
        if not gid:
            return None, None
        for wait in (1, 3, 6, 10):
            time.sleep(wait if not getattr(self.transport, "fake", False) else 0)
            g = self.transport.generation(gid)
            if g.status == 200:
                data = json.loads(g.body).get("data", {})
                if data.get("total_cost") is not None:
                    return Decimal(str(data["total_cost"])), data
        return None, None

    def dispatch(self, rid):
        if self.api == "openai":
            return self.dispatch_openai(rid)
        got = self._reserve(rid)
        if got is None:
            return "skipped"
        aid, body, res = got
        self.ledger.append({"event": "dispatch", "request_id": rid, "attempt_id": aid})
        r = self.transport.send(body)
        raw_path = os.path.join(self.dir, "responses", f"{aid.replace('#', '_')}.json")
        with open(raw_path, "wb") as f:
            f.write(json.dumps({"status": r.status, "error": r.error}).encode() + b"\n" + (r.body or b""))
        if r.status is None:
            self.ledger.append({"event": "unresolved", "request_id": rid, "attempt_id": aid, "reason": r.error})
            self._halt(rid, aid, f"transport error: {r.error}")
            return "unresolved"
        try:
            j = json.loads(r.body) if r.body else {}
        except ValueError:
            j = {}
        if r.status != 200:
            if r.status >= 500 or j.get("id") or j.get("usage"):
                charge, _ = self._charge(j) if (j.get("id") or j.get("usage")) else (None, None)
                if charge is None:
                    self.ledger.append({"event": "unresolved", "request_id": rid, "attempt_id": aid,
                                        "reason": f"HTTP {r.status}"})
                    self._halt(rid, aid, f"HTTP {r.status} with unknown charge")
                    return "unresolved"
                self.ledger.append({"event": "reconcile", "request_id": rid, "attempt_id": aid,
                                    "charge_usd": str(charge)})
                self.ledger.append({"event": "invalid", "request_id": rid, "attempt_id": aid, "reason": f"HTTP {r.status}"})
                self._halt(rid, aid, f"HTTP {r.status} was billed")
                return "invalid"
            reason = (j.get("error") or {}).get("message", "") if isinstance(j.get("error"), dict) else str(j)[:200]
            self.ledger.append({"event": "failed_not_billed", "request_id": rid, "attempt_id": aid,
                                "reason": f"HTTP {r.status}: {reason}"})
            if r.status in (401, 402, 403):
                self._halt(rid, aid, f"HTTP {r.status}: {reason}")
            return "failed"
        charge, gen = self._charge(j)
        if charge is None:
            self.ledger.append({"event": "unresolved", "request_id": rid, "attempt_id": aid, "reason": "charge unknown"})
            self._halt(rid, aid, "charge could not be established")
            return "unresolved"
        usage = j.get("usage") or {}
        self.ledger.append({"event": "reconcile", "request_id": rid, "attempt_id": aid, "charge_usd": str(charge),
                            "generation_id": j.get("id"), "provider": j.get("provider"), "model": j.get("model"),
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")})
        if charge > res:
            self._halt(rid, aid, f"charge {charge} above reservation {res}")
        if j.get("provider") not in (None, "OpenAI") or "gpt-5.1" not in str(j.get("model", "")):
            self.ledger.append({"event": "suspect", "request_id": rid, "attempt_id": aid,
                                "reason": f"served by {j.get('provider')} / {j.get('model')}"})
            self._halt(rid, aid, "unexpected provider or model")
            return "suspect"
        try:
            choice = j["choices"][0]
            if choice.get("finish_reason") not in ("stop", None):
                raise ValueError(f"finish_reason {choice.get('finish_reason')}")
            obj = parse_json(choice["message"]["content"])
            problem = (check_forecast if self.requests[rid]["kind"] == "forecast" else check_probe)(obj)
            if problem:
                raise ValueError(problem)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            self.ledger.append({"event": "invalid", "request_id": rid, "attempt_id": aid, "reason": str(exc)[:300]})
            return "invalid"
        self.ledger.append({"event": "valid", "request_id": rid, "attempt_id": aid})
        return "valid"

    def _validate(self, rid, aid, choice):
        try:
            if choice.get("finish_reason") not in ("stop", None):
                raise ValueError(f"finish_reason {choice.get('finish_reason')}")
            obj = parse_json(choice["message"]["content"])
            problem = (check_forecast if self.requests[rid]["kind"] == "forecast" else check_probe)(obj)
            if problem:
                raise ValueError(problem)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            self.ledger.append({"event": "invalid", "request_id": rid, "attempt_id": aid, "reason": str(exc)[:300]})
            return "invalid"
        self.ledger.append({"event": "valid", "request_id": rid, "attempt_id": aid})
        return "valid"

    def dispatch_openai(self, rid):
        got = self._reserve(rid)
        if got is None:
            return "skipped"
        aid, body, res = got
        self.ledger.append({"event": "dispatch", "request_id": rid, "attempt_id": aid})
        r = self.transport.send(body)
        raw_path = os.path.join(self.dir, "responses", f"{aid.replace('#', '_')}.json")
        with open(raw_path, "wb") as f:
            f.write(json.dumps({"status": r.status, "error": r.error}).encode() + b"\n" + (r.body or b""))
        if r.status is None:
            self.ledger.append({"event": "unresolved", "request_id": rid, "attempt_id": aid, "reason": r.error})
            self._halt(rid, aid, f"transport error, billing unknown: {r.error}")
            return "unresolved"
        try:
            j = json.loads(r.body) if r.body else {}
        except ValueError:
            j = {}
        if r.status != 200:
            err = j.get("error") if isinstance(j.get("error"), dict) else {}
            reason = f"HTTP {r.status} {err.get('code') or err.get('type') or ''}: {(err.get('message') or '')[:160]}"
            self.ledger.append({"event": "failed_not_billed", "request_id": rid, "attempt_id": aid, "reason": reason})
            if r.status in (400, 401, 402, 403, 404):
                self._halt(rid, aid, reason)
            return "failed"
        usage = j.get("usage")
        if not usage or "prompt_tokens" not in usage or "completion_tokens" not in usage:
            self.ledger.append({"event": "unresolved", "request_id": rid, "attempt_id": aid, "reason": "no usage"})
            self._halt(rid, aid, "response without usage")
            return "unresolved"
        tier = j.get("service_tier")
        charge = openai_charge(usage, tier)
        self.ledger.append({"event": "reconcile", "request_id": rid, "attempt_id": aid,
                            "charge_usd": str(charge.quantize(Decimal("0.000001"))), "response_id": j.get("id"),
                            "model": j.get("model"), "service_tier": tier,
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")})
        if charge > res:
            self._halt(rid, aid, f"charge {charge} above reservation {res}")
        if j.get("model") != OPENAI_SNAPSHOT or tier != "flex":
            self.ledger.append({"event": "suspect", "request_id": rid, "attempt_id": aid,
                                "reason": f"served as {j.get('model')} at tier {tier}"})
            self._halt(rid, aid, "unexpected snapshot or service tier")
            return "suspect"
        try:
            choice = j["choices"][0]
        except (KeyError, IndexError, TypeError):
            self.ledger.append({"event": "invalid", "request_id": rid, "attempt_id": aid, "reason": "no choices"})
            return "invalid"
        return self._validate(rid, aid, choice)

    def submit(self, ids, workers=1):
        if not self.priced:
            self.price_check()
        results, stop = {}, {"reason": None}

        def one(rid):
            if stop["reason"]:
                return rid, "not sent"
            try:
                return rid, self.dispatch(rid)
            except StopAtCap as exc:
                stop["reason"] = str(exc)
                return rid, "stopped at cap"
            except Refusal as exc:
                stop["reason"] = str(exc)
                return rid, f"refused: {exc}"
        if workers <= 1:
            for rid in ids:
                results[rid] = one(rid)[1]
        else:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                for rid, outcome in ex.map(one, ids):
                    results[rid] = outcome
        return results, stop["reason"]


# ----------------------------------------------------------------------------- answers and scoring

def answers(run_dir, kind):
    led = Ledger(os.path.join(run_dir, "ledger.jsonl"))
    out = {}
    for e in led.events():
        if e.get("event") == "valid":
            rid, aid = e["request_id"], e["attempt_id"]
            if not rid.startswith("F-" if kind == "forecast" else "P-"):
                continue
            raw = open(os.path.join(run_dir, "responses", f"{aid.replace('#', '_')}.json"), "rb").read()
            body = json.loads(raw.split(b"\n", 1)[1])
            out[rid] = json.loads(body["choices"][0]["message"]["content"])
    return out


def status(run_dir):
    st = Ledger(os.path.join(run_dir, "ledger.jsonl")).state()
    man = json.load(open(os.path.join(run_dir, "manifest.json")))
    kinds = {}
    for r in man["requests"]:
        k = r["kind"] if r["kind"] == "probe" else r["arm"]
        atts = st["attempts"].get(r["request_id"], [])
        s = "valid" if r["request_id"] in st["valid"] else (atts[-1]["status"] if atts else "not sent")
        kinds.setdefault(k, {}).setdefault(s, 0)
        kinds[k][s] += 1
    return {"committed_usd": str(st["committed"]), "unresolved_usd": str(st["unresolved"]),
            "open_usd": str(sum(st["open"].values(), Decimal("0"))), "exposure_usd": str(st["exposure"]),
            "halts": {k: v["reason"] for k, v in st["halts"].items()}, "by_kind": kinds}


def main():
    cmd, run_id = sys.argv[1], sys.argv[2]
    run_dir = os.path.join(HERE, "runs", run_id)
    if cmd == "authorize":
        raw = open(os.path.join(run_dir, "manifest.json"), "rb").read()
        path = os.path.join(run_dir, "authorization.json")
        if os.path.exists(path):
            sys.exit("authorization exists")
        json.dump({"authorization_id": f"EXP09-{run_id}-A1", "manifest_sha256": sha(raw), "cap_usd": "50",
                   "approved_by": "Robert Vetter", "approved_on": "2026-09-27",
                   "source": "decisions.md, decision 4: cap $50 for now; stop at the cap and report",
                   "model": ("gpt-5.1-2025-11-13, direct OpenAI Chat Completions, service_tier flex (decisions 9, 10)"
                             if json.loads(raw).get("api") == "openai"
                             else "openai/gpt-5.1 via OpenRouter, provider openai/flex, no fallback"),
                   "written": now()}, open(path, "w"), indent=1)
        print(open(path).read())
    elif cmd == "status":
        print(json.dumps(status(run_dir), indent=1))
    elif cmd == "probes":
        for rid, a in sorted(answers(run_dir, "probe").items()):
            print(rid, json.dumps(a))
    elif cmd == "submit":
        args = sys.argv[3:]
        workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 1
        man = json.load(open(os.path.join(run_dir, "manifest.json")))
        if "--ids" in args:
            ids = [a for a in args[args.index("--ids") + 1:] if not a.startswith("--")]
        elif "--probes" in args:
            ids = [r["request_id"] for r in man["requests"] if r["kind"] == "probe"]
        elif "--forecasts" in args:
            ids = [r["request_id"] for r in man["requests"] if r["kind"] == "forecast"]
        else:
            sys.exit(__doc__)
        man_api = man.get("api", "openrouter")
        transport = OpenAITransport(openai_key()) if man_api == "openai" else HttpxTransport(api_key())
        runner = Runner(run_dir, transport)
        passes = int(args[args.index("--passes") + 1]) if "--passes" in args else 1
        todo, counts, stop = list(ids), {}, None
        for n in range(passes):
            results, stop = runner.submit(todo, workers)
            counts = {}
            for v in results.values():
                counts[v] = counts.get(v, 0) + 1
            print(json.dumps({"pass": n + 1, "results": counts, "stopped": stop,
                              "status": status(run_dir)}), flush=True)
            todo = [rid for rid, v in results.items() if v == "failed"]
            if stop or not todo or runner.ledger.state()["halts"]:
                break
            time.sleep(60)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
