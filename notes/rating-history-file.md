# The Moody's 17g-7(b) rating history files, pulled and parsed

*Analysis and write-up by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert registered
the Moody's account and downloaded both file sets; the model parsed them. Everything below is computed
directly from the files, dated 11 August 2026, stored locally under `data/` (gitignored, not
redistributed, pending the open terms-of-use question).*

## What the files are

Two sets, both in the SEC's ROCR XBRL format, one small XML per entity:

| Set | Files | Content |
|---|---|---|
| Obligor | 21,383 | Entity-level ratings: corporate family ratings, issuer ratings, probability of default. One file per obligor with its full action history since June 2012 |
| Issuer | 65,535 | Instrument-level ratings: one record per security with CUSIP, coupon, maturity, par value, and that instrument's own action history |

Parsed totals from the obligor set: 106,590 rating actions across 21,383 obligors. By class: 8,589 US
Public, **8,146 Corporate**, 2,774 Financial, 1,189 Insurance, 512 international public, 171
Sovereign. Action codes: NW (new), UP, DG, HS (history start, the rating outstanding at the June 2012
regime start), and several withdrawal codes; a small residue of records carries no code and needs a
second look.

## Finding 1: the 12-month embargo is real and fully used

The file set is dated 11 August 2026. The most recent rating action in it is from **August 2025**.
Moody's uses the entire delay the rule permits, to the month.

Consequences, now measured rather than feared. The public file provides complete rating paths and
persistence baselines **up to twelve months ago**, which fully powers the historical arm of the
evaluation: the pre-cutoff side of the within-model contrast, the persistence baseline, and the Task B
rating-path inputs for observation dates up to August 2025. It provides **nothing** for the
post-cutoff clean window. For that window the labels must come from the lab's dataset or another
source, which upgrades the lab-dataset question from important to strictly blocking for the
clean-window arm.

## Finding 2: the label pipeline must join both file sets

The methodology's label rule (senior unsecured for investment grade, corporate family rating for
speculative grade) maps onto the files in a way the files themselves demonstrate:

Dollar General shows the investment-grade side. Its CFR was withdrawn in March 2013, when it crossed
into investment grade; from then on its rating lives at instrument level, as Senior Unsecured records
in the issuer set, where the March 2025 downgrade from Baa2 to Baa3 sits with its exact date.

Kohl's and Macy's show the other direction: when a company falls out of investment grade, a CFR is
newly assigned (Kohl's on 12 December 2022, Macy's in March 2020).

So investment-grade labels generally require the issuer set, speculative-grade labels the obligor
set, and transitions move an issuer from one to the other. The evaluation harness needs to encode
this.

## Finding 3: all seven labels verified, one open defect closed

| Company | Label used so far | File says | Verdict |
|---|---|---|---|
| Walmart | Aa2 | LT Issuer Rating Aa2, **zero actions since the 2012 history start** | confirmed |
| Target | A2 | LT Issuer Rating A2, zero actions since 2012 | confirmed |
| Dollar General | Baa3 | Senior Unsecured Baa2 to Baa3 on 2025-03-28 | confirmed, dated |
| Macy's | Ba1 (was flagged unverified) | CFR path Ba1, Ba3, Ba2, then **Ba1 up on 2022-02-23**, unchanged through the file end | **confirmed, defect closed** |
| Kohl's | B2 | CFR Ba3 to **B2 on 2025-05-13** | confirmed, dated |
| Gap | Ba2 | CFR Ba3 to **Ba2 up on 2025-02-20**, unchanged through file end | confirmed; the memory probe's "Ba1" was genuinely wrong |
| Victoria's Secret | Ba3 | CFR Ba3 new on 2021-06-21, unchanged | confirmed |

The Macy's which-rating defect from the assumptions review is resolved: the filing's "long-term debt
Ba1" coincides with the CFR, so the blind test's one exact hit stands. The verification covers the
file window (through August 2025); the filings themselves, dated January to March 2026, independently
show the same values at their own dates, so the labels are now confirmed by two sources at two points
in time.

Walmart and Target deserve a sentence of their own: **neither has had a single rating action in
thirteen years.** That is Ding's inertia point in its purest form, visible in the raw data.

## What the files do not answer

**The Retail and Apparel issuer count.** The files classify no finer than "Corporate"; the
methodology sector is not a field. Counting the sector requires joining obligors to an industry
classification (via LEI or name matching to EDGAR's SIC codes), which is now a concrete, mechanical
next step rather than an unknown. Register item 10 stays open with that path attached.

**Anything after August 2025.** Post-cutoff labels, the entire clean window, and any 2026 rating
actions are invisible here.

## Bookkeeping

Both zip archives live in `data/` and stay out of git. The parsed intermediate (one JSON of all
obligor paths) is reproducible from the zips with the parsing script and is not committed either.
