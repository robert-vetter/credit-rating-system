# Experiment plan

*Written by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert set the objective and the
constraints; the model did the API research and drafted the design. API facts in the configuration
section were verified against Anthropic's published model documentation on the date above. Everything
about the credit data is an estimate and is marked as such.*

The purpose of this document is to fix a baseline that survives review. It responds to two points
raised by the lab: that ratings leak through channels beyond the filing (Giesecke), and that ratings
are inert, so a model that simply remembers a rating that has not changed will look like it is
predicting one (Ding).

Both are correct and both change the design. The second one changes it more than the first.

## The core problem, restated

An accuracy number for a rating predictor is uninterpretable on its own, because the trivial baseline
is very strong. Ratings change rarely: most issuer-years are unchanged from the prior year. A system
that outputs the last known rating and nothing else will score well.

So the quantity of interest is not accuracy. It is **accuracy relative to persistence**:

    lift = MAE(persistence baseline) - MAE(system)

If that is not positive, nothing else in the evaluation matters. The blind test already showed the
adjacent version of this problem: a memory-only control scored 0.40 notches MAE against 1.40 for the
full document-based analysis. Persistence is the same failure mode with the model's memory replaced by
a lookup table, and it will be at least as hard to beat.

Everything below is organised around measuring that lift honestly.

## Phase 0: Configuration to freeze

**Verified against Anthropic's API documentation.** These are not preferences; several are hard
constraints that change what the experiment can do.

**Retrieval is structurally disableable.** On the Anthropic API, web search, web fetch and code
execution are tools that must be declared in the request's `tools` array. A request with no `tools`
array cannot perform retrieval of any kind. This is a property of the request, not an instruction to
the model, and it is the correct answer to the concern about internet grounding: the guarantee comes
from the request shape. Note that the earlier blind test did not have this guarantee: it instructed
agents not to search and relied on their self-report. That must not be repeated.

**Sampling parameters are gone on current models.** `temperature`, `top_p` and `top_k` are removed on
Claude Opus 5, Opus 4.8 and Opus 4.7 and return HTTP 400 if sent. Non-default values are rejected on
Sonnet 5. Determinism via `temperature=0` is therefore unavailable on the frontier models. Older
models (Opus 4.5, Sonnet 4.5, Haiku 4.5) still accept them.

Consequence: run-to-run variance cannot be assumed away. It has to be measured. Every configuration in
this plan is run with **k replicates per sample** and the within-sample standard deviation is reported
alongside the mean. If replicate variance is comparable to the effect being measured, the effect is
not real.

**Knowledge cutoffs, and the window they imply.** Anthropic publishes two dates per model. The
training data cutoff is the conservative bound and is what should be used.

| Model | Reliable knowledge | Training data | Clean window as of Aug 2026 |
|---|---|---|---|
| Claude Opus 5 | May 2026 | May 2026 | 3 months |
| Claude Sonnet 5 | Jan 2026 | Jan 2026 | 7 months |
| Claude Opus 4.8 | Jan 2026 | Jan 2026 | 7 months |
| Claude Sonnet 4.6 | Aug 2025 | Jan 2026 | 7 months |
| Claude Opus 4.6 | May 2025 | Aug 2025 | 12 months |
| Claude Opus 4.5 | May 2025 | Aug 2025 | 12 months |
| Claude Sonnet 4.5 | Jan 2025 | Jul 2025 | 13 months |
| Claude Haiku 4.5 | Feb 2025 | Jul 2025 | 13 months |

The frontier model has the worst window. Opus 4.5 quadruples it and additionally still accepts
sampling parameters, which makes it the better baseline model on both counts despite being weaker.
This is a deliberate trade: the baseline should be a clean measurement, not the highest score.

**Two API features that materially change what is affordable.** The Batch API processes up to 100,000
requests asynchronously at 50% of standard pricing, which is the right mechanism for a few hundred
samples with replicates. Prompt caching charges cached content at roughly 0.1x on reads: the
methodology text is identical across every request in a run, so it should sit behind a cache
breakpoint. Together these make a several-hundred-sample run with replicates and ablations tractable
rather than a budget question.

**Output format.** Structured outputs (`output_config.format` with a JSON schema) constrain the
response to a schema, which removes the parsing fragility of the earlier text-block approach. The
schema should require all eight subfactor scores, the four extracted metrics, and a citation span for
each qualitative score.

## Phase 1: Leakage audit

Giesecke's point is that stripping the 10-K is necessary but not sufficient. This phase enumerates the
channels and tests each one rather than assuming.

**Channels already confirmed.** The 10-K ratings disclosure was found and stripped in all seven
companies run so far. It appears both as a labelled table and in running MD&A prose.

**Channels to test.** Each of these is a hypothesis with a cheap test attached:

The 10-Q carries the same disclosure obligation and probably the same table. Test by scanning a sample
of 10-Qs for agency mentions.

Coupon step-up clauses reveal a downgrade even with the rating removed. Kohl's disclosed a 175 basis
point step-up caused by downgrades; the step-up survives naive stripping because it need not name an
agency. Test by scanning for step-up and coupon-adjustment language independently of agency terms.

Credit agreement pricing grids map rating levels directly to interest spreads and are filed as
exhibits. This is the most direct leak available and is not in the 10-K body at all. Test by pulling
credit agreement exhibits for a sample and checking how many contain an explicit rating-to-spread
table.

