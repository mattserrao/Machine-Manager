---
name: bus-follow-up-actions
description: The 135 "Follow up:" actions raised from the BUS sheet (Nov 2025-Oct 2026) grouped by subject with counts, ids and owners; recurring nuisance items that never became RCFAs; read to spot repeats and what is open
type: topic
aliases: ["BUS follow-ups", "BUS sheet actions", "Follow up actions", "recurring BUS items"]
---
## BUS issues behind the follow-ups
- The BUS issues themselves (status trail, WOs, owners) are in [[bus-sheet-issues-2025-11-to-2026-05]] (2025-11-01 to 2026-05-03), [[bus-issue-sheet]] (2026-04-24 onward) and [[bus-issues-2026-10-late]]; per-subject pages: [[dryer-can-13]], [[dryer-can-4]], [[machine-chest]], [[steam-header]], [[forming-hp-shower]], [[2nd-section-pv-fan]], [[reel-drive]], [[flat-boxes]], [[wire-guide]], [[stock-prep-recurring-issues]].

## How it works
- Each BUS sheet item gets an action "Follow up: <item> (<asset>)" in bucket "BUS follow-ups", created the day of the BUS sheet ("From the BUS sheet, <Mon dd>"), due 1 to 3 weeks later. [Action SM-0002]
- tool: overdue_actions (open ones); search_records for history. Open BUS follow-ups as of 2026-11-10: SM-0243, SM-0244, SM-0245, SM-0246, SM-0248 ([[open-actions]]).
- All other BUS follow-ups in this batch are Completed (some late, listed in [[open-actions]]).

## Recurring subjects (count of follow-ups, ids, owner)
- Dryer can 13 condensate flooding (cold can): 9; SM-0038, 0060, 0090, 0108, 0113, 0122, 0219, 0222, 0232 (Jan-Oct 2026); Eamon Takahashi. Most repeated item; no RCFA. [Action SM-0038] [Action SM-0232]
- Machine chest level control hunting: 7; SM-0035, 0055, 0058, 0100, 0178, 0236 plus SM-0083 (dye trouble, machine slowed 1.1 h); Fenna Gallagher / Ingrid Solberg. [Action SM-0035] [Action SM-0236]
- Hood supply fan bearing noisy: 7; SM-0069, 0071, 0103, 0120, 0140, 0157, 0238; Gloria Nakamura; see [[hood-supply-fan]]. [Action SM-0238]
- Dryer can 4 doctor blade worn: 6; SM-0003, 0008, 0047, 0067, 0137, 0155; Gloria Nakamura. [Action SM-0155]
- Winder slitter dust: 6; SM-0016, 0018, 0041, 0143, 0204, 0245 (open, In progress, due 2026-11-05); Dolores Vance. [Action SM-0245]
- Forming HP shower oscillator stalling: 6; SM-0005, 0039, 0209, 0228, plus open SM-0244 (due 2026-11-18, Not started) and SM-0246 (due 2026-11-06, Not started); Gloria Nakamura. Two open at once. [Action SM-0244] [Action SM-0246]
- 2nd section PV fan amps low: 6; SM-0087, 0096, 0101, 0109, 0114, 0127 (Mar-May 2026); Gloria Nakamura. [Action SM-0127]
- Reel drive turn-up missed twice on nights: 6; SM-0029, 0148, 0158, 0161, 0188, 0203; Desmond Pike; see [[reel-drum]]. [Action SM-0203]
- 1st press top roll doctor chatter: 6; SM-0021, 0075, 0085, 0089, 0175, 0213; Gloria Nakamura; see [[p1-roll-top]]. [Action SM-0213]
- 2nd press bottom felt guide hunting: 6; SM-0050, 0070, 0082, 0214, 0224, 0243 (open); Sunniva Brooks; see [[p2-felt-bottom]]. [Action SM-0243]
- 1st press top felt conditioning low: 5 (SM-0073, 0099, 0197, 0231, 0237) plus plugging follow-ups; Sunniva Brooks; see [[p1-felt-top]].
- HD cleaner reject valve sticking: 5; SM-0049, 0077, 0147, 0184, 0191; Fenna Gallagher. [Action SM-0191]
- Fan pump packing leaking: 4; SM-0020, 0078, 0097, 0150; see [[fan-pump]].
- Flat box cover wear at the TS edge: 4; SM-0002, 0116, 0160, 0221; Curtis Lindahl. [Action SM-0221]
- Steam header pressure dips at grade changes: 4; SM-0149, 0166, 0180, 0217; Eamon Takahashi. [Action SM-0217]
- Dryer can 6 / sheet breaks: "4 or 5 sheet breaks in 24 h, mostly at the dryer (Dryer can 6)" SM-0046, 0051, 0074, 0154; Tobias Renner. [Action SM-0154]
- 2nd press top felt sheet breaks 4-6 in 24 h, mostly at the press: SM-0019, 0115, 0131, 0173; see [[p2-felt-top]]. Reel drum sheet breaks: SM-0153.
- Winder telescoping rolls: 3 (SM-0088, 0211, 0220); Ragger rope breaking: 3 (SM-0007, 0024, 0176); Pulper rotor amps swinging with bale feed: 3 (SM-0023, 0042, 0072; see [[pulper-rotor]]); Couch roll seal strip water low: 3 (see [[couch-roll]]); Vacuum pump seal water temperature high: 3 (see [[vacuum-pump]]); Thickener shower nozzles plugging: 3 (SM-0107, 0192, 0202).
- Hood exhaust humidity high: 2 (SM-0210; SM-0248 open); LC cleaner tips plugging: 2 (SM-0037, 0062); Fine screen DP creeping up: 2 (SM-0118, 0235); Coarse screen rejects high SM-0129; Headbox edge flow streak at the FS SM-0233 ([[headbox]]).
- Follow-ups of failure events: SM-0014 (reel drum DS bearing), SM-0053/0054 ([[forming-fabric-damage]]), SM-0094 ([[rectifier-fault-mcc-dc-bus]]), SM-0104 (press shower nozzles), SM-0125, SM-0130, SM-0179 ([[press-felt-plugging]]), SM-0144 ([[hood-exhaust-fan]]), SM-0169 (rectifier, pulper), SM-0215 (reel drum DS bearing vibration rising from Bonvoy).

## Issues behind the follow-ups
- The sheet issues (with ids, WOs, owners, closing text) for Apr-Oct 2026 are in [[bus-issue-sheet]]; they are issues, the follow-ups above are the Actions raised from them.

## Observations (computed)
- Subjects raised 6 or more times without an RCFA: Dryer can 13, Machine chest, Dryer can 4, Winder slitters, Forming HP shower oscillator, 2nd section PV fan, Reel drive, 1st press top roll, 2nd press bottom felt guide. A related Reliability action SM-0230 exists only for 3rd section rotary joint leaks ([[open-actions]]).
- Counts are by subject text in the batch and may be off by one where the subject wording varies.

## Issue-level detail
- Daily status trail, issue ids and WOs for BUS issues 2026-10-16 to 10-31 (27 issues, 6 open at 10-31): [[bus-issues-2026-10-late]].
