---
name: bearing-failed-between-vibration-routes
description: Recurring failure mode - rotating-equipment bearing fails between monthly vibration routes (P-F interval shorter than route); 9 RCFAs on 4 assets, pulper rotor and dryer drive lineup repeat; read for recurrence and whether the standard 3-action fix is done
type: failure-mode
aliases: ["bearing failure", "bearing failed between routes", "P-F interval shorter than the monthly route", "no online vibration", "monthly route frequency"]
---
## Current picture (as of 2026-11-10; tool: rcfa_status)
- 9 RCFAs, about 49.3 h and 1,531 t (computed), on couch roll, dryer drive lineup, pulper rotor and 2nd press drive. [RCFA-SM-25-001] [RCFA-SM-26-028]
- Open: RCFA-SM-26-013 (pulper, SM-0124 overdue), -026 (dryer drive, SM-0207 overdue), -028 (2nd press drive, SM-0226 online sensor overdue, SM-0227 due 11-23). [Action SM-0124] [Action SM-0207] [Action SM-0226] [Action SM-0227]
- Stated root cause is identical on every case: "Bearing failed between vibration routes (P-F interval shorter than the monthly route)". [RCFA-SM-25-001]
- Standard 3-action fix: two-weekly route, online vibration sensor, grease review; sensor recorded done yet later RCFAs again say "no online vibration". [RCFA-SM-26-028]
- Pi lead times where stated: about 9 to 22 days. [RCFA-SM-26-013] [RCFA-SM-26-028]
- Reel drum DS bearing (Aug-Oct 2026) is a live case without an RCFA: see [[reel-drum]]. [Bonvoy Report 2026-10-31]
- Lead-time detail: [[precursor-lead-times]].

## Pattern
- Stated root cause on every case: "Bearing failed between vibration routes (P-F interval shorter than the monthly route)". [RCFA-SM-25-001]
- Contributing, same wording each time: "Lubrication interval; monthly route frequency; no online vibration on this asset". [RCFA-SM-26-010]
- Standard 3-action fix on each RCFA: (1) add the asset to a two-weekly route, (2) install an online vibration sensor, (3) review grease type and interval. All owned by Gloria Nakamura. [RCFA-SM-26-005]
- Tool for the RCFA list: rcfa_status (all 29 in [[rcfa-register]]); for stops: downtime_summary group=equipment kind=break.
- Totals over the 9 RCFAs below: about 49.3 h down and 1,531 t lost (computed from the RCFA header values). [RCFA-SM-25-001 ... RCFA-SM-26-028]

## Events (event date, RCFA, asset, downtime, loss, Pi lead time)
- 2025-11-19 [RCFA-SM-25-001] [[couch-roll]] 4 h, 126 t; closed 2026-01-21. No Pi lead time stated. [RCFA-SM-25-001]
- 2025-12-24 [RCFA-SM-25-002] [[dryer-drive-lineup]] 7.3 h, 228 t; trend in Pi PM1:DRYER_DRIVE_VIB about 18 days before the stop; closed 2026-02-23. [RCFA-SM-25-002]
- 2026-01-22 [RCFA-SM-26-005] [[pulper-rotor]] 5 h, 157 t; PM1:PULPER_VIB about 15 days; closed 2026-03-22. [RCFA-SM-26-005]
- 2026-03-18 [RCFA-SM-26-010] [[2nd-press-drive]] 3.9 h, 120 t; closed 2026-05-21. [RCFA-SM-26-010]
- 2026-04-28 [RCFA-SM-26-013] [[pulper-rotor]] 4.5 h, 139 t; PM1:PULPER_VIB about 22 days; OPEN, grease review SM-0124 overdue. [RCFA-SM-26-013]
- 2026-06-24 [RCFA-SM-26-018] [[dryer-drive-lineup]] 5 h, 153 t; PM1:DRYER_DRIVE_VIB about 20 days; closed 2026-08-18. [RCFA-SM-26-018]
- 2026-07-20 [RCFA-SM-26-022] [[pulper-rotor]] 5.9 h, 184 t; PM1:PULPER_VIB about 18 days; closed 2026-09-22. [RCFA-SM-26-022]
- 2026-08-26 [RCFA-SM-26-026] [[dryer-drive-lineup]] 6.8 h, 211 t; PM1:DRYER_DRIVE_VIB about 10 days; OPEN, grease review SM-0207 overdue. [RCFA-SM-26-026]
- 2026-09-20 [RCFA-SM-26-028] [[2nd-press-drive]] 6.9 h, 213 t; PM1:PRESS2_DS_VIB about 9 days; OPEN, sensor SM-0226 overdue, grease review SM-0227 not started. [RCFA-SM-26-028]

