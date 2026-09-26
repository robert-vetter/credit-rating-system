# Dates, supplied filings and reference labels

*Prepared by OpenAI Codex, directed by Robert Vetter, 17 September 2026. Filing selections checked against the frozen EXP04-ARM1-A1 current-input audits; fiscal periods joined by accession to SEC manifests; labels checked against the accepted candidate record. Action months checked against the cached disclosure evidence. No labels were changed or certified current by this review.*

[Summary and results](README.md) · [Exact prompts](PROMPTS.md)

## Model and information dates

| Date concept | Qwen main experiment | Earlier Opus pilot |
|---|---|---|
| Model | Qwen3-235B-A22B-Instruct-2507 | Claude Opus 4.6 |
| Training-data cutoff | **Not vendor-stated** | **August 2025**, vendor-reported |
| Alternative bound | **21 July 2025**, public checkpoint release; not a training-cutoff claim | Reliable knowledge cutoff May 2025 is a different, narrower concept and was not used as the training boundary |
| Rating-history endpoint | 28 August 2025 | 28 August 2025 |
| Primary filings eligible | 30 September 2025 < public filing date ≤ 29 August 2026 | Same |
| Target outstanding-rating date | 29 August 2026 | Same |
| Executed | 13 September 2026 | 10 September 2026 |

Cutoff evidence: [Qwen checkpoint/model card](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507), [dated checkpoint review](../../experiments/04-open-weight-cross-section/review-codex-2026-09-12.md), and [Opus vendor-evidence snapshot](../../experiments/03-oos-values-first/evidence/opus-4-6-cutoff-2026-09-10.md). These are the evidence records used for the experiments, not a new verification of hosted model weights.

## Actual supplied documents: the primary 19

**Each document entry is `financial period end / public SEC filing date`.** K = 10-K; Q = 10-Q. All dates are ISO YYYY-MM-DD. These are the actual primary documents in Qwen's current-input arm, not all filings available or the older XBRL source history. The label-source date is its **publication date**, not a rating-action date or a certification of the rating at the target date.

| Issuer | K: period end / filed | Qs: period end / filed | Prior → accepted label | Label-source publication |
|---|---|---|---|---|
| Bath & Body Works | 2026-01-31 / 2026-03-12 | 2026-05-02 / 2026-05-27; 2026-08-01 / 2026-08-26 | Ba2 → Ba2 | 2026-08-26 |
| Best Buy | 2026-01-31 / 2026-03-18 | 2026-05-02 / 2026-06-05 | A3 → A3 | 2026-03-18 |
| Dick's Sporting Goods | 2026-01-31 / 2026-03-27 | 2026-05-02 / 2026-06-04 | Baa2 → Baa2 | 2026-06-04 |
| Dollar General* | 2026-01-30 / 2026-03-20 | 2026-05-01 / 2026-06-02; 2026-07-31 / 2026-08-27 | Baa3 → Baa3 | 2026-08-27 |
| Floor & Decor | 2025-12-25 / 2026-02-19 | 2026-03-26 / 2026-04-30; 2026-06-25 / 2026-07-30 | Ba3 → Ba3 | 2026-07-30 |
| Gap | 2026-01-31 / 2026-03-17 | 2026-05-02 / 2026-05-29; 2026-08-01 / 2026-08-28 | Ba2 → Ba2 | 2026-03-17 |
| Kohl's* | 2026-01-31 / 2026-03-19 | 2026-05-02 / 2026-06-04 | B2 → B2 | 2026-06-04 |
| Leslie's | 2025-10-04 / 2025-12-18 | 2026-01-03 / 2026-02-18; 2026-04-04 / 2026-05-13; 2026-07-04 / 2026-08-12 | Caa3 → Caa3 | 2025-12-18 |
| Levi Strauss | 2025-11-30 / 2026-01-28 | 2026-05-31 / 2026-07-08 | Ba1 → Ba1 | 2026-01-28 |
| Lowe's | 2026-01-30 / 2026-03-23 | 2026-05-01 / 2026-05-28; 2026-07-31 / 2026-08-27 | Baa1 → Baa1 | 2026-08-27 |
| Macy's | 2026-01-31 / 2026-03-27 | 2026-05-02 / 2026-06-04 | Ba1 → Ba1 | 2026-03-27 |
| **Nike** | 2026-05-31 / 2026-07-15 | **None** | **A1 → A2** | 2026-07-15 |
| PVH | 2026-02-01 / 2026-03-31 | 2026-05-03 / 2026-06-05 | Baa3 → Baa3 | 2026-06-05 |
| Signet | 2026-01-31 / 2026-03-19 | 2026-05-02 / 2026-06-02 | Ba3 → Ba3 | 2026-03-19 |
| Target | 2026-01-31 / 2026-03-11 | 2026-05-02 / 2026-05-29; 2026-08-01 / 2026-08-28 | A2 → A2 | 2026-08-28 |
| Tractor Supply | 2025-12-27 / 2026-02-19 | 2026-03-28 / 2026-05-07; 2026-06-27 / 2026-08-06 | Baa1 → Baa1 | 2026-02-19 |
| V.F. | 2026-03-28 / 2026-05-20 | 2026-06-27 / 2026-07-29 | Ba2 → Ba2 | 2026-07-29 |
| Victoria's Secret | 2026-01-31 / 2026-03-20 | 2026-05-02 / 2026-06-05 | Ba3 → Ba3 | 2026-06-05 |
| Walmart | 2026-01-31 / 2026-03-13 | 2026-04-30 / 2026-05-29; 2026-07-31 / 2026-08-28 | Aa2 → Aa2 | 2026-08-28 |

