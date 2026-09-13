# Experiment 04, Arm 1 results: a post-release, history-conditioned disclosure-label pilot on Qwen3-235B-A22B-Instruct-2507

*Written 2026-09-13 by Claude (Fable 5.1), directed by Robert Vetter. Model runs on 2026-09-13
from 01:00 to 04:00 UTC under authorization EXP04-ARM1-A1 (decisions D5 to D12 in
decisions.md), through OpenRouter to DeepInfra's fp8 endpoint. Every number below was
computed offline from the append-only ledger, the raw responses, the frozen manifest and the
audit files under runs/EXP04-ARM1-A1/ (gitignored, on this machine) by `run_openrouter.py
score` and `report.py`, which score both models through `evaluation/pipeline/score_run.py`.
The specification as executed is RUN-SPEC.md; the review that shaped it is
review-codex-2026-09-12.md. Nothing has been sent to the lab.*

## What this measures

The outstanding Moody's rating at 2026-08-29 for 20 Retail and Apparel issuers, as the
issuers themselves disclosed it in filings after the 2025-09-30 boundary, estimated by an
open-weight model whose public checkpoint was released on 2025-07-21, from the latest 10-K
and subsequent 10-Qs (rating disclosures redacted) plus a history pack that ends on
2025-08-28. Two channels: the scorecard computed by `system/scorecard.py` from the ten
figures and four grades the model extracts, and the model's own overall judgement. Three
replicates per issuer at temperature 0. Two arms: the current, repaired inputs for all 20
(the main measurement), and the exact saved inputs Opus 4.6 saw in Experiment 03 for the
seven issuers it scored (the model comparison). One memory probe per issuer ran first.

The labels are hand-read company disclosures whose validity at the observation date is not
established. Qurate's label predates the bankruptcy described in its input filings and names
a subsidiary's corporate family rating, so the primary cohort is the other 19 and Qurate is a
diagnostic (decision D8). Persistence is the rating in effect at the history end: exact on 18
of 19 and on 18 of 20.

## Headline, primary cohort of 19

| Channel, consensus of three replicates | Exact | Within one notch | MAE, notches | False alarms on 18 unchanged |
|---|---|---|---|---|
| Model judgement | 17/19 (89%) | 19/19 | 0.10 | 1 |
| Scorecard from extracted inputs | 3/19 (16%) | 10/19 | 1.84 | 15 |
| Persistence | 18/19 (95%) | 19/19 | 0.05 | 0 |

On all 20, the judgement is 17/20 exact with MAE 0.20, the scorecard 3/20 with MAE 1.80, and
persistence 18/20 with MAE 0.15. Every replicate is within a notch of these consensus figures
(tables below). The single changed case in the primary cohort, Nike A1 to A2, was missed by
the judgement (A1 in every replicate) and moved the wrong way by the scorecard (Aa3
consensus). Qurate, Caa1 to Caa3, was missed by the judgement (Caa1) and moved the right way
but one notch short by the scorecard (Caa2).

## Reading

Neither channel beats persistence, and with one or two changed cases none could be shown to.
The judgement channel is persistence with one false alarm: on 19 of 20 issuers all three
replicates returned the rating from the history pack, and the model's own field
`vs_last_known` says "unchanged" in 52 of 60 current-input responses. The one exception is
Dollar General, where all three replicates said "upgrade" to Baa2 against a Baa3 label. The
scorecard channel is systematically favourable, as the calibration study and Experiment 03
found: of 60 valid current-input responses, 36 rate the issuer higher than its label, 9
exactly and 15 lower, a mean signed error of 1.23 notches in the issuer's favour. That is
arithmetic on the model's extracted figures and grades, not a rating judgement, and it is
where the replicates disagree: the judgement's spread is zero on 19 of 20 issuers, the
scorecard's exceeds one notch on 4 (Levi Strauss Baa3, A2, A2; Signet A3, Baa1, Aa2; Nike
Aa2, Aa3, A1; Target A1, Aa3, Aa3), and the four qualitative grades agree across the three
replicates on only 8 of 20 issuers.

