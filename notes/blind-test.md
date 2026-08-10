# Blind test: five companies, stripped filings, independent sessions

*Analysis and write-up by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert designed
this test after the first two runs, specifically to remove the contamination those runs suffered from.
The five rating runs were executed by five separate agent sessions with no access to this
conversation, no web access, and filings with the credit-ratings disclosure removed. A sixth
independent session produced the memory control. Ground truth was taken from the ratings disclosure in
each filing before stripping.*

## Why this test exists

The first two runs (Walmart, Kohl's) had three contamination paths. The model already knew the
answers, the filings disclose their own credit ratings, and the analysis was performed inside a
conversation where the answers had already been discussed. Any of the three is enough to invalidate the
result.

This test closes all three and adds the control that makes the result interpretable.

## Design

Five companies were chosen to span the rating scale and to include two apparel names, since the
methodology contains apparel-specific wording that neither Walmart nor Kohl's exercised.

Each 10-K was pulled from EDGAR and passed through a two-pass stripper that removes any line
mentioning a rating agency, the phrases credit rating, debt rating and investment grade, and any table
row containing a rating symbol. Verification after stripping: zero agency mentions and zero rating
symbols remaining in all five files, with the financial statements intact.

Each filing then went to a separate agent session with the methodology text, instructed to derive the
scorecard from the documents only, with no web access and no use of prior knowledge of the company's
rating. All five reported no web use.

The control session received no documents at all, only the five company names, and was asked for each
company's Moody's rating from memory.

## Results

| Company | Actual | Blind run | Error | Memory only | Error |
|---|---|---|---|---|---|
| Walmart | Aa2 | A1 | +2 | not run | |
| Target | A2 | Baa1 | +2 | A2 | 0 |
| Dollar General | Baa3 | Baa2 | -1 | Baa2 | -1 |
| Macy's | Ba1 | Ba1 | 0 | Ba1 | 0 |
| Gap | Ba2 | Baa3 | -2 | Ba1 | -1 |
| Victoria's Secret | Ba3 | Ba1 | -2 | Ba3 | 0 |
| Kohl's | B2 | Ba3 | -2 | not run | |

Positive error means the run was harsher than the actual rating. Walmart and Kohl's are the earlier
contaminated runs, included for the scale picture but excluded from the comparison against the control.

## Finding 1: the memory control outperforms the analysis

| | Mean absolute error | Bias |
|---|---|---|
| Blind runs, five companies with a control | 1.40 notches | -0.60 |
| Memory only, no documents at all | **0.40 notches** | -0.40 |

The model guessing from memory, given nothing but a company name, is three and a half times more
accurate than the same model working carefully through the methodology and a full 10-K.

The control got three of five exactly right and was never more than one notch out. The document-based
analysis got one of five exactly right.

Where the two disagree the comparison is sharper still. Blind and memory agreed on Dollar General and
Macy's, so for those two nothing can be concluded about which process produced the answer. They
disagreed on Target, Gap and Victoria's Secret, meaning the blind run genuinely derived something
independent. In all three cases the derivation was worse than the recollection.

The consequence for evaluation is direct. On companies of this profile, any accuracy number produced by
a pipeline of this kind is uninterpretable, because a system that ignores the documents entirely scores
better. Contamination here is not a small correction to the result; it exceeds the signal.

## Finding 2: compression is real and survives better extraction

Across all seven companies the actual ratings span 12 notches, from Aa2 to B2. The predictions span 8,
from A1 to Ba3. Every prediction at the investment-grade end is too harsh and every prediction at the
speculative end is too generous.

This is the pattern first noticed on Walmart and Kohl's and it now holds on seven names. It is also
what Moody's itself describes in the Limitations section of the methodology, where it states the
scorecard is bounded and therefore aligns least well with assigned ratings at the upper and lower ends
of the scale. So part of this is a property of the instrument, not of the model.

Worth noting that the five blind sessions performed markedly better extraction than the two earlier
runs. All five capitalised operating leases into both debt and EBITDA, imputed lease interest at the
disclosed discount rate, and reasoned explicitly about which one-off items to strip. Several ran their
own sensitivity checks unprompted. The extraction improved and the compression did not go away, which
suggests compression is not primarily an extraction problem.

## Finding 3: the ordering is nearly right even though the level is not

Spearman rank correlation between actual and predicted is **0.937** across the seven companies.

That is a meaningful split. The model places these companies in almost the correct order and then
squeezes them into too narrow a band. Ordering and calibration are separable problems, and the second
one is the sort of thing a monotonic recalibration can address once there are enough samples to fit
one. This is the most encouraging number in the test.

Hit rates, blind runs, all seven: exact 1 of 7, within one notch 2 of 7, within two notches 7 of 7.

## Finding 4: what this does to the proposed error metric

Using the scale Aaa=1 through C=21, the same two-notch error measures very differently depending on
where it sits:

| Company | Error | AAPE |
|---|---|---|
| Walmart | 2 notches | 66.7% |
| Target | 2 notches | 33.3% |
| Gap | 2 notches | 16.7% |
| Victoria's Secret | 2 notches | 15.4% |
| Kohl's | 2 notches | 13.3% |

Five identical errors, measured five different ways, spanning a factor of five. Overall AAPE across the
seven is 22.2%, a number that says more about which companies were sampled than about how the system
performed.

This interacts badly with Finding 2. The scorecard is documented as least reliable at the ends of the
scale, and percentage error on ordinal codes weights the top of the scale most heavily, so the metric
concentrates its attention exactly where the instrument is known to be weakest.

Mean absolute error in notches is reported above alongside it and is not subject to this. If a genuine
ratio scale is wanted, mapping ratings onto idealised default rates would give one.

## Methodological defect in this test

The ground-truth file was left in the same directory as the stripped filings. Two of the five sessions
explicitly reported seeing it and declining to open it; the other three did not mention it.

There is reasonable evidence it was not used: both sessions that mentioned it produced wrong answers,
Target off by two notches and Gap off by two notches. But this should not have been possible and the
next run must keep ground truth outside the working directory.

## Open items

The compression could be tested directly by fitting a recalibration on a larger sample and checking
whether it generalises. That needs more than seven points.

The memory control should become standard on every run rather than a one-off, since it is cheap and it
is the only thing that makes an accuracy number interpretable.

None of this addresses the underlying problem, which is that these are all large, heavily covered US
issuers. The obvious next test is companies the model is unlikely to know well, and filing years far
enough back that the point-in-time question bites.
