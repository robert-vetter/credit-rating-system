"""
Error metrics for the blind test described in blind-test.md.
Written by Claude (Opus 5). Run with plain python3, no dependencies.

Ground truth is taken from each company's own ratings disclosure in its 10-K,
read before that disclosure was stripped out of the copy given to the runs.
"""

SCALE = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
         "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]
N = {r: i + 1 for i, r in enumerate(SCALE)}

# company, actual, blind scorecard run, memory-only control (None where not run)
RUNS = [
    ("Walmart",           "Aa2",  "A1",   None),   # contaminated, first run
    ("Target",            "A2",   "Baa1", "A2"),
    ("Dollar General",    "Baa3", "Baa2", "Baa2"),
    ("Macy's",            "Ba1",  "Ba1",  "Ba1"),
    ("Gap",               "Ba2",  "Baa3", "Ba1"),
    ("Victoria's Secret", "Ba3",  "Ba1",  "Ba3"),
    ("Kohl's",            "B2",   "Ba3",  None),   # contaminated, second run
]

mae = lambda xs: sum(abs(x) for x in xs) / len(xs)
bias = lambda xs: sum(xs) / len(xs)


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        out, i = [0] * len(v), 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den


if __name__ == "__main__":
    blind_all = [N[b] - N[t] for _, t, b, _ in RUNS]
    blind_ctl = [N[b] - N[t] for _, t, b, m in RUNS if m]
    memory    = [N[m] - N[t] for _, t, _, m in RUNS if m]

    print(f"{'':<18}{'actual':>7}{'blind':>7}{'err':>5}{'memory':>9}{'err':>5}")
    for c, t, b, m in RUNS:
        em = f"{N[m]-N[t]:+d}" if m else "-"
        print(f"{c:<18}{t:>7}{b:>7}{N[b]-N[t]:>+5}{m or '-':>9}{em:>5}")

    print(f"\nMAE in notches")
    print(f"  blind, all 7                {mae(blind_all):.2f}  bias {bias(blind_all):+.2f}")
    print(f"  blind, 5 with a control     {mae(blind_ctl):.2f}  bias {bias(blind_ctl):+.2f}")
    print(f"  memory only, no documents   {mae(memory):.2f}  bias {bias(memory):+.2f}")

    for k in (0, 1, 2):
        hits = sum(1 for v in blind_all if abs(v) <= k)
        print(f"  within {k} notch(es): {hits}/{len(blind_all)}")

    actual = [N[t] for _, t, _, _ in RUNS]
    pred   = [N[b] for _, _, b, _ in RUNS]
    print(f"\nCompression")
    print(f"  actual spans {max(actual)-min(actual)} notches, predictions span {max(pred)-min(pred)}")
    print(f"  Spearman rank correlation {spearman(actual, pred):.3f}")

    print(f"\nAAPE on the ordinal codes, for comparison")
    apes = [abs(N[b] - N[t]) / N[t] * 100 for _, t, b, _ in RUNS]
    for (c, t, b, _), a in zip(RUNS, apes):
        print(f"  {c:<18} {abs(N[b]-N[t])} notch -> {a:5.1f}%")
    print(f"  overall AAPE {sum(apes)/len(apes):.1f}%")
