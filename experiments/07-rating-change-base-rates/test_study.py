"""
Tests for run_study.py (Experiment 07, pre-check P13). Hand-built rating files go through the
real label rule of build_observations.py, then through the study's counting functions.

Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter.
Run from the repository root:
    python3 -m unittest discover -s experiments/07-rating-change-base-rates -p 'test_*.py'
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_study as S  # noqa: E402
from build_observations import GRID, label_at, lines_of  # noqa: E402


def rec(r, d, rac, rt="LT Corporate Family Ratings"):
    return {"R": r, "RAD": d, "RAC": rac, "RT": rt}


def su(r, d, rac):
    return rec(r, d, rac, "Senior Unsecured")


def entity(oi, obligor=(), instruments=()):
    return {"oi": oi, "obligor_records": list(obligor),
            "instruments": [{"meta": {}, "records": list(i)} for i in instruments]}


def observations(ratings, scope="in"):
    """The builder's observation loop, without filings."""
    ent, sen = lines_of(ratings)
    obs, prev = [], None
    for t in GRID:
        label, level, oi, amb = label_at(ent, sen, t)
        if label is None:
            prev = None
            continue
        obs.append({"date": t, "label": label, "label_level": level, "label_oi": oi,
                    "label_ambiguous": amb, "persistence": prev,
                    "changed": (label != prev) if prev else None})
        prev = label
    return {"scope": scope, "observations": obs}


def study(ratings):
    doc = observations(ratings)
    return S.company_records("x", doc, ratings), doc


def at(c, t):
    return next(q for q in c["quarters"] if q["date"] == t)


class Counting(unittest.TestCase):
    def test_first_observation_has_no_quarterly_record(self):
        c, doc = study({"entities": [entity("1", [rec("Ba2", "2013-02-01", "NW")])]})
        self.assertEqual(c["labelled"][0], "2013-03-31")
        self.assertEqual(len(c["quarters"]), len(c["labelled"]) - 1)
        self.assertFalse(any(q["changed"] for q in c["quarters"]))

    def test_downgrade_counts_with_sign_and_action(self):
        c, _ = study({"entities": [entity("1", [rec("Ba2", "2013-02-01", "NW"),
                                                rec("B1", "2014-05-10", "DG")])]})
        q = at(c, "2014-06-30")
        self.assertTrue(q["changed"])
        self.assertEqual(q["delta"], 2)          # positive is a downgrade
        self.assertEqual(q["actions"], 1)
        self.assertFalse(q["level_switch"])

    def test_level_switch_kohls_pattern(self):
        # bond Baa2 -> Ba2 and a new corporate family rating Ba1 on the same day
        r = {"entities": [entity("1", [rec("Ba1", "2022-12-12", "NW")],
                                 [[su("Baa1", "2012-09-18", "NW"), su("Baa2", "2016-04-19", "DG"),
                                   su("Ba2", "2022-12-12", "DG")]])]}
        c, _ = study(r)
        q = at(c, "2022-12-31")
        self.assertTrue(q["changed"])
        self.assertEqual((q["prev"], q["cur"], q["delta"]), ("Baa2", "Ba1", 2))   # the bond fell 3
        self.assertTrue(q["level_switch"])
        self.assertEqual(q["actions"], 0)        # the entity line only has an NW record

    def test_new_bond_with_other_rating_switches_label_without_action(self):
        # the label rule takes the most recently dated live record, so the switch happens when
        # the new bond is issued, not when the old one matures; the builder flags it ambiguous
        r = {"entities": [entity("1", [], [
            [su("Baa1", "2012-06-15", "HS"), su("WR", "2015-03-01", "WE")],
            [su("Baa2", "2014-01-15", "NW")]])]}
        c, _ = study(r)
        q = at(c, "2014-03-31")
        self.assertTrue(q["changed"])
        self.assertEqual(q["delta"], 1)
        self.assertEqual(q["actions"], 0)
        self.assertTrue(q["ambiguous"])
        self.assertFalse(q["level_switch"])
        self.assertFalse(q["source_switch"])     # same entity; caught as a change without action
        self.assertFalse(at(c, "2015-03-31")["changed"])

    def test_maturity_with_same_rating_is_no_change(self):
        r = {"entities": [entity("1", [], [
            [su("Baa1", "2012-06-15", "HS"), su("WR", "2015-03-01", "WE")],
            [su("Baa1", "2014-01-15", "NW")]])]}
        c, _ = study(r)
        self.assertFalse(at(c, "2015-03-31")["changed"])

    def test_several_bonds_moving_together_are_one_action(self):
        r = {"entities": [entity("1", [], [
            [su("A3", "2012-06-15", "HS"), su("Baa1", "2016-05-02", "DG")],
            [su("A3", "2012-06-15", "HS"), su("Baa1", "2016-05-02", "DG")],
            [su("A3", "2013-01-10", "NW"), su("Baa1", "2016-05-02", "DG")]])]}
        c, _ = study(r)
        q = at(c, "2016-06-30")
        self.assertTrue(q["changed"])
        self.assertEqual(q["actions"], 1)

    def test_reversal_inside_a_quarter_is_invisible_on_the_grid(self):
        r = {"entities": [entity("1", [rec("B1", "2012-06-15", "HS"), rec("B2", "2017-04-03", "DG"),
                                       rec("B1", "2017-06-20", "UP")])]}
        c, _ = study(r)
        q = at(c, "2017-06-30")
        self.assertFalse(q["changed"])
        self.assertEqual(q["actions"], 2)

    def test_company_withdrawal_ends_early_and_censors_windows(self):
        r = {"entities": [entity("1", [rec("Caa1", "2012-06-15", "HS"), rec("WR", "2016-08-01", "WE")])]}
        c, _ = study(r)
        self.assertTrue(c["ends_early"])
        self.assertEqual(c["labelled"][-1], "2016-06-30")
        self.assertFalse(any(q["changed"] for q in c["quarters"]))
        windows, censored = S.forward_windows(c)
        self.assertEqual(censored, 4)            # the last four labelled quarters lack a full window

    def test_gap_drops_the_next_quarter_from_the_denominator(self):
        r = {"entities": [entity("1", [rec("Ba3", "2012-06-15", "HS"), rec("WR", "2014-02-01", "WE"),
                                       rec("B1", "2014-08-01", "NW")])]}
        c, _ = study(r)
        self.assertEqual(c["gaps"], ["2014-03-31", "2014-06-30"])
        self.assertNotIn("2014-09-30", [q["date"] for q in c["quarters"]])

    def test_forward_window(self):
        c, _ = study({"entities": [entity("1", [rec("Ba2", "2012-06-15", "HS"),
                                                rec("Ba3", "2015-05-01", "DG")])]})
        windows, censored = S.forward_windows(c)
        w = {x["date"]: x for x in windows}
        self.assertTrue(w["2014-09-30"]["changed"])      # change lands in quarter 3 of the window
        self.assertFalse(w["2015-06-30"]["changed"])
        self.assertTrue(w["2014-06-30"]["changed"])      # quarter 4 of the window
        self.assertFalse(w["2014-03-31"]["changed"])     # window ends 2015-03-31
        self.assertEqual(censored, 4)

    def test_annual_pairs_are_q4_only(self):
        c, doc = study({"entities": [entity("1", [rec("A2", "2012-06-15", "HS"),
                                                  rec("A3", "2014-02-01", "DG")])]})
        pairs = S.lag_pairs(c, doc, 4, q4_only=True)
        self.assertTrue(all(p["date"].endswith("12-31") for p in pairs))
        p = {x["date"]: x for x in pairs}
        self.assertTrue(p["2014-12-31"]["changed"])
        self.assertFalse(p["2015-12-31"]["changed"])


