"""
Retail and Apparel scorecard arithmetic, Moody's methodology of 12 Sep 2025.

The engine is the bottom half and is exact. The top half is company inputs, hand-extracted
from the 10-Ks, and that is where all the arguing happens. See the write-ups next to this file.

Run with plain python3, no dependencies. python3 scorecard.py
"""

# ----------------------------------------------------------------------------- company inputs

WALMART = {
    "label": "Walmart FY2026 (year ended 31 Jan 2026), USD m",
    "revenue": 713_163,
    "operating_income": 29_825,
    "d_and_a": 14_203,
    "capex": 26_642,
    "interest": 2_318 + 481,          # debt interest plus finance lease interest, gross
    "cash": 10_727,
    "dividends": 7_507,
    "cfo": 41_565,
    "wc_swing": -1_136 - 1_443 + 1_611 + 1_607 + 113,
    "debt": (6_596 + 3_542 + 34_624    # short term, current portion, long term
             + 856 + 5_905             # finance leases
             + 1_631 + 13_941),        # operating leases
    "qualitative": {
        "Market Characteristics": "A",
        "Market Position": "Aa",
        "Revenue and Earnings Stability": "Aa",
        "Financial Policy": "Aa",
    },
}

KOHLS = {
    "label": "Kohl's FY2025 (year ended 31 Jan 2026), USD m",
    "revenue": 15_527,
    "operating_income": 624,
    "d_and_a": 700,
    "capex": 372,
    "interest": 288,                   # reported net, Kohl's does not split out gross on the face
    "cash": 674,
    "dividends": 56,
    "cfo": 1_380,
    "wc_swing": 203 + 91 + 130 - 103 - 96,
    "debt": (0 + 0 + 1_436             # revolver, current portion, long term
             + 85 + 2_365              # finance leases and financing obligations
             + 94 + 2_650),            # operating leases
    "qualitative": {
        "Market Characteristics": "B",
        "Market Position": "B",
        "Revenue and Earnings Stability": "Caa",
        "Financial Policy": "Ba",
    },
}

WEIGHTS = {
    "Revenue": 0.15,
    "Market Characteristics": 0.10,
    "Market Position": 0.10,
    "Revenue and Earnings Stability": 0.10,
    "Debt/EBITDA": 0.15,
    "(EBITDA-Capex)/Interest": 0.15,
    "RCF/Net Debt": 0.10,
    "Financial Policy": 0.15,
}

# ----------------------------------------------------------------------------- engine

# (metric at the good end, metric at the bad end, numeric good, numeric bad), Aaa first
BANDS = {
    "revenue_usd_bn": [
        (150.0, 100.0, 0.5, 1.5), (100.0, 50.0, 1.5, 4.5), (50.0, 25.0, 4.5, 7.5),
        (25.0, 10.0, 7.5, 10.5), (10.0, 4.0, 10.5, 13.5), (4.0, 1.5, 13.5, 16.5),
        (1.5, 0.5, 16.5, 19.5), (0.5, 0.0, 19.5, 20.5),
    ],
    "debt_ebitda": [
        (0.0, 0.5, 0.5, 1.5), (0.5, 1.0, 1.5, 4.5), (1.0, 2.0, 4.5, 7.5),
        (2.0, 3.0, 7.5, 10.5), (3.0, 4.0, 10.5, 13.5), (4.0, 6.0, 13.5, 16.5),
        (6.0, 8.0, 16.5, 19.5), (8.0, 12.0, 19.5, 20.5),
    ],
    "rcf_net_debt_pct": [
        (100.0, 80.0, 0.5, 1.5), (80.0, 60.0, 1.5, 4.5), (60.0, 40.0, 4.5, 7.5),
        (40.0, 25.0, 7.5, 10.5), (25.0, 15.0, 10.5, 13.5), (15.0, 10.0, 13.5, 16.5),
        (10.0, 5.0, 16.5, 19.5), (5.0, 0.0, 19.5, 20.5),
    ],
    "ebitda_capex_interest": [
        (25.0, 20.0, 0.5, 1.5), (20.0, 16.0, 1.5, 4.5), (16.0, 9.0, 4.5, 7.5),
        (9.0, 4.5, 7.5, 10.5), (4.5, 2.5, 10.5, 13.5), (2.5, 1.25, 13.5, 16.5),
        (1.25, 0.25, 16.5, 19.5), (0.25, 0.0, 19.5, 20.5),
    ],
}

