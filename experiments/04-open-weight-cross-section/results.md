# Experiment 04, Arm 1 results: a post-release, history-conditioned disclosure-label pilot on Qwen3-235B-A22B-Instruct-2507, with a disclosed redaction failure

*Written 2026-09-13 by Claude (Fable 5.1), directed by Robert Vetter, and revised the same day
after Codex's post-run audit (review-codex-2026-09-13.md), whose sixteen corrections are
applied and listed at the end. Model runs on 2026-09-13 from 01:00 to 04:00 UTC under
authorization EXP04-ARM1-A1 (decisions D5 to D12 in decisions.md), through OpenRouter to
DeepInfra's fp8 endpoint. Every number was computed offline from the append-only ledger, the
raw responses, the frozen manifest and the audit files under runs/EXP04-ARM1-A1/ (gitignored,
on this machine) by `run_openrouter.py score` and `report.py`, which score both models through
`evaluation/pipeline/score_run.py`; the audit reconstructed them independently. Nothing has
been sent to the lab.*

## What this measures

Twenty Retail and Apparel issuers, each with a Moody's rating that the issuer itself disclosed
in a filing after the 2025-09-30 boundary, hand-read and confirmed. The model estimates the
rating at 2026-08-29 from the latest 10-K and subsequent 10-Qs, with rating disclosures
redacted, plus a history pack that ends on 2025-08-28. The labels are accepted disclosures;
that each was still the outstanding rating on the observation date is not verified. Two
channels: the scorecard computed by `system/scorecard.py` from the ten figures and four grades
the model extracts, and the model's own overall judgement. Three replicates per issuer at
temperature 0. Two arms: the current, repaired inputs for all 20 (the main measurement), and
the exact saved inputs Opus 4.6 saw in Experiment 03 for the seven issuers it scored (the
matched-information comparison). One memory probe per issuer ran first.

Qurate's label predates the bankruptcy described in its input filings and names a
subsidiary's corporate family rating, so the primary cohort is the other 19 and Qurate is a
diagnostic (decision D8). Persistence is the rating in effect at the history end: exact on 18
of 19 and on 18 of 20.

## The redaction failure found in the audit

The audit found that Kohl's two input filings render their rating table one cell per line:
"Corporate credit", "B2", "B+", "BB-", "Outlook", "Stable" (or "Positive" in the 10-Q),
"Negative", "Negative". The redactor removed the line with the agency names and the sentence
before it, then stopped at "Corporate credit", and its orphan-row rule ignores a lone "B2".
So all three current-input replicates for Kohl's received the disclosed B2, which equals the
label and the prior. A second, weaker residual found afterwards: Dollar General's filings
keep "Commercial paper rating", "Outlook", "P-3", "Stable outlook", "A-2", "Stable outlook"
after the Baa3 cell was removed; a Prime-3 short-term rating constrains the long-term rating
to the Baa range. No other body carries its issuer's rating symbol in rating context (a scan
of every body for lone symbol or outlook cells near rating words finds only these two).

The frozen cohort, bodies and records are unchanged. The 19-issuer result stands as recorded
with this failure disclosed, and two post-hoc sensitivities are reported next to it: 18
issuers without Kohl's, and 17 without Kohl's and Dollar General. They are audited pilot
results, not a clean benchmark selected in advance. For future runs `system/redact.py` now
has a structural second pass (`redact_v2`) that removes rating-table blocks and orphaned
cells, and a scan (`rating_fragments`) that the preparation step requires to return nothing;
both cases are regression tests, and the scan finds nothing in any of the run's 50 documents
after the second pass. The paid bodies are not repaired retroactively.

## Headline

| Current inputs, consensus of three replicates | Judgement exact, MAE | Scorecard exact, MAE | Persistence exact, MAE |
|---|---|---|---|
| Original 19, with the Kohl's leak | 17/19, 2/19 = 0.11 | 3/19, 35/19 = 1.84 | 18/19, 1/19 = 0.05 |
| Post-hoc 18, without Kohl's | 16/18, 2/18 = 0.11 | 3/18, 32/18 = 1.78 | 17/18, 1/18 = 0.06 |
| Post-hoc 17, without Kohl's and Dollar General | 16/17, 1/17 = 0.06 | 3/17, 29/17 = 1.71 | 16/17, 1/17 = 0.06 |
| All 20, with Qurate | 17/20, 4/20 = 0.20 | 3/20, 36/20 = 1.80 | 18/20, 3/20 = 0.15 |

