---
name: dryer-drive-lineup
description: Dryer drive lineup (asset 00072742, 2nd dryer section) - 5 RCFAs Dec 2025-Oct 2026 (3 bearing, 1 rectifier, 1 driveshaft u-joint); RCFA-SM-26-026 and -029 open
type: equipment
aliases: ["asset 00072742", "dryer drive", "dryer driveshaft", "PM1:DRYER_DRIVE_VIB", "MCC-2 DC bus"]
---
## Current picture (as of 2026-11-10; tool: rcfa_status)
- 5 RCFAs Dec 2025 - Oct 2026 (3 bearing/rectifier closed, 2 open), about 27.6 h and 856 t (computed). [RCFA-SM-25-002] [RCFA-SM-26-029]
- Open: RCFA-SM-26-026 (bearing 2026-08-26, 6.8 h, 211 t; grease review SM-0207 overdue, due 2026-10-29). [RCFA-SM-26-026] [Action SM-0207]
- Open: RCFA-SM-26-029 (driveshaft u-joint 2026-10-14, 4.8 h, 148 t, "Joint grease interval missed"; SM-0239 weekly lube route overdue, due 2026-11-05). [RCFA-SM-26-029] [Action SM-0239]
- Emergency WO 26108981 "Driveshaft snaps", 14.3 h est, 15.7 h act, done 10-15. [WO 26108981]
- Scoped for 11/11: WO 26108813 MCC lineup clean and torque check (8 h, Reserved). [WO 26108813]
- MCC thermography WO 26109065 completed 10-26. [WO 26109065]
- Bearing RCFAs had Pi PM1:DRYER_DRIVE_VIB lead times of about 18, 20 and 10 days. [RCFA-SM-25-002] [RCFA-SM-26-018] [RCFA-SM-26-026]
- See [[bearing-failed-between-vibration-routes]], [[rectifier-fault-mcc-dc-bus]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO 26108981 "Driveshaft snaps: Dryer drive lineup", emergency (type 3, prio 1), requested 2026-10-14, completed 10-15, est 14.3 h act 15.7 h: "Dryer driveshaft snaps. Millwrights called in." [WO 26108981]
- Scoped for [[out-2026-11-11]]: WO 26108813 "MCC lineup clean and torque check" (E&I Omar Szabo, 8 h, Reserved). Done earlier: MCC thermography WO 26109065 (completed 10-26); monthly vibration route (Keel) WO 26108820 (10-14, 6.6 h). [WO 26108813] [WO 26109065] [WO 26108820]
- Weekly "Lube route: dryers and reel" (4 h): 26108540, 26108687, 26108918, 26109093 done; 26109268 Approved (planned 11-01). [WO 26109268]

## RCFAs on this asset (tool: rcfa_status)
- 2025-12-24 bearing failure, 7.3 h, 228 t, Pi PM1:DRYER_DRIVE_VIB trend about 18 days before; RCFA-SM-25-002 closed 2026-02-23. [RCFA-SM-25-002]
- 2026-03-22 rectifier fault (MCC DC bus down), 3.7 h, 116 t; RCFA-SM-26-011 closed 2026-04-04. [RCFA-SM-26-011]
- 2026-06-24 bearing failure, 5 h, 153 t, about 20 days of Pi trend; RCFA-SM-26-018 closed 2026-08-18. [RCFA-SM-26-018]
- 2026-08-26 bearing failure, 6.8 h, 211 t, about 10 days of Pi trend; RCFA-SM-26-026 OPEN. [RCFA-SM-26-026]
- 2026-10-14 driveshaft snaps: "Dryer driveshaft universal joint failed", contributing "Joint grease interval missed", 4.8 h, 148 t; RCFA-SM-26-029 OPEN. [RCFA-SM-26-029]
- Five RCFAs total about 27.6 h and 856 t (computed). Lead on all: Mei Fairbanks.

## Open actions (as of 2026-11-10)
- SM-0207 grease type and interval review (RCFA-SM-26-026), Gloria Nakamura, due 2026-10-29, In progress, OVERDUE. [Action SM-0207]
- SM-0239 add driveshaft u-joints to the weekly lube route (RCFA-SM-26-029), Gloria Nakamura, due 2026-11-05, In progress, OVERDUE. [Action SM-0239]
- Done: two-weekly route SM-0025/0163/0205 (2026-01-13, 2026-07-06, 2026-09-13); online sensor SM-0026/0164 done, SM-0206 done 2026-10-11 (3 days late). [Action SM-0205] [Action SM-0206]
- The Oct 14 driveshaft failure came 3 days after the online sensor on this asset was completed (2026-10-11); a different mechanism (u-joint grease), not caught by the vibration sensor per the RCFA wording. [RCFA-SM-26-029]

## What crews saw before the 2025-12-24 bearing failure (shift reports; tool: shift_reports)
- First operator note: night shift Dec 9 "Operators mentioned the Dryer drive lineup: bearing sounds rough on rounds", 14 days before the stop. [Shift Report PM1-SHIFT-2025-12-09-N]
- The note was repeated on 12 more shifts up to the stop: Dec 12 D ("Not sure yet; flagging it"), Dec 13 D and N, Dec 14 N, Dec 15 D, Dec 17 D, Dec 18 N (tag DRYER_DRIVE_VIB named), Dec 19 D and N, Dec 20 D and N, Dec 22 D (DRYER_DRIVE_VIB named). Wording stayed "bearing sounds rough on rounds" with a question mark; no WO or planned change was raised in the reports. [Shift Report PM1-SHIFT-2025-12-12-D] [Shift Report PM1-SHIFT-2025-12-13-D] [Shift Report PM1-SHIFT-2025-12-18-N] [Shift Report PM1-SHIFT-2025-12-19-D] [Shift Report PM1-SHIFT-2025-12-20-N] [Shift Report PM1-SHIFT-2025-12-22-D]
- The Dec 10 outage (20 h, [[out-2025-12-10]]) fell inside this window and the reports do not mention a bearing change at it; the Keel route that day read 0.055 in/s Good (see below). [Shift Report PM1-SHIFT-2025-12-10-D]
- Stop: night shift Dec 23, 03:55 on Dec 24 (shift-report clock; the downtime log shows 08:55 for the same event, a 5 h offset also seen on the other Dec events), "bearing failure on the Dryer drive lineup, 7.3 h down. bearingfail: bearing vibration rising (bonvoy) for 35 days before", WO 26101694, 441 min unplanned, grade 34 Super. [Shift Report PM1-SHIFT-2025-12-23-N]
- Aftermath: Dec 24 D 196 t, sheet on 56.1%, 316 min unplanned counted in that shift. Handover status: "repaired; running" (Dec 24), "watching after restart" (Dec 25), "closed" (Dec 26). [Shift Report PM1-SHIFT-2025-12-24-D] [Shift Report PM1-SHIFT-2025-12-25-D] [Shift Report PM1-SHIFT-2025-12-26-D]
- Lesson for the mode: crews flagged rough bearing sound for about 2 weeks and the Bonvoy ramp started 2025-11-25; see [[bearing-failed-between-vibration-routes]] and [[precursor-lead-times]].

## BUS issues Dec 2025 - Mar 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2025-12-24 BUS issue: dryer drive lineup (2nd dryer section, asset 00072742) bearing failure 7.3 h, WO 26101694, Gloria Nakamura, "bearing vibration rising (bonvoy) for 35 days before"; closed 2025-12-26. [BUS 2025-12-24 issue dce845fac4917112]
- 2026-02-03 BUS issue: "Bearing vibration rising (Bonvoy)", Mei Fairbanks, WO 26102695, "Grease and take daily readings"; closed 02-04 "Done; running normal" (no stop). [BUS 2026-02-03 issue 198ee46aa83b9eef]
- 2026-03-22 BUS issue: rectifier fault, MCC-2 DC bus down, 3.7 h, WO 26103836; closed 03-25. See [[rectifier-fault-mcc-dc-bus]]. [BUS 2026-03-22 issue c98cfe8be4bebedc]

## Keel vibration route (reports library; see [[vibration-routes]])
- PM1:DRYER_DRIVE_VIB route readings in/s: 11/12/2025 0.065; 12/10/2025 0.055 (highest fixed point that day); 01/14/2026 0.064; 02/11 0.062; 03/11 0.060; 04/08 0.056; 05/13 0.060; 06/10 0.227 Alert; 07/08 0.024; 08/12 0.104 Good; 09/09 0.066; 10/14 0.067 [DOC KV-VR-251112 p.1] [DOC KV-VR-251210 p.1] [DOC KV-VR-260610 p.1] [DOC KV-VR-260812 p.1] [DOC KV-VR-261014 p.1]
- 06/10/2026: 0.227 Alert in the readings but the findings say "No new findings. All points within limits." (CONFLICT inside the report); the bearing failed 14 days later (RCFA-SM-26-018, 06/24) [DOC KV-VR-260610 p.1] [RCFA-SM-26-018]
- 08/12/2026 reading 0.104 (Good, below Alert) 14 days before the 08/26 failure (RCFA-SM-26-026); 12/10/2025 route read 0.055 14 days before the 12/24 failure [DOC KV-VR-260812 p.1] [DOC KV-VR-251210 p.1]
- No route alert on 10/14/2026 (0.067), the day of the u-joint failure that evening (RCFA-SM-26-029); consistent with a u-joint not seen as bearing vibration [DOC KV-VR-261014 p.1]

## Modes
- [[bearing-failed-between-vibration-routes]] (3 repeats); [[rectifier-fault-mcc-dc-bus]]; u-joint lube miss (single event). Related BUS follow-ups: Dryer can 4/6/13 in [[bus-follow-up-actions]].

## Downtime log events (minutes per the log)
- 2025-12-24 08:55 bearing failure 441 min, WO 26101694, RCFA-SM-25-002; "bearing vibration rising (bonvoy) for 35 days before" (RCFA says about 18 days of Pi trend). Grade 34 Super, crew B. [downtime DT-251224-0083]
- 2026-02-04 15:00 planned bearing change 163 min, WO 26102695, "found Feb 03 (bearing vibration rising (bonvoy))": the vibration route/Bonvoy caught the bearing and it was changed planned. No RCFA. [downtime DT-260204-0151]
- 2026-03-22 20:15 rectifier fault (MCC-2 DC bus) 224 min, WO 26103836, RCFA-SM-26-011. [downtime DT-260322-0219]
- 2026-06-25 03:53 bearing failure 297 min, WO 26106244, RCFA-SM-26-018; 41 days of rising vibration per the log (RCFA about 20). Crew D. [downtime DT-260624-0405]
- 2026-08-26 10:02 bearing failure 408 min, WO 26107735, RCFA-SM-26-026; 20 days of rising vibration per the log (RCFA about 10). [downtime DT-260826-0513]
- 2026-10-15 00:06 (log id DT-261014-0589, shift PM1-SHIFT-2026-10-14-N) driveshaft snaps 287 min, WO 26108981, RCFA-SM-26-029, grade 24#, crew D: "Dryer driveshaft snaps. Millwrights called in." The RCFA dates it 2026-10-14 (shift date); the log timestamp is just after midnight on 10-15. A 2nd press top felt break of 80 min followed at 04:53 the same night. [downtime DT-261014-0589] [downtime DT-261015-0590] [Shift Report PM1-SHIFT-2026-10-14-N]
- Three bearing stops total 1,146 min; with rectifier 224 min the unplanned total on this asset in the batch is 1,370 min (the planned 163 min change is separate). [downtime DT-251224-0083] [downtime DT-260322-0219] [downtime DT-260624-0405] [downtime DT-260826-0513]

## Shift reports Feb 2026 (the planned bearing change that worked)
- Handover 02-03 Day and Night: "Dryer drive lineup: bearing vibration rising (Bonvoy) -> grease and take daily readings". [Shift Report PM1-SHIFT-2026-02-03-D] [Shift Report PM1-SHIFT-2026-02-03-N]
- 02-04 Day: planned stop 163 min at 10:00, "Bearing change (found on the vibration route)", WO 26102695, crew A; shift 242 t, 68.6% sheet on. Handover 02-04 Day/Night "done; running normal". [Shift Report PM1-SHIFT-2026-02-04-D] [Shift Report PM1-SHIFT-2026-02-04-N]
- First sign to change: about 1 day (flagged 02-03 handover, changed 02-04 10:00). Contrast with the unplanned bearing failures of 2025-12-24 and later: [[bearing-failed-between-vibration-routes]]. [Shift Report PM1-SHIFT-2026-02-04-D]
- CONFLICT: the shift report puts the stop at 10:00; the downtime log row above says 15:00 (a 5 h offset, same offset as the 2nd press drive and forming fabric rows; see [[2nd-press-drive]], [[forming-fabric-damage]]). [Shift Report PM1-SHIFT-2026-02-04-D] [downtime DT-260204-0151]
- The Bonvoy ramps listed below (Nov-Dec 2025 and May-Jun 2026) do not cover 2026-02-03; the "(Bonvoy)" flag in the handover has no matching DRYER_DRIVE_VIB exception on this page. [Shift Report PM1-SHIFT-2026-02-03-D]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072742 Dryer drive lineup, section sec-dryer-2)
- Emergency bearing failures (type 3, prio 1; hours are labour, not downtime): 2026-06-25 14.9 h est / 16.4 h act "bearingfail: bearing vibration rising (bonvoy) for 41 days before" [WO 26106244]; 2026-08-26 20.4 h / 22.4 h "...for 20 days before" [WO 26107735]. Both MECH Beatrix Hale.
- Outage "MCC lineup clean and torque check" (E&I Omar Szabo, type 4): 2026-07-08 8 h est [WO 26105768]; 2026-08-19 6 h est [WO 26106797]; 2026-09-30 8 h est [WO 26107861]. Nov 11 has WO 26108813 ([[out-2026-11-11]]).
- Preventive on this asset: "Monthly vibration route (Keel Vibration Services)" 6 h est MECH, completed 2026-06-10, 07-08, 08-12, 09-09 [WO 26105782] [WO 26106454] [WO 26107280] [WO 26108029]; "MCC thermography" E&I 3 h est, completed 2026-06-28, 07-26, 08-25, 09-26 [WO 26106125] [WO 26106902] [WO 26107546] [WO 26108323]; "Lube route: dryers and reel" MILL 4 h est, 16 WOs 2026-06-14 to 2026-09-29 (asset logged as Dryer drive lineup). These dates match the Keel route dates in [[vibration-routes]].
- Related dryer-section corrective WOs: [[dryer-can-13]] (cold can), [[2nd-section-pv-fan]]. See [[work-orders-jun-sep-2026]].

