---
name: 2nd-press-drive
description: 2nd press drive (asset 00072371, Press section) - 3 RCFAs in 2026 (motor winding Feb, bearing Mar and Sep); RCFA-SM-26-007 and -028 open with overdue actions
type: equipment
aliases: ["asset 00072371", "2nd press drive motor", "PM1:PRESS2_DS_VIB"]
---
## RCFAs (tool: rcfa_status)
- 2026-02-15 motor failure (winding insulation), 4.3 h, 133 t; RCFA-SM-26-007 OPEN. [RCFA-SM-26-007]
- 2026-03-18 bearing failure, 3.9 h, 120 t; RCFA-SM-26-010 closed 2026-05-21. [RCFA-SM-26-010]
- 2026-09-20 bearing failure, 6.9 h, 213 t, Pi PM1:PRESS2_DS_VIB about 9 days before; RCFA-SM-26-028 OPEN. [RCFA-SM-26-028]
- Total about 15.1 h and 466 t (computed). Lead Mei Fairbanks on all.

## Actions
- RCFA-007: ADX test SM-0063 done 2026-03-08; spare motor rewound and stocked SM-0065 done 2026-03-27; MCC room cooling check SM-0064 due 2026-04-20 In progress, OVERDUE (Desmond Pike). [Action SM-0064]
- RCFA-010: two-weekly route SM-0091 done 2026-04-06; online sensor SM-0092 done 2026-04-30; grease review SM-0093 done 2026-05-21. [Action SM-0092]
- RCFA-028: two-weekly route SM-0225 done 2026-10-07; online sensor SM-0226 due 2026-11-02 In progress OVERDUE; grease review SM-0227 due 2026-11-23 Not started (Gloria Nakamura). [Action SM-0226] [Action SM-0227]
- The Sep bearing failure came after the online-sensor action SM-0092 was recorded complete (2026-04-30); RCFA-028 again lists "no online vibration on this asset" as contributing. [RCFA-SM-26-028]
- Modes: [[motor-winding-insulation-failure]], [[bearing-failed-between-vibration-routes]].

## BUS issues Feb - Mar 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2026-02-15 BUS issue: motor failure 4.3 h, WO 26102961, Desmond Pike; closed 2026-02-17. [BUS 2026-02-15 issue 707d92f265190994]
- 2026-03-18 BUS issue: bearing failure 3.9 h, "failed (not caught on the route)", WO 26103696, Gloria Nakamura; closed 2026-03-21. [BUS 2026-03-18 issue 82bdcc20cda82140]

## Keel vibration route (reports library; see [[vibration-routes]])
- PM1:PRESS2_DS_VIB route readings in/s: 11/12/2025 0.062; 12/10/2025 0.023; 01/14/2026 0.061; 02/11 0.065; 03/11 0.249 Alert; 04/08 0.071; 05/13 0.058; 06/10 0.063; 07/08 0.023; 08/12 0.061; 09/09 0.110 Good; 10/14 0.059 [DOC KV-VR-260311 p.1] [DOC KV-VR-261014 p.1]
- 03/11/2026: "2nd press drive: 0.25 in/s (Alert). Plan a bearing change." with "Bearing defect frequencies present"; the bearing failed 7 days later (03/18, RCFA-SM-26-010). CONFLICT: the RCFA says "failed (not caught on the route)" [DOC KV-VR-260311 p.1] [RCFA-SM-26-010]
- 09/09/2026: 0.110 in/s (Good, below the 0.15 Alert) 11 days before the 09/20 failure (RCFA-SM-26-028) [DOC KV-VR-260909 p.1]
- 04/08/2026 0.071 Good after the March failure, i.e. the bearing was replaced; the Sep failure came 5 months later

