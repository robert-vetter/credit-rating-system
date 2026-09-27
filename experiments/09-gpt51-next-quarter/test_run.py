"""
Tests for the Experiment 09 runner (pre-check P13), against a fake transport. No network.

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter.
    python3 -m unittest discover -s experiments/09-gpt51-next-quarter -p 'test_*.py'
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R  # noqa: E402

GOOD = {"p_down": 0.2, "p_unchanged": 0.7, "p_up": 0.1, "most_likely_rating_at_period_end": "Ba2",
        "size_if_change_notches": 1, "reasons": [{"reason": "r", "quote": "q", "source": "10-K filed 2024-03-21"}],
        "insufficient_information": False}
PROBE = {"recalled_rating": "Ba2", "recalled_as_of": "2024", "actions_from_october_2024": [],
         "credit_situation_after_september_2024": "unknown"}


def completion(obj, cost="0.01", provider="OpenAI", model="openai/gpt-5.1-20251113", finish="stop", raw=None):
    return R.Response(200, json.dumps({"id": "gen-1", "provider": provider, "model": model,
                                       "choices": [{"finish_reason": finish,
                                                    "message": {"content": raw if raw is not None else json.dumps(obj)}}],
                                       "usage": {"cost": float(cost), "prompt_tokens": 10, "completion_tokens": 5}}).encode())


class Fake:
    fake = True

    def __init__(self, replies=(), price=("0.000000625", "0.000005")):
        self.replies = list(replies)
        self.sent = []
        self.price = price
        self.lock = threading.Lock()

    def endpoints(self):
        return R.Response(200, json.dumps({"data": {"endpoints": [
            {"name": "OpenAI | openai/gpt-5.1-20251113", "tag": "openai/flex",
             "pricing": {"prompt": self.price[0], "completion": self.price[1]}}]}}).encode())

    def send(self, body):
        with self.lock:
            self.sent.append(body)
            return self.replies.pop(0) if self.replies else completion(GOOD)

    def generation(self, gid):
        return R.Response(404, b"")


def make_run(requests, cap="50", authorize=True):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "bodies"))
    reqs = []
    for r in requests:
        body = json.dumps({"model": "openai/gpt-5.1", "id": r["request_id"]}).encode()
        open(os.path.join(d, "bodies", f"{r['request_id']}.json"), "wb").write(body)
        reqs.append({**r, "body_sha256": hashlib.sha256(body).hexdigest()})
    raw = json.dumps({"requests": reqs}).encode()
    open(os.path.join(d, "manifest.json"), "wb").write(raw)
    if authorize:
        json.dump({"manifest_sha256": hashlib.sha256(raw).hexdigest(), "cap_usd": cap},
                  open(os.path.join(d, "authorization.json"), "w"))
    return d


PROBE_REQ = {"request_id": "P-x", "kind": "probe", "company": "x", "reservation_usd": "0.05"}
FORE_REQ = {"request_id": "F-x-2024-12-31", "kind": "forecast", "company": "x", "probe_id": "P-x",
            "reservation_usd": "0.30"}


def review(d, companies=("x",)):
    json.dump({"reviewed": list(companies)}, open(os.path.join(d, "probe_review.json"), "w"))


class Guards(unittest.TestCase):
    def tearDown(self):
        for d in getattr(self, "dirs", []):
            shutil.rmtree(d, ignore_errors=True)

    def run_dir(self, *a, **k):
        d = make_run(*a, **k)
        self.dirs = getattr(self, "dirs", []) + [d]
        return d

    def test_no_authorization_no_dispatch(self):
        d = self.run_dir([PROBE_REQ], authorize=False)
        t = Fake()
        with self.assertRaises(R.Refusal):
            R.Runner(d, t)
        self.assertEqual(t.sent, [])

    def test_manifest_changed_after_authorization(self):
        d = self.run_dir([PROBE_REQ])
        m = json.load(open(os.path.join(d, "manifest.json")))
        m["requests"][0]["reservation_usd"] = "0.01"
        json.dump(m, open(os.path.join(d, "manifest.json"), "w"))
        with self.assertRaises(R.Refusal):
            R.Runner(d, Fake())

    def test_no_price_check_no_dispatch(self):
        d = self.run_dir([PROBE_REQ])
        t = Fake()
        with self.assertRaises(R.Refusal):
            R.Runner(d, t).dispatch("P-x")
        self.assertEqual(t.sent, [])

    def test_price_above_ceiling_refused(self):
        d = self.run_dir([PROBE_REQ])
        t = Fake(price=("0.00000125", "0.00001"))
        with self.assertRaises(R.Refusal):
            R.Runner(d, t).price_check()
        self.assertEqual(t.sent, [])

    def test_forecast_needs_reviewed_probe(self):
        d = self.run_dir([PROBE_REQ, FORE_REQ])
        t = Fake(replies=[completion(PROBE)])
        run = R.Runner(d, t)
        run.price_check()
        with self.assertRaises(R.Refusal):
            run.dispatch("F-x-2024-12-31")
        self.assertEqual(run.dispatch("P-x"), "valid")
        with self.assertRaises(R.Refusal):
            run.dispatch("F-x-2024-12-31")           # answered but not reviewed
        review(d)
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "valid")
        self.assertEqual(len(t.sent), 2)
        self.assertEqual(run.ledger.state()["committed"], Decimal("0.02"))

    def test_over_cap_stops_without_sending(self):
        d = self.run_dir([PROBE_REQ], cap="0.04")
        t = Fake()
        run = R.Runner(d, t)
        run.price_check()
        with self.assertRaises(R.StopAtCap):
            run.dispatch("P-x")
        self.assertEqual(t.sent, [])

    def test_parallel_workers_cannot_overrun_the_cap(self):
        reqs = [{"request_id": f"P-{i}", "kind": "probe", "company": str(i), "reservation_usd": "0.40"} for i in range(6)]
        d = self.run_dir(reqs, cap="1.00")
        t = Fake(replies=[completion(PROBE, cost="0.40") for _ in range(6)])
        run = R.Runner(d, t)
        results, stop = run.submit([r["request_id"] for r in reqs], workers=6)
        self.assertLessEqual(len(t.sent), 2)
        self.assertIsNotNone(stop)
        self.assertLessEqual(run.ledger.state()["exposure"], Decimal("1.00"))

    def test_valid_request_is_not_sent_again(self):
        d = self.run_dir([PROBE_REQ])
        t = Fake(replies=[completion(PROBE)])
        run = R.Runner(d, t)
        run.price_check()
        self.assertEqual(run.dispatch("P-x"), "valid")
        self.assertEqual(run.dispatch("P-x"), "skipped")
        self.assertEqual(len(t.sent), 1)


class Outcomes(unittest.TestCase):
    def setUp(self):
        self.d = make_run([PROBE_REQ, FORE_REQ])
        review(self.d)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def runner(self, *replies):
        t = Fake(replies=[completion(PROBE)] + list(replies))
        run = R.Runner(self.d, t)
        run.price_check()
        run.dispatch("P-x")
        return run, t

    def test_probabilities_not_summing_to_one_are_invalid_but_charged(self):
        bad = dict(GOOD, p_up=0.3)
        run, _ = self.runner(completion(bad))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "invalid")
        self.assertEqual(run.ledger.state()["committed"], Decimal("0.02"))

    def test_truncated_answer_is_invalid(self):
        run, _ = self.runner(completion(GOOD, finish="length"))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "invalid")

    def test_duplicate_keys_are_invalid(self):
        raw = '{"p_down": 0.2, "p_down": 0.2, "p_unchanged": 0.7, "p_up": 0.1}'
        run, _ = self.runner(completion(None, raw=raw))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "invalid")

    def test_payment_required_halts_without_charge(self):
        run, t = self.runner(R.Response(402, json.dumps({"error": {"message": "Insufficient credits"}}).encode()))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "failed")
        st = run.ledger.state()
        self.assertTrue(st["halts"])
        self.assertEqual(st["committed"], Decimal("0.01"))
        with self.assertRaises(R.Refusal):
            run.dispatch("F-x-2024-12-31")

    def test_transport_error_is_unresolved_and_counted(self):
        run, _ = self.runner(R.Response(None, b"", "ReadTimeout"))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "unresolved")
        st = run.ledger.state()
        self.assertEqual(st["unresolved"], Decimal("0.30"))
        self.assertTrue(st["halts"])

    def test_other_provider_is_suspect_and_halts(self):
        run, _ = self.runner(completion(GOOD, provider="Azure"))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "suspect")
        self.assertTrue(run.ledger.state()["halts"])

    def test_charge_above_reservation_halts(self):
        run, _ = self.runner(completion(GOOD, cost="0.50"))
        run.dispatch("F-x-2024-12-31")
        self.assertTrue(run.ledger.state()["halts"])

    def test_server_error_without_id_stays_unresolved(self):
        run, _ = self.runner(R.Response(502, b"bad gateway"))
        self.assertEqual(run.dispatch("F-x-2024-12-31"), "unresolved")
        self.assertEqual(run.ledger.state()["unresolved"], Decimal("0.30"))


if __name__ == "__main__":
    unittest.main()
