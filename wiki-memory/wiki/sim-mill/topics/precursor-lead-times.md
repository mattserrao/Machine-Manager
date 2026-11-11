---
name: precursor-lead-times
description: How many days of warning the downtime log gives before each unplanned failure (bearing vibration, vacuum, syphon differential, Uhle vacuum, HP shower plugging) and how this differs from the RCFA Pi lead times; read when asked "was it detectable / how early"
type: topic
aliases: ["days before failure", "lead time", "early warning", "found on the route", "bonvoy lead time", "not caught on the route"]
---
## Lead times stated in the downtime log (days before the stop)
- Bearing vibration rising (Bonvoy): dryer drive lineup 35 (DT-251224-0083), pulper rotor 31 (DT-260122-0130), pulper rotor 43 (DT-260428-0277), dryer drive lineup 41 (DT-260624-0405), pulper rotor 35 (DT-260720-0461), dryer drive lineup 20 (DT-260826-0513). [downtime DT-251224-0083] [downtime DT-260122-0130] [downtime DT-260428-0277] [downtime DT-260624-0405] [downtime DT-260720-0461] [downtime DT-260826-0513]
- "Not caught on the route" (no precursor stated): couch roll, reel drum DS bearing, 2nd press drive bearing. [downtime DT-251119-0024] [downtime DT-251124-0032] [downtime DT-260318-0207]
- Vacuum pump (couch vacuum falling, pump at full speed): 33 days. [downtime DT-251230-0089]
- Fan pump (flow and headbox pressure dipping in bursts): 16 days. [downtime DT-260102-0094]
- Syphon differential falling: 22 days (DT-251231-0091, DT-260410-0245). [downtime DT-251231-0091] [downtime DT-260410-0245]
- Press shower nozzles plugging: 25, 14, 24 and 27 days. [downtime DT-260207-0157] [downtime DT-260401-0236] [downtime DT-260630-0417] [downtime DT-260805-0485]
- Uhle vacuum climbing and press solids falling (felt plugged): 16, 26, 21, 19 days. [downtime DT-260512-0322] [downtime DT-260513-0327] [downtime DT-260721-0462] [downtime DT-260814-0496]
- Hood exhaust temperature up and moisture drifting: 23 days. [downtime DT-260528-0354]

## Caught before failure (planned instead of unplanned)
- Bearing change on the vibration route 2026-02-04 (found Feb 03). [downtime DT-260204-0151]
- Press felt chemical wash 2026-02-21 (found Feb 18). [downtime DT-260221-0177]
- Rotary joint / syphon repair 2026-06-26 (found Jun 24). [downtime DT-260626-0408]
- Of 22 events with a stated trend (19 unplanned stops, 3 planned jobs), only the 3 planned jobs were caught in time; the 19 others reached an unplanned stop. [downtime DT-260204-0151] [downtime DT-260221-0177] [downtime DT-260626-0408]

## What the crews wrote before the failure (January 2026 shift reports; tool: shift_reports)
- Pulper rotor: first "bearing sounds rough on rounds" note 2026-01-08, 14 days before the 01-22 failure; noted on 14 shifts in all; no inspection noted. Log lead time 31 d, RCFA 15 d, Keel route alert 01-14 (8 d). See [[pulper-rotor]]. [Shift Report PM1-SHIFT-2026-01-08-D] [Shift Report PM1-SHIFT-2026-01-22-D]
- 2nd press bottom felt: Uhle vacuum climbing / press solids falling in the handover from 2026-01-14, 7 days before the planned change; WO 26102149 raised 01-16; the felt changed at the outage, no stop. See [[p2-felt-bottom]]. [Shift Report PM1-SHIFT-2026-01-14-D] [Shift Report PM1-SHIFT-2026-01-16-D]
- Hood supply fan: "bearing noisy" 01-18 and 01-24, cleared by greasing; failure 46 days later. See [[hood-supply-fan]]. [Shift Report PM1-SHIFT-2026-01-18-D]
- Fan pump, vacuum pump, 2nd section syphon: the failures (12-30, 01-01, 01-02) are before or at the start of the batch, so only the post-failure trend text appears. See [[fan-pump]], [[vacuum-pump]], [[syphon-failure]]. [Shift Report PM1-SHIFT-2026-01-01-D] [Shift Report PM1-SHIFT-2026-01-03-D]
- 3rd section rotary joint 01-06: no crew warning in the preceding reports. See [[3rd-section-rotary-joint]]. [Shift Report PM1-SHIFT-2026-01-05-D]

