# system/ — the rating system under construction

`scorecard.py` is the deterministic scoring engine for the Moody's Retail and Apparel
methodology (September 2025): subfactor scores → weights → weighted aggregate → Exhibit 5
lookup → scorecard-indicated outcome. Written for the first manual runs (notes/), it is the
seed of the production system: the model's job is to propose the eight subfactor inputs, this
engine turns them into a rating deterministically, so every rating is reproducible arithmetic.

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
