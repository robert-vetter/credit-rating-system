# first go at Walmart

Xiaowei suggested trying the task on a model before building anything, so I did that today. Nothing
clever, just the Retail and Apparel methodology and Walmart's FY2026 10-K pulled off EDGAR, and then
working through the scorecard by hand. No pipeline, no tools, no retrieval. The point was to see
where it falls over.

The arithmetic is in scorecard.py next to this file, so you can rerun it and change the inputs.

## what came out

Numbers straight off the filing, year ended 31 January 2026, USD millions:

    revenue                713,163
    operating income        29,825
    D&A                     14,203
    EBITDA                  44,028      operating income + D&A
    capex                   26,642
    gross interest           2,799      debt interest 2,318 + finance lease 481
    total debt              67,095      borrowings + both lease types
    cash                    10,727
    net debt                56,368
    FFO                     40,813      CFO less the working capital swing
    RCF                     33,306      FFO less common dividends

    revenue              $713.2bn      score  0.50
    debt/EBITDA             1.52x      score  6.07
    (EBITDA-capex)/int      6.21x      score  9.36
    RCF/net debt            59.1%      score  4.64

Then the four qualitative ones. I gave market characteristics an A, market position an Aa, revenue
and earnings stability an Aa, and financial policy an Aa. Weighted sum comes to 4.503, which maps to
A1.

Walmart is actually Aa2 as far as I know, though somebody should confirm that against a Moody's
source rather than my memory. So the naive run lands two notches low. That is not a disaster, a
scorecard output sitting a notch or two off the assigned rating is normal because the committee
applies other considerations on top. But the interesting part is not the gap.

## the interesting part

4.503. The boundary between Aa3 and A1 is at 4.5. The whole thing came out three thousandths on the
wrong side of a line.

So I went back and changed one judgment call at a time to see what it takes to flip it. Seven things
flip it, and none of them are mistakes, they are all choices a reasonable person could defend:

If market characteristics is an Aa instead of an A, it goes to Aa3. Walmart is mostly groceries and
staples, demand is inelastic, barriers are enormous, but competition is also genuinely fierce. I sat
between the two categories for a while and picked A more or less on a coin flip.

If market position is Aaa instead of Aa, it flips. Walmart is the biggest retailer on earth with
dominant positions in multiple broad categories, which is close to the literal Aaa wording. I went
with Aa only because the Aaa text says no anticipated threats from any front and Amazon exists.

Same for revenue and earnings stability at Aaa, and financial policy at Aaa. Both flip it.

If I use interest net of interest income, 2,431 instead of 2,799, coverage goes from 6.21x to 7.15x
and it flips. The methodology says interest expense and I read that as gross, but net is a defensible
reading.

If I leave operating leases out of debt, leverage drops from 1.52x to 1.17x and it flips.

And if I take RCF straight off operating cash flow instead of backing out the working capital swing,
it flips too.

So the outcome is not really A1. The outcome is a coin sitting on its edge, and which way it falls is
decided by four qualitative calls I made from prose and three definitional choices nobody wrote down.
The arithmetic is completely deterministic and completely beside the point.

## what I did not do

I used reported figures. Moody's does not. They restate onto their own definitions before computing
anything, pensions, hybrids given partial equity credit, securitisations brought back on, unusual
items stripped out. I did none of that, and for Walmart it probably does not matter much because the
balance sheet is clean, but for a levered retailer it would move leverage by a lot. That whole layer
is missing from what I did and I think it is the single biggest gap between this and a real analyst.

I also did not look at anything except the 10-K. No peer comparison, no forward view, and the
methodology is explicit that ratings are forward looking and the scorecard is fed by expectations,
not just by last year's accounts.

## the thing that worries me most

I know Walmart is Aa2. I knew it before I opened the filing. So when I was sitting between A and Aa
on market characteristics, or between Aa and Aaa on market position, I cannot honestly say the answer
I already knew was not pulling on me. Four qualitative subfactors carry 45% of the weight and every
one of them is a judgment made from prose, which is exactly where that kind of leakage would hide,
and it would be invisible in the output because the reasoning reads fine either way.

Quick check on this: if you ask for Walmart's rating with no filing at all, you get Aa2 straight
back, instantly, with a confident explanation. So the model is not deriving anything, it is
recalling. Which means the 4.503 above tells us almost nothing about whether this approach works. It
tells us the model can do arithmetic and write plausible prose about a company it already knows.

This is the same look-ahead problem EDGAR-Forecast was built around, and I think it has to be settled
before any number from a run like this means anything. Doing it on well-known large caps in the
current year is close to worthless as evaluation.

## what I take from this for the architecture

Three things, roughly.

The scoring engine should be a plain function with tests, not anything a model touches. It is forty
lines and it is exact. Every notch of variance we saw came from the inputs, so that is where the work
is.

The qualitative subfactors are the actual problem, not a side issue. 45% of the weight, and on this
run they were also the thing that decided the outcome. Whatever we build needs those scores to be
argued from cited passages in the filing and checkable afterwards, otherwise we cannot tell an
analysis from a memory.

And the Moody's adjustments need to be their own block. They sit between extraction and scoring, some
of them are mechanical and some are judgment, and skipping them is the difference between reading a
filing and rating a company.

I would also say the evaluation harness has to come early rather than last, because until the
point-in-time thing is handled we have no way to tell whether any of this is working.

## next

Rerun the same thing on a company that is not investment grade and not famous, and on an older filing
year, and see how much of the apparent competence survives. Also worth doing the same run twice with
the qualitative scores forced to be justified with quotes, and seeing whether they move.
