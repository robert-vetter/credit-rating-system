import re

AGENCY = re.compile(r"moody|standard\s*&\s*poor|standard and poor|\bs&p\b|fitch|"
                    r"credit rating|debt rating|ratings? agenc|rating downgrade|"
                    r"investment[- ]grade|noninvestment|non-investment", re.I)

# unambiguous rating symbols: cannot plausibly be anything else in a table cell
HARD = re.compile(r"^(Aaa|Aa[123]|Baa[123]|Ba[123]|Caa[123]|AAA|AA[+-]?|BBB[+-]?|BB[+-]?|CCC[+-]?)$")
# ambiguous on their own, only count when another symbol shares the line
SOFT = re.compile(r"^(A[123]|B[123]|Ca|C|A[+-]?|B[+-]?|P-[123]|A-[123]\+?|F[123]|NR|WR)$")

def cells(line):
    return [c.strip() for c in line.split("\t") if c.strip()]

def is_rating_row(line):
    cs = cells(line)
    if not cs:
        return False
    hard = sum(1 for c in cs if HARD.match(c))
    soft = sum(1 for c in cs if SOFT.match(c))
    if hard:
        return True
    # a row of nothing but ambiguous symbols plus a short label is a ratings row
    return soft >= 2 and len(cs) - soft <= 2

def strip(lines):
    out, removed, i = [], [], 0
    while i < len(lines):
        if AGENCY.search(lines[i]):
            removed.append(lines[i]); i += 1
            swallowed = 0
            while i < len(lines) and swallowed < 16:
                if is_rating_row(lines[i]) or len(lines[i].strip()) < 3:
                    removed.append(lines[i]); i += 1; swallowed += 1
                else:
                    break
            continue
        if is_rating_row(lines[i]):          # second pass, catches orphaned table rows
            removed.append(lines[i]); i += 1
            continue
        out.append(lines[i]); i += 1
    return out, removed

for t in ["TGT", "DG", "GPS", "M", "VSCO"]:
    lines = open(f"{t}_raw.txt").read().split("\n")
    kept, removed = strip(lines)
    open(f"{t}_clean.txt", "w").write("\n".join(kept))
    print(f"{t:<6} {len(lines):>5} -> {len(kept):>5}   {len(removed):>3} entfernt")
