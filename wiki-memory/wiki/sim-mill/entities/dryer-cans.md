---
name: dryer-cans
description: Dryer can sheet breaks by section (can 3 in 1st, can 6 in 2nd, can 11 in 3rd, can 16 in 4th dryer section) Nov 2025 - Sep 2026; read for dryer break counts and which can breaks most
type: equipment
aliases: ["Dryer can 3", "Dryer can 6", "Dryer can 11", "Dryer can 16", "dryer section breaks", "sheet break (dryer)"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108799 "Inspect dryer can heads and syphons, all sections" (asset 00072504 dryer can 10, MECH, 8 h, Reserved) and WO 26108750 "Change all dryer doctor blades" (asset 00072385 dryer can 1, OPS, 4 h, Reserved). [WO 26108799] [WO 26108750]
- Dryer can 13 "condensate flooding (cold can)" corrective WOs 26108617 (10-03) and 26108757 (10-13). Weekly doctor blade check (can 1) and dry end rounds (can 10): see [[work-order-routes-and-corrective]]. [WO 26108617] [WO 26108757]

## Sheet breaks at the dryers (downtime log 2025-11-01 to 2026-09-01)
- 174 dryer-section breaks, about 6,914 min, average about 40 min. Tool: downtime_summary group=equipment kind=break. [downtime DT-251104-0004 to DT-260830-0518]
- 3rd dryer section, dryer can 11: 46 breaks, 1,841 min (most by count). [downtime DT-251118-0019]
- 1st dryer section, dryer can 3: 45 breaks, 1,858 min (most by minutes). [downtime DT-251109-0011]
- 4th dryer section, dryer can 16: 42 breaks, 1,603 min. [downtime DT-251109-0010]
- 2nd dryer section, dryer can 6: 41 breaks, 1,612 min. [downtime DT-251104-0004]
- The four counts are within 10% of each other: no single can stands out, unlike the 2nd press top felt (175) in [[p2-felt-top]]. [downtime DT-251104-0004 to DT-260830-0518]
- Dryer breaks logged only at cans 3, 6, 11 and 16 (one per section) in this log. [downtime DT-251104-0004]
- Related dryer-section stops are not breaks: syphon / rotary joint events in [[syphon-failure]]; drive events in [[dryer-drive-lineup]]; hood fans in [[hood-fan-failures]].
- Overall break picture: [[breaks-by-location]].
- BUS sheet: dryer can 6 "4 or 5 sheet breaks in 24 h, mostly at the dryer" review issues (Tobias Renner, closed "Watching") on 2025-11-08, 2026-01-04, 01-26, 02-08 (4 breaks) and 02-26 (5 breaks); other dryer-can BUS items are [[dryer-can-4]] (doctor blade) and [[dryer-can-13]] (cold can). [BUS 2025-11-08 issue 6ac0d02df6d85ad4] [BUS 2026-02-26 issue 3bae93a2b2b1ef66]

## November 2025 as the crews logged it (shift reports; one month, not the full log)
- 16 dryer breaks, 659 min in Nov 2025: can 6 five (213 min: 11-04N 27, 11-07N 44, 11-14D 43, 11-19N 48, 11-22D 51), can 16 five (181 min), can 11 four (182 min: 47, 34, 48, 53), can 3 two (83 min, both 11-09). Longest 53 min (can 11, 11-23N). [Shift Report PM1-SHIFT-2025-11-04-N] [Shift Report PM1-SHIFT-2025-11-23-N]
- 11-09 handover "Dryer can 6: 4 sheet breaks in 24 h, mostly at the dryer → watching" (Day and Night). The logged stops in the prior 24 h in this batch are cans 16, 3, 3 (11-09) and can 6 once (11-07 Night, 44 min), so the "4 in 24 h" count does not match one can; BUS follow-ups of this wording are in [[bus-follow-up-actions]]. [Shift Report PM1-SHIFT-2025-11-09-D] [Shift Report PM1-SHIFT-2025-11-09-N]
- 11-07 Night: two dryer breaks within 63 min (can 11 at 19:30, can 6 at 20:33, 91 min together). [Shift Report PM1-SHIFT-2025-11-07-N]
- Doctor blade: "Dryer can 4: doctor blade worn → change blade on the next break" 11-06 to 11-08 (changed 11-08 Day/Night), then reappeared 11-16 to 11-18 as the same item, so the blade was worn again 8 days later. [Shift Report PM1-SHIFT-2025-11-06-D] [Shift Report PM1-SHIFT-2025-11-08-D] [Shift Report PM1-SHIFT-2025-11-16-D]
- Flooded can: "Dryer can 13: condensate flooding (cold can)" 11-19 to 11-23, see [[syphon-failure]]. [Shift Report PM1-SHIFT-2025-11-19-D]
- Cross-check each against tool downtime_events kind=break location="Dryer can N".

## January 2026 as the crews logged it (shift reports 2026-01-01 to 01-31)
- Dryer breaks in the Stops lists: can 3 11 breaks (419 min), can 16 6 (222), can 6 5 (178), can 11 4 (164); 26 breaks, 983 min, versus 19 at the 2nd press top felt (1,408 min; [[p2-felt-top]]). [Shift Report PM1-SHIFT-2026-01-03-D] [Shift Report PM1-SHIFT-2026-01-18-N]
- Can 3 dominated Jan (11 of 26); in the log Nov-Aug it was close to the others (45, 1,858 min). [Shift Report PM1-SHIFT-2026-01-03-N]
- Dryer can 6 watch: handover "4 sheet breaks in 24 h, mostly at the dryer -> watching" 01-05 Day/Night; again 01-26 ("shift leads to review break tapes") and 01-27 ("watching"). The report counts do not show 4 can-6 breaks in any 24 h (can 6: 01-03, 01-10, 01-18, 01-25, 01-26). CONFLICT/unclear, tool: downtime_events equipment="Dryer can 6". [Shift Report PM1-SHIFT-2026-01-05-D] [Shift Report PM1-SHIFT-2026-01-26-D] [Shift Report PM1-SHIFT-2026-01-27-D]
- Other dryer items: can 4 doctor blade worn 01-10 to 01-11, changed 01-12; can 13 condensate flooding 01-17/18 (see [[syphon-failure]]). [Shift Report PM1-SHIFT-2026-01-10-D] [Shift Report PM1-SHIFT-2026-01-12-D]
- Three dryer breaks in one night shift: 01-03 Night (cans 3, 3, 6), 01-18 Night (cans 16, 6, 11, plus a press break) and 01-25 Night (cans 3, 11, 6). [Shift Report PM1-SHIFT-2026-01-03-N] [Shift Report PM1-SHIFT-2026-01-18-N] [Shift Report PM1-SHIFT-2026-01-25-N]

## February 2026 as the crews logged it (shift reports)
- 17 dryer breaks, 663 min in the Feb reports: can 3 six (256 min: 02-07 08:00 48 and 16:36 45, 02-09 44, 02-10 42, 02-18 44, 02-25 33), can 11 four (143 min: 47, 36, 33, 27), can 16 four (131 min: 29, 28, 39, 35), can 6 three (133 min: 54, 49, 30). Longest 54 min (can 6, 02-21 04:57). Counted from the Stops lists; cross-check tool downtime_events kind=break location="Dryer can N". [Shift Report PM1-SHIFT-2026-02-07-D] [Shift Report PM1-SHIFT-2026-02-21-N] [Shift Report PM1-SHIFT-2026-02-25-D] [Shift Report PM1-SHIFT-2026-02-26-N]
- Worst day 02-07 Day: three dryer breaks (cans 3, 11, 3; 140 min) plus the shower stop, 251 t. [Shift Report PM1-SHIFT-2026-02-07-D]
- Doctor blade: "Dryer can 4: doctor blade worn -> change blade on the next break" 02-01 Day/Night; "changed" 02-02 to 02-03 (02-02 still also lists "change blade on the next break"); back 02-18 Day to 02-19 Night; "changed" 02-20 Day/Night; back 02-21 Day/Night; "changed" 02-22 Day/Night. Worn again 15 days after the first change (computed). [Shift Report PM1-SHIFT-2026-02-01-D] [Shift Report PM1-SHIFT-2026-02-02-D] [Shift Report PM1-SHIFT-2026-02-18-D] [Shift Report PM1-SHIFT-2026-02-20-D]
- Cold can 13 flooding 02-14/15 and 02-26/27: see [[syphon-failure]].

## March 2026 as the crews logged it (shift reports 2026-03-01 to 03-31)
- 8 dryer-section breaks, 312 min (computed): can 11 40 min (03-01 N) and 45 min (03-29 D); can 16 33 and 32 min (03-17 D); can 6 34 min (03-17 D) and 33 min (03-22 D, 10 h before the dryer drive rectifier fault); can 3 41 min (03-27 D) and 54 min (03-31 D). [Shift Report PM1-SHIFT-2026-03-01-N] [Shift Report PM1-SHIFT-2026-03-17-D] [Shift Report PM1-SHIFT-2026-03-22-D] [Shift Report PM1-SHIFT-2026-03-31-D]
- 03-17 Day had 3 dryer breaks (99 min, sheet on 86.2%) in one shift; no "N sheet breaks in 24 h, mostly at the dryer" handover item appears in March. Other dryer handover items: "Dryer can 4: doctor blade worn → change blade on the next break" 03-05 to 03-07, 03-18, 03-19, 03-21, 03-22, 03-29 and 03-30. [Shift Report PM1-SHIFT-2026-03-17-D] [Shift Report PM1-SHIFT-2026-03-05-D]
- See [[dryer-drive-lineup]] (2026-03-22 stop) and [[syphon-failure]] (can 13).

## Update: 2026-09-02 to 2026-10-31 (counted from the rows)
- 30 dryer breaks, 1,227 min: can 6 (2nd section) 9 / 298 min, can 11 (3rd) 8 / 354, can 16 (4th) 7 / 319, can 3 (1st) 6 / 256; average about 41 min. [downtime DT-260905-0530 to DT-261030-0629]
- Longest: 54 min (can 3, DT-261013-0587), 53 (can 11, DT-260910-0539 and DT-260927-0567) and 52 (can 6, DT-261026-0619). No single can stands out (6 to 9 breaks each). [downtime DT-261013-0587] [downtime DT-260910-0539] [downtime DT-260927-0567] [downtime DT-261026-0619]
- Dec 2025 shift reports: 12 dryer breaks, 478 min: can 11 x8 (303 min), can 16 x2 (85), can 3 x1 (47), can 6 x1 (43); can 11 breaks ranged 27 to 52 min (Dec 1 D 44, Dec 5 N 27, Dec 8 N 52, Dec 23 D 44). [Shift Report PM1-SHIFT-2025-12-08-N] [Shift Report PM1-SHIFT-2025-12-23-D]
- Non-break dryer stops in the window: 3rd section rotary joint leak 2026-10-02 ([[3rd-section-rotary-joint]]), 4th section rotary joint / syphon planned repair 2026-10-16 ([[4th-section-rotary-joint-ds]]), dryer driveshaft 2026-10-15 ([[dryer-drive-lineup]]). [downtime DT-261002-0576] [downtime DT-261016-0592] [downtime DT-261014-0589]

## BUS issues Apr-Oct 2026 (list in [[bus-issue-sheet]])
- Dryer can 6 (asset 00072476, 2nd dryer section) "4 or 5 sheet breaks in 24 h, mostly at the dryer", Tobias Renner, "Shift leads to review break tapes" then "Watching": 6 issues, 04-24 (4), 04-27 (5), 05-13 (4, two cycles), 06-11 (4), 07-17 (4), 09-17 (4). [BUS 2026-04-24 .. BUS 2026-04-25 | issue f80319a8373c5318] [BUS 2026-04-27 .. BUS 2026-04-28 | issue 2167ec4192e22413]
- Dryer can 4 doctor blade worn (asset 00072406, 1st dryer section), Gloria Nakamura, "Change blade on the next break" then "Changed": 10 issues, 05-17 (10 days), 05-28, 06-13, 06-16, 07-28, 08-08, 08-19, 08-31 (10 days), 09-23 (10 days), 10-04 (10 days). [BUS 2026-05-17 .. BUS 2026-05-26 | issue e7e29d133eba159a] [BUS 2026-10-04 .. BUS 2026-10-13 | issue 863ab8282e63f358]
- Dryer can 13 flooding: [[dryer-can-13]].

## BUS issue Oct 2026
- Dryer can 6 (asset 00072476): issue d949965d5eed11b8, "5 sheet breaks in 24 h, mostly at the dryer", 10-18 to 10-19, Tobias Renner, "Shift leads to review break tapes" then "Watching" Closed; no WO.

## Work orders Jun-Sep 2026 (WO extract work-orders-3)
- Outage "Inspect dryer can heads and syphons, all sections" (logged on asset 00072504 Dryer can 10, MECH Beatrix Hale, type 4): 2026-07-08 4 h est [WO 26105754]; 2026-08-19 8 h est [WO 26106783]; 2026-09-30 8 h est [WO 26107847]. Syphon failures in the same months: planned catch 06-26 on the 4th section ([[4th-section-rotary-joint-ds]], WO 26106279) and the 3rd section DS joint leak 06-23 ([[3rd-section-rotary-joint]], WO 26106237); can 13 cold-can WOs in [[dryer-can-13]].
- Weekly "Operator rounds: dry end" (OPS, 1 h est, asset Dryer can 10): 16 WOs completed 2026-06-15 to 2026-09-28; weekly "Doctor blade check: dryers" (OPS, 2 h est, asset Dryer can 1): 16 WOs 2026-06-15 to 2026-09-30; outage "Change all dryer doctor blades" 2026-07-08 [WO 26105705], 2026-08-19 [WO 26106734], 2026-09-30 [WO 26107798] (6 h est each). See [[work-orders-jun-sep-2026]]. See [[bus-issues-2026-10-late]]. [BUS 2026-10-19]

## Work orders Feb-Jun 2026 (work-orders-2)
- Weekly PM "Doctor blade check: dryers" (Dryer can 1, asset 00072385, OPS, 2 h est): 16 WOs, 26102975 (done 02-24) to 26105607 (06-08); "Operator rounds: dry end" (Dryer can 10, asset 00072504, OPS, 1 h est): 17 WOs, 26102849 to 26105621. [WO 26102975] [WO 26105607] [WO 26102849] [WO 26105621]
- Outage "Change all dryer doctor blades" (OPS): WO 26103493 ([[out-2026-04-15]], 8/8.8 h) and WO 26104557 ([[out-2026-05-27]], 6/6.6 h); "Inspect dryer can heads and syphons, all sections" (MECH, booked on can 10): WO 26103542 and WO 26104599. [WO 26103493] [WO 26104557] [WO 26103542] [WO 26104599]
- Cold-can repeats on can 13: [[dryer-can-13]]; flooding/syphon stops: [[syphon-failure]].