## BUS issues (Jun-Oct 2026; owner Gloria Nakamura; list in [[bus-issue-sheet]])
- 2026-06-24 bearing 5.0 h, WO 26106244, "rising for 41 days before". [BUS 2026-06-24 .. BUS 2026-06-25 | issue a087f20c8958c226]
- 2026-08-26 bearing 6.8 h, WO 26107735, "rising for 20 days before". [BUS 2026-08-26 .. BUS 2026-08-27 | issue a1678a06376c0002]
- 2026-10-14 driveshaft snaps 4.8 h, "Millwrights called in", WO 26108981 (RCFA-SM-26-029), closed 10-15; this WO number is not on the downtime rows above. [BUS 2026-10-14 .. BUS 2026-10-15 | issue 8073fc5c0d602eb1]
- Dryer-section nuisance items nearby: Dryer can 6 break-tape reviews, Dryer can 4 doctor blade, [[dryer-can-13]] ([[dryer-cans]]).

## Asset and Pi tags (from equipment/Pi tag listing)
- Dryer drive lineup is asset 00072742 (kind drive, section sec-dryer-2, parent PM1 2nd dryer section 00072042). Pi tag: PM1:DRYER_DRIVE_VIB bearing vibration (in/s). [equipment 00072742] [Pi tag PM1:DRYER_DRIVE_VIB]
- See [[pi-tag-map]].

