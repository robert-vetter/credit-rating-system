# second go, Kohl's

Same exercise as Walmart, different company, to see whether anything from the first run was a fluke.
I picked Kohl's on purpose because it is the opposite case in three ways at once. It is mid-cap rather
than the largest retailer on earth, it is speculative grade rather than Aa, and it is a department
store in a segment that has been shrinking for a decade, so the qualitative descriptions actually
have to do some work instead of everything landing in the top box.

Same inputs as before, nothing else. Retail and Apparel methodology, the FY2025 10-K off EDGAR, year
ended 31 January 2026. Numbers are in scorecard.py, both companies now run from the same engine.

## what came out

    revenue                15,527
    operating income          624
    D&A                       700
    EBITDA                  1,324
    capex                     372
    interest expense          288      reported net, Kohl's does not split gross on the face
    total debt              6,630      revolver at zero, plus long term, plus both lease types
    cash                      674
    net debt                5,956
    RCF                     1,099

    revenue              $15.5bn      score  9.39
    debt/EBITDA            5.01x      score 15.01
    (EBITDA-capex)/int     3.31x      score 12.29
    RCF/net debt           18.5%      score 12.46

Qualitative I gave market characteristics a B, market position a B, revenue and earnings stability a
Caa, and financial policy a Ba. That last one is higher than it looks because Kohl's cut the dividend
from 222 to 56 and repaid 440 of debt this year, which is creditor friendly behaviour whatever you
think of the business.

Aggregate 13.351, which maps to Ba3.

## the part I did not expect

With Walmart I was certain of the answer before I started. Aa2, no hesitation, and I said in the last
write-up that I could not rule out that certainty pulling on the four qualitative calls.

With Kohl's I am not certain. My recollection is somewhere around Ba2 or Ba3 with a chance it has
been taken lower since, and I would not put money on any of those. So this run is closer to an
actual derivation than the Walmart one was, simply because there was less to remember.

Someone needs to check the real rating against a Moody's source. But notice what that means for
evaluation: the run where the model was confident is the run whose result is worth least, and the run
where it was unsure is the one that tells us something. That is backwards from how you would normally
read a confident answer, and it is going to be a problem if we ever score these automatically.

## how fragile is it this time

Less fragile than Walmart, which is the good news. The aggregate sits 0.149 from the nearest notch
boundary rather than 0.003. So the Walmart knife edge was partly bad luck rather than a structural
feature.

Still not comfortable though. Of the twelve one-step changes I tried on the four qualitative scores,
five flip the outcome. Market characteristics or market position one step worse takes it to B1.
Revenue and earnings stability one step better takes it to Ba2. Financial policy one step worse takes
it to B1, two steps worse also B1.

So the pattern from Walmart holds. The arithmetic is exact and the answer is decided by prose
judgments. What changed is only how much slack there happens to be around the particular number.

## the seasonality test

The methodology has a section on seasonality that says, in short, that year-end metrics may not be
representative of a retailer's real financial strength, because working capital and debt swing hard
through the year. Retailers with January year-ends close their books right after converting the
holiday inventory into cash, which is the most flattering moment of the year.

That is testable, so I tested it. Kohl's Q3 balance sheet, dated 1 November 2025, against the year-end
one we used:

    cash            144  at Q3      674  at year end
    inventories   3,895  at Q3    2,745  at year end
    total debt    6,802  at Q3    6,630  at year end
    net debt      6,658  at Q3    5,956  at year end

Net debt is 12% higher at the Q3 date, almost entirely because the cash is not there yet. Rerunning
leverage and RCF off the Q3 balance sheet moves the aggregate from 13.351 to 13.439.

It does not flip the rating here, so I want to be careful not to oversell it. But 0.088 of movement
from nothing more than choosing a different balance sheet date is more than the entire margin Walmart
had. On a company sitting near a boundary it decides the answer, and there is nothing in the 10-K
that tells you this is happening. You have to go and pull the 10-Q.

## what I take from this one

The mechanics transfer fine. The same engine ran both companies with no changes and the interpolation
behaved sensibly at both ends of the scale, so the scoring function is not the problem and probably
never will be.

Two runs is two runs and I am not drawing conclusions from it. But the same thing decided both
outcomes, which was the four qualitative scores plus a handful of definitional choices about what
counts as debt and what counts as interest, and it seems worth assuming that keeps being true until
something shows otherwise.

The more useful thing this run produced is the document question, which got long enough that I put it
in its own file next to this one.