Every replicate is within a notch of its consensus figure (tables below). Within one notch:
judgement 19/19, scorecard 10/19, persistence 19/19. False alarms on the 18 unchanged issuers
of the primary cohort: judgement 1 (Dollar General), scorecard 15. The single changed case in
the primary cohort, Nike A1 to A2, was missed by the judgement (A1 in every replicate) and
moved the wrong way by the scorecard (Aa3 consensus). Qurate, Caa1 to Caa3, was missed by the
judgement (Caa1) and moved the right way but one notch short by the scorecard (Caa2).

## Reading

Neither channel beats persistence on any cohort. The descriptive facts are these. Of 60
current-input direct ratings, 56 equal the prior supplied in the history pack; all three
replicates equal the prior on 18 of 20 issuers (Dollar General upgrades in all three, Signet
downgrades in replicate 2); the consensus equals persistence except for Dollar General. The
model's own `vs_last_known` field contradicts the rating it gave in five responses: Gap
replicates 1 and 3 and Kohl's replicate 3 say "upgrade" and return the prior, Signet
replicate 2 says "upgrade" and returns a downgrade to B1, Signet replicate 3 says "upgrade" and
returns the prior. Direction is therefore derived from the ratings, never from that field.
Anchoring on the supplied prior is a hypothesis consistent with all of this; it is not a
demonstrated mechanism, because no prior-withheld control was run.

The scorecard channel is favourable and unstable. Of 60 current-input responses it rates the
issuer above its label in 36, exactly in 9 and below in 15, a mean signed error of 74/60 =
1.23 notches in the issuer's favour; against persistence the counts are 32 above, 11 equal,
17 below. The audit traced part of this to accounting-concept errors rather than to the
arithmetic: Signet's saved replicate 2 returns zero debt and zero interest (undefined ratio,
channel failed) and its current replicate 3 returns zero debt with interest 4, although the
10-K shows $1,217.3 million of operating-lease liabilities and the 4 is net interest income;
Nike's interest is +50 in two replicates, the net interest income line, and 323 in the third,
the cash interest paid; Nike's saved replicates use pretax income 3,900 as operating income
instead of 3,850; Gap's replicate 3 labels FY2026 figures "2025-01-31". Across replicates the
figures are consistent without being correct: revenue, operating income, D&A and dividends
identical on 18 of 20 issuers, cash and CFO on 17, capex and interest on 16, debt on 13, the
working-capital swing on 6; the four qualitative grades identical on 13, 13, 11 and 10
issuers respectively and jointly on 8. Reference XBRL rows were in the input, so consistency
is not evidence of independent extraction. Nike's scorecard reached Aa2 in replicate 1 with
all four factors graded Aaa. Which missing Moody's adjustments, definition errors and grading
choices cause the gap is not established; each is a testable hypothesis.

On the seven issuers Opus 4.6 scored, with the same supplied information (documents, pack,
task and schema, verified byte for byte), Qwen's judgement replicates 1 and 2 give Opus's
aggregate numbers, 4/7 exact, 6/7 within one, MAE 4/7, with different mistakes: Qwen rates
Signet Ba2 and Qurate Caa1 where Opus gave Ba1 and Ca, and Qwen's replicate 2 misses on
Victoria's Secret instead of Signet. Replicate 3 has five valid responses, 3/7 over planned.
Qwen's scorecard is worse in replicate 1 (2/7, MAE 13/7 against Opus's 3/7, 8/7) and has
different coverage afterwards; matched persistence baselines for every incomplete channel are
in the tables. Inference settings differ (Opus: adaptive high-effort thinking, API defaults;
Qwen: non-thinking fp8 deployment, temperature 0, provider-enforced schema), so this is an
aggregate-metric comparison on matched inputs, not equivalence. The whole Qwen run cost $1.24
against $8.74 for the seven Opus issuers; the token prices were 3.6% and 4.4% of Opus's batch
prices, and the two totals buy different sets of calls.

## Coverage, attempts and spend

Planned: 20 probes, 60 current-input and 21 saved-input document requests. Dispatched: 111
attempts, the 101 planned plus the ten extra attempts Robert allowed. Valid: 20 probes and
79 of 81 document requests. Two requests have no valid response: Qurate's third saved-input
replicate (a transport failure, then an output-length loop on its retry) and Victoria's
Secret's third saved-input replicate (a transport failure with no retry allowance left). One
valid response has a failed scorecard channel (Signet, saved inputs, replicate 2) and a
retained direct rating. All 60 current-input requests are valid.

Spend: $1.242279 committed for 104 reconciled responses (exact provider charges sum to
$1.242229), plus $0.141521 held for the seven attempts that failed before any HTTP response,
whose billing the runner treats as unknown. Total against the $3.00 cap: $1.383800; the
highest exposure at any ledger event, counting open reservations, was $1.388231. The account's
usage rose by the reconciled charges to within a tenth of a cent, which is corroborative
aggregate evidence only and does not resolve any individual attempt; the seven reservations
stay counted. The OpenRouter balance after the run is $6.31.

