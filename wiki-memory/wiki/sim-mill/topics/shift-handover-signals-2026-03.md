---
name: shift-handover-signals-2026-03
description: What PM1 crews wrote in the March 2026 shift reports (62 shifts, 03-01 to 03-31) before and after the March stops: which handover items were early signs, which stops had none, recurring handover items and their BUS follow-up ids
type: topic
aliases: ["March 2026 shift reports", "shift reports 2026-03", "handover signals March"]
---
## Scope and tool
- Source: shift reports PM1-SHIFT-2026-03-01-D to PM1-SHIFT-2026-03-31-N (tool: shift_reports). Each has tonnes, sheet-on %, "Stops and breaks" lines (with WO for unplanned stops) and a four-item "Handover" list carried until fixed. [Shift Report PM1-SHIFT-2026-03-01-D] [Shift Report PM1-SHIFT-2026-03-31-N]
- Crews: A Harlan Mbeki, B Lucille Brandt, C Rafael Okonkwo, D Wynn Castellano (shift leads). [Shift Report PM1-SHIFT-2026-03-02-D]
- Clock note: shift-report times of the March stops are 4 h earlier than the downtime-log timestamps for the same events. [Shift Report PM1-SHIFT-2026-03-18-D] [downtime DT-260318-0207]

## Unplanned stops in March and whether the handovers warned
- 03-06 REF 2 refiner motor, 274 min, WO 26103346: no warning item 03-01 to 03-05. [[ref-2-refiner-motor]] [Shift Report PM1-SHIFT-2026-03-06-D]
- 03-11 (00:39) Hood supply fan "fog fan down", 284 min, WO 26103507: only "hood exhaust humidity high" (exhaust fan) 03-09/03-10 before. [[hood-supply-fan]] [Shift Report PM1-SHIFT-2026-03-10-N]
- 03-12 slowdown 67 min, Machine chest "dye trouble", WO 26103612: "level control hunting → tune LIC loop" ran 03-04 to 03-08 and again 03-28/29; fixed "back to full rate". [Shift Report PM1-SHIFT-2026-03-12-D] [Shift Report PM1-SHIFT-2026-03-08-N]
- 03-18 2nd press drive bearing, 232 min, WO 26103696: no warning item (route Alert 03-11 not in handovers). [[2nd-press-drive]] [Shift Report PM1-SHIFT-2026-03-18-D]
- 03-21 2nd press bottom felt blown, 142 min, WO 26103801: guide hunting flagged 03-12/13. [[press-felt-blows]] [Shift Report PM1-SHIFT-2026-03-21-D]
- 03-22 Dryer drive lineup rectifier fault, 224 min, WO 26103836: no warning item. [[rectifier-fault-mcc-dc-bus]] [Shift Report PM1-SHIFT-2026-03-22-D]
- 2026-04-02 (after the batch) 1st press top felt HP shower: flagged "felt looks wet coming out of the nip" from 03-25. [[p1-felt-top]] [Shift Report PM1-SHIFT-2026-03-25-D]
- Planned outage 03-04 (shutdown 06:00 per crews): [[out-2026-03-04]]. [Shift Report PM1-SHIFT-2026-03-04-D]

## Breaks as crews logged them (computed from the March stop lines)
- 2nd press top felt 20 breaks, 1,513 min; reel drum 10 breaks, 154 min; dryer cans 8 breaks, 312 min. See [[p2-felt-top]], [[reel-drum]], [[dryer-cans]], [[breaks-by-location]]. [Shift Report PM1-SHIFT-2026-03-18-N] [Shift Report PM1-SHIFT-2026-03-29-N]
- Worst shift: 03-18 Day, 225 t, sheet on 54.7% (bearing stop plus a 94 min press break); 03-10 Night 240 t (fog fan). [Shift Report PM1-SHIFT-2026-03-18-D] [Shift Report PM1-SHIFT-2026-03-10-N]