QUALITATIVE = {"Aaa": 1, "Aa": 3, "A": 6, "Baa": 9, "Ba": 12, "B": 15, "Caa": 18, "Ca": 20}

OUTCOME = [
    (1.5, "Aaa"), (2.5, "Aa1"), (3.5, "Aa2"), (4.5, "Aa3"),
    (5.5, "A1"), (6.5, "A2"), (7.5, "A3"),
    (8.5, "Baa1"), (9.5, "Baa2"), (10.5, "Baa3"),
    (11.5, "Ba1"), (12.5, "Ba2"), (13.5, "Ba3"),
    (14.5, "B1"), (15.5, "B2"), (16.5, "B3"),
    (17.5, "Caa1"), (18.5, "Caa2"), (19.5, "Caa3"), (20.5, "Ca"),
]


def score_quant(metric, value):
    bands = BANDS[metric]
    best, worst = bands[0][0], bands[-1][1]
    ascending = best > worst                     # a higher metric value is better
    if (ascending and value >= best) or (not ascending and value <= best):
        return 0.5
    if (ascending and value <= worst) or (not ascending and value >= worst):
        return 20.5
    for good, bad, n_good, n_bad in bands:
        inside = good >= value >= bad if ascending else good <= value <= bad
        if inside:
            return n_good + (good - value) / (good - bad) * (n_bad - n_good)
    raise ValueError(f"{value} fell through the bands for {metric}")


def outcome(aggregate):
    for ceiling, label in OUTCOME:
        if aggregate <= ceiling:
            return label
    return "C"


def derive(c):
    ebitda = c["operating_income"] + c["d_and_a"]
    net_debt = c["debt"] - c["cash"]
    ffo = c["cfo"] - c["wc_swing"]
    rcf = ffo - c["dividends"]
    return {
        "ebitda": ebitda, "net_debt": net_debt, "ffo": ffo, "rcf": rcf,
        "revenue_usd_bn": c["revenue"] / 1000,
        "debt_ebitda": c["debt"] / ebitda,
        "ebitda_capex_interest": (ebitda - c["capex"]) / c["interest"],
        "rcf_net_debt_pct": 100 * rcf / net_debt,
    }


def build(c, overrides=None):
    """Returns [(subfactor, weight, numeric score)]. overrides swaps single scores."""
    m = derive(c)
    rows = [
        ("Revenue", score_quant("revenue_usd_bn", m["revenue_usd_bn"])),
        ("Market Characteristics", QUALITATIVE[c["qualitative"]["Market Characteristics"]]),
        ("Market Position", QUALITATIVE[c["qualitative"]["Market Position"]]),
        ("Revenue and Earnings Stability", QUALITATIVE[c["qualitative"]["Revenue and Earnings Stability"]]),
        ("Debt/EBITDA", score_quant("debt_ebitda", m["debt_ebitda"])),
        ("(EBITDA-Capex)/Interest", score_quant("ebitda_capex_interest", m["ebitda_capex_interest"])),
        ("RCF/Net Debt", score_quant("rcf_net_debt_pct", m["rcf_net_debt_pct"])),
        ("Financial Policy", QUALITATIVE[c["qualitative"]["Financial Policy"]]),
    ]
    if overrides:
        rows = [(n, overrides.get(n, s)) for n, s in rows]
    return [(n, WEIGHTS[n], s) for n, s in rows]


def aggregate(rows):
    return sum(w * s for _, w, s in rows)


def report(c):
    m = derive(c)
    rows = build(c)
    total = aggregate(rows)
    print(c["label"])
    print(f"  EBITDA {m['ebitda']:,}   net debt {m['net_debt']:,}   FFO {m['ffo']:,}   RCF {m['rcf']:,}")
    print(f"  revenue ${m['revenue_usd_bn']:.1f}bn   debt/EBITDA {m['debt_ebitda']:.2f}x   "
          f"(EBITDA-capex)/int {m['ebitda_capex_interest']:.2f}x   RCF/net debt {m['rcf_net_debt_pct']:.1f}%")
    print()
    for name, weight, score in rows:
        print(f"    {name:<32} {weight:>5.0%}  {score:>6.2f}  {weight*score:>6.3f}")
    print(f"    {'aggregate':<32} {'':>5}  {'':>6}  {total:>6.3f}")
    margin = min(abs(total - ceiling) for ceiling, _ in OUTCOME)
    print(f"\n  scorecard-indicated outcome: {outcome(total)}   "
          f"(nearest notch boundary is {margin:.3f} away)\n")


if __name__ == "__main__":
    for company in (WALMART, KOHLS):
        report(company)