| Attempt | Status | Reason | Charge, USD |
|---|---|---|---|
| probe-X20#a1 | invalid | parse: Unterminated string starting at: line 1 column 152 (char 151) | 0.000050 |
| doc-current-X04-r2#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |
| doc-current-X04-r3#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |
| doc-current-X06-r2#a1 | invalid | finish_reason 'length' | 0.017438 |
| doc-current-X13-r3#a1 | invalid | finish_reason 'length' | 0.023192 |
| doc-current-X14-r1#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |
| doc-saved-X14-r3#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |
| doc-saved-X14-r3#a2 | invalid | finish_reason 'length' | 0.026300 |
| doc-current-X15-r3#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |
| doc-current-X16-r1#a1 | invalid | finish_reason 'length' | 0.016133 |
| doc-saved-X19-r2#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |
| doc-saved-X19-r3#a1 | unresolved | no HTTP response: ReadError: [SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac (_ssl.c:2657) | None |

Ten retries were used, one per request: six after transport failures, three after
output-length loops and one after the malformed probe answer; nine succeeded and one (Qurate's
saved replicate 3, retried after a transport failure) ended in an output-length loop. The
seven transport failures were the same TLS error ("bad record MAC") 0.028 to 0.155 seconds
after dispatch, before any HTTP response, five on bodies above 160,000 tokens and two at
120,000; from the second one on, every request ran in its own process, which did not remove
the fault. The four output-length failures were repetition loops, three inside the direct
rationale and one (Target) later in the qualitative rationale, each running to the 8,192-token
ceiling and charged $0.016 to $0.026; no ceiling was enlarged. Walmart's first probe answer
ended inside a JSON string with a stop reason of "stop"; its retry was valid.

## Protocol evidence

All 104 reconciled responses (83 documents, 21 probes) reported exactly the locally rendered
prompt token count, the pilot probe 165 against 165 and the largest document 242,155 against
242,155. That is accounting equality consistent with compatible chat rendering; it does not
prove that nothing was transformed server-side or that the model attended to every document.
Every response named the authorized model string and the provider DeepInfra and carried a
generation id. 103 of 104 charges were confirmed against the generation record; probe-X03#a1
was reconciled from its response cost alone because its record was unavailable. The
generation payloads themselves were not archived in this run (the runner now archives them).
A strict JSON schema was requested; the provider did not guarantee it, as the malformed probe
answer and the four length loops show. Valid document answers were 441 to 1,029 completion
tokens, median 607.

The 20 probes completed and were reviewed before any document request of their issuer; 19
declined to state a rating, Bath & Body Works gave a Baa3 with low confidence and said its
values were fabricated (flagged for invented action text), and none recalled a post-bound
rating or action; a negative probe does not establish absent memory. The pilot pair (Qurate's
probe and its saved-input document, the largest body) passed the transport, schema, cap and
period checks; seven of its ten figures equalled Opus's saved extraction (debt, dividends and
the working-capital swing differed), and its rationale's claim that the company had emerged
from Chapter 11 is unsupported by the supplied August 4 filing, which describes a confirmed
plan with conditions outstanding. That was a quality observation, not a protocol failure.

The executed run stayed within its guards, and hashes of every body, the code, the prompts
and the primary documents were re-verified by every submitting process. The audit then
demonstrated two defects with fake responses that did not occur in the run: an error
response carrying a charge was released as unbilled, and a response charging more than the
cap was accepted without a halt. Both are repaired with tests (an error response with billing
evidence is reconciled or held unresolved and halts; a charge above its reservation or an
exposure above the cap halts; every process performs its own live price check; generation
payloads are archived). A parse or schema failure of a complete response is recorded with its
charge and does not halt by itself, by design.

## Validity conditions and reading rules, as revised by the review

V1, probes first with flags: met. V2, the 20 by 3 grid with coverage and no bought
replacements: met for the current arm (60 of 60), 19 of 21 for the saved arm. V3, the token
policy: met on every response. V4, provenance per response: met, with one charge reconciled
from the response alone. V5, hashes and date checks: met; the redaction review did not, since
it checked removed lines and agency mentions and could not see the surviving table cells.
V6, one scoring path for both models: met.