## Bonvoy (tag PM1:DRYER_DRIVE_VIB, 68 tag-days; tool: bonvoy_exceptions; see [[bonvoy]])
- Ramp 1: 2025-11-25 -> 2025-12-24 (30 d), daily max 0.080 -> 0.411 in/s; ends on the RCFA-SM-25-002 failure date. [Bonvoy PM1:DRYER_DRIVE_VIB 2025-11-25] [Bonvoy PM1:DRYER_DRIVE_VIB 2025-12-24]
- Ramp 2: 2026-05-21 -> 2026-06-24 (35 d), daily max 0.087 -> 0.413; ends on the RCFA-SM-26-018 date; plus a 5 h blip 2026-04-17. [Bonvoy PM1:DRYER_DRIVE_VIB 2026-05-21] [Bonvoy PM1:DRYER_DRIVE_VIB 2026-06-24]
- 2026-08-25 (7 h, max 0.396) and 2026-08-26 (4 h, max 0.408): the day before and the day of the RCFA-SM-26-026 failure. Only 2 days flagged, so the RCFA's "about 10 days" of trend is not visible as flagged days (the band was already wide, -0.1675 to 0.3792). [Bonvoy PM1:DRYER_DRIVE_VIB 2026-08-25] [Bonvoy PM1:DRYER_DRIVE_VIB 2026-08-26]
- Nothing flagged on this tag after 2026-08-26 in the record; the 2026-10-14 u-joint failure (RCFA-SM-26-029) did not show on the vibration tag. [Bonvoy PM1:DRYER_DRIVE_VIB 2026-08-26]
- Dryer-section syphon differential / steam lows: [[bonvoy-multi-tag-dips]]. Mode page: [[bearing-failed-between-vibration-routes]].

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- Emergency WO 26103836 rectifier fault, MCC-2 DC bus down (2026-03-22, 11.2 / 12.3 h, RCFA-SM-26-011): [[rectifier-fault-mcc-dc-bus]]. [WO 26103836]
- Weekly PM "Lube route: dryers and reel" (asset 00072742, MILL Beatrix Hale, 4 h est): 16 WOs, 26102954 (done 02-23) to 26105586 (06-07). Monthly "MCC thermography" (E&I Omar Szabo, 3 h est): 26103045, 26103787, 26104473, 26105320. [WO 26102954] [WO 26105586] [WO 26103045] [WO 26105320]
- "Monthly vibration route (Keel Vibration Services)" is booked on this asset (MECH Beatrix Hale, 6 h est / 6.6 h act): WO 26103304 (done 03-11), 26104060 (04-08), 26105005 (05-13), the same dates as the Keel route documents; see [[vibration-routes]]. [WO 26103304] [WO 26104060] [WO 26105005]
- Outage "MCC lineup clean and torque check" (E&I): WO 26103556 ([[out-2026-04-15]], 8/8.8 h) and WO 26104613 ([[out-2026-05-27]], 6/6.6 h). No lineup bearing event in the WOs for Feb-Jun; the 2026-02-04 planned bearing change was WO 26102695 (other extract). [WO 26103556] [WO 26104613]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26101694 "Bearing failure: Dryer drive lineup" (asset 00072742, type 3, prio 1, requested and completed 2025-12-24, MECH Beatrix Hale, est 22 h act 24.2 h, the biggest emergency after the forming fabric hole): "bearingfail: bearing vibration rising (bonvoy) for 35 days before." [WO 26101694]
- Planned bearing change WO 26102695 "Bearing change (found on the vibration route)" (type 1, prio 1, requested 2026-02-03, planned and completed 2026-02-04, est 8.2 h act 9 h): 9 h of work against 24.2 h for the unplanned failure. [WO 26102695] [WO 26101694]
- Outage WO "MCC lineup clean and torque check" (E&I Omar Szabo): 26100504 ([[out-2025-12-10]]), 26101512 ([[out-2026-01-21]]), 26102576 ([[out-2026-03-04]]); preventive MCC thermography (E&I, 3.3 h act) monthly: 26100091, 26100882, 26101631, 26102282. [WO 26100504] [WO 26102576] [WO 26100091] [WO 26102282]
- Monthly vibration route by Keel Vibration Services is a WO on this asset: 26100511 (done 2025-11-12), 26101162 (12-10), 26102023 (2026-01-14), 26102730 (02-11), 6.6 h act each. [WO 26100511] [WO 26102730] See [[vibration-routes]].
- Weekly "Lube route: dryers and reel" (MILL, 4.4 h act): 17 WOs, 26100021 ... 26102814. [WO 26100021] [WO 26102814]
- The MCC lineup clean at 12-10 and the lube routes preceded the 12-24 bearing failure; none of the 12-10 outage WOs changed the bearing ([[out-2025-12-10]]). [WO 26100504] [WO 26101694]