## Recurrence
- Pulper rotor: 3 bearing RCFAs (Jan, Apr, Jul 2026) after the same action set each time. [RCFA-SM-26-005] [RCFA-SM-26-013] [RCFA-SM-26-022]
- Dryer drive lineup: 3 bearing RCFAs (Dec 2025, Jun 2026, Aug 2026). [RCFA-SM-25-002] [RCFA-SM-26-018] [RCFA-SM-26-026]
- 2nd press drive: 2 bearing RCFAs (Mar, Sep 2026). [RCFA-SM-26-010] [RCFA-SM-26-028]
- Couch roll: 1 (Nov 2025); the action set was completed in full by 2026-01-21. [RCFA-SM-25-001]
- Each repeat follows a closed RCFA that had the same "two-weekly route + online sensor + grease review" actions completed, so the fix has not stopped repeats on pulper rotor, dryer drive lineup or 2nd press drive (observation from the dates; no RCFA states this).
- Related but different mode on the same assets: [[rectifier-fault-mcc-dc-bus]], [[motor-winding-insulation-failure]], dryer driveshaft u-joint ([[dryer-drive-lineup]] RCFA-SM-26-029), pulper drive IGBT trip ([[pulper-rotor]] RCFA-SM-26-021).
- Hood fan bearing failures follow the same "no vibration monitoring" theme: [[hood-fan-failures]].

## What the Keel monthly routes showed before the stops (reports library; detail in [[vibration-routes]])
- Route alerts (above 0.15 in/s) preceded 5 of the 9 failures by 7-20 days: couch roll 0.216 on 11/12/2025 then failure 11/19 (7 d); pulper rotor 0.275 on 01/14 then 01/22 (8 d) and 0.169 on 04/08 then 04/28 (20 d); 2nd press drive 0.249 on 03/11 then 03/18 (7 d); dryer drive 0.227 on 06/10 then 06/24 (14 d) [DOC KV-VR-251112 p.1] [DOC KV-VR-260114 p.1] [DOC KV-VR-260311 p.1] [DOC KV-VR-260408 p.1] [DOC KV-VR-260610 p.1]
- The other four were below Alert on the last route before the stop: dryer drive 0.055 (12/10/2025) and 0.104 (08/12/2026), pulper 0.062 (07/08), 2nd press drive 0.110 (09/09) [DOC KV-VR-251210 p.1] [DOC KV-VR-260812 p.1] [DOC KV-VR-260708 p.1] [DOC KV-VR-260909 p.1]
- CONFLICT: RCFA-SM-25-001 and RCFA-SM-26-010 describe the failure as "not caught on the route", while the preceding Keel route (7 days earlier) recorded an Alert and "Plan a bearing change" on each [RCFA-SM-25-001] [RCFA-SM-26-010] [DOC KV-VR-251112 p.1] [DOC KV-VR-260311 p.1]
- In three route reports (01/14, 04/08, 06/10) the Alert reading carried no note and the findings said "No new findings. All points within limits." [DOC KV-VR-260114 p.1] [DOC KV-VR-260408 p.1] [DOC KV-VR-260610 p.1]
- Alerts that did NOT end in a failure: 1st press drive 0.155 on 08/12/2026 (back to 0.056 on 09/09) and fan pump 0.265 on 09/09 (back to 0.061 on 10/14); each recommended "Plan a bearing change" [DOC KV-VR-260812 p.1] [DOC KV-VR-261014 p.1]; see [[1st-press-drive]], [[fan-pump]]
- Open case now: [[reel-drum]] DS bearing, BPFO outer race defect, 0.173 (08/12) to 0.274 (09/09) to 0.389 (10/14) in/s; change "no later than the Nov 11 outage" [DOC KV-VR-261014 p.1]