R1, persistence is the baseline and is not beaten. R2, exact accuracy on the full eligible
cohort leads the tables, with the original denominators kept and the post-hoc cohorts
labelled as such. R3, agreement with XBRL was not scored as extraction accuracy. R4, the
allowed statement: on 19 post-release disclosure labels, one of which carried its disclosed
rating into the input, Qwen3-235B-A22B-Instruct-2507's judgement scored 17 of 19 exact with
MAE 0.11 against persistence's 18 of 19 and 0.05, with one false alarm on 18 unchanged
issuers, and its scorecard channel 3 of 19 with MAE 1.84; without that issuer, 16 of 18 and
0.11 against 17 of 18 and 0.06; on the seven issuers Opus 4.6 also scored, with the same
supplied information, two of Qwen's three judgement replicates matched Opus's aggregate
4/7 and MAE 0.57. R5, no escalation follows; a second model, more replicates and Arm 2
remain unauthorized (D11 open).

## What is not claimed

Verified outstanding labels at 2026-08-29; successful redaction of every current input;
absent contamination; solved extraction or semantic correctness of the extracted figures;
advance forecasting of any rating action; a demonstrated anchoring mechanism; equivalence to
Opus 4.6 beyond the matched seven; a production-ready runner before the audit's repairs;
generalised superiority of either channel over persistence. The 60 current-input responses
are 20 issuers, not 60 observations, and the current and saved arms differ in pack, peer
policy and trimming, so only the saved arm is a matched-information comparison.

## Corrections applied on 2026-09-13 after the audit

