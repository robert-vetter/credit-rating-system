# system/ — the rating system under construction

`scorecard.py` is the deterministic scoring engine for the Moody's Retail and Apparel
methodology (September 2025): subfactor scores → weights → weighted aggregate → Exhibit 5
lookup → scorecard-indicated outcome. Written for the first manual runs (notes/), it is the
seed of the production system: the model's job is to propose the eight subfactor inputs, this
engine turns them into a rating deterministically, so every rating is reproducible arithmetic.

## Offline accounting development prototype

*Written by OpenAI Codex, directed by Robert Vetter, 2026-09-17. Verified against local
companyfacts, numeric inline-XBRL matches and offline regression tests. Accounting
interpretations remain machine-proposed and pending human review.*

`evidence_ledger.py` preserves raw fact dates, exact intervals, units, accessions,
source hashes and JSON pointers. It keeps conflicting alternatives, filters facts by
public availability, and can locate matching consolidated numeric inline-XBRL elements
in cached filings. A numeric source match does not certify accounting meaning.

`accounting_checks.py` separates gross, net and cash interest; inventories debt and
lease components; and checks total/current/noncurrent reconciliation without adding a
total to its own components. Missing inputs remain unresolved. It does not calculate
Moody's-adjusted total debt, RCF, full TTM metrics, qualitative grades or a final rating.

The new reader uses exact calendar durations; the legacy `fetch_xbrl.py` duration bug
and compact caches are intentionally unchanged to preserve earlier experiments.
Run `python3 evaluation/pipeline/accounting_benchmark.py` for the three-case review.

## Existing model component

`analyst.py` is the model half: one raw Messages API call (structured output, streaming, no
tools array so retrieval is structurally off) that reads redacted filings and proposes the
scorecard inputs plus a free-form direct rating. `redact.py` removes rating self-disclosures
from filing text before the model sees it, logging what it cut.

Sector expansion later means one configuration (bands, weights, qualitative criteria) per
methodology on top of the same mechanics.

Review update, 2026-09-12, by Codex at Robert's direction: negative Debt/EBITDA and net-cash
RCF scoring now follow page 5 footnotes 2 and 3. Non-finite inputs and undefined ratio cases
fail explicitly. Regression checks live in `experiments/03-oos-values-first/test_integrity.py`;
measured impact and limitations are in `docs/oos-integrity-review.md`.

Redaction update, 2026-09-13: `redact.py` gained `redact_v2()`, which runs the original pass
and then removes rating tables rendered one cell per line and orphan rating symbols near rating
context, and `rating_fragments()`, which scans an assembled model input and must return nothing
before a run. The original `redact()` is unchanged, so the saved Experiment 03 and 04 inputs
still replay byte for byte. The reason is a real failure: a disclosed rating survived the first
pass and reached the model in Experiment 04 (docs/leakage-audit.md, update of 2026-09-13).
Cases from Kohl's and Dollar General are regressions in
`experiments/04-open-weight-cross-section/test_runner.py`.
