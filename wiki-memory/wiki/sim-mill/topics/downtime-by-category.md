---
name: downtime-by-category
description: PM1 downtime split by kind (break, unplanned, planned, slowdown) and the list of the largest unplanned stops Nov 2025 - Sep 2026; read for "biggest stops" questions
type: topic
aliases: ["downtime summary", "biggest unplanned stops", "unplanned downtime list", "downtime by kind"]
---
## Totals (522 events, 2025-11-01 to 2026-09-01)
- break 471 events, 21,945 min; unplanned 38 events, 9,510 min; planned 10 events, 8,848 min; slowdown 3 events, 514 min. Tool: downtime_summary (group=kind). [downtime DT-251101-0001 to DT-260901-0522]
- Planned time is 7 x 1,200 min outages plus three short planned jobs; see [[planned-outage-history]]. [downtime DT-251210-0058]

## Largest unplanned stops (minutes)
- 570 forming fabric hole 2026-02-09, [[form-bottom]]. [downtime DT-260209-0163]
- 450 unplanned 2nd press top felt change 2026-05-19, [[p2-felt-top]]. [downtime DT-260519-0344]
- 441 dryer drive lineup bearing 2025-12-24, [[dryer-drive-lineup]]. [downtime DT-251224-0083]
- 408 dryer drive lineup bearing 2026-08-26. [downtime DT-260826-0513]
- 362 fan pump impeller 2026-01-02, [[fan-pump]]. [downtime DT-260122-0130]
- 356 pulper rotor bearing 2026-07-20, [[pulper-rotor]]. [downtime DT-260720-0461]
- 347 1st press top felt plugged (emergency wash) 2026-07-21, [[press-felt-plugging]]. [downtime DT-260721-0462]
- 321 2nd press bottom felt plugged 2026-05-12. [downtime DT-260512-0322]
- 315 headbox slime build-up 2026-07-11, [[headbox]]. [downtime DT-260711-0439]
- 307 hood exhaust fan 2026-05-28, [[hood-fan-failures]]. [downtime DT-260528-0354]
- 303 pulper rotor bearing 2026-01-22. [downtime DT-260122-0130]
- 297 dryer drive lineup bearing 2026-06-25. [downtime DT-260624-0405]

## Slowdowns (not full stops)
- HD cleaner blowout 239 min 2025-11-01, WO 26100308: "Stock is everywhere. Pulping stopped, and the chest is draining" (Stock prep / HD cleaners). [downtime DT-251101-0001] [Shift Report PM1-SHIFT-2025-11-01-D]
- Dye trouble 67 min 2026-03-12, Machine chest, WO 26103612: dye pump hiccup, sheet off-color. [downtime DT-260312-0199]
- REF 2 refiner plates clash 208 min 2026-06-24, WO 26106272; see [[ref-refb]]. [downtime DT-260624-0400]

## Recurring failure modes
- [[bearing-failed-between-vibration-routes]] (9 unplanned, 2,714 min), [[press-felt-plugging]], [[press-felt-plugging]], [[syphon-failure]], [[rectifier-fault-mcc-dc-bus]], [[press-felt-blows]], [[slime-buildup]]. Event-to-RCFA map: [[rcfa-register]].
- Breaks are tracked separately: [[breaks-by-location]].