On the seven issuers Opus 4.6 scored, with byte-identical inputs, Qwen's judgement replicates
1 and 2 give exactly Opus's numbers, 4/7 exact, 6/7 within one, MAE 0.57, and replicate 3
gives 3/7 with two responses missing. Its scorecard is worse and less stable than Opus's
(2/7 exact and MAE 1.86 in replicate 1 against Opus's 3/7 and 1.14), with one undefined
ratio (Signet, replicate 2, where the model returned zero interest and zero debt). The
comparison is between selected Opus successes on matched information and different inference
settings: Opus used adaptive high-effort thinking, Qwen is a non-thinking fp8 deployment at
temperature 0 with a JSON schema enforced by the provider.

## Coverage, attempts and spend

Planned: 20 probes, 60 current-input and 21 saved-input document requests. Dispatched: 111
attempts, the 101 planned plus the ten extra attempts Robert allowed. Valid: 20 probes and
79 of 81 document requests. Two requests have no valid response: Qurate's third saved-input
replicate (a transport failure, then an output-length loop on its single retry) and
Victoria's Secret's third saved-input replicate (a transport failure with no retry allowance
left). One valid response has a failed scorecard channel (Signet, saved inputs, replicate 2)
and a retained direct rating. All 60 current-input requests are valid.

Spend: $1.242279 committed for 104 reconciled responses (exact provider charges sum to
$1.242229), plus $0.141521 held for the seven attempts that failed before any HTTP response,
whose billing the runner treats as unknown. Total against the $3.00 cap: $1.383800. The
account's usage rose from 47.4475 to 48.6897 credits, a difference equal to the reconciled
charges within a tenth of a cent, so the seven held attempts were most likely never billed;
they stay counted. The OpenRouter balance after the run is $6.31.

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

Ten retries were used, one per request: nine succeeded and one (Qurate's saved replicate 3)
ended in a second failure of a different kind. Seven transport failures were the same TLS
error ("bad record MAC") within a tenth of a second of dispatch, five of them on bodies above
160,000 tokens and two at 120,000; after the second one every request ran in its own process
with a fresh connection, which did not remove the fault. Four output-length failures were
repetition loops inside a rationale string that ran to the 8,192-token ceiling with a normal
stop reason absent; each cost between $0.016 and $0.026 and was recorded, and no ceiling was
enlarged. Walmart's first probe answer ended inside a JSON string with a stop reason of
"stop"; its retry was valid.

## Protocol evidence

Every one of the 104 reconciled responses reported exactly the locally rendered prompt token
count (difference 0 on all of them), so the provider applied the same chat template as the
local tokenizer, injected no schema text and compressed nothing. Every response named the
authorized model string and the provider DeepInfra and carried a generation id; the charge in
each response equalled the generation record's total. Valid document answers were 441 to
1,029 completion tokens, median 607. The 20 probes completed and were reviewed before any
document request of their issuer; none recalled a post-bound rating or action, 18 declined to
state any rating, Bath & Body Works produced a Baa3 with low confidence and stated that its
values were fabricated, and Walmart's valid retry declined. The pilot pair (Qurate's probe
and its saved-input document, the largest body) passed the review's acceptance conditions
before the rest ran (pilot_review.json). Hashes of every body, the code, the prompts and the
primary documents were re-verified by every submitting process; the manifest hash is bound
to authorization.json.

## Validity conditions and reading rules, as revised by the review

V1, probes first with flags: met; one flag, Bath & Body Works' invented action text; no
issuer excluded on probe grounds. V2, the 20 by 3 grid with per-channel coverage and no bought
replacements: met for the current arm (60 of 60), 19 of 21 for the saved arm, both reported
with their denominators. V3, the rendered-count token policy: met on every response. V4,
provenance per response: met. V5, hashes and date checks: met (audit/current, audit/legacy,
preflight in every process). V6, one scoring path for both models: met.

R1, persistence is the baseline and is not beaten. R2, exact accuracy on the full eligible
cohort leads the tables. R3, agreement with XBRL was not scored as extraction accuracy. R4,
the allowed statement: on 19 post-release disclosure labels, Qwen3-235B-A22B-Instruct-2507's
judgement scored 17 of 19 exact with MAE 0.10 against persistence's 18 of 19 and 0.05, with
one false alarm on 18 unchanged issuers, and its scorecard channel 3 of 19 with MAE 1.84; on
the seven issuers Opus 4.6 also scored, the two models' judgement MAEs on identical inputs
were 0.57 and 0.57. R5, no escalation follows from these numbers; a second model, more
replicates and Arm 2 remain unauthorized.

## What is not claimed

Verified outstanding labels at 2026-08-29; absent contamination (a release-date bound and
negative probes do not establish it); solved extraction (the scorecard channel's figures vary
across replicates and one response returned zero debt for Signet); advance forecasting of any
rating action; equivalence to Opus 4.6 beyond the matched seven; generalised superiority of
either channel over persistence. The 60 current-input responses are 20 issuers, not 60
observations.

## Tables

### Current inputs, all 20 issuers

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) |
|---|---|---|---|---|
| Scorecard, replicate 1 | 20/20 | 2/20 (10%) | 13/20 (65%) | 1.70 |
| Scorecard, replicate 2 | 20/20 | 5/20 (25%) | 10/20 (50%) | 1.70 |
| Scorecard, replicate 3 | 20/20 | 2/20 (10%) | 11/20 (55%) | 2.10 |
| Scorecard, consensus (median of 3) | 20/20 | 3/20 (15%) | 11/20 (55%) | 1.80 |
| Judgement, replicate 1 | 20/20 | 17/20 (85%) | 19/20 (95%) | 0.20 |
| Judgement, replicate 2 | 20/20 | 16/20 (80%) | 19/20 (95%) | 0.25 |
| Judgement, replicate 3 | 20/20 | 17/20 (85%) | 19/20 (95%) | 0.20 |
| Judgement, consensus (median of 3) | 20/20 | 17/20 (85%) | 19/20 (95%) | 0.20 |
| Persistence | 20/20 | 18/20 (90%) | 19/20 (95%) | 0.15 |

