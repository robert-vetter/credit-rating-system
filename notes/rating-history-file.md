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
| Issuer | 73,687 | Instrument-level ratings: one record per security with CUSIP, coupon, maturity, par value, and that instrument's own action history |

Parsed totals from the obligor set: 106,590 rating actions across 21,383 obligors. By class: 8,589 US
Public, **8,146 Corporate**, 2,774 Financial, 1,189 Insurance, 512 international public, 171
Sovereign. Action codes: NW (new), UP, DG, HS (history start, the rating outstanding at the June 2012
regime start), and several withdrawal codes; a small residue of records carries no code and needs a
second look.

## Finding 1: the 12-month embargo is real and fully used

The file set is dated 11 August 2026. The most recent rating action in it is from **August 2025**.
Moody's uses the entire delay the rule permits, to the month. A live consequence surfaced during
mapping verification: Nike's 10-K of July 2026 discloses a Moody's senior unsecured rating of A2
while the file still carries A1, so a downgrade happened inside the embargo window and the public
file does not know it (evaluation/mapping-verification.md).

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

## The sector count, done: 164 issuers, 86 actively rated

The files classify no finer than "Corporate", so the sector count required a join: union the
Corporate entities of both sets, match names to EDGAR CIKs (two tiers: listed companies, then all
SEC filers, with EDGAR's "/NEW/"-style suffixes normalised away), fetch each match's SIC industry
code from the SEC submissions API, and filter to Retail and Apparel codes (5200-5999 excluding
restaurants, which have their own methodology; apparel manufacturing 2300-2399; footwear and
leather; apparel wholesale). The pipeline is `sector_count.py` next to this file; the frame lands in
`data/retail_frame.json`.

Numbers: of 13,025 Corporate entities in the union (8,146 obligor-level plus 4,879 issuer-only),
3,920 matched uniquely to an EDGAR CIK. **164 are Retail and Apparel; 86 of those carry an active
rating as of the file end (August 2025): 31 investment grade, 55 speculative.** The distribution
spans Aa2 (Walmart) to Caa3 and is thickest in the Ba range, which is where rating changes happen.

**Correction history on the entity counts, kept in full because the second correction refutes the
first.** The original note said 13,026 union entities, 4,880 issuer-only, 4,057 matches. A revision
"corrected" this to 12,926 / 4,780 / 3,890, citing a second script with no shared code that
confirmed the smaller numbers. That confirmation was worthless: both scripts parsed entity headers
through the same fixed 1,600-byte window, and 101 issuer-set Corporate files carry a namespace
preamble long enough to push the entity id past it (Apple, PepsiCo, McDonald's, AT&T, UPS and
Heineken were among the silently dropped). Independent code is not an independent check when it
shares the assumption under test. With window-free parsing the verified figures are **13,025 union
entities, 4,879 issuer-only, 3,920 unique EDGAR matches**, so the original numbers were nearly right
(their small residue is consistent with an empty-id phantom entry) and the first "correction" made
them worse. All 31 newly recovered EDGAR matches are non-retail (closest: McDonald's, SIC 5812,
restaurants, excluded by design), so the frame below is unaffected. The frame totals also survived
the earlier fixes by coincidence: the restaurant exclusion removed entities, the name-matching fix
added five, and the two cancelled; the membership changed even though 164 did not.

Three findings from building it. First, **the union matters**: purely investment-grade issuers such
as Home Depot, Costco, TJX, Ross and AutoZone have no obligor-set file at all, because they carry no
entity-level rating; they exist only at instrument level. A frame built on the obligor set alone
misses most of the investment-grade half. Second, activity has to be judged **per instrument**, not
per action: individual bonds mature and get withdrawn while the issuer stays rated, and a
latest-action check misclassifies such issuers as dead (Dollar General was the tell). Third, the
old 150-250 estimate for the sector was about right for the frame (164) but the usable number is
the 86 active ones; for Ding's "few hundred samples" this means sampling issuer-dates rather than
issuers, or adding sectors, both of which the plan already contemplates.

**Verification that both sets are required, in numbers.** The two sets join exactly, not by name:
6,218 entity IDs appear in both, and the names agree in 100.0% of them, so the obligor-to-issuer
join is keyed and lossless (only the Moody's-to-EDGAR step uses name matching). Dropping the issuer
set would cost 30 of the 86 active issuers their label: 24 have no obligor-set file at all (the Home
Depot type) and 6 exist there only with withdrawn entity ratings (the Dollar General type). Dropping
the obligor set would cost 6 issuers entirely (rated with no rated instruments, for example Gildan
and Wayfair) and would put the remaining 50 speculative-grade names on the wrong label level, since
the methodology wants the CFR there and instrument ratings can sit a notch or two away (Kohl's: CFR
B2, senior unsecured B3).

**Manual scope pass over all 164, done.** Every member was classified against the methodology's own
scope section (retailers to end consumers including grocery, drugstores, auto dealers and e-commerce
are in, as are apparel and footwear designers; restaurants, B2B distribution, propane and fuel
distribution, pharmacy benefit managers, pure brand licensors and diversified holdings are out).
Results on the 164 entities: 137 in scope, 23 out, 4 uncertain (CVS, whose drugstore is wrapped in a
PBM and an insurer; Samsonite, on the accessories-versus-durables boundary; Good Sam; and Amazon,
whose retailing is in scope on the methodology's own wording but which is a cloud company wearing a
retailer's SIC code, so which Moody's methodology actually governs it is not ours to assume). Among
the 86 actively rated entities, 8 leave as out of scope: two propane distributors (AmeriGas, Suburban
Propane), four B2B resellers or auction houses whose retail SIC is misleading (CDW, Insight,
OpenLane, Covetrus), one building-materials distributor selling to contractors rather than consumers
(Builders FirstSource), and one diversified holding company (Compass Diversified).
Restaurants no longer appear at all: Starbucks and Wendy's carry SIC 5810, which the first filter did
not exclude and the script now does (5810-5819).

**A name-matching fix, and what it cost before it was found.** The normalisation deleted periods
outright, so Moody's `AMAZON.COM, INC.` became `AMAZONCOM` while EDGAR's `AMAZON COM INC` became
`AMAZON COM`, and the two never met. The bug surfaced when Amazon was used as an offhand example and
turned out to be missing from the frame despite an obvious retail SIC code. The matcher now indexes
both readings of a period separately and tries the strict one first, which is verified to be strictly
additive: on identical inputs it keeps all 3,847 matches the old rule found and adds 43. Five of the
43 are Retail and Apparel: Amazon.com, V.F. Corporation, J.Crew, AutoTrader.com and Cencosud. Of
those, V.F. Corporation is a genuine addition to the usable set (Ba2, entity-level, current 10-K
filer); Amazon is rated A1 but parked as uncertain above; J.Crew and AutoTrader have no active rating;
Cencosud is rated Baa3 but stopped filing with the SEC in 2017.

A second bug travelled with it. Instrument-level lookups addressed the issuer archive through a
directory prefix that does not exist inside it, so every such read raised `KeyError` and was caught as
"no rating". It was invisible while the frame was built from a path that happened not to use it, and
would have silently emptied the investment-grade half of any rebuild. Both fixes are in
`sector_count.py`; recomputing the 86 active ratings with the corrected path reproduces all previously
recorded values exactly, so the published label table is unaffected.

Deduplicating corporate groups (Amer Sports three times, Macy's, Walgreens, Wayfair, Dillard's and
others twice; Safeway folded into Albertsons) leaves **66 distinct in-scope groups with an active
rating**. Verifying each group's actual filing status against EDGAR then caught two systematic
problems the name match alone missed: companies that went private and re-listed under a new CIK
(BJ's, Leslie's, National Vision, RH), and bond-issuing subsidiaries whose parent does the filing
(Signet UK Finance versus Signet Jewelers, Torrid LLC versus Torrid Holdings, Sally Holdings versus
Sally Beauty Holdings; Gildan additionally files the Canadian 40-F, which the first form filter
missed). After remapping, the split is:

**63 groups are current annual filers and usable for present-day observation dates: 23 investment
grade, 40 speculative,** spanning Aa2 to Caa3. Three are foreign filers (JD.com, Vipshop on 20-F,
Canada Goose on 40-F) whose document set differs from the 10-K pattern and should be treated as
their own stratum. A further 10 in-scope groups are usable for historical observation dates only,
because their filings stop (Walgreens through 2024, Michaels through 2021, Whole Foods through
2017, and so on): still valid samples for the historical arm inside their filing windows.

**The reverse completeness pass, and what it recovered.** Checking the join from the other side
(SIC codes fetched for all ~8,000 currently listed SEC companies, then every listed retailer not
covered by a confirmed mapping treated as a question) found that the forward name match had missed
real issuers through three further normalisation classes, each now fixed in `variants()` and
verified strictly additive: apostrophes (O'REILLY vs O REILLY), hyphens (G-III vs G III), and
"AND" versus "&" (PETCO HEALTH AND WELLNESS). It also surfaced the class no normalisation can fix,
rated subsidiaries named nothing like their listed parent (JILL ACQUISITION LLC under J.Jill,
SPROUTS FARMERS MARKETS HOLDINGS under Sprouts, CANADA GOOSE INC. under Canada Goose Holdings),
and a subtler trap: strict name matches that land on a dormant co-registrant CIK instead of the
filing company (G-III, Murphy Oil USA, Floor & Decor), which look correct and would silently
yield an empty document set. The harvest, all confirmed against the rating files and EDGAR:
seven active additions usable today (O'Reilly Baa1, Murphy USA Ba1, Floor & Decor Ba3, Canada
Goose Ba3, J.Jill B1, plus Petco's rating reattached to its actual post-2021 listed filer, plus
Sherwin-Williams Baa2 as a scope question), 7-Eleven Baa2 with pre-2005 filings, seven
withdrawn-rating retailers for the historical arm (Abercrombie & Fitch, Birkenstock, Sportsman's
Warehouse, Sprouts, Vince, Pep Boys, Bon-Ton) plus Sears and Toys 'R' Us, and Cintas and Playboy
as mapped but out of scope. Good Sam's filings were traced to Camping World Holdings. The frame is
now 186 entities, 95 actively rated; the uncertain scope calls stand at five (CVS, Samsonite,
Good Sam, Amazon, Sherwin-Williams). Residual, stated plainly: a rated subsidiary with a name
unlike its parent AND no listed parent match survives both directions; nothing catches it except
sector-by-sector eyeballing of the unmatched Moody's names.

The remaining imperfection is honest and bounded: the roughly 5,000 unmatched corporates include
genuinely private retailers that Moody's rates but that file nothing with the SEC, which our system
could not score anyway, and the three uncertain scope calls need a decision, not more data.

## What the files do not answer

**Anything after August 2025.** Post-cutoff labels, the entire clean window, and any 2026 rating
actions are invisible here.

## Bookkeeping

Both zip archives live in `data/` and stay out of git. The parsed intermediate (one JSON of all
obligor paths) is reproducible from the zips with the parsing script and is not committed either.
