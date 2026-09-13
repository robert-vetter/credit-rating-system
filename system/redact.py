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


# ----------------------------------------------------------------------------- version 2, 2026-09-13
# The 2026-09-13 audit of Experiment 04 found that filings render rating tables one cell per
# line: "Corporate credit / B2 / B+ / BB- / Outlook / Stable / Negative / Negative" (Kohl's) or
# "Rating Agency / Senior unsecured debt rating / Commercial paper rating / Outlook / Moody's /
# Baa3 / P-3 / Stable outlook / Standard & Poor's / BBB / A-2 / Stable outlook" (Dollar General).
# redact() removes the agency line and rating rows, but a lone "B2" or "P-3" is not a rating row
# under its cell heuristic and a row label such as "Corporate credit" stops the swallow, so cells
# survived in the model input. redact_v2() keeps the first pass and adds a structural pass that
# removes whole rating-table blocks and orphaned symbol cells, and rating_fragments() scans the
# assembled text for what would remain. redact() itself is unchanged so that the saved
# Experiment 03 and 04 inputs still replay byte for byte.
SYMBOL = re.compile(r"^\(?P?\)?(Aaa|Aa[123]|A[123]|Baa[123]|Ba[123]|B[123]|Caa[123]|Ca|AAA|AA[+-]?|A[+-]?|"
                    r"BBB[+-]?|BB[+-]?|B[+-]?|CCC[+-]?|CC|NR|WR|P-[123]|NP|A-[123]\+?|F[123]|F1\+)$")
AGENCY_CELL = re.compile(r"(?i)^(moody['\u2019]?s?|s&p|standard\s*&\s*poor['\u2019]?s?|standard and poor['\u2019]?s?|fitch)( ratings| global| investors service)?$")
ROW_LABEL = re.compile(r"(?i)^(rating agency|rating|ratings|credit rating(s)?|corporate( credit| family)?( rating)?|issuer( credit)?( rating)?|"
                       r"senior (un)?secured( debt| notes)?( rating| with subsidiary guarantee)?|long[- ]term( debt)?( rating)?|"
                       r"short[- ]term( debt)?( rating)?|commercial paper( rating)?|outlook|senior debt( outlook)?|"
                       r"long-term debt outlook|senior unsecured debt with subsidiary guarantee|senior secured debt with subsidiary guarantee)$")
OUTLOOK_CELL = re.compile(r"(?i)^(stable|positive|negative|developing|(stable|positive|negative|developing) outlook|"
                          r"outlook (stable|positive|negative|developing)|under review|review for (up|down)grade|watch (positive|negative))$")
BLANK = re.compile(r"^[\s\u200b\u00a0]*$")
CONTEXT = re.compile(r"(?i)rating|credit|outlook|moody|s&p|standard\s*&\s*poor|fitch")


def _kind(line):
    t = line.strip()
    if BLANK.match(t):
        return "blank"
    if AGENCY_CELL.match(t):
        return "agency"
    if SYMBOL.match(t):
        return "symbol"
    if OUTLOOK_CELL.match(t):
        return "outlook"
    if ROW_LABEL.match(t):
        return "label"
    return None


def redact_v2(text):
    """First pass as redact(), then removal of rating-table blocks rendered one cell per line and
    of orphaned symbol cells near rating context. Returns (clean_text, removed_lines)."""
    clean, removed = redact(text)
    lines = clean.split("\n")
    kinds = [_kind(l) for l in lines]
    drop = [False] * len(lines)
    i = 0
    while i < len(lines):
        if kinds[i] in ("agency", "label", "symbol", "outlook"):
            j = i
            while j < len(lines) and kinds[j] is not None:
                j += 1
            block = [k for k in kinds[i:j] if k != "blank"]
            # a rating table block: at least one symbol and at least one agency or label cell,
            # or at least two symbols with an outlook cell
            if ("symbol" in block and ("agency" in block or "label" in block)) or \
                    (block.count("symbol") >= 2 and "outlook" in block):
                for k in range(i, j):
                    drop[k] = True
            i = j
        else:
            i += 1
    for i, k in enumerate(kinds):
        if k == "symbol" and not drop[i]:
            window = "\n".join(lines[max(0, i - 12): i + 13])
            if CONTEXT.search(window):
                drop[i] = True
    out = [l for l, d in zip(lines, drop) if not d]
    removed += [l for l, d in zip(lines, drop) if d]
    return "\n".join(out), removed


def rating_fragments(text):
    """Lines that still look like rating-table cells: a lone symbol or outlook cell within 12
    lines of rating context. Empty means the specified checks passed, nothing more."""
    lines = text.split("\n")
    found = []
    for i, l in enumerate(lines):
        k = _kind(l)
        if k in ("symbol", "outlook"):
            window = "\n".join(lines[max(0, i - 12): i + 13])
            if CONTEXT.search(window):
                found.append({"line": i, "text": l.strip()[:60], "kind": k})
    return found
