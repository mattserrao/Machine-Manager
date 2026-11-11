---
name: handover-watch-items-2025-12
description: Dec 2025 shift-report handover items that did not become stops (steam header, HD/LC cleaners, winder, headbox, wire guide, PV fan, machine chest, ragger) with first/last dates; read when asked what crews were watching in December 2025 or whether an item recurred
type: topic
aliases: ["December 2025 handover items", "shift report handover list", "shift handover watch items"]
---
## How to read
- Handover lines are "Equipment: problem → status" and carry over shift to shift until closed; tool: shift_reports (date range 2025-12-01 to 2025-12-31). Items tied to stops are on the equipment pages: [[dryer-drive-lineup]], [[vacuum-pump]], [[syphon-failure]], [[2nd-section-rotary-joint-ds]], [[fan-pump]], [[reel-drum]], [[p2-felt-top]].
- Shift report clock runs 5 h earlier than the downtime log for the Dec failure events (e.g. 19:23 vs 00:23); keep the source named.

## Items that recurred or stayed open
- Steam header: "pressure dips at grade changes → review boiler master response", on and off Dec 1 to Dec 31 (most persistent item); Dec 15 status "ramp rate changed" but the item returned Dec 21. See [[steam-pressure-by-grade]]. [Shift Report PM1-SHIFT-2025-12-01-D] [Shift Report PM1-SHIFT-2025-12-15-D] [Shift Report PM1-SHIFT-2025-12-31-D]
- Dryer can 13 condensate flooding (cold can) Dec 19 to Dec 31, no closing status: [[3rd-section-rotary-joint]]. [Shift Report PM1-SHIFT-2025-12-19-D]
- Winder drums "telescoping rolls → check winder tension tapers" Dec 5 to Dec 14 (Dec 6 "taper adjusted", back Dec 8 as "check"); winder slitters "dust → change slitter blades" Dec 5 to Dec 10 ("changed" Dec 6, back Dec 8, "changed" Dec 10). See [[winder-drums]]. [Shift Report PM1-SHIFT-2025-12-05-D] [Shift Report PM1-SHIFT-2025-12-06-D] [Shift Report PM1-SHIFT-2025-12-13-D]
- 2nd section PV fan "amps low → check belts" Dec 7 to Dec 11, no closing status in December. [Shift Report PM1-SHIFT-2025-12-07-D] [Shift Report PM1-SHIFT-2025-12-11-D]
- Machine chest "level control hunting → tune LIC loop" Dec 11 to Dec 13, no closing status. [Shift Report PM1-SHIFT-2025-12-11-D] [Shift Report PM1-SHIFT-2025-12-13-D]
- Wire guide "palm drifting to the TS": Dec 15 "regulator replaced"; returned Dec 21 to Dec 31 ("check guide air supply"; Dec 29 "regulator replaced" again). [Shift Report PM1-SHIFT-2025-12-15-D] [Shift Report PM1-SHIFT-2025-12-21-D] [Shift Report PM1-SHIFT-2025-12-29-D]
- LC cleaners "tips plugging" Dec 16 to Dec 24 (cleaned, then "clean tips"). [Shift Report PM1-SHIFT-2025-12-16-D] [Shift Report PM1-SHIFT-2025-12-24-D]
- HD cleaners "reject valve sticking" Dec 6 to Dec 8 (Dec 8 "valve rebuilt"), came back Dec 16. [Shift Report PM1-SHIFT-2025-12-06-D] [Shift Report PM1-SHIFT-2025-12-08-D] [Shift Report PM1-SHIFT-2025-12-16-D]
- Headbox "edge flow streak at the FS → adjust FS edge valve" Dec 9 to Dec 10; see [[headbox]]. [Shift Report PM1-SHIFT-2025-12-09-D]
- Ragger "rope breaking → re-thread the rope" Dec 25 to Dec 26; Dec 27 "rethreaded; new rope ordered". [Shift Report PM1-SHIFT-2025-12-25-D] [Shift Report PM1-SHIFT-2025-12-27-D]
- Hood supply fan "bearing noisy → grease and monitor" Dec 28 to Dec 29: [[hood-supply-fan]]. Hood exhaust humidity Dec 1 to Dec 3: [[hood-exhaust-fan]]. [Shift Report PM1-SHIFT-2025-12-28-D]
- 1st press doctor chatter Dec 18 to Dec 20: [[p1-roll-top]]. 2nd press bottom felt guide hunting Dec 20 to Dec 21: [[p2-felt-bottom]]. [Shift Report PM1-SHIFT-2025-12-18-D] [Shift Report PM1-SHIFT-2025-12-20-D]

## December production and break totals from the 62 shift reports
- Shifts with 0 t: Dec 10 D only (planned outage); the outage nights and restart are on [[out-2025-12-10]]. [Shift Report PM1-SHIFT-2025-12-10-D]
- Breaks listed in the reports: 2nd press top felt 16 (1,178 min), reel drum 18 (298), dryer cans 12 (478: can 11 x8, can 16 x2, can 3, can 6). Tool for the log version: downtime_summary group=equipment kind=break; see [[breaks-by-location]], [[dryer-cans]].
- Lowest output shifts: Dec 30 N 241 t (vacuum pump stop), Dec 24 D 196 t (dryer drive bearing aftermath), Dec 31 N 294 t (2nd section syphon). [Shift Report PM1-SHIFT-2025-12-30-N] [Shift Report PM1-SHIFT-2025-12-24-D] [Shift Report PM1-SHIFT-2025-12-31-N]
- Crews rotate A, B, C, D; Dec leads: A Harlan Mbeki, B Lucille Brandt, C Rafael Okonkwo, D Wynn Castellano. [Shift Report PM1-SHIFT-2025-12-01-D] [Shift Report PM1-SHIFT-2025-12-04-D] [Shift Report PM1-SHIFT-2025-12-08-N]