## Downtime log events
- 2026-02-15 22:45 motor failure 258 min, WO 26102961, RCFA-SM-26-007, grade 31#, crew A. [downtime DT-260215-0170] [Shift Report PM1-SHIFT-2026-02-15-D]
- 2026-03-18 10:30 bearing failure 232 min, WO 26103696, RCFA-SM-26-010: "bearing failed (not caught on the route)". [downtime DT-260318-0207]
- 2026-09-20 11:59 bearing failure 412 min, WO 26108393, RCFA-SM-26-028, grade 24#, crew B: "bearingfail: bearing vibration rising (bonvoy) for 18 days before." Lead-time spread kept: log 18 days, RCFA about 9 days (Pi), Bonvoy 17 flagged days, Keel route 09/09 only 0.110 Good. The log minutes (412) are the largest 2026 stop on this asset. [downtime DT-260920-0561] [Shift Report PM1-SHIFT-2026-09-20-D]
- Unlike March (press breaks within 4 h of the bearing stop), no 2nd press top felt break is logged between 2026-09-18 and 2026-09-26; the next is 2026-09-27 03:01 (62 min). [downtime DT-260926-0566] [downtime DT-260917-0558]
- 2026-03-18 14:22 a 94 min 2nd press top felt break followed the bearing stop within four hours, and five more press breaks of 56-91 min came by 2026-03-21; see [[p2-felt-top]]. [downtime DT-260318-0208]

## What crews saw around the 2026-03-18 bearing failure (shift reports Mar 2026; see [[shift-handover-signals-2026-03]])
- Before: no 2nd press drive item appears in any handover list 2026-03-01 to 2026-03-17, although the Keel route of 03-11 had read 0.249 in/s Alert "Plan a bearing change". Handovers that fortnight were on couch roll seal strip, pulper, fine screens, vacuum pump, HD cleaners, hood exhaust, fan pump, winder. [Shift Report PM1-SHIFT-2026-03-11-D] [Shift Report PM1-SHIFT-2026-03-17-D]
- The only press-section sign crews logged before the stop was 2nd press top felt breaks: 66 min (03-01 N), 83 (03-04 N, first break after the outage restart), 71 (03-11 N), 64 (03-14 N). [Shift Report PM1-SHIFT-2026-03-01-N] [Shift Report PM1-SHIFT-2026-03-11-N] [Shift Report PM1-SHIFT-2026-03-14-N]
- The day: 03-18 Day, crew C (Rafael Okonkwo): "Lost 3.9 h (120 t) to bearing failure on the 2nd press drive at 06:30. WO 26103696"; stop line "Unplanned 232 min · 2nd press drive · Bearing failure". 225 t, sheet on 54.7%. [Shift Report PM1-SHIFT-2026-03-18-D]
- CONFLICT on start time: shift report 06:30; downtime log 10:30 (DT-260318-0207). The same 4 h offset holds for the other March stops (hood supply fan, blown felt, rectifier fault), so the log timestamps appear to be 4 h later than the shift report clock. Both kept. [Shift Report PM1-SHIFT-2026-03-18-D] [downtime DT-260318-0207]
- Same shift: a 94 min 2nd press top felt break at 10:22 (log 14:22). Night shift 03-18 (crew B, Lucille Brandt) had three more press breaks, 59, 91 and 56 min. [Shift Report PM1-SHIFT-2026-03-18-D] [Shift Report PM1-SHIFT-2026-03-18-N]
- Handover after the stop (03-20 Day): "2nd press drive: bearing failure: 3.9 h down. 2nd press drive bearing failed (not caught on the route). → watching after restart" (also 03-20 N). [Shift Report PM1-SHIFT-2026-03-20-D] [Shift Report PM1-SHIFT-2026-03-20-N]
- Press breaks 03-18 to 03-22 in the shift reports: 10 breaks of 56-94 min, 804 min (computed), against the six cited in [[p2-felt-top]]; the rest fall after the stop (03-19 N 90, 03-20 N 89 and 66, 03-21 D 94, 03-21 N 73, 03-22 N 92). [Shift Report PM1-SHIFT-2026-03-19-N] [Shift Report PM1-SHIFT-2026-03-22-N]

## Shift reports Feb 2026 (motor failure 2026-02-15, RCFA-SM-26-007)
- No early sign on this drive in the handovers or notes before the failure: the 02-14 and earlier handovers list flat box cover, pulper, machine chest, dryer can 13 and 2nd press bottom felt guide, not the drive. [Shift Report PM1-SHIFT-2026-02-14-D] [Shift Report PM1-SHIFT-2026-02-14-N]
- 02-15 Day: "Down 4.3 h at 17:45, 2nd press drive: motor failure. WO 26102961"; stop line "17:45 Unplanned 258 min"; Day shift shows 15 min unplanned and Night 243 min (15+243 = 258). Grade change to 31# earlier that shift. [Shift Report PM1-SHIFT-2026-02-15-D] [Shift Report PM1-SHIFT-2026-02-15-N]
- CONFLICT on start time: shift reports say 17:45; the downtime row above says 22:45 (+5 h). 17:45 + 258 min = 22:03, which matches the 22:03 2nd press top felt break (92 min) logged right at restart. [Shift Report PM1-SHIFT-2026-02-15-N] [downtime DT-260215-0170]
- Handover after restart: 02-16 Day/Night "motor failure: 4.3 h down -> watching after restart"; 02-17 Day/Night "-> closed". [Shift Report PM1-SHIFT-2026-02-16-D] [Shift Report PM1-SHIFT-2026-02-17-D]
- Night 02-15 192 t, sheet on 53.5%. [Shift Report PM1-SHIFT-2026-02-15-N]

