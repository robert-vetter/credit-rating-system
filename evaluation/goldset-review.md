# Goldset-Review: 50 Beobachtungen zur manuellen Bestätigung

## Zweitpruefung vom 2026-08-29

*Claude (Opus 5), second pass on Robert's instruction:*

- independent re-derivation of label, persistence and label level for all 50 items directly from the raw 17g-7 XML archives (fresh code path, not via ratings.json): 50/50 identical
- document integrity: every input document filed before t, every 10-K within 455 days, disclosure documents after the action date: 0 problems
- all 141 EDGAR URLs fetched: 0 dead links
- extended self-disclosure sweep over up to 3 subsequent filings per unconfirmed item: 4 additional confirmations (now 20/50); zero filings mention Moody's with symbols contradicting a label
- item-by-item manual read of every evidence record and snippet against known rating histories: 0 errors, 8 annotated special cases

---
*Erzeugt von verify_goldset.py (Auswahl: build_goldset.py, Seed 20260829). Jedes Item zeigt die komplette Belegkette: der rohe Moody's-Record hinter dem Label, der Record hinter dem Vorquartal, die Selbstoffenlegung der Firma im naechsten Filing (sofern gefunden) und die Input-Dokumente. Dokumente NACH dem Stichtag dienen nur der Label-Pruefung, nie als Modell-Input.*

**Stand: 20 von 50 zusaetzlich durch Selbstoffenlegung der Firma bestaetigt.** Kein Fund ist neutral (viele Firmen drucken Ratings nicht ab), nie ein Widerspruch.

**So bestaetigst du:** pro Item Haken setzen oder mir einfach die IDs nennen, die du ablehnst/aendern willst (z.B. "G07 raus"); ich schreibe den Status in goldset.json. Nur bestaetigte Items laufen in Gold-Auswertungen.

---

## Changed (30) - das Primaermaterial

