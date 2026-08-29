"""
Rating-disclosure redaction, importable form of the blind test's stripper.

Written by Claude (Opus 5). Original: notes/scripts/strip_ratings.py (kept as the experiment
artifact); logic identical, packaged as functions.

Why this exists: filings disclose their own credit ratings (docs/leakage-audit.md), so feeding
a raw filing to the system hands it the answer. Two passes over the text lines: (1) any line
mentioning an agency or rating vocabulary is removed together with up to 16 following lines
that look like rating-table rows, (2) orphaned rating-table rows are removed on their own.
Redaction is logged, never silent: redact() returns the removed lines so every run can store
what was cut. Known residual (measured in the blind test): indirect leaks such as credit-
agreement pricing grids survive; contamination is controlled by design (Task B), not by
claiming the stripper is perfect.
"""
import re

AGENCY = re.compile(r"moody|standard\s*&\s*poor|standard and poor|\bs&p\b|fitch|"
                    r"credit rating|debt rating|ratings? agenc|rating downgrade|"
                    r"investment[- ]grade|noninvestment|non-investment", re.I)
HARD = re.compile(r"^\(?P?\)?(Aaa|Aa[123]|Baa[123]|Ba[123]|Caa[123]|AAA|AA[+-]?|BBB[+-]?|BB[+-]?|CCC[+-]?)$")
SOFT = re.compile(r"^(A[123]|B[123]|Ca|C|A[+-]?|B[+-]?|P-[123]|A-[123]\+?|F[123]|NR|WR)$")


def _cells(line):
    return [c.strip() for c in line.split("\t") if c.strip()]


def _is_rating_row(line):
    cs = _cells(line)
    if not cs:
        return False
    if any(HARD.match(c) for c in cs):
        return True
    soft = sum(1 for c in cs if SOFT.match(c))
    return soft >= 2 and len(cs) - soft <= 2


def redact(text):
    """Returns (clean_text, removed_lines)."""
    lines = text.split("\n")
    out, removed, i = [], [], 0
    while i < len(lines):
        if AGENCY.search(lines[i]):
            removed.append(lines[i]); i += 1
            swallowed = 0
            while i < len(lines) and swallowed < 16:
                if _is_rating_row(lines[i]) or len(lines[i].strip()) < 3:
                    removed.append(lines[i]); i += 1; swallowed += 1
                else:
                    break
            continue
        if _is_rating_row(lines[i]):
            removed.append(lines[i]); i += 1
            continue
        out.append(lines[i]); i += 1
    return "\n".join(out), removed