1. The opening now measures against accepted disclosed labels whose validity at t is
   unverified. 2. The Kohl's leak is disclosed, the original 19 kept, the post-hoc 18 added
   (and, from a later scan, Dollar General's short-term rating fragments and a post-hoc 17).
3. The primary judgement MAE is 2/19 = 0.11, not 0.10 (a double rounding in the report).
4. All three replicates equal the prior on 18 of 20, not 19; Signet's replicate 2 is the
   second exception. 5. 56 of 60 direct ratings equal the prior; the five action-field
   contradictions are listed. 6. Matched valid-subset persistence baselines appear in every
   table; the spread table requires three valid ratings. 7. 103 of 104 generation records;
   probe-X03#a1 reconciled from its response; payloads not archived. 8. The pilot probe was
   165 rendered and 165 reported; accounting equality replaces "proved absence of
   compression". 9. The schema was requested, not guaranteed. 10. Six transport retries,
   three length retries, one malformed-probe retry; TLS timing 0.028 to 0.155 seconds.
11. The $1.388231 maximum exposure; the account reading is corroborative only. 12. The two
   demonstrated guard defects and the non-halting parse branch are disclosed. 13. Signet's
   current replicate 3, the net-interest errors, Nike's pretax income and Gap's fiscal date
   are added. 14. The pilot's figure agreement is seven of ten and its emergence claim is
   unsupported. 15. The Opus comparison is limited to matched supplied information and
   specified replicates; equivalence and "2% of the cost" are withdrawn; anchoring and missing
   adjustments are hypotheses. 16. D11 stays open and the two arms are described as differing
   in pack, peer policy and trimming.

## Tables

### Current inputs, all 20 issuers

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 20/20 | 2/20 (10%) | 13/20 (65%) | 1.70 (34/20) | 18/20, MAE 0.15 |
| Scorecard, replicate 2 | 20/20 | 5/20 (25%) | 10/20 (50%) | 1.70 (34/20) | 18/20, MAE 0.15 |
| Scorecard, replicate 3 | 20/20 | 2/20 (10%) | 11/20 (55%) | 2.10 (42/20) | 18/20, MAE 0.15 |
| Scorecard, consensus (median of 3) | 20/20 | 3/20 (15%) | 11/20 (55%) | 1.80 (36/20) | 18/20, MAE 0.15 |
| Judgement, replicate 1 | 20/20 | 17/20 (85%) | 19/20 (95%) | 0.20 (4/20) | 18/20, MAE 0.15 |
| Judgement, replicate 2 | 20/20 | 16/20 (80%) | 19/20 (95%) | 0.25 (5/20) | 18/20, MAE 0.15 |
| Judgement, replicate 3 | 20/20 | 17/20 (85%) | 19/20 (95%) | 0.20 (4/20) | 18/20, MAE 0.15 |
| Judgement, consensus (median of 3) | 20/20 | 17/20 (85%) | 19/20 (95%) | 0.20 (4/20) | 18/20, MAE 0.15 |
| Persistence, full cohort | 20/20 | 18/20 (90%) | 19/20 (95%) | 0.15 (3/20) | |

### Current inputs, primary cohort of 19

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 19/19 | 2/19 (11%) | 12/19 (63%) | 1.74 (33/19) | 18/19, MAE 0.05 |
| Scorecard, replicate 2 | 19/19 | 5/19 (26%) | 10/19 (53%) | 1.68 (32/19) | 18/19, MAE 0.05 |
| Scorecard, replicate 3 | 19/19 | 2/19 (11%) | 10/19 (53%) | 2.16 (41/19) | 18/19, MAE 0.05 |
| Scorecard, consensus (median of 3) | 19/19 | 3/19 (16%) | 10/19 (53%) | 1.84 (35/19) | 18/19, MAE 0.05 |
| Judgement, replicate 1 | 19/19 | 17/19 (89%) | 19/19 (100%) | 0.11 (2/19) | 18/19, MAE 0.05 |
| Judgement, replicate 2 | 19/19 | 16/19 (84%) | 19/19 (100%) | 0.16 (3/19) | 18/19, MAE 0.05 |
| Judgement, replicate 3 | 19/19 | 17/19 (89%) | 19/19 (100%) | 0.11 (2/19) | 18/19, MAE 0.05 |
| Judgement, consensus (median of 3) | 19/19 | 17/19 (89%) | 19/19 (100%) | 0.11 (2/19) | 18/19, MAE 0.05 |
| Persistence, full cohort | 19/19 | 18/19 (95%) | 19/19 (100%) | 0.05 (1/19) | |

### Current inputs, post-hoc 18 without Kohl's

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 18/18 | 2/18 (11%) | 12/18 (67%) | 1.61 (29/18) | 17/18, MAE 0.06 |
| Scorecard, replicate 2 | 18/18 | 5/18 (28%) | 10/18 (56%) | 1.61 (29/18) | 17/18, MAE 0.06 |
| Scorecard, replicate 3 | 18/18 | 2/18 (11%) | 10/18 (56%) | 2.11 (38/18) | 17/18, MAE 0.06 |
| Scorecard, consensus (median of 3) | 18/18 | 3/18 (17%) | 10/18 (56%) | 1.78 (32/18) | 17/18, MAE 0.06 |
| Judgement, replicate 1 | 18/18 | 16/18 (89%) | 18/18 (100%) | 0.11 (2/18) | 17/18, MAE 0.06 |
| Judgement, replicate 2 | 18/18 | 15/18 (83%) | 18/18 (100%) | 0.17 (3/18) | 17/18, MAE 0.06 |
| Judgement, replicate 3 | 18/18 | 16/18 (89%) | 18/18 (100%) | 0.11 (2/18) | 17/18, MAE 0.06 |
| Judgement, consensus (median of 3) | 18/18 | 16/18 (89%) | 18/18 (100%) | 0.11 (2/18) | 17/18, MAE 0.06 |
| Persistence, full cohort | 18/18 | 17/18 (94%) | 18/18 (100%) | 0.06 (1/18) | |

### Current inputs, post-hoc 17 without Kohl's and Dollar General

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 17/17 | 2/17 (12%) | 12/17 (71%) | 1.53 (26/17) | 16/17, MAE 0.06 |
| Scorecard, replicate 2 | 17/17 | 5/17 (29%) | 10/17 (59%) | 1.59 (27/17) | 16/17, MAE 0.06 |
| Scorecard, replicate 3 | 17/17 | 2/17 (12%) | 10/17 (59%) | 2.06 (35/17) | 16/17, MAE 0.06 |
| Scorecard, consensus (median of 3) | 17/17 | 3/17 (18%) | 10/17 (59%) | 1.71 (29/17) | 16/17, MAE 0.06 |
| Judgement, replicate 1 | 17/17 | 16/17 (94%) | 17/17 (100%) | 0.06 (1/17) | 16/17, MAE 0.06 |
| Judgement, replicate 2 | 17/17 | 15/17 (88%) | 17/17 (100%) | 0.12 (2/17) | 16/17, MAE 0.06 |
| Judgement, replicate 3 | 17/17 | 16/17 (94%) | 17/17 (100%) | 0.06 (1/17) | 16/17, MAE 0.06 |
| Judgement, consensus (median of 3) | 17/17 | 16/17 (94%) | 17/17 (100%) | 0.06 (1/17) | 16/17, MAE 0.06 |
| Persistence, full cohort | 17/17 | 16/17 (94%) | 17/17 (100%) | 0.06 (1/17) | |

### Saved Experiment 03 inputs, the seven Opus successes, and Opus 4.6 on the same inputs

**Seven**

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 7/7 | 2/7 (29%) | 5/7 (71%) | 1.86 (13/7) | 5/7, MAE 0.43 |
| Scorecard, replicate 2 | 6/7 | 2/7 (29%) | 4/6 (67%) | 1.00 (6/6) | 4/6, MAE 0.50 |
| Scorecard, replicate 3 | 5/7 | 0/7 (0%) | 4/5 (80%) | 1.80 (9/5) | 4/5, MAE 0.20 |
| Scorecard, consensus (median of 3) | 4/7 | 1/7 (14%) | 4/4 (100%) | 0.75 (3/4) | 3/4, MAE 0.25 |
| Judgement, replicate 1 | 7/7 | 4/7 (57%) | 6/7 (86%) | 0.57 (4/7) | 5/7, MAE 0.43 |
| Judgement, replicate 2 | 7/7 | 4/7 (57%) | 6/7 (86%) | 0.57 (4/7) | 5/7, MAE 0.43 |
| Judgement, replicate 3 | 5/7 | 3/7 (43%) | 5/5 (100%) | 0.40 (2/5) | 4/5, MAE 0.20 |
| Judgement, consensus (median of 3) | 5/7 | 3/7 (43%) | 5/5 (100%) | 0.40 (2/5) | 4/5, MAE 0.20 |
| Persistence, full cohort | 7/7 | 5/7 (71%) | 6/7 (86%) | 0.43 (3/7) | |

**Six without Qurate**

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 6/6 | 2/6 (33%) | 4/6 (67%) | 2.00 (12/6) | 5/6, MAE 0.17 |
| Scorecard, replicate 2 | 5/6 | 2/6 (33%) | 4/5 (80%) | 0.80 (4/5) | 4/5, MAE 0.20 |
| Scorecard, replicate 3 | 5/6 | 0/6 (0%) | 4/5 (80%) | 1.80 (9/5) | 4/5, MAE 0.20 |
| Scorecard, consensus (median of 3) | 4/6 | 1/6 (17%) | 4/4 (100%) | 0.75 (3/4) | 3/4, MAE 0.25 |
| Judgement, replicate 1 | 6/6 | 4/6 (67%) | 6/6 (100%) | 0.33 (2/6) | 5/6, MAE 0.17 |
| Judgement, replicate 2 | 6/6 | 4/6 (67%) | 6/6 (100%) | 0.33 (2/6) | 5/6, MAE 0.17 |
| Judgement, replicate 3 | 5/6 | 3/6 (50%) | 5/5 (100%) | 0.40 (2/5) | 4/5, MAE 0.20 |
| Judgement, consensus (median of 3) | 5/6 | 3/6 (50%) | 5/5 (100%) | 0.40 (2/5) | 4/5, MAE 0.20 |
| Persistence, full cohort | 6/6 | 5/6 (83%) | 6/6 (100%) | 0.17 (1/6) | |

**Opus 4.6 on the same saved inputs (Experiment 03, corrected arithmetic, one response each)**

| Channel | Valid / planned | Exact | Within one | MAE | Persistence on the same valid issuers |
|---|---|---|---|---|---|
| Scorecard, seven | 7/7 | 3/7 (43%) | 6/7 (86%) | 1.14 (8/7) | 5/7, MAE 0.43 |
| Judgement, seven | 7/7 | 4/7 (57%) | 6/7 (86%) | 0.57 (4/7) | 5/7, MAE 0.43 |
| Persistence, full cohort | 7/7 | 5/7 (71%) | 6/7 (86%) | 0.43 (3/7) | |
| Scorecard, six | 6/6 | 3/6 (50%) | 5/6 (83%) | 1.17 (7/6) | 5/6, MAE 0.17 |
| Judgement, six | 6/6 | 4/6 (67%) | 5/6 (83%) | 0.50 (3/6) | 5/6, MAE 0.17 |
| Persistence, full cohort | 6/6 | 5/6 (83%) | 6/6 (100%) | 0.17 (1/6) | |

### Changed and unchanged diagnostics, current inputs, 19 primary

| Channel | Changed valid | Changed exact | Direction correct | Unchanged valid | False alarms |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 1 | 0 | 0 | 18 | 16 |
| Scorecard, replicate 2 | 1 | 0 | 0 | 18 | 13 |
| Scorecard, replicate 3 | 1 | 0 | 0 | 18 | 16 |
| Scorecard, consensus | 1 | 0 | 0 | 18 | 15 |
| Judgement, replicate 1 | 1 | 0 | 0 | 18 | 1 |
| Judgement, replicate 2 | 1 | 0 | 0 | 18 | 2 |
| Judgement, replicate 3 | 1 | 0 | 0 | 18 | 1 |
| Judgement, consensus | 1 | 0 | 0 | 18 | 1 |

### Changed and unchanged diagnostics, current inputs, post-hoc 18

| Channel | Changed valid | Changed exact | Direction correct | Unchanged valid | False alarms |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 1 | 0 | 0 | 17 | 15 |
| Scorecard, replicate 2 | 1 | 0 | 0 | 17 | 12 |
| Scorecard, replicate 3 | 1 | 0 | 0 | 17 | 15 |
| Scorecard, consensus | 1 | 0 | 0 | 17 | 14 |
| Judgement, replicate 1 | 1 | 0 | 0 | 17 | 1 |
| Judgement, replicate 2 | 1 | 0 | 0 | 17 | 2 |
| Judgement, replicate 3 | 1 | 0 | 0 | 17 | 1 |
| Judgement, consensus | 1 | 0 | 0 | 17 | 1 |

### Changed and unchanged diagnostics, current inputs, all 20

| Channel | Changed valid | Changed exact | Direction correct | Unchanged valid | False alarms |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 2 | 0 | 1 | 18 | 16 |
| Scorecard, replicate 2 | 2 | 0 | 0 | 18 | 13 |
| Scorecard, replicate 3 | 2 | 0 | 1 | 18 | 16 |
| Scorecard, consensus | 2 | 0 | 1 | 18 | 15 |
| Judgement, replicate 1 | 2 | 0 | 0 | 18 | 1 |
| Judgement, replicate 2 | 2 | 0 | 0 | 18 | 2 |
| Judgement, replicate 3 | 2 | 0 | 0 | 18 | 1 |
| Judgement, consensus | 2 | 0 | 0 | 18 | 1 |

### Changed and unchanged diagnostics, saved inputs, seven

| Channel | Changed valid | Changed exact | Direction correct | Unchanged valid | False alarms |
|---|---|---|---|---|---|
| Scorecard, replicate 1 | 2 | 0 | 2 | 5 | 3 |
| Scorecard, replicate 2 | 2 | 0 | 1 | 4 | 2 |
| Scorecard, replicate 3 | 1 | 0 | 1 | 4 | 4 |
| Scorecard, consensus | 1 | 0 | 1 | 3 | 2 |
| Judgement, replicate 1 | 2 | 0 | 0 | 5 | 1 |
| Judgement, replicate 2 | 2 | 0 | 0 | 5 | 1 |
| Judgement, replicate 3 | 1 | 0 | 0 | 4 | 1 |
| Judgement, consensus | 1 | 0 | 0 | 4 | 1 |

### Per issuer, current inputs

| ID | Issuer | Persistence | Label | Scorecard r1, r2, r3 | Scorecard consensus | Judgement r1, r2, r3 | Judgement consensus | FY label |
|---|---|---|---|---|---|---|---|---|
| X01 | bath-body-works | Ba2 | Ba2 | Ba2, Ba2, Ba1 | Ba2 | Ba2, Ba2, Ba2 | Ba2 | 2025; FY ending 2026-01-31 |
| X02 | best-buy-co | A3 | A3 | A3, A3, A3 | A3 | A3, A3, A3 | A3 | FY 2026; FY ending 2026-01-31 |
| X03 | dick-s-sporting-goods | Baa2 | Baa2 | Baa3, Baa3, Baa3 | Baa3 | Baa2, Baa2, Baa2 | Baa2 | 2026; FY 2026 (ended 2026-01-31) |
| X04 | dollar-general | Baa3 | Baa3 | A3, Baa1, A3 | A3 | Baa2, Baa2, Baa2 | Baa2 | 2025; FY ending 2026-01-30 |
| X05 | floor-decor | Ba3 | Ba3 | Baa3, Baa3, Baa3 | Baa3 | Ba3, Ba3, Ba3 | Ba3 | FY 2025; FY ending 2025-12-25 |
| X06 | gap-inc-the | Ba2 | Ba2 | Baa3, Baa2, Baa3 | Baa3 | Ba2, Ba2, Ba2 | Ba2 | 2025-01-31; FY 2025; FY 2026 |
| X07 | kohl-s | B2 | B2 | Ba1, Ba2, Ba2 | Ba2 | B2, B2, B2 | B2 | 2025; 2026; FY ending 2026-01-31 |
| X08 | leslie-s-poolmart | Caa3 | Caa3 | Caa2, Caa3, B3 | Caa2 | Caa3, Caa3, Caa3 | Caa3 | FY 2025; FY ending 2025-10-04 |
| X09 | levi-strauss | Ba1 | Ba1 | Baa3, A2, A2 | A2 | Ba1, Ba1, Ba1 | Ba1 | 2025-11-30; FY ending 2025-11-30 |
| X10 | lowe-s-companies | Baa1 | Baa1 | Baa2, Baa2, Baa2 | Baa2 | Baa1, Baa1, Baa1 | Baa1 | 2025; 2026; FY 2025 |
| X11 | macy-s | Ba1 | Ba1 | Baa3, Baa3, Baa3 | Baa3 | Ba1, Ba1, Ba1 | Ba1 | 2025 |
| X12 | nike | A1 | A2 (changed) | Aa2, Aa3, A1 | Aa3 | A1, A1, A1 | A1 | 2026-05-31; FY2026 |
| X13 | pvh | Baa3 | Baa3 | Ba2, Ba2, Ba2 | Ba2 | Baa3, Baa3, Baa3 | Baa3 | 2025; FY2026 |
| X14 | qurate-qvc | Caa1 | Caa3 (changed) | Caa2, Caa1, Caa2 | Caa2 | Caa1, Caa1, Caa1 | Caa1 | 2025; FY 2025 |
| X15 | signet | Ba3 | Ba3 | A3, Baa1, Aa2 | A3 | Ba3, B1, Ba3 | Ba3 | FY 2026 (ended 2026-01-31); FY ending 2026-01-31 |
| X16 | target | A2 | A2 | A1, Aa3, Aa3 | Aa3 | A2, A2, A2 | A2 | 2026-01-31; FY 2025 |
| X17 | tractor-supply | Baa1 | Baa1 | Baa2, Baa1, Baa1 | Baa1 | Baa1, Baa1, Baa1 | Baa1 | 2025-12-27; FY 2025; FY ending 2025-12-27 |
| X18 | v-f | Ba2 | Ba2 | Ba1, Ba1, Ba1 | Ba1 | Ba2, Ba2, Ba2 | Ba2 | FY 2026 (ended 2026-03-28); FY ending 2026-03-28 |
| X19 | victoria-s-secret | Ba3 | Ba3 | B1, B1, B1 | B1 | Ba3, Ba3, Ba3 | Ba3 | 2025; 2026 |
| X20 | walmart | Aa2 | Aa2 | Aa3, Aa2, Aa3 | Aa3 | Aa2, Aa2, Aa2 | Aa2 | FY ending 2026-01-31; FY2026 |

### Per issuer, saved inputs

| ID | Issuer | Persistence | Label | Scorecard r1, r2, r3 | Scorecard consensus | Judgement r1, r2, r3 | Judgement consensus | FY label |
|---|---|---|---|---|---|---|---|---|
| X12 | nike | A1 | A2 (changed) | A3, A3, A3 | A3 | A1, A1, A1 | A1 | FY 2026; FY 2026 (ended 2026-05-31); FY2026 |
| X14 | qurate-qvc | Caa1 | Caa3 (changed) | Caa2, Caa1, none | incomplete: 2 of 3 valid | Caa1, Caa1, none | incomplete: 2 of 3 valid | 2025; 2025-12-31 |
| X15 | signet | Ba3 | Ba3 | A1, fail, Baa1 | incomplete: 2 of 3 valid | Ba2, Ba3, Ba2 | Ba2 | FY 2026; Fiscal 2026; Fiscal 2026 (ended January 31, 2026) |
| X16 | target | A2 | A2 | A2, A1, A1 | A1 | A2, A2, A2 | A2 | 2025; FY ending 2026-01-31 |
| X17 | tractor-supply | Baa1 | Baa1 | Baa2, Baa1, Baa2 | Baa2 | Baa1, Baa1, Baa1 | Baa1 | 2025-12-27; FY ending 2025-12-27 |
| X19 | victoria-s-secret | Ba3 | Ba3 | Ba1, Ba1, none | incomplete: 2 of 3 valid | Ba3, Ba2, none | incomplete: 2 of 3 valid | 2025 |
| X20 | walmart | Aa2 | Aa2 | Aa2, Aa2, Aa3 | Aa2 | Aa2, Aa2, Aa2 | Aa2 | FY ending 2026-01-31 |

### Replicate spread (partial observed spread where a replicate is missing)

- current inputs, scorecard: spread 0 on 8, 1 on 8, more than 1 on 4, undefined on 0 of 20 issuers.
- current inputs, judgement: spread 0 on 19, 1 on 1, more than 1 on 0, undefined on 0 of 20 issuers.
- current inputs: qualitative grades identical across the three replicates on 8 of 20 issuers.
- saved inputs, scorecard: spread 0 on 2, 1 on 4, more than 1 on 1, undefined on 0 of 7 issuers.
- saved inputs, judgement: spread 0 on 5, 1 on 2, more than 1 on 0, undefined on 0 of 7 issuers.
- saved inputs: qualitative grades identical across the three replicates on 2 of 7 issuers.

## Files

runs/EXP04-ARM1-A1/ (gitignored): manifest.json and bodies/ (the frozen plan and every body),
ledger.jsonl (every reservation, dispatch, charge, failure, halt and reviewer note),
responses/ (raw bytes of every response), audit/ (per-issuer document and pack provenance,
the saved-input evidence, removed lines, probes, residual scan, hashes, environment),
gates/ (the acceptance-gate evidence and the test run before the pilot), probe_review.json,
pilot_review.json, results/ (attempts, flat records per arm and replicate, consensus,
scores.json, report.md), submit-documents.log and drive_per_request.py. The audit is
review-codex-2026-09-13.md.