## What the crews wrote before the March 2026 stops (shift reports; tool: shift_reports; detail [[shift-handover-signals-2026-03]])
- REF 2 motor (03-06), 2nd press drive bearing (03-18), hood supply fan (03-11), dryer drive rectifier fault (03-22): no crew warning on the asset in the preceding handovers (only 2nd press top felt breaks, and "hood exhaust humidity high" 03-09/03-10 before the supply fan stop). [Shift Report PM1-SHIFT-2026-03-05-D] [Shift Report PM1-SHIFT-2026-03-17-D] [Shift Report PM1-SHIFT-2026-03-10-D]
- 2nd press bottom felt blown (03-21): guide hunting flagged 03-12/13, 8 days earlier, cleared by cleaning the paddle. [Shift Report PM1-SHIFT-2026-03-12-D] [Shift Report PM1-SHIFT-2026-03-21-D]
- 1st press top felt HP shower (stop 2026-04-02): "felt looks wet coming out of the nip" first flagged 03-25 Day, 8 days before the stop; Uhle vacuum setpoint raised 0.5 inHg 03-26 to 03-28; the flag named UHLE_P1T_VAC and PRESS_SOLIDS on 03-27. The best crew-side catch in the March reports. [Shift Report PM1-SHIFT-2026-03-25-D] [Shift Report PM1-SHIFT-2026-03-27-D] [downtime DT-260401-0236]
- Pulper rotor (stop 04-28, log: vibration rising 43 days): only "rotor amps swinging" on 03-01 in March. [Shift Report PM1-SHIFT-2026-03-01-D]
- Shift report clock times of the March stops are 4 h earlier than the downtime log timestamps (06:30 vs 10:30, 00:39 vs 04:39, 12:02 vs 16:02, 16:15 vs 20:15). [Shift Report PM1-SHIFT-2026-03-18-D] [downtime DT-260318-0207]

## CONFLICT / basis note
- The RCFA headers give lead times about half those in the log for the same events (dryer drive 18 vs 35, pulper 15 vs 31 and 22 vs 43, fan pump 8 vs 16, vacuum pump 17 vs 33; see [[bearing-failed-between-vibration-routes]], [[fan-pump]], [[vacuum-pump]]). Keep both and name the source; the log text counts days from first trend, the RCFA from the Pi tag trend. [RCFA-SM-25-002] [downtime DT-251224-0083]
- Bonvoy tag details: [[bonvoy]], [[bonvoy-tag-catalog]].

## What the Dec 2025 shift reports said before the three December failures (crew notes, not Bonvoy)
- Dryer drive lineup bearing (stop Dec 24): "bearing sounds rough on rounds" first Dec 9 N, then 12 more shifts, 14 days of crew flags; no WO. [Shift Report PM1-SHIFT-2025-12-09-N] [Shift Report PM1-SHIFT-2025-12-22-D] See [[dryer-drive-lineup]].
- Vacuum pump (stop Dec 30): "couch vacuum down a bit" first Dec 7 N (23 days), seal water temperature high first Dec 17 D (13 days), strainer cleaned Dec 23. [Shift Report PM1-SHIFT-2025-12-07-N] [Shift Report PM1-SHIFT-2025-12-17-D] See [[vacuum-pump]].
- 2nd section rotary joint syphon (stop Dec 31): "section differential lower than normal" first Dec 22 N (9 days). [Shift Report PM1-SHIFT-2025-12-22-N] See [[2nd-section-rotary-joint-ds]].
- Fan pump (stop Jan 2): headbox pressure bouncing Dec 24 D (9 days). [Shift Report PM1-SHIFT-2025-12-24-D] See [[fan-pump]].
- 4th section broken syphon (stop Dec 2): no earlier crew flag in the Dec 1 reports. [Shift Report PM1-SHIFT-2025-12-01-D]
- In all four warned cases the crew flagged "not sure yet" for 9 to 23 days and no WO was raised before the stop; crew flags are an earlier signal than the RCFA Pi lead times for the vacuum pump and dryer drive.