## Recurring handover items in March (item, dates, BUS follow-up in the register)
- Fine screens ΔP creeping up: 03-01 to 03-02 ("flush at the next grade change"); BUS family SM-0118, 0235. [Shift Report PM1-SHIFT-2026-03-02-D]
- 1st press top roll doctor chatter: 03-01/02, 03-14 to 03-15 (blade changed, chatter gone), 03-17 to 03-18, 03-21 to 03-22, 03-30 to 03-31 (same item open and "blade changed" at once); [[p1-roll-top]]. [Shift Report PM1-SHIFT-2026-03-15-D] [Shift Report PM1-SHIFT-2026-03-30-D]
- Vacuum pump seal water temperature high: 03-02/03, 03-12 to 03-14; [[vacuum-pump]].
- Machine chest level control hunting: 03-04 to 03-08, 03-28/29; BUS family SM-0100 etc. [Shift Report PM1-SHIFT-2026-03-28-D]
- HD cleaners reject valve sticking: 03-04 to 03-08, "instrument tech to stroke the valve"; LC cleaner tips plugging 03-03, 03-04, 03-20/21. [Shift Report PM1-SHIFT-2026-03-04-D] [Shift Report PM1-SHIFT-2026-03-20-D]
- Winder slitter dust: 03-04 to 03-09, 03-14 to 03-16, 03-26 to 03-28 ("changed"); winder telescoping rolls 03-10/11, 03-16/17, 03-24/25 ("taper adjusted"). [Shift Report PM1-SHIFT-2026-03-10-D] [Shift Report PM1-SHIFT-2026-03-25-D]
- Hood exhaust humidity high 03-09/10; fan pump packing leaking 03-09/10, 03-19/20, 03-25 to 03-27 ([[fan-pump]]); ragger rope breaking 03-09 to 03-10, 03-18 to 03-19. [Shift Report PM1-SHIFT-2026-03-09-D] [Shift Report PM1-SHIFT-2026-03-19-D]
- 2nd section PV fan amps low: 03-11, 03-15 to 03-17, 03-25 to 03-26, 03-30 to 03-31 ("belts tensioned" / "check belts"); BUS SM-0087, 0096, 0101, 0109 etc. [Shift Report PM1-SHIFT-2026-03-17-D] [Shift Report PM1-SHIFT-2026-03-31-D]
- Forming HP shower oscillator stalling: 03-14 to 03-16, "check oscillator drive", not closed in March; BUS family SM-0005, 0039, ... ([[press-hp-showers]], [[bus-follow-up-actions]]). [Shift Report PM1-SHIFT-2026-03-14-D] [Shift Report PM1-SHIFT-2026-03-16-N]
- Thickener shower nozzles plugging 03-23 to 03-24 ("cleaned"); couch roll seal strip water low 03-01, 03-17/18 ([[couch-roll]]); pulper rotor amps swinging 03-01 ([[pulper-rotor]]); dryer can 13 cold can ([[syphon-failure]]); dryer can 4 doctor blade worn 03-05 to 03-07 and later ([[dryer-cans]]); reel spool bar damage 03-07/08 ([[reel-drum]]). [Shift Report PM1-SHIFT-2026-03-23-D] [Shift Report PM1-SHIFT-2026-03-24-D]
- Flat box cover wear at the TS edge: 03-21 "inspect at the next outage", 03-22 "added to outage scope" ([[out-2026-04-15]]). [Shift Report PM1-SHIFT-2026-03-22-D]
- Hood supply fan bearing noisy 03-31 ([[hood-supply-fan]]). [Shift Report PM1-SHIFT-2026-03-31-D]

## Reading rule
- Handover items are carried unchanged for 2-6 shifts and then replaced; "no item in handovers" means not in the four lines carried, not that nothing was said in the shift notes. Related months: [[shift-handover-signals-2025-11]], [[precursor-lead-times]].