*Residual disclosures were found for Kohl's and Dollar General; both remain in the original primary cohort and are excluded only in the explicitly post-hoc sensitivities. Primary cohort: **19 issuers, 47 supplied documents, one endpoint rating change**. Levi Strauss's 2026-04-07 10-Q was dropped by the fixed context-length rule and is not listed as supplied.

**Separate diagnostic, not a twentieth primary issuer:** Qurate/QVC received a K for 2025-12-31 filed 2026-04-15 and a Q for 2026-06-30 filed 2026-08-04. Its 2026-05-15 Q was dropped in this arm. Prior Caa1; accepted Caa3 label published **2025-11-05**, concerning LI LLC's corporate-family rating. That label predates bankruptcy information in the inputs and is not a verified rating for consolidated QVC Group at the target date. All executed issuers including this diagnostic: **20 issuers, 49 supplied documents, two endpoint changes**.

## Known rating changes and their timing

| Case | Rating change | Action timing supported by local evidence | Public evidence | Interpretation |
|---|---|---|---|---|
| Nike | A1 → A2 | **November 2025**; exact day not established locally | 10-Q filed **2025-12-30** explicitly says the downgrade occurred in November; latest accepted A2 label is from the **2026-07-15** K | The one changed issuer in the primary 19; judgement remained A1 |
| Qurate diagnostic | Caa1 → Caa3 | **October 2025**; exact day not established locally | 10-Q filed **2025-11-05** describes the October action for LI LLC CFR | Not counted in primary 19; entity/type and stale-label limitations prevent a clean current-rating assessment |
| Leslie's, timing check | Caa1 → Caa3 | **2025-08-13**, official local history | Later K filed **2025-12-18** discusses the downgrade | Before the September document boundary and before the August 28 prior-rating endpoint. Post-release for Qwen, but already included in the supplied prior; not an endpoint change in this experiment |

The Nike/Qurate action months are after both the Qwen release bound and the common September boundary. **The 18 unchanged endpoint labels do not certify zero intervening actions.** A downgrade followed by an upgrade, outlook changes or withdrawals would require a complete history to establish.

A recent filing can also quote an older rating state. For example, Levi Strauss's January 2026 filing describes a rating as of November 30, 2025. Absence of a later disclosure is not evidence that the rating remained unchanged through August 29, 2026.

## What is still needed

Complete rated-entity/type-specific histories from the baseline through the target date, including withdrawals and a coverage-through date. Until then, the results are accuracy **against accepted company disclosures**, not fully verified outstanding-rating accuracy. Label-source/action dates must never be substituted for one another.

<details>
<summary>Local record provenance and optional source links</summary>

Actual inputs: `experiments/04-open-weight-cross-section/runs/EXP04-ARM1-A1/audit/current/X01.json` through `X20.json`, joined by accession to `evaluation/companies/<slug>/filings/manifest.json`. These caches are local/gitignored. Accepted label sources and SEC URLs are in [candidates.json](../../experiments/03-oos-values-first/candidates.json); this table preserves the decisions rather than relabelling cases. Nike and Qurate action wording is reproduced in [label-review.md](../../experiments/03-oos-values-first/label-review.md). Leslie's exact action date is in the local official `ratings.json`, OI 825431804, LT Corporate Family Ratings, RAD 2025-08-13.

</details>