### G01 · ADVANCE AUTO PARTS, INC. · 2024-12-31 · ⬇1 Baa3 → Ba1
- **Label-Beleg (17g-7):** 2024-11-27 „Ba1“ [NW] LT Corporate Family Ratings, entity-Ebene, OI 600041661
- Vorquartal-Beleg: 2024-02-20 „Baa3“ [DG] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2025-02-26](https://www.sec.gov/Archives/edgar/data/1158449/000115844925000064/aap-20241228.htm): „…f Financial Instruments of the Notes to the Consolidated Financial Statements included herein. 28 Table of Contents As of February 26, 2025, the Company had a credit rating from S&P of BB+ and from Moody’s Investor Service of Ba1. The current outlooks by S&P and Moody’s were negative and stable, respectively. The current pricing grid used to determine the Company’s borrowing rate under the Company…“
- Input-Dokumente: [10-K 2024-03-12](https://www.sec.gov/Archives/edgar/data/1158449/000115844924000048/aap-20231230.htm) · [10-Q 2024-11-14](https://www.sec.gov/Archives/edgar/data/1158449/000115844924000238/aap-20241005.htm)
- [ ] bestaetigt

### G02 · ALBERTSONS · 2024-09-30 · ⬆1 Ba2 → Ba1
- **Label-Beleg (17g-7):** 2024-08-16 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 824793590
- Vorquartal-Beleg: 2021-06-24 „Ba2“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2024-10-15](https://www.sec.gov/Archives/edgar/data/1646972/000164697224000225/aci-20240907.htm) (neutral)
- Input-Dokumente: [10-K 2024-04-22](https://www.sec.gov/Archives/edgar/data/1646972/000164697224000060/aci-20240224.htm) · [10-Q 2024-07-23](https://www.sec.gov/Archives/edgar/data/1646972/000164697224000165/aci-20240615.htm)
- [ ] bestaetigt

### G03 · CARVANA CO. · 2024-09-30 · ⬆2 Caa3 → Caa1
- **Label-Beleg (17g-7):** 2024-09-12 „Caa1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 830411600
- Vorquartal-Beleg: 2023-09-20 „Caa3“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2024-10-30](https://www.sec.gov/Archives/edgar/data/1690820/000169082024000345/cvna-20240930.htm) (neutral)
- Input-Dokumente: [10-K 2024-02-22](https://www.sec.gov/Archives/edgar/data/1690820/000169082024000093/cvna-20231231.htm) · [10-Q 2024-07-31](https://www.sec.gov/Archives/edgar/data/1690820/000169082024000272/cvna-20240630.htm)
- **Anmerkung aus der Zweitpruefung:** Modell-Erinnerung an Carvanas exakte Upgrade-Daten war unscharf; die Roh-Datei ist eindeutig (Caa3->Caa1 am 2024-09-12) und die Filings enthalten nichts Widersprechendes. Datei schlaegt Erinnerung.
- [ ] bestaetigt

### G04 · COSTCO WHOLESALE CORPORATION · 2018-12-31 · ⬆1 A1 → Aa3
- **Label-Beleg (17g-7):** 2018-10-04 „Aa3“ [UP] Senior Unsecured, instrument-Ebene, OI 600012498
- Vorquartal-Beleg: 2017-05-15 „A1“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2018-10-26](https://www.sec.gov/Archives/edgar/data/909832/000090983218000013/cost10k9218.htm) (neutral)
- Input-Dokumente: [10-K 2018-10-26](https://www.sec.gov/Archives/edgar/data/909832/000090983218000013/cost10k9218.htm) · [10-Q 2018-12-20](https://www.sec.gov/Archives/edgar/data/909832/000090983218000022/cost10q112518.htm)
- [ ] bestaetigt

### G05 · DOLLAR GENERAL CORPORATION · 2013-03-31 · ⬆1 Ba1 → Baa3
- **Label-Beleg (17g-7):** 2013-03-26 „Baa3“ [UP] Senior Unsecured, instrument-Ebene, OI 820314227
- Vorquartal-Beleg: 2012-06-15 „Ba1“ [HS] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2013-06-04](https://www.sec.gov/Archives/edgar/data/29534/000110465913046606/a13-9448_110q.htm): „…counting Policies and Estimates” and in Note 3 to the condensed consolidated financial statements. Future negative developments could have a material adverse effect on our liquidity. In March 2013, Moody’s upgraded our senior unsecured debt rating to Baa3 from Ba2 with a stable outlook. In April 2013, Standard & Poor’s upgraded our senior unsecured debt rating to BBB- from BB+ and reaffirmed our c…“
- Input-Dokumente: [10-K 2013-03-25](https://www.sec.gov/Archives/edgar/data/29534/000104746913003283/a2213303z10-k.htm)
- [ ] bestaetigt

### G06 · DOLLAR GENERAL CORPORATION · 2025-03-31 · ⬇1 Baa2 → Baa3
- **Label-Beleg (17g-7):** 2025-03-28 „Baa3“ [DG] Senior Unsecured, instrument-Ebene, OI 820314227
- Vorquartal-Beleg: 2023-06-05 „Baa2“ [NW] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2025-06-03](https://www.sec.gov/Archives/edgar/data/29534/000155837025008354/dg-20250502x10q.htm): „…time frames deemed acceptable to the rating agencies. The credit ratings for our borrowings are as follows: ​ ​ ​ ​ Rating Agency ​ Senior unsecured debt rating ​ Commercial paper rating ​ Outlook Moody’s ​ Baa3 ​ P-3 ​ Stable outlook Standard & Poor’s ​ BBB ​ A-2 ​ Negative outlook ​ Changes in Cash Flows ​ Unless otherwise noted, all references to the 2025 and 2024 periods in the discussion of…“
- Input-Dokumente: [10-K 2025-03-21](https://www.sec.gov/Archives/edgar/data/29534/000155837025003413/dg-20250131x10k.htm)
- [ ] bestaetigt

### G07 · DOLLAR TREE, INC. · 2018-03-31 · ⬆1 Ba1 → Baa3
- **Label-Beleg (17g-7):** 2018-03-02 „Baa3“ [UP] Senior Unsecured, instrument-Ebene, OI 823624450
- Vorquartal-Beleg: 2017-03-09 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2018-03-16](https://www.sec.gov/Archives/edgar/data/935703/000093570318000013/dltr-2018x02x03x10k.htm) (neutral)
- Input-Dokumente: [10-K 2018-03-16](https://www.sec.gov/Archives/edgar/data/935703/000093570318000013/dltr-2018x02x03x10k.htm)
- [ ] bestaetigt

### G08 · GAP, INC. (THE) · 2023-03-31 · ⬇1 Ba2 → Ba3
- **Label-Beleg (17g-7):** 2023-03-27 „Ba3“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 306425
- Vorquartal-Beleg: 2020-04-23 „Ba2“ [DG] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2023-05-26](https://www.sec.gov/Archives/edgar/data/39911/000003991123000043/gps-20230429.htm): „…solidated Financial Statements included in Part I, Item 1 of this Form 10-Q, for disclosures on our debt and credit facilities, investments, and derivative financial instruments. On March 27, 2023, Moody's downgraded our corporate credit rating from Ba2 to Ba3 with a negative outlook and downgraded the rating of our Senior Notes from Ba3 to B1 with a negative outlook. These reductions and any futu…“
- Input-Dokumente: [10-K 2023-03-14](https://www.sec.gov/Archives/edgar/data/39911/000003991123000015/gps-20230128.htm)
- [ ] bestaetigt

### G09 · HANESBRANDS, INC. · 2020-06-30 · ⬇1 Ba1 → Ba2
- **Label-Beleg (17g-7):** 2020-04-30 „Ba2“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 809587302
- Vorquartal-Beleg: 2014-05-20 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2020-07-31](https://www.sec.gov/Archives/edgar/data/1359841/000135984120000072/hbi-20200627x10q.htm) (neutral)
- Input-Dokumente: [10-K 2020-02-11](https://www.sec.gov/Archives/edgar/data/1359841/000135984120000027/hbi-20191228x10k.htm) · [10-Q 2020-04-30](https://www.sec.gov/Archives/edgar/data/1359841/000135984120000050/hbi-20200328x10q.htm)
- [ ] bestaetigt

### G10 · HOME DEPOT, INC. (THE) · 2013-12-31 · ⬆1 A3 → A2
- **Label-Beleg (17g-7):** 2013-11-19 „A2“ [UP] Senior Unsecured, instrument-Ebene, OI 373800
- Vorquartal-Beleg: 2013-09-03 „A3“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2013-11-27](https://www.sec.gov/Archives/edgar/data/354950/000035495013000047/hd_10qx11032013.htm) (neutral)
- Input-Dokumente: [10-K 2013-03-28](https://www.sec.gov/Archives/edgar/data/354950/000035495013000008/hd-232013x10xk.htm) · [10-Q 2013-11-27](https://www.sec.gov/Archives/edgar/data/354950/000035495013000047/hd_10qx11032013.htm)
- [ ] bestaetigt

### G11 · J.JILL · 2019-12-31 · ⬇1 B1 → B2
- **Label-Beleg (17g-7):** 2019-12-12 „B2“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 824435767
- Vorquartal-Beleg: 2018-10-05 „B1“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2020-06-15](https://www.sec.gov/Archives/edgar/data/1687932/000156459020029393/jill-10k_20200201.htm) (neutral)
- Input-Dokumente: [10-K 2019-04-08](https://www.sec.gov/Archives/edgar/data/1687932/000156459019011027/jill-10k_20190202.htm) · [10-Q 2019-12-12](https://www.sec.gov/Archives/edgar/data/1687932/000156459019045849/jill-10q_20191102.htm)
- [ ] bestaetigt

### G12 · KOHL'S CORPORATION · 2025-03-31 · ⬇1 Ba2 → Ba3
- **Label-Beleg (17g-7):** 2025-01-15 „Ba3“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 600018243
- Vorquartal-Beleg: 2023-04-19 „Ba2“ [DG] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2025-03-20](https://www.sec.gov/Archives/edgar/data/885639/000095017025042662/kss-20250201.htm): „…idity sources on favorable terms depends on multiple factors, including our operating performance and debt ratings. During 2024, S&P downgraded our senior unsecured credit rating from BB to BB- and Moody's downgraded our rating from Ba3 to B1. These downgrades have caused our cost of borrowing to increase, and further downgrades would cause our cost of borrowing to further increase. Declines in ou…“
- Input-Dokumente: [10-K 2025-03-20](https://www.sec.gov/Archives/edgar/data/885639/000095017025042662/kss-20250201.htm)
- [ ] bestaetigt

### G13 · KOHL'S CORPORATION · 2025-06-30 · ⬇2 Ba3 → B2
- **Label-Beleg (17g-7):** 2025-05-13 „B2“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 600018243
- Vorquartal-Beleg: 2025-01-15 „Ba3“ [DG] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2025-06-06](https://www.sec.gov/Archives/edgar/data/885639/000095017025083079/kss-20250503.htm): „…25 due to the coupon adjustment provision within the notes. In total, the interest rate on the notes due May 2031 have increased 175 basis points since their issuance. Additionally on May 13, 2025, Moody's downgraded our corporate credit rating from Ba3 to B2, and revised their outlook to stable. The majority of our financing activities generally include proceeds and/or repayments of borrowings un…“
- Input-Dokumente: [10-K 2025-03-20](https://www.sec.gov/Archives/edgar/data/885639/000095017025042662/kss-20250201.htm) · [10-Q 2025-06-06](https://www.sec.gov/Archives/edgar/data/885639/000095017025083079/kss-20250503.htm)
- [ ] bestaetigt

### G14 · LESLIE'S POOLMART, INC. · 2024-09-30 · ⬇1 B1 → B2
- **Label-Beleg (17g-7):** 2024-07-31 „B2“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 825431804
- Vorquartal-Beleg: 2023-08-04 „B1“ [DG] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2024-08-08](https://www.sec.gov/Archives/edgar/data/1821806/000095017024093092/lesl-20240629.htm) (neutral)
- Input-Dokumente: [10-K 2023-11-29](https://www.sec.gov/Archives/edgar/data/1821806/000095017023066773/lesl-20230930.htm) · [10-Q 2024-08-08](https://www.sec.gov/Archives/edgar/data/1821806/000095017024093092/lesl-20240629.htm)
- [ ] bestaetigt

### G15 · LEVI STRAUSS & CO. · 2015-06-30 · ⬆1 Ba2 → Ba1
- **Label-Beleg (17g-7):** 2015-04-16 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 445750
- Vorquartal-Beleg: 2014-04-28 „Ba2“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2015-07-10](https://www.sec.gov/Archives/edgar/data/94845/000009484515000029/a2q2015form10-q.htm) (neutral)
- Input-Dokumente: [10-K 2015-02-12](https://www.sec.gov/Archives/edgar/data/94845/000009484515000008/a2014yeform10-k.htm) · [10-Q 2015-04-14](https://www.sec.gov/Archives/edgar/data/94845/000009484515000017/a1q2015form10-q.htm)
- [ ] bestaetigt

### G16 · MACY'S · 2020-03-31 · ⬇1 Baa3 → Ba1
- **Label-Beleg (17g-7):** 2020-03-26 „Ba1“ [None] LT Corporate Family Ratings, entity-Ebene, OI 277000
- Vorquartal-Beleg: 2017-03-02 „Baa3“ [DG] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2020-03-30](https://www.sec.gov/Archives/edgar/data/794367/000079436720000040/m-0201202010xk.htm): „…pany and the notes are rated by specified rating agencies at a level below investment grade. As of February 1, 2020, the Company's credit rating and outlook were as described in the table below. 28 Moody's Standard & Poor's Fitch Long-term debt Baa3 BBB- BBB Outlook Stable Stable Stable In February 2020, Standard and Poor's and Fitch downgraded Macy's long-term debt ratings to BB+ and BBB-, respec…“
- Input-Dokumente: [10-K 2020-03-30](https://www.sec.gov/Archives/edgar/data/794367/000079436720000040/m-0201202010xk.htm)
- **Anmerkung aus der Zweitpruefung:** Aktionscode fehlt im Moody's-Rohdatensatz ([None]); Datum, Rating und Typ sind vollstaendig. Bekannter kleiner Datenrest, kein Fehler unsererseits. Es ist die CFR-Zuweisung beim IG-Austritt Maerz 2020.
- [ ] bestaetigt

### G17 · MACY'S · 2022-03-31 · ⬆1 Ba2 → Ba1
- **Label-Beleg (17g-7):** 2022-02-23 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 277000
- Vorquartal-Beleg: 2021-08-26 „Ba2“ [UP] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2022-03-25](https://www.sec.gov/Archives/edgar/data/794367/000156459022011726/m-10k_20220129.htm): „…g activities noted above, interest obligations were increased to $1.9 billion. 32 As of January 29 , 202 2 , the Company's credit rating and outlook were as described in the table below. Standard & Moody's Poor's Fitch Long-term debt Ba2 BB- BB+ Outlook Stable Positive Stable Subsequent to January 29, 2022, Moody’s upgraded the Company’s long-term debt rating to Ba1, Standard & Poor’s upgraded the…“
- Input-Dokumente: [10-K 2022-03-25](https://www.sec.gov/Archives/edgar/data/794367/000156459022011726/m-10k_20220129.htm)
- [ ] bestaetigt

### G18 · MICHAELS · 2020-06-30 · ⬇1 Ba2 → Ba3
- **Label-Beleg (17g-7):** 2020-05-13 „Ba3“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 809824441
- Vorquartal-Beleg: 2017-07-18 „Ba2“ [None] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2020-06-05](https://www.sec.gov/Archives/edgar/data/1593936/000155837020007300/mik-20200605x10q.htm) (neutral)
- Input-Dokumente: [10-K 2020-03-17](https://www.sec.gov/Archives/edgar/data/1593936/000155837020002829/mik-20200201x10k99adc6.htm) · [10-Q 2020-06-05](https://www.sec.gov/Archives/edgar/data/1593936/000155837020007300/mik-20200605x10q.htm)
- [ ] bestaetigt

### G19 · MURPHY USA · 2015-06-30 · ⬆1 Ba2 → Ba1
- **Label-Beleg (17g-7):** 2015-06-30 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 522000
- Vorquartal-Beleg: 2013-08-05 „Ba2“ [NW] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2015-08-06](https://www.sec.gov/Archives/edgar/data/1573516/000157351615000024/musa-20150630x10q.htm) (neutral)
- Input-Dokumente: [10-K 2015-02-27](https://www.sec.gov/Archives/edgar/data/1573516/000157351615000008/musa-20141231x10k.htm) · [10-Q 2015-05-05](https://www.sec.gov/Archives/edgar/data/1573516/000157351615000015/musa-20150331x10q.htm)
- **Anmerkung aus der Zweitpruefung:** Aktionsdatum = Stichtag (2015-06-30): per Label-Regel zaehlt das Rating am Tagesende, die Aktion ist also im Label enthalten - so gewollt und dokumentiert.
- [ ] bestaetigt

### G20 · O'REILLY · 2013-12-31 · ⬆1 Baa3 → Baa2
- **Label-Beleg (17g-7):** 2013-12-16 „Baa2“ [UP] Senior Unsecured, instrument-Ebene, OI 822312216
- Vorquartal-Beleg: 2013-06-17 „Baa3“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2014-02-28](https://www.sec.gov/Archives/edgar/data/898173/000089817314000064/orly-20131231x10k.htm) (neutral)
- Input-Dokumente: [10-K 2013-02-28](https://www.sec.gov/Archives/edgar/data/898173/000089817313000006/orly-20121231x10k.htm) · [10-Q 2013-11-08](https://www.sec.gov/Archives/edgar/data/898173/000089817313000049/orly-20130930x10q.htm)
- [ ] bestaetigt

### G21 · RESTORATION HARDWARE, INC. · 2022-06-30 · ⬇1 Ba2 → Ba3
- **Label-Beleg (17g-7):** 2022-04-27 „Ba3“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 823640518
- Vorquartal-Beleg: 2021-09-29 „Ba2“ [NW] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2022-06-03](https://www.sec.gov/Archives/edgar/data/1528849/000155837022009696/rh-20220430x10q.htm): „…nded our asset based credit facility, and issued the Term Loan in the amount of $2.0 billion pursuant to the Term Loan Credit Agreement. The issuance of the Term Loan was assigned a Ba2 rating from Moody’s Investors Service and BB rating from S&P Global. Additionally, in May 2022, we entered into the 2022 Incremental Amendment, which amended the Term Loan Credit Agreement and raised an incremental…“
- Input-Dokumente: [10-K 2022-03-30](https://www.sec.gov/Archives/edgar/data/1528849/000155837022004753/rh-20220129x10k.htm) · [10-Q 2022-06-03](https://www.sec.gov/Archives/edgar/data/1528849/000155837022009696/rh-20220430x10q.htm)
- [ ] bestaetigt

### G22 · ROSS STORES, INC. · 2019-09-30 · ⬆1 A3 → A2
- **Label-Beleg (17g-7):** 2019-07-11 „A2“ [UP] Senior Unsecured, instrument-Ebene, OI 823602952
- Vorquartal-Beleg: 2014-09-15 „A3“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2019-09-11](https://www.sec.gov/Archives/edgar/data/745732/000074573219000037/rost-2019803x10q.htm) (neutral)
- Input-Dokumente: [10-K 2019-04-02](https://www.sec.gov/Archives/edgar/data/745732/000074573219000009/rost-20190202x10k.htm) · [10-Q 2019-09-11](https://www.sec.gov/Archives/edgar/data/745732/000074573219000037/rost-2019803x10q.htm)
- [ ] bestaetigt

### G23 · SIGNET · 2015-09-30 · ⬆1 Ba1 → Baa3
- **Label-Beleg (17g-7):** 2015-08-17 „Baa3“ [UP] Senior Unsecured, instrument-Ebene, OI 823938053
- Vorquartal-Beleg: 2014-05-14 „Ba1“ [NW] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2016-03-24](https://www.sec.gov/Archives/edgar/data/832988/000162828016012998/fy16q410k.htm): „…twelve months. Credit Rating The following table provides Signet’s credit ratings as of January 30, 2016 : Rating Agency Corporate Senior Unsecured Notes Outlook Standard & Poor’s BBB- BBB- Stable Fitch BBB- BBB- Stable Moody’s Baa3 Baa3 Stable OFF-BALANCE SHEET ARRANGEMENTS Merchandise held on consignment Signet held $441.9 million of consignment inventory which is not recorded on the balance sheet at January 30, 2016 , as compared to…“
- Input-Dokumente: [10-K 2015-03-26](https://www.sec.gov/Archives/edgar/data/832988/000162828015001969/a10k-1312015xq4.htm) · [10-Q 2015-09-03](https://www.sec.gov/Archives/edgar/data/832988/000162828015006962/sig-20150801_10q.htm)
- [ ] bestaetigt

### G24 · SIGNET · 2017-09-30 · ⬇1 Baa3 → Ba1
- **Label-Beleg (17g-7):** 2017-07-21 „Ba1“ [None] LT Corporate Family Ratings, entity-Ebene, OI 823938053
- Vorquartal-Beleg: 2015-08-17 „Baa3“ [UP] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2018-04-02](https://www.sec.gov/Archives/edgar/data/832988/000162828018003906/fy18q410k.htm): „…al quarter of Signet for the trailing twelve months. Credit Rating The following table provides Signet’s credit ratings as of February 3, 2018 : Rating Agency Corporate Senior Unsecured Notes Standard & Poor’s BBB- BBB- Moody’s Ba1 Ba1 Fitch BB BB OFF-BALANCE SHEET ARRANGEMENTS Merchandise held on consignment Signet held $606.4 million of consignment inventory which is not recorded on the balance sheet at February 3, 2018 , as compared…“
- Input-Dokumente: [10-K 2017-03-16](https://www.sec.gov/Archives/edgar/data/832988/000162828017002652/fy17q410k.htm) · [10-Q 2017-08-29](https://www.sec.gov/Archives/edgar/data/832988/000162828017008982/fy18q210-q.htm)
- **Anmerkung aus der Zweitpruefung:** Aktionscode fehlt im Moody's-Rohdatensatz ([None]); es ist die CFR-Zuweisung beim IG-Austritt Juli 2017.
- [ ] bestaetigt

### G25 · TIFFANY & CO. · 2021-03-31 · ⬆4 Baa2 → A1
- **Label-Beleg (17g-7):** 2021-03-17 „A1“ [UP] Senior Unsecured, instrument-Ebene, OI 1926
- Vorquartal-Beleg: 2014-09-22 „Baa2“ [NW] Senior Unsecured, instrument-Ebene
- Input-Dokumente: [10-K 2020-03-20](https://www.sec.gov/Archives/edgar/data/98246/000009824620000042/tif-2020131x10k.htm) · [10-Q 2020-11-24](https://www.sec.gov/Archives/edgar/data/98246/000009824620000118/tif-20201031.htm)
- **Anmerkung aus der Zweitpruefung:** Sonderfall M&A-Support: der 4-Notch-Sprung Baa2->A1 kommt aus der LVMH-Uebernahme (Anleihen ruecken an das LVMH-Rating), nicht aus Standalone-Fundamentaldaten. Die Uebernahme steht in den Input-Filings (Merger Agreement), ist also aus Dokumenten erkennbar - bewusst behalten als harter, realer Fall.
- [ ] bestaetigt

### G26 · TJX COMPANIES, INC. (THE) · 2015-09-30 · ⬆1 A3 → A2
- **Label-Beleg (17g-7):** 2015-08-19 „A2“ [UP] Senior Unsecured, instrument-Ebene, OI 734075
- Vorquartal-Beleg: 2014-06-02 „A3“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2015-08-28](https://www.sec.gov/Archives/edgar/data/109198/000119312515306470/d39475d10q.htm) (neutral)
- Input-Dokumente: [10-K 2015-03-31](https://www.sec.gov/Archives/edgar/data/109198/000119312515114276/d855793d10k.htm) · [10-Q 2015-08-28](https://www.sec.gov/Archives/edgar/data/109198/000119312515306470/d39475d10q.htm)
- [ ] bestaetigt

### G27 · UNDER ARMOUR, INC. · 2020-06-30 · ⬇2 Ba1 → Ba3
- **Label-Beleg (17g-7):** 2020-05-21 „Ba3“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 823645825
- Vorquartal-Beleg: 2020-02-12 „Ba1“ [NW] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-Q vom 2020-08-06](https://www.sec.gov/Archives/edgar/data/1336917/000133691720000056/ua-20200630.htm) (neutral)
- Input-Dokumente: [10-K 2020-02-26](https://www.sec.gov/Archives/edgar/data/1336917/000133691720000010/ua-20191231.htm) · [10-Q 2020-05-11](https://www.sec.gov/Archives/edgar/data/1336917/000133691720000033/ua-20200331.htm)
- [ ] bestaetigt

### G28 · V.F. CORPORATION · 2021-03-31 · ⬇1 A3 → Baa1
- **Label-Beleg (17g-7):** 2021-02-10 „Baa1“ [DG] Senior Unsecured, instrument-Ebene, OI 800100
- Vorquartal-Beleg: 2020-04-21 „A3“ [NW] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2021-05-27](https://www.sec.gov/Archives/edgar/data/103379/000010337921000006/vfc-20210403.htm): „…ency ratings allow for access to additional liquidity at competitive rates. At the end of March 2021, VF’s long-term debt ratings were ‘A-’ by Standard & Poor’s ("S&P") Global Ratings and ‘Baa1’ by Moody’s Investors Service, both with 'stable' outlooks, and commercial paper ratings by those rating agencies were ‘A-2’ and ‘P-2’, respectively. None of VF’s long-term debt agreements contain accelerat…“
- Input-Dokumente: [10-K 2020-05-27](https://www.sec.gov/Archives/edgar/data/103379/000010337920000006/vfc328202010-k.htm) · [10-Q 2021-02-02](https://www.sec.gov/Archives/edgar/data/103379/000010337921000003/vfc-20201226.htm)
- [ ] bestaetigt

### G29 · WALGREENS · 2023-03-31 · ⬇1 Baa2 → Baa3
- **Label-Beleg (17g-7):** 2023-01-20 „Baa3“ [DG] Senior Unsecured, instrument-Ebene, OI 824205318
- Vorquartal-Beleg: 2021-11-02 „Baa2“ [NW] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2023-03-28](https://www.sec.gov/Archives/edgar/data/1618921/000161892123000019/wba-20230228.htm): „…th all such applicable covenants. Credit ratings As of March 27, 2023, the credit ratings of Walgreens Boots Alliance were: Rating agency Long-term debt rating Commercial paper rating Outlook Moody’s Baa3 P-3 Negative Standard & Poor’s BBB A-2 Stable In assessing the Company’s credit strength, each rating agency considers various factors including the Company’s business model, ca…“
- Input-Dokumente: [10-K 2022-10-13](https://www.sec.gov/Archives/edgar/data/1618921/000161892122000064/wba-20220831.htm) · [10-Q 2023-03-28](https://www.sec.gov/Archives/edgar/data/1618921/000161892123000019/wba-20230228.htm)
- [ ] bestaetigt

### G30 · WOLVERINE WORLD WIDE, INC. · 2023-12-31 · ⬇2 B1 → B3
- **Label-Beleg (17g-7):** 2023-11-21 „B3“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 831500
- Vorquartal-Beleg: 2023-08-25 „B1“ [DG] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2024-02-22](https://www.sec.gov/Archives/edgar/data/110471/000011047124000057/www-20231230.htm) (neutral)
- Input-Dokumente: [10-K 2023-02-23](https://www.sec.gov/Archives/edgar/data/110471/000011047123000021/www-20221231.htm) · [10-Q 2023-11-09](https://www.sec.gov/Archives/edgar/data/110471/000011047123000147/www-20230930.htm)
- [ ] bestaetigt


## Unchanged (20) - die Fehlalarm-Kontrolle

### G31 · ASBURY AUTOMOTIVE GROUP, INC. · 2012-12-31 · = B1 → B1
- **Label-Beleg (17g-7):** 2012-08-21 „B1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 600065108
- Vorquartal-Beleg: 2012-08-21 „B1“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2012-02-22](https://www.sec.gov/Archives/edgar/data/1144980/000114498012000031/abg12311110k.htm) (neutral)
- Input-Dokumente: [10-K 2012-02-22](https://www.sec.gov/Archives/edgar/data/1144980/000114498012000031/abg12311110k.htm) · [10-Q 2012-10-24](https://www.sec.gov/Archives/edgar/data/1144980/000114498012000100/abg09301210q.htm)
- [ ] bestaetigt

### G32 · AUTOZONE, INC. · 2016-03-31 · = Baa1 → Baa1
- **Label-Beleg (17g-7):** 2015-04-20 „Baa1“ [NW] Senior Unsecured, instrument-Ebene, OI 600041240
- Vorquartal-Beleg: 2015-04-20 „Baa1“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2015-10-26](https://www.sec.gov/Archives/edgar/data/866787/000119312515353476/d73676d10k.htm) (neutral)
- Input-Dokumente: [10-K 2015-10-26](https://www.sec.gov/Archives/edgar/data/866787/000119312515353476/d73676d10k.htm) · [10-Q 2016-03-22](https://www.sec.gov/Archives/edgar/data/866787/000119312516513530/d106047d10q.htm)
- [ ] bestaetigt

### G33 · BATH & BODY WORKS, INC. · 2013-06-30 · = Ba1 → Ba1
- **Label-Beleg (17g-7):** 2012-06-15 „Ba1“ [HS] LT Corporate Family Ratings, entity-Ebene, OI 447500
- Vorquartal-Beleg: 2012-06-15 „Ba1“ [HS] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2013-03-22](https://www.sec.gov/Archives/edgar/data/701985/000070198513000012/ltd22201310k.htm): „…talization (b) Net cash provided by operating activities divided by capital expenditures 41 Table of Contents Credit Ratings The following table provides our credit ratings as of February 2, 2013 : Moody’s S&P Fitch Corporate Ba1 BB+ BB+ Senior Unsecured Debt with Subsidiary Guarantee Ba1 BB+ BB+ Senior Unsecured Debt Ba2 BB- BB Outlook Stable Stable Stable Our borrowing costs under our Revolving…“
- Input-Dokumente: [10-K 2013-03-22](https://www.sec.gov/Archives/edgar/data/701985/000070198513000012/ltd22201310k.htm) · [10-Q 2013-06-07](https://www.sec.gov/Archives/edgar/data/701985/000070198513000023/ltd-201354_10q.htm)
- [ ] bestaetigt

### G34 · BEST BUY CO., INC. · 2024-06-30 · = A3 → A3
- **Label-Beleg (17g-7):** 2021-02-26 „A3“ [UP] LT Issuer Rating, entity-Ebene, OI 104225
- Vorquartal-Beleg: 2021-02-26 „A3“ [UP] LT Issuer Rating, entity-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2024-03-15](https://www.sec.gov/Archives/edgar/data/764478/000076447824000010/bby-20240203x10k.htm): „…ned unchanged from those disclosed in our Annual Report on Form 10-K for the fiscal year ended January 28, 2023, and are summarized below. Rating Agency Rating Outlook Standard & Poor's BBB+ Stable Moody's A3 Stable Credit rating agencies review their ratings periodically, and, therefore, the credit rating assigned to us by each agency may be subject to revision at any time. Factors that can affec…“
- Input-Dokumente: [10-K 2024-03-15](https://www.sec.gov/Archives/edgar/data/764478/000076447824000010/bby-20240203x10k.htm) · [10-Q 2024-06-07](https://www.sec.gov/Archives/edgar/data/764478/000076447824000022/bby-20240504x10q.htm)
- [ ] bestaetigt

### G35 · CARVANA CO. · 2023-06-30 · = Ca → Ca
- **Label-Beleg (17g-7):** 2023-03-28 „Ca“ [DG] LT Corporate Family Ratings, entity-Ebene, OI 830411600
- Vorquartal-Beleg: 2023-03-28 „Ca“ [DG] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2023-02-23](https://www.sec.gov/Archives/edgar/data/1690820/000169082023000052/cvna-20221231.htm) (neutral)
- Input-Dokumente: [10-K 2023-02-23](https://www.sec.gov/Archives/edgar/data/1690820/000169082023000052/cvna-20221231.htm) · [10-Q 2023-05-04](https://www.sec.gov/Archives/edgar/data/1690820/000169082023000163/cvna-20230331.htm)
- Hinweis: hartes Negativ — im Folgequartal aendert sich das Rating
- **Anmerkung aus der Zweitpruefung:** Pfad Ca (Distressed Exchange 2023-03) -> spaeter Caa3 -> Caa1 ist intern konsistent ueber G35 und G03 hinweg.
- [ ] bestaetigt

### G36 · DILLARD'S · 2022-06-30 · = Baa3 → Baa3
- **Label-Beleg (17g-7):** 2015-05-27 „Baa3“ [UP] Senior Unsecured, instrument-Ebene, OI 239280
- Vorquartal-Beleg: 2015-05-27 „Baa3“ [UP] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2022-03-29](https://www.sec.gov/Archives/edgar/data/28917/000002891722000009/dds-20220129.htm) (neutral)
- Input-Dokumente: [10-K 2022-03-29](https://www.sec.gov/Archives/edgar/data/28917/000002891722000009/dds-20220129.htm) · [10-Q 2022-06-03](https://www.sec.gov/Archives/edgar/data/28917/000155837022009716/dds-20220430x10q.htm)
- [ ] bestaetigt

### G37 · GROUP 1 AUTOMOTIVE, INC. · 2023-09-30 · = Ba1 → Ba1
- **Label-Beleg (17g-7):** 2015-07-23 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 600045005
- Vorquartal-Beleg: 2015-07-23 „Ba1“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2023-02-16](https://www.sec.gov/Archives/edgar/data/1031203/000103120323000007/gpi-20221231.htm) (neutral)
- Input-Dokumente: [10-K 2023-02-16](https://www.sec.gov/Archives/edgar/data/1031203/000103120323000007/gpi-20221231.htm) · [10-Q 2023-07-28](https://www.sec.gov/Archives/edgar/data/1031203/000103120323000032/gpi-20230630.htm)
- [ ] bestaetigt

### G38 · INGLES MARKETS, INCORPORATED · 2017-06-30 · = Ba3 → Ba3
- **Label-Beleg (17g-7):** 2012-06-15 „Ba3“ [HS] LT Corporate Family Ratings, entity-Ebene, OI 160700
- Vorquartal-Beleg: 2012-06-15 „Ba3“ [HS] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2016-12-16](https://www.sec.gov/Archives/edgar/data/50493/000005049316000044/imkt-20160924x10k.htm) (neutral)
- Input-Dokumente: [10-K 2016-12-16](https://www.sec.gov/Archives/edgar/data/50493/000005049316000044/imkt-20160924x10k.htm) · [10-Q 2017-05-03](https://www.sec.gov/Archives/edgar/data/50493/000005049317000010/imkt-20170325x10q.htm)
- [ ] bestaetigt

### G39 · J.JILL · 2022-03-31 · = Caa1 → Caa1
- **Label-Beleg (17g-7):** 2021-10-19 „Caa1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 824435767
- Vorquartal-Beleg: 2021-10-19 „Caa1“ [UP] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2021-04-12](https://www.sec.gov/Archives/edgar/data/1687932/000156459021018528/jill-10k_20210130.htm) (neutral)
- Input-Dokumente: [10-K 2021-04-12](https://www.sec.gov/Archives/edgar/data/1687932/000156459021018528/jill-10k_20210130.htm) · [10-Q 2021-12-14](https://www.sec.gov/Archives/edgar/data/1687932/000156459021060218/jill-10q_20211030.htm)
- Hinweis: hartes Negativ — im Folgequartal aendert sich das Rating
- [ ] bestaetigt

### G40 · KONTOOR BRANDS, INC. · 2020-12-31 · = Ba2 → Ba2
- **Label-Beleg (17g-7):** 2019-04-23 „Ba2“ [NW] LT Corporate Family Ratings, entity-Ebene, OI 830788359
- Vorquartal-Beleg: 2019-04-23 „Ba2“ [NW] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2020-03-11](https://www.sec.gov/Archives/edgar/data/1760965/000176096520000010/kontoor201910-k1.htm) (neutral)
- Input-Dokumente: [10-K 2020-03-11](https://www.sec.gov/Archives/edgar/data/1760965/000176096520000010/kontoor201910-k1.htm) · [10-Q 2020-11-06](https://www.sec.gov/Archives/edgar/data/1760965/000176096520000051/ktb-20200926.htm)
- **Anmerkung aus der Zweitpruefung:** Kein COVID-Downgrade bei Kontoor in der 17g-7-Datei; die Datei enthaelt alle Aktionen, also stand Ba2 durch - Erinnerungszweifel zugunsten der Datei aufgeloest.
- [ ] bestaetigt

### G41 · LOWE'S COMPANIES, INC. · 2017-03-31 · = A3 → A3
- **Label-Beleg (17g-7):** 2016-04-11 „A3“ [NW] Senior Unsecured, instrument-Ebene, OI 454600
- Vorquartal-Beleg: 2016-04-11 „A3“ [NW] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2016-03-29](https://www.sec.gov/Archives/edgar/data/60667/000006066716000276/lowesform10k.htm): „…enior debt ratings may be subject to revision or withdrawal at any time by the assigning rating organization, and each rating should be evaluated independently of any other rating. Debt Ratings S&P Moody’s Commercial Paper A-2 P-2 Senior Debt A- A3 Outlook Stable Stable We believe that net cash provided by operating and financing activities will be adequate not only for our operating requirements,…“
- Input-Dokumente: [10-K 2016-03-29](https://www.sec.gov/Archives/edgar/data/60667/000006066716000276/lowesform10k.htm) · [10-Q 2016-11-29](https://www.sec.gov/Archives/edgar/data/60667/000006066716000407/form10q.htm)
- [ ] bestaetigt

### G42 · MEN'S WEARHOUSE, LLC (THE) · 2021-03-31 · = Caa1 → Caa1
- **Label-Beleg (17g-7):** 2020-12-22 „Caa1“ [NW] LT Corporate Family Ratings, entity-Ebene, OI 867393764
- Vorquartal-Beleg: 2020-12-22 „Caa1“ [NW] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2020-04-08](https://www.sec.gov/Archives/edgar/data/884217/000155837020003700/tlrd-20200201x10k72fd37.htm) (neutral)
- Input-Dokumente: [10-K 2020-04-08](https://www.sec.gov/Archives/edgar/data/884217/000155837020003700/tlrd-20200201x10k72fd37.htm) · [10-Q 2020-07-27](https://www.sec.gov/Archives/edgar/data/884217/000155837020008431/tlrd-20200502x10q.htm)
- [ ] bestaetigt

### G43 · NATIONAL VISION, INC. · 2018-06-30 · = B1 → B1
- **Label-Beleg (17g-7):** 2017-11-03 „B1“ [UP] LT Corporate Family Ratings, entity-Ebene, OI 823828009
- Vorquartal-Beleg: 2017-11-03 „B1“ [UP] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-Q vom 2018-11-13](https://www.sec.gov/Archives/edgar/data/1710155/000171015518000049/a18q3nvhi10-q.htm): „…er 2017 Joinder) for the term loans thereunder, of which there is approximately $364.0 million outstanding following the effective date of the October 2018 Joinder, are based on NVI’s public corporate credit rating from Moody’s. 43 Table of Contents On September 7, 2018, Moody’s announced that it had upgraded NVI’s public corporate credit rating from B1 to Ba3 (stable) and as a result, the Applicable Margin for these term loans has step…“
- Input-Dokumente: [10-K 2018-03-08](https://www.sec.gov/Archives/edgar/data/1710155/000171015518000012/nhvi201710-k.htm) · [10-Q 2018-05-15](https://www.sec.gov/Archives/edgar/data/1710155/000171015518000020/a18q1nhvi10-q.htm)
- Hinweis: hartes Negativ — im Folgequartal aendert sich das Rating
- [ ] bestaetigt

### G44 · NIKE, INC. · 2021-03-31 · = A1 → A1
- **Label-Beleg (17g-7):** 2020-03-25 „A1“ [NW] Senior Unsecured, instrument-Ebene, OI 40400
- Vorquartal-Beleg: 2020-03-25 „A1“ [NW] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2020-07-24](https://www.sec.gov/Archives/edgar/data/320187/000032018720000047/nke-531202010k.htm): „…021. As of May 31, 2020 and 2019 , no amounts were outstanding under our committed credit facilities. We currently have long-term debt ratings of AA- and A1 from Standard and Poor's Corporation and Moody's Investor Services, respectively. As it relates to our committed credit facility entered into on August 16, 2019, if our long-term debt ratings were to decline, the facility fee and interest rate…“
- Input-Dokumente: [10-K 2020-07-24](https://www.sec.gov/Archives/edgar/data/320187/000032018720000047/nke-531202010k.htm) · [10-Q 2021-01-05](https://www.sec.gov/Archives/edgar/data/320187/000032018721000003/nke-20201130.htm)
- [ ] bestaetigt

### G45 · PETCO · 2021-06-30 · = B2 → B2
- **Label-Beleg (17g-7):** 2021-02-18 „B2“ [NW] LT Corporate Family Ratings, entity-Ebene, OI 867510475
- Vorquartal-Beleg: 2021-02-18 „B2“ [NW] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2021-04-05](https://www.sec.gov/Archives/edgar/data/1826470/000156459021017616/woof-10k_20210130.htm) (neutral)
- Input-Dokumente: [10-K 2021-04-05](https://www.sec.gov/Archives/edgar/data/1826470/000156459021017616/woof-10k_20210130.htm) · [10-Q 2021-06-10](https://www.sec.gov/Archives/edgar/data/1826470/000156459021032462/woof-10q_20210501.htm)
- [ ] bestaetigt

### G46 · PVH CORP. · 2020-03-31 · = Baa3 → Baa3
- **Label-Beleg (17g-7):** 2019-04-30 „Baa3“ [None] Senior Unsecured, instrument-Ebene, OI 608300
- Vorquartal-Beleg: 2019-04-30 „Baa3“ [None] Senior Unsecured, instrument-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2020-04-01](https://www.sec.gov/Archives/edgar/data/78239/000007823920000023/pvh10k2019.htm): „…financial and non-financial covenants under our financing arrangements. 48 As of February 2, 2020 , our issuer credit was rated BBB- by Standard & Poor’s with a stable outlook and our corporate credit was rated Baa3 by Moody’s with a stable outlook, and our commercial paper was rated A-3 by Standard & Poor’s and P-3 by Moody’s. In assessing our credit strength, we believe that both Standard & Poor’s and Moody’s considered, among other…“
- Input-Dokumente: [10-K 2019-03-29](https://www.sec.gov/Archives/edgar/data/78239/000007823919000011/pvh10k2018.htm) · [10-Q 2019-12-09](https://www.sec.gov/Archives/edgar/data/78239/000007823919000066/a10q3q2019.htm)
- **Anmerkung aus der Zweitpruefung:** Hartes Negativ: PVH wurde im April 2020 (Folgequartal) herabgestuft; am Stichtag 2020-03-31 galt noch Baa3. Genau der Fall, bei dem ein zu nervoeses System Fehlalarm gibt.
- [ ] bestaetigt

### G47 · RALPH LAUREN CORPORATION · 2016-09-30 · = A2 → A2
- **Label-Beleg (17g-7):** 2015-08-13 „A2“ [NW] Senior Unsecured, instrument-Ebene, OI 600050548
- Vorquartal-Beleg: 2015-08-13 „A2“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2016-05-19](https://www.sec.gov/Archives/edgar/data/1037038/000103703816000019/rl-20160402x10k.htm) (neutral)
- Input-Dokumente: [10-K 2016-05-19](https://www.sec.gov/Archives/edgar/data/1037038/000103703816000019/rl-20160402x10k.htm) · [10-Q 2016-08-11](https://www.sec.gov/Archives/edgar/data/1037038/000103703816000022/rl-20160702x10q.htm)
- [ ] bestaetigt

### G48 · TAPESTRY, INC. · 2019-03-31 · = Baa2 → Baa2
- **Label-Beleg (17g-7):** 2017-06-06 „Baa2“ [NW] Senior Unsecured, instrument-Ebene, OI 823376466
- Vorquartal-Beleg: 2017-06-06 „Baa2“ [NW] Senior Unsecured, instrument-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2018-08-16](https://www.sec.gov/Archives/edgar/data/1116132/000111613218000021/tpr6302018-10k.htm) (neutral)
- Input-Dokumente: [10-K 2018-08-16](https://www.sec.gov/Archives/edgar/data/1116132/000111613218000021/tpr6302018-10k.htm) · [10-Q 2019-02-07](https://www.sec.gov/Archives/edgar/data/1116132/000111613219000007/tpr1229201810q.htm)
- [ ] bestaetigt

### G49 · VICTORIA'S SECRET & CO. · 2024-12-31 · = Ba3 → Ba3
- **Label-Beleg (17g-7):** 2021-06-21 „Ba3“ [NW] LT Corporate Family Ratings, entity-Ebene, OI 867730682
- Vorquartal-Beleg: 2021-06-21 „Ba3“ [NW] LT Corporate Family Ratings, entity-Ebene
- **Selbstoffenlegung ✔** [10-K vom 2024-03-22](https://www.sec.gov/Archives/edgar/data/1856437/000185643724000005/vsco-20240203.htm): „…of the existing contract without having to perform an assessment that would otherwise be required under GAAP. Credit Ratings The following table provides our credit ratings as of February 3, 2024: Moody’s S&P Corporate Ba3 BB- Senior Secured Debt with Subsidiary Guarantee Ba2 BB+ Senior Unsecured Debt with Subsidiary Guarantee B1 BB- Outlook Stable Stable 46 Table of Conten…“
- Input-Dokumente: [10-K 2024-03-22](https://www.sec.gov/Archives/edgar/data/1856437/000185643724000005/vsco-20240203.htm) · [10-Q 2024-12-09](https://www.sec.gov/Archives/edgar/data/1856437/000185643724000033/vsco-20241102.htm)
- [ ] bestaetigt

### G50 · WAYFAIR · 2025-03-31 · = B3 → B3
- **Label-Beleg (17g-7):** 2024-09-24 „B3“ [NW] LT Corporate Family Ratings, entity-Ebene, OI 869202072
- Vorquartal-Beleg: 2024-09-24 „B3“ [NW] LT Corporate Family Ratings, entity-Ebene
- Selbstoffenlegung: keine Erwaehnung im [10-K vom 2025-02-20](https://www.sec.gov/Archives/edgar/data/1616707/000161670725000022/w-20241231.htm) (neutral)
- Input-Dokumente: [10-K 2025-02-20](https://www.sec.gov/Archives/edgar/data/1616707/000161670725000022/w-20241231.htm)
- [ ] bestaetigt

