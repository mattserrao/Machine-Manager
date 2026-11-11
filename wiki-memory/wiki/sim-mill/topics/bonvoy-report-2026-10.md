---
name: bonvoy-report-2026-10
description: the seven daily Bonvoy Reports for 2026-10-25 to 2026-10-31 (couch roll vibration, REF 2 plate wear, reel drum danger watch, headbox, freeness, REF 1); read for what was ranked and linked WOs/docs at the end of October 2026
type: topic
aliases: ["Bonvoy Report 2026-10-25", "Bonvoy Report 2026-10-31", "daily Bonvoy report", "Bonvoy_Report_PM1"]
---
Tool: bonvoy_report date=<day>. Each report has "report_date" = day + 1 (day 2026-10-25 is report_date 2026-10-26, file Bonvoy_Report_PM1_2026-10-25.json). See [[bonvoy]].

## Ranked items by day (rank 1 first)
- 2026-10-25: 2 tags. 1 [[couch-roll]] COUCH_DS_VIB 19 h, 9-day streak, 18.6 sigma, +14.93 %/day; 2 REF_B_SE 19 h, 6-day streak. [Bonvoy Report 2026-10-25]
- 2026-10-26: 3 tags. COUCH_DS_VIB 10-day streak; REF_B_SE 7-day; new HB_P Low 4 h (rank 3, 11.6 psi mode). [Bonvoy Report 2026-10-26]
- 2026-10-27: 2 tags, all continuing: COUCH_DS_VIB 11-day, REF_B_SE 8-day. [Bonvoy Report 2026-10-27]
- 2026-10-28: 3 tags: COUCH 12-day (22 h), REF_B_SE 9-day (22 h), HB_P Low 7 h. [Bonvoy Report 2026-10-28]
- 2026-10-29: 2 tags: COUCH 13-day (12 h, trend 10.74 %/day), REF_B_SE 10-day (9 h). [Bonvoy Report 2026-10-29]
- 2026-10-30: 3 tags: COUCH 14-day (23 h), REF_B_SE 11-day (22 h), new FREENESS Low 17 h (rank 3, mean 447.6, min 421). [Bonvoy Report 2026-10-30]
- 2026-10-31: 4 tags: COUCH 15-day (24 h, 13.5 sigma, +19.91 %/day), REF_B_SE 12-day (24 h, mean 64.54, max 86.2), FREENESS 2-day, new REF_A_SE High 3 h (rank 4, 72 of 84 days). [Bonvoy Report 2026-10-31]

## Linked work orders and documents carried by the items
- COUCH_DS_VIB item carries WO 26108274 "Rebuild couch roll seal strips", status 30; rcfas empty; doc null. [Bonvoy Report 2026-10-25]
- REF_B_SE item carries WO 26108911 "Change REF 2 refiner plates", status 30. Docs: Ridgeway plate report RR-PL-260930-B (2026-09-30) on 10-25, then Ridgeway field visit RR-FV-261026 (2026-10-26, "REF 2 plates wearing fast") from 10-26. See [[ref-refb]]. [Bonvoy Report 2026-10-26]
- REF_A_SE item carries WO 26108904 "Change REF 1 refiner plates", status 30 (the doc shown is also RR-FV-261026). See [[ref-refa]]. [Bonvoy Report 2026-10-31]
- HB_P item carries WO 26108778 "Headbox slice inspection and clean", status 40, and doc RCFA-SM-26-020 "Slime build-up: Headbox" (2026-07-11), though its rcfas list is empty. See [[headbox]]. [Bonvoy Report 2026-10-26]
- WO status codes 30 and 40 are shown as numbers only; their meaning is not in these reports.

## Watch list (above alarm limit, from the report "watch" block)
- Reel drum DS bearing (story F2): "Known bearing defect on the Reel drum DS bearing, found on the Aug 12 vibration route." Danger limit 0.4; values 0.411 (10-25), 0.416, 0.418, 0.424 (10-28), 0.359 (10-29, Alert level), 0.423 (10-30), 0.426 (10-31); flagged false because "its baseline has moved up with it". See [[reel-drum]]. [Bonvoy Report 2026-10-25] [Bonvoy Report 2026-10-29] [Bonvoy Report 2026-10-31]
- Couch roll COUCH_DS_VIB Alert limit 0.15: 0.162 (10-26), 0.172, 0.187, 0.174 (10-29), 0.219 (10-30), 0.236 (10-31); flagged true. [Bonvoy Report 2026-10-26] [Bonvoy Report 2026-10-31]

## Report wording worth reusing
- Couch cause text: "Overall vibration above its normal band: a developing bearing defect or looseness."; check: "Ask Keel for an off-route reading with a spectrum (BPFO / BPFI, 1x running speed); check lubrication and the bearing temperature." [Bonvoy Report 2026-10-25]
- REF 2 cause text: "REF 2's plates (on since Sep 30) are wearing fast: energy per ton climbing since Oct 7. Only one Ridgeway set on hand for two refiners." [Bonvoy Report 2026-10-25]
- Headline 2026-10-31: "Couch roll: Couch roll DS bearing vibration high for 24 h, 15 days running". [Bonvoy Report 2026-10-31]
- Grade field on items: 24# on 10-25/26/28, "31#, 34 Super" for REF_B_SE on 10-30, 34 Super on 10-31. [Bonvoy Report 2026-10-30]