Covenant language conditioned on investment-grade status leaks the side of the boundary the company
sits on, which is the economically important distinction. Test with a targeted phrase scan.

Bond coupon levels are a market-derived signal that prices the rating in. A 10% senior secured coupon
communicates speculative grade without naming it. This one is **not strippable** and is arguably
legitimate credit information an analyst would see, so the decision is whether to treat market data as
in scope. That decision should be explicit in the baseline spec rather than left implicit.

**Deliverable.** A table of channels with three columns: strippable yes/no, measured prevalence in a
sample, and decision taken. Stripping code must be regression-tested against that table.

## Phase 2: Contamination measurement

Three probes, each producing a number rather than an assumption.

**Memory probe.** For every sample, one additional call with no documents at all, asking for the rating
from the company name. The gap between this and the document-based run is the contamination estimate.
This already produced the single most important result so far and should become standard on every run.
It costs one call per sample.

**Cutoff gradient.** This is the design that turns the cutoff problem from a constraint into a
measurement. Run the same sample set across models whose training cutoffs differ by month, holding the
prompt and the documents fixed. If accuracy on a given observation date degrades as the model's cutoff
moves earlier relative to that date, the degradation is memorisation, measured directly. If accuracy is
flat across cutoffs, the model is deriving rather than recalling and the whole contamination worry is
smaller than feared.

The table above supplies the gradient for free: Opus 5 at May 2026, Sonnet 5 and Opus 4.8 at January
2026, Opus 4.5 and Opus 4.6 at August 2025, Sonnet 4.5 at July 2025. Four distinct cutoff points
spanning eleven months, on the same API, with no extra data collection.

**Familiarity gradient.** Contamination is not uniform: the blind test knew Walmart cold and was wrong
about Kohl's. Stratify the sample by a coverage proxy such as market capitalisation or index
membership and report the memory probe separately per stratum. Expect the contamination estimate to be
much larger for large caps, which has a direct consequence for sample construction.

## Phase 3: The baseline

**Sample definition.** Ding has clarified this: the unit is the outstanding rating at a date after the
training cutoff, not a rating action. Every issuer with a rating in force at the observation date is
one sample. That makes a few hundred reachable.

**The label.** The methodology states that the scorecard is oriented to the senior unsecured rating for
investment-grade companies and to the corporate family rating for speculative-grade ones. Selecting
the label therefore requires knowing which side of the boundary the issuer is on, which is mildly
circular. Resolve it by using the actual current rating to determine the category and then taking the
corresponding label, and write that rule into the spec so it is reproducible.

**Baselines to beat, in order of severity:**

Persistence, meaning the last known rating carried forward. This is the one that matters and it is
strong.

Memory-only, meaning the model with no documents. Already measured at 0.40 notches on five companies.

Sector prior, meaning the median rating of the sector. Weak, but it bounds the floor.

**Metrics.** Report all of these, not one:

Mean absolute error in notches, as the primary number, because it is position-independent and
interpretable in one sentence.

Average absolute percentage error on the ordinal codes, as requested by the lab. Report it alongside
the demonstration that identical two-notch errors measure between 13.3% and 66.7% depending on
position, so the number is read with that in mind.

Spearman rank correlation, because the seven-company result showed ordering at 0.937 while the level
was compressed. Those are separate problems and should be measured separately.

Hit rates within one and two notches.

Classification accuracy at the Baa3/Ba1 boundary, because that is the economically decisive threshold.

Lift over persistence on each of the above.

Where a genuine ratio scale is wanted, ratings can be mapped onto published idealised default rates
and percentage error computed there; that is defensible in a way that percentage error on ordinal
codes is not.

**Stratified reporting.** The headline number must be broken out by whether the rating changed since
the model's cutoff. On unchanged issuers every method looks good and the comparison is uninformative.
The changed subset is where the signal is, and it will be small, so report its size honestly.

## Phase 4: Ablations

Only after the baseline is fixed. Each of these is one configuration change against the frozen spec:

Deterministic scoring engine versus letting the model do the arithmetic. Expect this to be free
accuracy, since the arithmetic is exact and contributed no variance in any run so far.

With and without the Moody's restatements stage.

With and without the 10-Q, testing whether the seasonal distortion measured on Kohl's (12% higher net
debt at the Q3 date) is systematic.

With and without a peer set for the stability subfactor, which is currently scored without any basis.

Effort level swept across the range, since it is the main cost and latency lever.

Monotonic recalibration fitted on a held-out split, testing whether the compression observed across
seven companies is correctable. Given a rank correlation of 0.937 with a compressed level, this is the
single most promising intervention available and it is cheap.

## Open dependencies

The lab's existing dataset is still unspecified: how many firms, which years, which sectors, and which
rating is recorded. Sample construction and sector scope both depend on it.

Whether the sector methodologies share scoring mechanics determines whether multi-sector expansion
costs one configuration file per sector or a rewrite. Checkable in an afternoon by downloading two more
methodologies and comparing structure.

The issuer count under the Retail and Apparel methodology is an estimate of 150 to 250 and has not been
verified against Moody's.

## What this plan deliberately does not do

It does not attempt to maximise the accuracy number. A baseline that looks good but cannot be
interpreted is worth less than a modest number with a measured contamination estimate attached to it.

It does not treat the training cutoff as a sufficient control. The cutoff is a crude proxy: the model
was wrong about a downgrade that occurred well inside its training window. Per-sample measurement
replaces the date filter.