## What the shift crews saw before the two Nov 2025 bearing stops (shift reports; see [[shift-handover-signals-2025-11]])
- Couch roll (stop 2025-11-19, WO 26100833, 243 min): no couch item on any handover 11-01 to 11-18; the Keel route of 11-12 had read 0.216 in/s Alert and Bonvoy was High from 11-07, but neither reached the shift handover. After the stop, the report repeated "not caught on the route". [Shift Report PM1-SHIFT-2025-11-18-N] [Shift Report PM1-SHIFT-2025-11-21-D] [DOC KV-VR-251112 p.1]
- Reel drum DS bearing (stop 11-24 23:30 per shift report, WO 26100945, 165 min): handovers show only indirect reel items in the prior 2 weeks, spool bar damage (11-10 to 11-15) and reel turn-up missed twice on nights (11-12, 11-13, 11-20, 11-21); no bearing noise, temperature or vibration item. [Shift Report PM1-SHIFT-2025-11-24-N] [Shift Report PM1-SHIFT-2025-11-12-N]
- Contrast: the hood supply fan bearing was on the handover as "bearing noisy" in four separate spells in Nov 2025 (11-01, 11-09/10, 11-19/20, 11-23 to 11-25) and was greased, and it did fail (2026-03-11, [[hood-supply-fan]]). Audible bearing noise reached the handover; rising vibration on the routes and Bonvoy did not. [Shift Report PM1-SHIFT-2025-11-01-D] [Shift Report PM1-SHIFT-2025-11-23-D]

## What the shift crews saw before the 2026-03-18 bearing stop (shift reports Mar 2026; see [[shift-handover-signals-2026-03]])
- No 2nd press drive item in handovers 03-01 to 03-17, including the days after the 03-11 Keel Alert; the stop came on 03-18 Day at 06:30 (shift clock). Handover after: "bearing failed (not caught on the route) → watching after restart" (03-20). [Shift Report PM1-SHIFT-2026-03-17-D] [Shift Report PM1-SHIFT-2026-03-20-D] See [[2nd-press-drive]].
- Same pattern as Nov 2025: crews' handover lists carried other items, and the route Alert did not reach the handover. Pulper rotor (04-28): only "amps swinging" on 03-01 in March. [Shift Report PM1-SHIFT-2026-03-01-D]

## Work orders for the Jun-Sep 2026 events (work-orders-3 extract; labour hours est / act, not downtime; all type 3 Emergency prio 1 unless noted)
- 2026-06-25 [[dryer-drive-lineup]] WO 26106244, 14.9 h / 16.4 h, "for 41 days before". [WO 26106244]
- 2026-07-20 [[pulper-rotor]] WO 26106916, 17.8 h / 19.6 h, "for 35 days before". [WO 26106916]
- 2026-08-26 [[dryer-drive-lineup]] WO 26107735, 20.4 h / 22.4 h, "for 20 days before". [WO 26107735]
- 2026-09-20 [[2nd-press-drive]] WO 26108393, 20.6 h / 22.7 h, "for 18 days before". [WO 26108393]
- Planned catches in the same months (bearing found on the Keel route, changed without a failure): 1st press drive WO 26107413 (found 08-12, changed 2026-08-19 at the outage, 8 h / 8.8 h, Corrective prio 2) [WO 26107413]; fan pump WO 26108169 (found 09-09, changed 2026-09-11, 6 h / 6.6 h, Corrective prio 1) [WO 26108169]. The reel drum DS bearing found 08-12 is NOT changed yet: WO 26107420 waits on parts, planned 2026-11-11 [WO 26107420]. See [[reel-drum]], [[1st-press-drive]], [[fan-pump]].
- Pattern: the WO hours of the failed-bearing emergencies (14.9-20.6 h est) are about 2-3 times those of the planned catches (6-8 h est). [WO 26106244] [WO 26108393] [WO 26107413] [WO 26108169]

