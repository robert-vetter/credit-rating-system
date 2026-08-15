# Blinding mini-test: can the model be stopped from knowing who it is rating?

*Analysis and write-up by Claude (Opus 5), directed by Robert Vetter, August 2026. Purpose: before
building the blinding ladder from the experiment plan, test cheaply whether blinding holds at all on
the seven companies already studied. Fourteen de-anonymisation probes were run as fresh sessions with
no conversation history. Tool non-use was verified structurally this time: the harness reports tool
calls per session, and all fourteen sessions show zero, which fixes the self-report weakness of the
earlier blind test. The probes ran on a frontier model, which makes the result an upper bound on
identification ability, the conservative direction for a feasibility check.*

## Design

Each probe presents an anonymised financial profile of one of the seven companies (US retail or
apparel, fiscal year ended early 2026) and asks for the single most likely company, with confidence
and up to two alternates.

**Condition A, exact numbers.** Revenue, EBITDA, adjusted debt, cash, capex, interest, dividends, all
as extracted in the earlier runs, in USD millions.

**Condition B, coarsened.** Revenue replaced by its scorecard band (for example "between $10bn and
$25bn"), everything else reduced to the three scorecard ratios plus dividend-payer status. This tests
whether the coarsest input the scorecard could still work with defeats identification.

## Results

| Company | A: exact numbers | B: band plus ratios |
|---|---|---|
| Walmart | identified, high | identified, high |
| Target | identified, high | identified, high |
| Dollar General | identified, high | identified, high |
| Macy's | identified, high | **wrong** (guessed Gap, medium; Macy's named as alternate) |
| Kohl's | identified, high | identified, medium |
| Gap | identified, high | identified, high |
| Victoria's Secret | identified, medium | identified, medium |

Condition A: **7 of 7** top-guess correct. Condition B: **6 of 7** top-guess correct, 7 of 7 within
the top three.

## Finding 1: exact numbers do not blind, at any size in this sample

Every company was identified from seven numbers. Two fingerprints did most of the work, and both are
structural rather than accidental:

**Dividends paid is a quasi-identifier.** It equals the public per-share dividend times the public
share count, so it uniquely tags a company even when everything else is rounded. Probes repeatedly
called it the clincher: Target's 2,053, Dollar General's 520, Kohl's post-cut 56, Macy's 197. It
cannot simply be dropped, because dividend behaviour feeds the Financial Policy subfactor and RCF.
This is the same signal-versus-leak tension the leakage audit found in Dollar General's fair-value
note.

**Debt composition is a fingerprint.** The split between funded debt and lease liabilities identified
Gap (small bonds, large lease book) and Kohl's (unusually large financing obligations from
sale-leasebacks) by shape alone.

## Finding 2: coarsening helps only where the band is crowded and the ratios are ordinary

The one blinding success, Macy's, happened in the only configuration where both conditions held: the
$10-25bn band contains several dividend-paying retailers, and Macy's ratio triple (3.0x, 8.2x, 37%)
is unremarkable within it. The probe guessed Gap and was wrong.

Everywhere else, identification survived coarsening through three routes: sparse bands (above $100bn
there are four candidates, in $25-50bn about three), distinctive ratios inside a crowded band (Gap's
74% RCF/net debt was called "the real fingerprint", Kohl's 5.0x leverage likewise), and elimination on
the fiscal-calendar-plus-dividend-status grid, which several probes ran explicitly.

## Finding 3: everything in the input leaks, including the framing

Two side observations that matter for building the real ladder. The Condition B prompt for Kohl's
described the dividend as "small", and the probe used exactly that adjective to finish the
identification; even qualitative descriptors are signal. And several probes remarked that the metric
set "reads like a Moody's credit opinion", meaning the adjusted-metrics framing itself tells the
model what context it is in. Blinding has to treat the whole prompt as the attack surface, not just
the named fields.

## Consequences for the experiment plan

**Rung 2 of the blinding ladder (blinded documents) is not viable for issuers of this profile.** If
seven numbers identify all seven companies, a full filing, with brand names, store counts, segment
language and litigation history, has no chance. For large, well-covered issuers, blinding is not a
usable lever, which shifts the full weight of contamination control onto the other two levers: the
rating path in the input (Task B) and the post-cutoff changed subset.

**Blinding may still work lower down the size distribution**, where bands are crowded and coverage is
thin, but that is exactly where it must be verified per sample. The de-anonymisation probe did its job
here at one cheap call per sample and stays mandatory wherever a blinded condition is claimed.

**Scoring rule for the real runs:** grade identification strictly on the top guess, but record the
alternates; Macy's counting as "blinded" while sitting in the alternates list shows the strict rule
flatters the blinding, so both should be reported.

## Caveats

Seven companies, all large, all US retail, all heavily covered; this is the hostile end of the
distribution for blinding, chosen deliberately. The probes ran as harness sessions rather than raw API
calls; tool non-use is verified by telemetry, but the production runs should still use the raw API as
specified in the plan. One probe's recollection of a Kohl's downgrade level was wrong in passing,
which is consistent with the earlier finding that model memory is confidently unreliable off the most
famous names.