## Unplanned stop -> WO -> RCFA map (log rows; minutes)
- DT-251119-0024 couch roll bearing 243, WO 26100833, RCFA-SM-25-001 ([[couch-roll]]). DT-251124-0032 reel drum DS bearing 165, WO 26100945, no RCFA ([[reel-drum]]). DT-251202-0044 4th section syphon 121, WO 26101127 ([[syphon-failure]]). DT-251224-0083 dryer drive bearing 441, WO 26101694, RCFA-SM-25-002 ([[dryer-drive-lineup]]). DT-251230-0089 vacuum pump 249, WO 26101876, RCFA-SM-25-003 ([[vacuum-pump]]). [downtime DT-251119-0024 to DT-251230-0089]
- DT-251231-0091 2nd section syphon 151, WO 26101890. DT-260102-0094 fan pump 362, WO 26101925, RCFA-SM-26-004 ([[fan-pump]]). DT-260106-0104 3rd section rotary joint 162, WO 26102009. DT-260122-0130 pulper bearing 303, WO 26102317, RCFA-SM-26-005 ([[pulper-rotor]]). DT-260207-0157 2nd press bottom felt HP shower 114, WO 26102793. DT-260209-0163 forming fabric 570, WO 26102842, RCFA-SM-26-006 ([[form-bottom]]). [downtime DT-251231-0091 to DT-260209-0163]
- DT-260215-0170 2nd press drive motor 258, WO 26102961, RCFA-SM-26-007 ([[2nd-press-drive]]). DT-260306-0196 REF 2 refiner motor 274, WO 26103346, RCFA-SM-26-008 ([[ref-refb]]). DT-260311-0197 hood supply fan 284, WO 26103507, RCFA-SM-26-009 ([[hood-fan-failures]]). DT-260318-0207 2nd press drive bearing 232, WO 26103696, RCFA-SM-26-010. DT-260321-0215 2nd press bottom felt blown 142, WO 26103801. DT-260322-0219 dryer drive rectifier 224, WO 26103836, RCFA-SM-26-011 ([[rectifier-fault-mcc-dc-bus]]). [downtime DT-260215-0170 to DT-260322-0219]
- DT-260401-0236 1st press top felt HP shower 136, WO 26104067. DT-260410-0245 4th section syphon 182, WO 26104256, RCFA-SM-26-012. DT-260428-0277 pulper bearing 269, WO 26104816, RCFA-SM-26-013. DT-260503-0289 1st press bottom felt blown 135, WO 26104942. DT-260512-0322 2nd press bottom felt plugged 321, WO 26105138, RCFA-SM-26-014. DT-260513-0327 1st press bottom felt plugged 217, WO 26105159, RCFA-SM-26-015. DT-260519-0344 2nd press top felt change 450, WO 26105306, RCFA-SM-26-016. DT-260528-0354 hood exhaust fan 307, WO 26105509, RCFA-SM-26-017. [downtime DT-260401-0236 to DT-260528-0354]
- DT-260623-0397 3rd section rotary joint 174, WO 26106237. DT-260624-0402 headbox side door 79, WO 26106258. DT-260624-0405 dryer drive bearing 297, WO 26106244, RCFA-SM-26-018. DT-260630-0417 1st press top felt HP shower 179, WO 26106440. DT-260706-0424 pulper rectifier 235, WO 26106545, RCFA-SM-26-019. DT-260711-0439 headbox slime 315, WO 26106636, RCFA-SM-26-020 ([[slime-buildup]]). DT-260718-0455 pulper drive trip 278, WO 26106867, RCFA-SM-26-021. DT-260720-0458 1st press bottom felt blown 154, WO 26106944. DT-260720-0461 pulper bearing 356, WO 26106916, RCFA-SM-26-022. [downtime DT-260623-0397 to DT-260720-0461]
- DT-260721-0462 1st press top felt plugged 347, WO 26106958, RCFA-SM-26-023. DT-260805-0485 1st press top felt HP shower 170, WO 26107287, RCFA-SM-26-024. DT-260814-0496 1st press bottom felt plugged 206, WO 26107469, RCFA-SM-26-025. DT-260826-0513 dryer drive bearing 408, WO 26107735, RCFA-SM-26-026. [downtime DT-260721-0462 to DT-260826-0513]
- Unplanned stops without an RCFA: reel drum bearing, two of three syphon stops, two rotary joint leaks, three of four HP shower stops, three felt blows, headbox side door. [downtime DT-251124-0032 to DT-260805-0485]
- Beyond 2026-09-01 (log end), unplanned days from the Production Reports: 2026-09-20 412 min, 2026-10-01 144 min, 2026-10-14 287 min; causes not in the reports (tool: downtime_events). Monthly and daily totals in [[production-daily-reports]]. [Production Report PM1-PROD-2026-09-20] [Production Report PM1-PROD-2026-10-14]
- Sep 2 - Oct 31, 2026 (4 unplanned, 1,044 min): DT-260907-0534 pulper rotor rectifier 201, WO 26108148, RCFA-SM-26-027 ([[pulper-rotor]]). DT-260920-0561 2nd press drive bearing 412, WO 26108393, RCFA-SM-26-028 ([[2nd-press-drive]]; the largest unplanned stop of the window; 4th largest in the log after 570, 450 and 441 min, computed). DT-261002-0576 3rd section rotary joint 144, WO 26108638, no RCFA ([[3rd-section-rotary-joint]]). DT-261014-0589 dryer driveshaft 287, WO 26108981, RCFA-SM-26-029 ([[dryer-drive-lineup]]). [downtime DT-260907-0534 to DT-261014-0589]
- Planned rows in the same window (5, 1,898 min): outage OUT-2026-09-30 1,200 and four short jobs of 133-216 min, all caught from a precursor; see [[planned-outage-history]]. 98 breaks (4,448 min) in the window: [[breaks-by-location]]. [downtime DT-260930-0573 to DT-261029-0626]
- Window total 107 rows, 7,390 min (4,448 break + 1,044 unplanned + 1,898 planned; computed); no slowdown rows. [downtime DT-260901-0523 to DT-261030-0629]
- RCFA ids on the window's unplanned rows: SM-26-027, -028, -029 (the one without is the 3rd section rotary joint leak); full RCFA list in [[rcfa-register]].
- RCFA ids in this log run SM-25-001 to SM-26-026 (26 ids), listed in order of event date; RCFA status and actions: tool rcfa_status; see [[rcfa-register]].