## Open items (as of 2026-11-10)
- SM-0124 grease review pulper rotor, due 2026-07-01, In progress. [Action SM-0124]
- SM-0207 grease review dryer drive lineup, due 2026-10-29, In progress. [Action SM-0207]
- SM-0226 online sensor 2nd press drive, due 2026-11-02, In progress. [Action SM-0226]
- SM-0227 grease review 2nd press drive, due 2026-11-23, Not started. [Action SM-0227]
- Late completion: SM-0206 online sensor dryer drive lineup due 2026-10-08, completed 2026-10-11. [Action SM-0206]

## Downtime log view (tool: downtime_events cause="Bearing failure"; Nov 2025 - Sep 1 2026)
- 9 unplanned "Bearing failure" stops, 2,714 min total: couch roll 243 (DT-251119-0024), reel drum DS bearing 165 (DT-251124-0032, WO 26100945, no RCFA filed), dryer drive lineup 441 (DT-251224-0083), pulper rotor 303 (DT-260122-0130), 2nd press drive 232 (DT-260318-0207), pulper rotor 269 (DT-260428-0277), dryer drive lineup 297 (DT-260624-0405), pulper rotor 356 (DT-260720-0461), dryer drive lineup 408 (DT-260826-0513). [downtime DT-251119-0024 to DT-260826-0513]
- Event text splits two kinds: "(not caught on the route)" for couch roll, reel drum DS bearing and 2nd press drive (no precursor); "bearing vibration rising (bonvoy) for N days before" for the other six: dryer drive 35, pulper 31, pulper 43, dryer drive 41, pulper 35, dryer drive 20 days. [downtime DT-251224-0083] [downtime DT-260122-0130] [downtime DT-260428-0277] [downtime DT-260624-0405] [downtime DT-260720-0461] [downtime DT-260826-0513]
- CONFLICT: these Bonvoy lead times (20-43 days) are longer than the Pi lead times stated in the RCFAs above (about 10-22 days); both kept. Either way the rise was visible weeks before the stop on six of nine, longer than a monthly route interval.
- The reel drum DS bearing failure (2025-11-25 04:30, 165 min, WO 26100945) has no RCFA in the downtime log; see [[reel-drum]].
- One planned bearing change was found on the vibration route: 2026-02-04 dryer drive lineup 163 min, WO 26102695, "found Feb 03 (bearing vibration rising (bonvoy))". It is the one case where the route/Bonvoy caught the bearing before failure. [downtime DT-260204-0151]

## Downtime log view, Sep-Oct 2026 addition
- 2026-09-20 2nd press drive bearing failure 412 min, WO 26108393, RCFA-SM-26-028: "bearing vibration rising (bonvoy) for 18 days before" (the 10th "Bearing failure" row; Bonvoy lead 17 flagged days, RCFA about 9 days, route 09/09 read 0.110 Good). [downtime DT-260920-0561] [[2nd-press-drive]]
- The 2026-09-11 fan pump bearing change (180 min, planned, "found on the Sep 09 vibration route") is the second planned catch of a bearing from the route, after the 2026-02-04 dryer drive change. [downtime DT-260911-0541] [[fan-pump]]
- 2026-10-15 dryer driveshaft failure (287 min, WO 26108981) is not logged as a bearing failure: cause "Driveshaft snaps", u-joint, see [[dryer-drive-lineup]]. [downtime DT-261014-0589]
- No "Bearing failure" row at the pulper rotor or reel drum in 2026-09-02 to 2026-10-31. [downtime DT-260901-0523 to DT-261030-0629]

