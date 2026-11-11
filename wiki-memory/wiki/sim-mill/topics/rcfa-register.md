---
name: rcfa-register
description: All 29 RCFAs RCFA-SM-25-001 to RCFA-SM-26-029 (Nov 2025-Oct 2026) in one table of lines - event date, asset, cause, downtime, loss, status; which are open; tool rcfa_status
type: topic
aliases: ["RCFA list", "RCFA status", "open RCFAs", "root cause failure analysis register"]
---
## How to get it
- tool: rcfa_status (status, actions, owners); downtime_summary group=equipment gives the stop minutes. Lead is Mei Fairbanks except clothing/process cases led by Tobias Renner. Open actions in [[open-actions]].
- 29 RCFAs: 18 closed, 11 open ("Open - actions pending") as of 2026-11-10 (computed from the batch).
- Header values (downtime h / loss t) come from each RCFA record.

## Closed (event date, asset, cause, h / t, closed)
- [RCFA-SM-25-001] 2025-11-19 [[couch-roll]] bearing, 4 / 126, closed 2026-01-21.
- [RCFA-SM-25-002] 2025-12-24 [[dryer-drive-lineup]] bearing, 7.3 / 228, closed 2026-02-23.
- [RCFA-SM-25-003] 2025-12-30 [[vacuum-pump]] vanes worn, seal water starved, 4.2 / 129, closed 2026-02-01.
- [RCFA-SM-26-004] 2026-01-02 [[fan-pump]] impeller cavitation, 6 / 187, closed 2026-02-05.
- [RCFA-SM-26-005] 2026-01-22 [[pulper-rotor]] bearing, 5 / 157, closed 2026-03-22.
- [RCFA-SM-26-008] 2026-03-06 [[ref-2-refiner-motor]] winding, 4.6 / 142, closed 2026-05-07.
- [RCFA-SM-26-009] 2026-03-11 [[hood-supply-fan]] bearing, 4.7 / 147, closed 2026-03-28.
- [RCFA-SM-26-010] 2026-03-18 [[2nd-press-drive]] bearing, 3.9 / 120, closed 2026-05-21.
- [RCFA-SM-26-011] 2026-03-22 [[dryer-drive-lineup]] rectifier, 3.7 / 116, closed 2026-04-04.
- [RCFA-SM-26-012] 2026-04-10 [[4th-section-rotary-joint-ds]] syphon loose, can flooded, 3 / 94, closed 2026-05-21.
- [RCFA-SM-26-018] 2026-06-24 [[dryer-drive-lineup]] bearing, 5 / 153, closed 2026-08-18.
- [RCFA-SM-26-019] 2026-07-06 [[pulper-rotor]] rectifier, 3.9 / 121, closed 2026-07-21.
- [RCFA-SM-26-020] 2026-07-11 [[headbox]] slime break-off, 5.2 / 163, closed 2026-08-02.
- [RCFA-SM-26-021] 2026-07-18 [[pulper-rotor]] drive IGBT trip, 4.6 / 144, closed 2026-08-22.
- [RCFA-SM-26-022] 2026-07-20 [[pulper-rotor]] bearing, 5.9 / 184, closed 2026-09-22.
- [RCFA-SM-26-023] 2026-07-21 [[p1-felt-top]] plugged, 5.8 / 179, closed 2026-08-27.
- [RCFA-SM-26-025] 2026-08-14 [[p1-felt-bottom]] plugged, 3.4 / 106, closed 2026-09-25.
- [RCFA-SM-26-027] 2026-09-07 [[pulper-rotor]] rectifier, 3.4 / 104, closed 2026-09-26.

## Open (with remaining actions as of 2026-11-10)
- [RCFA-SM-26-006] 2026-02-09 [[form-bottom]] fabric hole, 9.5 / 294; SM-0059 wad detector camera overdue. See [[forming-fabric-damage]].
- [RCFA-SM-26-007] 2026-02-15 [[2nd-press-drive]] motor winding, 4.3 / 133; SM-0064 MCC cooling check overdue. See [[motor-winding-insulation-failure]].
- [RCFA-SM-26-013] 2026-04-28 [[pulper-rotor]] bearing, 4.5 / 139; SM-0124 grease review overdue.
- [RCFA-SM-26-014] 2026-05-12 [[p2-felt-bottom]] plugged, 5.3 / 166; SM-0133 felt vendor review overdue.
- [RCFA-SM-26-015] 2026-05-13 [[p1-felt-bottom]] plugged, 3.6 / 112; SM-0135 Uhle shift check overdue.
- [RCFA-SM-26-016] 2026-05-19 [[p2-felt-top]] unplanned change, 7.5 / 232; SM-0138 Uhle on Bonvoy watch list overdue.
- [RCFA-SM-26-017] 2026-05-28 [[hood-exhaust-fan]], 5.1 / 159; SM-0145 belts on PM overdue.
- [RCFA-SM-26-024] 2026-08-05 [[p1-felt-top]] HP shower nozzles plugged, 2.8 / 88; SM-0195 strainer on clean list overdue.
- [RCFA-SM-26-026] 2026-08-26 [[dryer-drive-lineup]] bearing, 6.8 / 211; SM-0207 grease review overdue.
- [RCFA-SM-26-028] 2026-09-20 [[2nd-press-drive]] bearing, 6.9 / 213; SM-0226 sensor overdue, SM-0227 not started (due 2026-11-23).
- [RCFA-SM-26-029] 2026-10-14 [[dryer-drive-lineup]] driveshaft u-joint, 4.8 / 148; SM-0239 weekly lube route overdue.

## Patterns
- Bearing between routes, 9 RCFAs: [[bearing-failed-between-vibration-routes]]. Rectifier, 3: [[rectifier-fault-mcc-dc-bus]]. Press felt/shower, 6: [[press-felt-plugging]]. Motor winding, 2: [[motor-winding-insulation-failure]]. Hood fans, 2: [[hood-fan-failures]].
- Assets with the most RCFAs: [[pulper-rotor]] 6, [[dryer-drive-lineup]] 5, [[2nd-press-drive]] 3 (computed counts).
- Categories: Equipment failure, Clothing (fabric/felt cases 006, 014, 015, 016, 023, 025), Process (020, 024), Electrical (021). [RCFA-SM-26-021]
- Some "open" RCFAs have all but one action complete; an RCFA stays open while any action is In progress or Not started.
