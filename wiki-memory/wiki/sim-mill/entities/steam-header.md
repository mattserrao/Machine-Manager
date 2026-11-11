---
name: steam-header
description: Steam header (asset 00072154, listed under Stock prep on the BUS sheet) - pressure dips at grade changes, 18 BUS issues Nov 2025 - Oct 2026, each closed "Ramp rate changed"
type: equipment
aliases: ["asset 00072154", "steam header pressure dips", "Review boiler master response"]
---
- 9 BUS issues "Steam header pressure dips at grade changes", owner Eamon Takahashi, action "Review boiler master response", closed "Ramp rate changed". [BUS 2025-11-01 issue 4bf86750de3ee4dd]
- Start dates and WOs: 2025-11-01 (WO 26100336), 2025-11-04 (WO 26100399), 2025-11-23 (WO 26100938), 2025-11-29 (WO 26101085), 2025-12-04 (WO 26101190), 2025-12-13 (WO 26101351), 2025-12-20 (no WO), 2025-12-30 (WO 26101869), 2026-04-18 (WOs 26104424, 26104452). [BUS 2025-12-20 issue ffaeee01c9707a68] [BUS 2026-04-18 issue a941e7079f7298c1]
- Eight of the nine fall between 2025-11-01 and 2026-01-05; then none Jan 6 - Apr 17 in this batch. [BUS 2026-01-05 issue 3f869c6307b25cbe]
- Closing note is the same every time ("Ramp rate changed"), so the fix is a ramp-rate tweak at each grade change; no RCFA. Steam setpoints by grade: [[steam-pressure-by-grade]]. See [[bus-follow-up-actions]] (SM-0149, 0166, 0180, 0217), [[bus-sheet-issues-2025-11-to-2026-05]].

## May-Oct 2026 issues (9 more; owner Eamon Takahashi; list in [[bus-issue-sheet]])
- 9 issues 2026-05-26 to 2026-10-14, each "Review boiler master response" then "Ramp rate changed" after 2 to 10 days; the ramp rate was changed nine more times, no lasting fix. [BUS 2026-05-26 .. BUS 2026-05-27 | issue f269b96de8bed2b9] [BUS 2026-10-12 .. BUS 2026-10-14 | issue 635fba3a6a7a416b]
- Start dates and WOs: 05-26 WO 26105467; 06-02 WO 26105642; 06-10 WO 26105936; 07-03 WO 26106482 (10 days); 07-21 WO 26106979; 09-11 WO 26108204; 09-24 (no WO); 09-29 WO 26108589; 10-12 WO 26108946. [BUS 2026-07-03 .. BUS 2026-07-12 | issue f7c907a420939da5] [BUS 2026-09-24 .. BUS 2026-09-27 | issue d9ab2bfcbfac23e4] [BUS 2026-09-29 .. BUS 2026-10-01 | issue 068077222f270e74]
- Total on the sheet Nov 2025 - Oct 2026: 18 issues, no RCFA. Owner differs by source: Eamon Takahashi on the BUS sheet, INST Fenna Gallagher on the WOs. [BUS 2026-09-29 .. BUS 2026-10-01 | issue 068077222f270e74] [WO 26108589]

## Work orders Jun-Sep 2026 (WO extract work-orders-3; asset 00072154 Steam header, sec-stockprep)
- Corrective "Steam header pressure dips at grade changes" (type 1, prio 3, INST Fenna Gallagher): 4 WOs, all Closed: 26105936 (requested 06-10, done 06-13, 4 h est) [WO 26105936]; 26106482 (07-03, done 07-12, 3 h) [WO 26106482]; 26106979 (07-21, done 07-22, 2 h) [WO 26106979]; 26108204 (09-11, done 09-13, 4 h) [WO 26108204]. These match the BUS issue start dates 06-10, 07-03, 07-21, 09-11 listed above.
- Preventive "Steam trap survey" (MECH Beatrix Hale, 4 h est / 4.4 h act): 4 WOs completed 2026-06-25 [WO 26106111], 07-27 [WO 26106888], 08-24 [WO 26107532], 09-24 [WO 26108302] (about monthly).
- Dips continue after the ramp-rate change each time; the steam trap survey is on a monthly cadence but is not linked to the dips in any WO text. See [[steam-pressure-by-grade]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Corrective "Steam header pressure dips at grade changes" (type 1, prio 3, INST Fenna Gallagher): 7 WOs, all Closed: 26100336 (requested 2025-11-01, done 11-02, 3.3 h), 26100399 (11-04, done 11-10, 6.6 h), 26100938 (11-23, done 11-26, 4.4 h), 26101085 (11-29, done 12-02, 3.3 h), 26101190 (12-04, done 12-10, 2.2 h), 26101351 (12-13, done 12-15, 2.2 h), 26101869 (12-30, done 2026-01-05, 2.2 h). [WO 26100336] [WO 26100399] [WO 26100938] [WO 26101085] [WO 26101190] [WO 26101351] [WO 26101869]
- 7 requests in 59 days (2025-11-01 to 12-30); none after 2026-01-05 in this WO batch. [WO 26100336] [WO 26101869]
- The WOs file the header under section sec-stockprep. [WO 26100336]
- Preventive "Steam trap survey" (type 2, MECH Beatrix Hale, 4.4 h): 26100077 (done 2025-10-28), 26100868 (11-27), 26101610 (12-27), 26102268 (2026-01-27), about monthly. [WO 26100077] [WO 26100868] [WO 26101610] [WO 26102268]
- See [[repeat-corrective-work-orders]], [[routine-pm-work-orders]].

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- 4 "Steam header pressure dips at grade changes" WOs, INST Fenna Gallagher, type 1 prio 3, all Closed (requested -> done, actual h): 26104424 (04-18 -> 04-20, 3.3), 26104452 (04-19 -> 04-28, 6.6), 26105467 (05-26 -> 05-27, 3.3), 26105642 (06-02 -> 06-05, 2.2); 15.4 h in total (computed). None between 02-09 and 04-17 in this extract. [WO 26104424] [WO 26104452] [WO 26105467] [WO 26105642]
- Monthly "Steam trap survey" (MECH Beatrix Hale, 4 h est): 26103024 (done 02-27), 26103759 (03-27), 26104459 (04-28), 26105299 (05-26). [WO 26103024] [WO 26103759] [WO 26104459] [WO 26105299]
- The 05-19 early change of the 2nd press top felt cites "4th section steam at its limit" (WO 26105306); see [[steam-pressure-by-grade]], [[p2-felt-top]]. [WO 26105306]

## Oct 2026 late issue (from [[bus-issues-2026-10-late]])
- Issue 60b08b4b168cf47f (WO 26109289, Eamon Takahashi): 10-25 to 10-29, closed "Ramp rate changed". [BUS 2026-10-29]

## Gaps (checked 2026-11-10)
- Not on this page: the Sep 27 - Oct 31 work-order section (only WO 26108946 and 26109289 appear by id) and any Nov 11 scope; see [[work-order-routes-and-corrective]]. The 10-25 issue above is not in the "9 more" list (05-26 to 10-14), so the sheet total may be 19, not 18.
