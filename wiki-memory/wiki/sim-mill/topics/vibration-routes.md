---
name: vibration-routes
description: Keel Vibration Services monthly PM1 vibration route, Nov 2025 - Oct 2026 (12 routes): limits, which assets alerted, what was recommended, and how each alert lined up with failures; read for "was it caught on the route" and reel drum / fan pump / press drive alert history
type: topic
aliases: ["Keel route", "monthly vibration route", "KV-VR", "Keel Vibration Services", "vibration alerts", "overall velocity"]
---
## What it is
- Keel Vibration Services (analyst Anders Vollmer) issues a monthly PM1 vibration route; distribution Mei Fairbanks, Gloria Nakamura, Curtis Lindahl [DOC KV-VR-261014 p.1]
- Limits: "Alert 0.15 in/s, Danger 0.40 in/s (overall velocity)" [DOC KV-VR-261014 p.1]
- Doc ids are KV-VR-YYMMDD: 251112, 251210, 260114, 260211, 260311, 260408, 260513, 260610, 260708, 260812, 260909, 261014 (12 routes in this library), 28 or 35 days apart (computed); the latest is 10/14/2026
- Online counterpart: Pi tags PM1:<asset>_VIB and Bonvoy exceptions (tool bonvoy_exceptions / bonvoy_report; see [[bonvoy]]); this page is the route (periodic reading) view only
- Points: PM1:PULPER_VIB, PM1:REF_A_VIB, PM1:REF_B_VIB, PM1:FAN_PUMP_VIB, PM1:COUCH_DS_VIB, PM1:PRESS1_DS_VIB, PM1:PRESS2_DS_VIB, PM1:DRYER_DRIVE_VIB, PM1:REEL_DRUM_DS_VIB, PM1:WINDER_DRUM_VIB, plus portables on [[d2-froll-3]], [[d4-froll-1]], [[hood-supply-fan]], [[hood-exhaust-fan]] and the [[vacuum-pump]] [DOC KV-VR-261014 p.1]
- Document position ids tagged on every Keel report: d2-froll-3, d4-froll-1, ref-refa, ref-refb

## Alerts (overall in/s above 0.15) by route date
- 11/12/2025 [[couch-roll]] 0.216 Alert, "Bearing defect frequencies present", "Plan a bearing change" [DOC KV-VR-251112 p.1]
- 11/12/2025 [[reel-drum]] 0.133 Good (below Alert but 2-6x the 0.023-0.063 seen on the next seven routes) [DOC KV-VR-251112 p.1]
- Routes where an Alert row has no note and the findings say "No new findings. All points within limits." (a report-text CONFLICT): 01/14/2026 pulper 0.275, 04/08/2026 pulper 0.169, 06/10/2026 dryer drive 0.227 [DOC KV-VR-260114 p.1] [DOC KV-VR-260408 p.1] [DOC KV-VR-260610 p.1]; in these three cases the alert was not written up as a finding and a failure followed within 8-20 days
- 01/14/2026 [[pulper-rotor]] 0.275 Alert (no note) [DOC KV-VR-260114 p.1]
- 03/11/2026 [[2nd-press-drive]] 0.249 Alert, "Bearing defect frequencies present", "Plan a bearing change" [DOC KV-VR-260311 p.1]
- 04/08/2026 [[pulper-rotor]] 0.169 Alert [DOC KV-VR-260408 p.1]
- 06/10/2026 [[dryer-drive-lineup]] 0.227 Alert in the readings table, but the findings read "No new findings. All points within limits." CONFLICT inside the report [DOC KV-VR-260610 p.1]
- 08/12/2026 [[1st-press-drive]] 0.155 Alert, "Bearing defect frequencies present", "Plan a bearing change"; [[reel-drum]] 0.173 Alert, "Outer race defect frequency (BPFO) with harmonics", "Change at the next outage (Aug 19). Plan the bearing now." [DOC KV-VR-260812 p.1]
- 09/09/2026 [[fan-pump]] 0.265 Alert, "Bearing defect frequencies present", "Plan a bearing change"; reel drum 0.274 Alert BPFO [DOC KV-VR-260909 p.1]
- 10/14/2026 reel drum 0.389 Alert BPFO; all other points Good [DOC KV-VR-261014 p.1]
- Routes with no Alert row: 12/10/2025, 02/11, 05/13, 07/08/2026 ("No new findings. All points within limits.") [DOC KV-VR-251210 p.1] [DOC KV-VR-260211 p.1] [DOC KV-VR-260513 p.1] [DOC KV-VR-260708 p.1]