class WholeAnalysis(unittest.TestCase):
    def test_analyse_runs_on_fixture_companies(self):
        fixtures = [
            {"entities": [entity("1", [rec("Ba2", "2012-06-15", "HS"), rec("Ba3", "2015-05-01", "DG"),
                                       rec("Ba2", "2016-02-01", "UP")])]},
            {"entities": [entity("2", [rec("Ba1", "2022-12-12", "NW")],
                                 [[su("Baa2", "2012-09-18", "NW"), su("Ba2", "2022-12-12", "DG")]])]},
            {"entities": [entity("3", [rec("Caa1", "2012-06-15", "HS"), rec("WR", "2016-08-01", "WE")])]},
        ]
        companies = [(f"c{i}", observations(r), r, "", "") for i, r in enumerate(fixtures)]
        res = S.analyse(companies, lambda d: True)
        q = res["T1"][0]
        self.assertEqual(q["changed"], 3)
        self.assertEqual((q["upgrades"], q["downgrades"]), (1, 2))
        self.assertEqual(res["T7"]["level_switches"], 1)
        self.assertEqual(res["T6"]["after_change"]["n"] + res["T6"]["after_no_change"]["n"] > 0, True)
        self.assertIn("## T9", S.to_markdown(res, [("same", res)]))
        self.assertEqual(len(res["T9"]["companies"]), 1)          # the Caa1 company withdrawn in 2016


class RebuiltCompanies(unittest.TestCase):
    def test_rebuilt_label_loop_reproduces_an_existing_folder(self):
        import json
        import build_withdrawn as B
        base = os.path.join(S.COMPANIES, "kohl-s")
        with open(os.path.join(base, "ratings.json")) as f:
            ratings = json.load(f)
        with open(os.path.join(base, "observations.json")) as f:
            existing = json.load(f)["observations"]
        built = B.quarterly_labels(ratings)
        fields = ("date", "quarter", "label", "label_level", "label_oi", "label_ambiguous", "persistence", "changed")
        self.assertEqual([{k: o[k] for k in fields} for o in built],
                         [{k: o[k] for k in fields} for o in existing])

    def test_skipped_groups_are_exactly_those_without_a_current_rating(self):
        import json
        import build_withdrawn as B
        with open(os.path.join(S.ROOT, "evaluation", "mapping.json")) as f:
            items = json.load(f)
        skipped = B.skipped_groups(items)
        self.assertEqual(len(skipped), 75)
        self.assertEqual(set(B.slug(g) for g in skipped) & set(os.listdir(S.COMPANIES)), {"cdw"})   # skipped by the builder


class Statistics(unittest.TestCase):
    def test_precision_example_from_the_specification(self):
        self.assertAlmostEqual(S.precision(0.06, 0.9, 0.9), 0.054 / 0.148, places=6)

    def test_wilson_contains_the_rate(self):
        lo, hi = S.wilson(218, 3646)
        self.assertLess(lo, 218 / 3646)
        self.assertGreater(hi, 218 / 3646)

    def test_categories(self):
        self.assertEqual([S.category(r) for r in ("Aaa", "Aa1", "A3", "Baa3", "Ba1", "B3", "Caa3", "Ca")],
                         ["Aaa", "Aa", "A", "Baa", "Ba", "B", "Caa", "Ca-C"])
        self.assertTrue(S.investment_grade("Baa3"))
        self.assertFalse(S.investment_grade("Ba1"))


if __name__ == "__main__":
    unittest.main()