## Work order 2026-09-20
- WO 26108393 "Bearing failure: 2nd press drive" (asset 00072371): type 3 Emergency prio 1, requested and completed 2026-09-20, 20.6 h est / 22.7 h act (labour hours), MECH Beatrix Hale; "bearingfail: bearing vibration rising (bonvoy) for 18 days before." Ten days before the 2026-09-30 outage that changed the 2nd press felts and bottom roll ([[out-2026-09-30]]). [WO 26108393]

## BUS issue (list in [[bus-issue-sheet]])
- 2026-09-20 bearing failure 6.9 h, WO 26108393, "bearing vibration rising (bonvoy) for 18 days before" (RCFA says about 9 days of Pi trend; Bonvoy ramp 17 flagged days); owner Gloria Nakamura; "Watching after restart" 09-21, Closed 09-22. [BUS 2026-09-20 .. BUS 2026-09-22 | issue 72d7c7a1277db71a]

## Asset and Pi tags (from equipment/Pi tag listing)
- 2nd press drive is asset 00072371 (kind drive, section sec-press). Pi tags: PM1:PRESS2_LOAD 2nd press nip load (pli) and PM1:PRESS2_DS_VIB drive bearing vibration (in/s). [equipment 00072371] [Pi tag PM1:PRESS2_LOAD] [Pi tag PM1:PRESS2_DS_VIB]
- See [[pi-tag-map]].

## Bonvoy (tags PM1:PRESS2_DS_VIB 40 tag-days, PM1:PRESS2_LOAD 2; see [[bonvoy]])
- Ramp 1: 2026-02-24 -> 2026-03-18 (23 d), daily max 0.080 -> 0.401 in/s; ends on the RCFA-SM-26-010 date (2026-03-18). [Bonvoy PM1:PRESS2_DS_VIB 2026-02-24] [Bonvoy PM1:PRESS2_DS_VIB 2026-03-18]
- Ramp 2: 2026-09-04 -> 2026-09-20 (17 d), daily max 0.078 -> 0.408; ends on the RCFA-SM-26-028 date (2026-09-20). Bonvoy shows 17 flagged days vs the RCFA "about 9 days". [Bonvoy PM1:PRESS2_DS_VIB 2026-09-04] [Bonvoy PM1:PRESS2_DS_VIB 2026-09-20]
- Nip load PRESS2_LOAD High 2026-01-09 and 2026-04-10 (3 h, ~699 pli, max 715). [Bonvoy PM1:PRESS2_LOAD 2026-01-09] [Bonvoy PM1:PRESS2_LOAD 2026-04-10]
- Pattern: [[bearing-failed-between-vibration-routes]].

## Work orders Feb-Jun 2026 (work-orders-2; see [[emergency-work-orders-feb-jun-2026]])
- WO 26102961 "Motor failure: 2nd press drive", type 3 Emergency prio 1, requested and completed 2026-02-15, E&I Omar Szabo, est 12.9 h act 14.2 h, note "2nd press drive: motor failure." RCFA-SM-26-007. [WO 26102961]
- WO 26103696 "Bearing failure: 2nd press drive", Emergency, 2026-03-18, MECH Beatrix Hale, est 11.6 h act 12.8 h, note "2nd press drive bearing failed (not caught on the route)." RCFA-SM-26-010. [WO 26103696]
- The fortnightly "Press hydraulic unit inspection" WOs (8 between 02-28 and 06-04) are booked on the 1st press drive asset 00072308, not on this drive: [[1st-press-drive]], [[work-orders-feb-jun-2026]]. [WO 26103052]