## Reel drum DS bearing series (PM1:REEL_DRUM_DS_VIB, route values in/s)
- 11/12/2025 0.133; 12/10/2025 0.023; 01/14/2026 0.059; 02/11 0.059; 03/11 0.061; 04/08 0.063; 05/13 0.057; 06/10 0.060; 07/08 0.023; 08/12 0.173; 09/09 0.274; 10/14 0.389 [DOC KV-VR-251112 p.1] [DOC KV-VR-261014 p.1]
- 08/12 recommendation: change at the Aug 19 outage [DOC KV-VR-260812 p.1]
- 09/09: "Deferred from Aug 19 (no bearing in stores). Rate of rise is accelerating: change no later than the Nov 11 outage; consider a planned stop if it passes 0.50 in/s." [DOC KV-VR-260909 p.1]
- 10/14: same wording repeated at 0.39 in/s, 0.01 below the Danger limit of 0.40 [DOC KV-VR-261014 p.1]
- Rise 0.173 to 0.274 in 28 days (+0.101) then 0.274 to 0.389 in 35 days (+0.115), computed from the route dates; Bonvoy had it above 0.40 by 10/25 (see [[reel-drum]])
- Bearing part and ETA: see [[out-2026-11-11]] (SM-0201)

## Route alert versus failure (days from route to stop; computed)
- Couch roll: 0.216 on 11/12/2025, failed 11/19/2025 (7 d) [RCFA-SM-25-001]. The RCFA event text says "failed (not caught on the route)"; the route had flagged it a week earlier. CONFLICT between [RCFA-SM-25-001] and [DOC KV-VR-251112 p.1]
- Pulper rotor: 0.275 on 01/14/2026, failed 01/22/2026 (8 d) [RCFA-SM-26-005]; 0.169 on 04/08, failed 04/28 (20 d) [RCFA-SM-26-013]; 07/08 0.062 Good, failed 07/20 (12 d later) [RCFA-SM-26-022]
- 2nd press drive: 0.249 on 03/11/2026, failed 03/18 (7 d); RCFA-SM-26-010 text again says "(not caught on the route)" [RCFA-SM-26-010]; 09/09 0.110 (Good), failed 09/20 (11 d) [RCFA-SM-26-028]
- Dryer drive lineup: 12/10/2025 0.055 Good then failed 12/24 (14 d) [RCFA-SM-25-002]; 06/10/2026 0.227 Alert, failed 06/24 (14 d) [RCFA-SM-26-018]; 08/12 0.104 Good, failed 08/26 (14 d) [RCFA-SM-26-026]
- 1st press drive 0.155 on 08/12/2026 then Good 0.056 on 09/09 (change at an outage assumed, not stated) [DOC KV-VR-260909 p.1]
- Fan pump 0.265 on 09/09/2026, back to 0.061 on 10/14 (bearing change assumed, not stated) [DOC KV-VR-261014 p.1]
- Reading: a monthly route is 28-35 days apart, longer than the 7-14 day gap from the first alert to failure in these cases; see [[bearing-failed-between-vibration-routes]]

## Routine values (for judging "normal")
- Typical Good readings 0.053-0.076 in/s on the fixed points; the 12/10/2025 and 07/08/2026 routes read 0.022-0.026 on nearly every fixed point (dryer drive 0.055 on 12/10/2025) [DOC KV-VR-251210 p.1] [DOC KV-VR-260708 p.1]. Why those two routes are low is not stated; both fall on outage days ([[out-2025-12-10]], [[out-2026-07-08]])
- Refiner motors PM1:REF_A_VIB and PM1:REF_B_VIB stayed 0.057-0.073 and 0.062-0.072 in/s; no refiner alert in 12 routes [DOC KV-VR-261014 p.1]
- Felt rolls [[d2-froll-3]] 0.040-0.060 and [[d4-froll-1]] 0.047-0.062 in/s on every route; no alert [DOC KV-VR-261014 p.1]
- Vacuum pump portable 0.071-0.089 in/s (highest of the portables, no alert); hood supply fan 0.062-0.076; hood exhaust fan 0.056-0.075 [DOC KV-VR-260610 p.1] [DOC KV-VR-261014 p.1]
- Winder drums PM1:WINDER_DRUM_VIB 0.063-0.075 (0.026 on the two low routes); no alert [DOC KV-VR-261014 p.1]
- Related RCFA hood fan finding: "No vibration monitoring on the fan" [RCFA-SM-26-009]; hood fans appear as portables from 11/12/2025 on [DOC KV-VR-251112 p.1]