### Current inputs, primary cohort of 19

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) |
|---|---|---|---|---|
| Scorecard, replicate 1 | 19/19 | 2/19 (11%) | 12/19 (63%) | 1.74 |
| Scorecard, replicate 2 | 19/19 | 5/19 (26%) | 10/19 (53%) | 1.68 |
| Scorecard, replicate 3 | 19/19 | 2/19 (11%) | 10/19 (53%) | 2.16 |
| Scorecard, consensus (median of 3) | 19/19 | 3/19 (16%) | 10/19 (53%) | 1.84 |
| Judgement, replicate 1 | 19/19 | 17/19 (89%) | 19/19 (100%) | 0.10 |
| Judgement, replicate 2 | 19/19 | 16/19 (84%) | 19/19 (100%) | 0.16 |
| Judgement, replicate 3 | 19/19 | 17/19 (89%) | 19/19 (100%) | 0.10 |
| Judgement, consensus (median of 3) | 19/19 | 17/19 (89%) | 19/19 (100%) | 0.10 |
| Persistence | 19/19 | 18/19 (95%) | 19/19 (100%) | 0.05 |

### Saved Experiment 03 inputs, the seven Opus successes, and Opus 4.6 on the same inputs

**Seven**

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) |
|---|---|---|---|---|
| Scorecard, replicate 1 | 7/7 | 2/7 (29%) | 5/7 (71%) | 1.86 |
| Scorecard, replicate 2 | 6/7 | 2/7 (29%) | 4/6 (67%) | 1.00 |
| Scorecard, replicate 3 | 5/7 | 0/7 (0%) | 4/5 (80%) | 1.80 |
| Scorecard, consensus (median of 3) | 4/7 | 1/7 (14%) | 4/4 (100%) | 0.75 |
| Judgement, replicate 1 | 7/7 | 4/7 (57%) | 6/7 (86%) | 0.57 |
| Judgement, replicate 2 | 7/7 | 4/7 (57%) | 6/7 (86%) | 0.57 |
| Judgement, replicate 3 | 5/7 | 3/7 (43%) | 5/5 (100%) | 0.40 |
| Judgement, consensus (median of 3) | 5/7 | 3/7 (43%) | 5/5 (100%) | 0.40 |
| Persistence | 7/7 | 5/7 (71%) | 6/7 (86%) | 0.43 |

**Six without Qurate**

| Channel | Valid / planned | Exact (over planned) | Within one (over valid) | MAE (over valid) |
|---|---|---|---|---|
| Scorecard, replicate 1 | 6/6 | 2/6 (33%) | 4/6 (67%) | 2.00 |
| Scorecard, replicate 2 | 5/6 | 2/6 (33%) | 4/5 (80%) | 0.80 |
| Scorecard, replicate 3 | 5/6 | 0/6 (0%) | 4/5 (80%) | 1.80 |
| Scorecard, consensus (median of 3) | 4/6 | 1/6 (17%) | 4/4 (100%) | 0.75 |
| Judgement, replicate 1 | 6/6 | 4/6 (67%) | 6/6 (100%) | 0.33 |
| Judgement, replicate 2 | 6/6 | 4/6 (67%) | 6/6 (100%) | 0.33 |
| Judgement, replicate 3 | 5/6 | 3/6 (50%) | 5/5 (100%) | 0.40 |
| Judgement, consensus (median of 3) | 5/6 | 3/6 (50%) | 5/5 (100%) | 0.40 |
| Persistence | 6/6 | 5/6 (83%) | 6/6 (100%) | 0.17 |

**Opus 4.6 on the same saved inputs (Experiment 03, corrected arithmetic, one response each)**

| Channel | Valid / planned | Exact | Within one | MAE |
|---|---|---|---|---|
| Scorecard, seven | 7/7 | 3/7 (43%) | 6/7 (86%) | 1.14 |
| Judgement, seven | 7/7 | 4/7 (57%) | 6/7 (86%) | 0.57 |
| Persistence | 7/7 | 5/7 (71%) | 6/7 (86%) | 0.43 |
| Scorecard, six | 6/6 | 3/6 (50%) | 5/6 (83%) | 1.17 |
| Judgement, six | 6/6 | 4/6 (67%) | 5/6 (83%) | 0.50 |
| Persistence | 6/6 | 5/6 (83%) | 6/6 (100%) | 0.17 |

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

### Replicate spread

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
gates/ (the acceptance-gate evidence and the forty-test run), probe_review.json,
pilot_review.json, results/ (attempts, flat records per arm and replicate, consensus,
scores.json, report.md), submit-documents.log and drive_per_request.py.