## Bonvoy ramps behind these events (tool: bonvoy_exceptions tag=<tag>; see [[bonvoy]])
- Signature: the tag's daily High hours climb to ~24 h/day and the daily max rises from ~0.08 to ~0.40 in/s over 2-5 weeks; the Alert limit is 0.15 and the Danger limit 0.4 in/s. [Bonvoy Report 2026-10-26] [Bonvoy PM1:PULPER_VIB 2026-01-20]
- Each RCFA event date above is the last day (pulper Jan: the day before) of a Bonvoy ramp, with daily max 0.40-0.41 on the last day, so the RCFA "Pi lead time" is the length of the ramp. Ramps (first flagged day -> last day; days; daily max start -> end):
- [[couch-roll]] PM1:COUCH_DS_VIB 2025-11-07 -> 2025-11-19 (13 d; daily max 0.139 -> 0.405). [Bonvoy PM1:COUCH_DS_VIB 2025-11-07] [Bonvoy PM1:COUCH_DS_VIB 2025-11-19]
- [[dryer-drive-lineup]] PM1:DRYER_DRIVE_VIB 2025-11-25 -> 2025-12-24 (30 d, 0.080 -> 0.411); 2026-05-21 -> 2026-06-24 (35 d, 0.087 -> 0.413); then 2026-08-25/26 (7 h and 4 h, 0.396/0.408; the band was already very wide). [Bonvoy PM1:DRYER_DRIVE_VIB 2025-11-25] [Bonvoy PM1:DRYER_DRIVE_VIB 2026-06-24] [Bonvoy PM1:DRYER_DRIVE_VIB 2026-08-26]
- [[pulper-rotor]] PM1:PULPER_VIB 2025-12-25 -> 2026-01-21 (28 d, 0.086 -> 0.414); 2026-03-30 -> 2026-04-28 (30 d, 0.115 -> 0.413); 2026-07-05 -> 2026-07-20 (15 d listed, 07-08 not listed, 0.192 -> 0.407; first listed day already 0.192). The Jan ramp is 28 flagged days vs RCFA-SM-26-005's "about 15 days" Pi lead. [Bonvoy PM1:PULPER_VIB 2025-12-25] [Bonvoy PM1:PULPER_VIB 2026-04-28] [Bonvoy PM1:PULPER_VIB 2026-07-20]
- [[2nd-press-drive]] PM1:PRESS2_DS_VIB 2026-02-24 -> 2026-03-18 (23 d, 0.080 -> 0.401); 2026-09-04 -> 2026-09-20 (17 d, 0.078 -> 0.408). [Bonvoy PM1:PRESS2_DS_VIB 2026-03-18] [Bonvoy PM1:PRESS2_DS_VIB 2026-09-20]
- Lead-time wording differs from the RCFAs: RCFA-SM-26-028 says about 9 days, Bonvoy flagged PRESS2_DS_VIB for 17 days (2026-09-04..20); RCFA-SM-26-026 says about 10 days, Bonvoy has only 7 h and 4 h on 2026-08-25/26 for the dryer drive. [RCFA-SM-26-028] [RCFA-SM-26-026]

## Ramps with no RCFA in this wiki (candidates for a missed failure or a repair at an outage)
- [[reel-drum]] PM1:REEL_DRUM_DS_VIB 2025-11-07 -> 2025-11-24 (18 d, 0.087 -> 0.396) with PM1:REEL_DRUM_DS_TEMP up to 164.6 degF; and 2026-07-21 -> 2026-08-23 (34 d); the Aug defect was found on the Aug 12 vibration route and was still above Danger on 2026-10-31 (0.426). OPEN. [Bonvoy PM1:REEL_DRUM_DS_VIB 2025-11-24] [Bonvoy Report 2026-10-31]
- [[1st-press-drive]] PM1:PRESS1_DS_VIB 2026-07-30 -> 2026-08-19 (21 d, 0.089 -> 0.239); the record ends on 2026-08-19, the date of [[out-2026-08-19]]. [Bonvoy PM1:PRESS1_DS_VIB 2026-08-19]
- [[fan-pump]] PM1:FAN_PUMP_VIB 2026-08-26 -> 2026-09-11 (17 d, 0.076 -> 0.313); and 6 scattered days 2025-12-20..29 (max 0.110). [Bonvoy PM1:FAN_PUMP_VIB 2026-09-11]
- Open now (2026-10-31): couch roll DS (second ramp since 2026-10-17, Alert exceeded) and reel drum DS (Danger). [Bonvoy Report 2026-10-31]
