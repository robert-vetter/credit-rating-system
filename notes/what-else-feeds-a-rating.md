# what else feeds a rating

Both runs so far used one document, the 10-K, and that is clearly not enough. This is a first pass at
what else there is. It is not a plan, it is a list of things I found while doing the two runs, with a
note on which of them I have actually checked and which I am only assuming.

## the methodology asks for things the filing does not contain

This is the part I did not expect. If you read the scorecard descriptions closely, several of them
require information that is simply not in the company's own filing.

Revenue and earnings stability is scored against the peer group. The Ba description says performance
should be at least on par with peers, the B description says it may underperform relative to peers,
and the Caa one says the company has lagged its peer group. You cannot score that subfactor from one
company's accounts at all. You need a peer set, which means somebody has to decide who the peers are,
and then you need their numbers too. I scored it for both companies anyway, which in hindsight I
should not have done without saying so.

The same subfactor also asks whether the company meets its own financial targets. Targets are in
guidance and on earnings calls, not in the 10-K.

Market characteristics says the economic strength of the countries of operation influences the score.
That is macro data, external to everything.

Financial policy is explicitly about expectations, event risk, and management's public commitments,
and the methodology spends most of that section on M&A likelihood, shareholder distributions and
liquidity management rather than on anything you can read off a balance sheet.

And the whole thing is stated as forward looking. The methodology says historical results are useful
for understanding trends, not that they are the input. We have been treating last year's accounts as
the input.

## what is on EDGAR that we did not touch

I pulled the filing index for Kohl's to see what is actually there. Last few years, roughly:

    637  Form 4          insider transactions
    113  8-K             material events
    108  DFAN14A etc.    proxy contest material, 2020 through 2026
     19  10-Q            quarterly
      6  10-K            what we used
      5  DEF 14A         proxy, exec comp
      7  SD              conflict minerals

The 10-Q matters and I tested it, see the seasonality section in the Kohl's write-up. Net debt was 12%
higher at the Q3 date than at year end.

The 8-Ks matter more than I thought. Kohl's has filed 25 of them since January 2025. The last few
carry item codes 5.02 three times in three months, which is departure or election of directors and
officers, plus a 1.01 which is entry into a material agreement. Management turnover and new
agreements are exactly the kind of thing that feeds financial policy and governance, and none of it
is in the 10-K.

The proxy contest material is the clearest example. 108 filings across six years, including PREC14A
and DEFC14A which are contested proxy statements. An activist campaign is a direct input to event
risk and to whether financial policy favours shareholders or creditors. Reading only the 10-K, you
would not know it was happening.

DEF 14A gives executive compensation structure, which tells you what management is paid to optimise.
If the incentive plan is built around earnings per share, buybacks become more likely, and that is a
financial policy signal.

Credit agreements and indentures are filed as exhibits rather than as their own form type. That is
where covenants, maturity dates and security sit. We have not looked at a single one, and instrument
level ratings depend on them.

## the staleness problem, which I had not thought about

Today is August 2026. Kohl's 10-K covers the year ended 31 January 2026 and was filed on 13 March.
Since then there is a 10-Q for the quarter ended 2 May, and eight 8-Ks. So rating Kohl's today off the
10-K alone means ignoring five months of filed events, including three management changes.

That is not an edge case, it is the normal state. A 10-K is only current for a few weeks. Any system
that reads one filing and emits a rating is answering a question about the past.

## things that are not on EDGAR

Earnings call transcripts. Guidance and management tone live there, and guidance is what the
methodology means by targets. Sometimes the release is attached to an 8-K as exhibit 99.1 but the
call itself usually is not.

Peer financials are on EDGAR but only if you already know who the peers are. Choosing the peer set is
itself a judgment and it directly moves one of the eight subfactors.

Macro and country data for the market characteristics subfactor.

And Moody's own prior rating actions and press releases, which we should probably stay away from as
an input even though they are public, because they contain the answer.

## rough sense of what matters most

Very tentative, from two companies, so treat it as a hunch rather than a finding.

The 10-Q looks like the highest value addition, because it is cheap, it is structured the same as the
10-K, and it directly fixes a measurable distortion in three of the four quantitative subfactors.

After that the 8-K stream, because that is where event risk actually shows up and event risk is
written into the financial policy descriptions explicitly.

Peer data is probably third and it is the awkward one, because it is not a document you fetch, it is a
modelling decision about who counts as a peer, and then a whole second extraction pipeline for each
peer.

The proxy material is high value but only for companies where something is going on, so it is more of
a conditional fetch than a standing input.

## what I would try next

Rerun Kohl's with the 10-Q included and see whether using a four quarter average balance sheet instead
of a year-end snapshot changes anything systematically, rather than just at one date.

Take one company and read every 8-K from the last two years to see how much of it is genuinely rating
relevant versus routine. My guess is most of it is routine and the useful fraction is small but
important, but that is a guess and it is checkable.

Pick a peer set for Kohl's by hand, score revenue and earnings stability properly against it, and see
how far that moves from the number I made up.

And a third and fourth company, ideally an apparel one, because the methodology has apparel specific
wording in the market position descriptions that neither Walmart nor Kohl's exercised at all.
