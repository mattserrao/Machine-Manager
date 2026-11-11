---
name: hood-exhaust-fan
description: Hood exhaust fan (asset 00072756, 4th dryer section) - bearing and belt failure 2026-05-28 (RCFA-SM-26-017 open, belts-on-PM action overdue); hood exhaust humidity follow-ups
type: equipment
aliases: ["asset 00072756", "hood exhaust", "PM1:HOOD_EXH_TEMP", "hood exhaust fan belts"]
---
- 2026-05-28 failure, 5.1 h, 159 t, "Hood exhaust fan bearing and belt failure"; Pi PM1:HOOD_EXH_TEMP and PM1:REEL_MOIST trend about 12 days before; RCFA-SM-26-017 OPEN; lead Mei Fairbanks. [RCFA-SM-26-017]
- SM-0145 add hood exhaust fan belts to the monthly PM (Gloria Nakamura), due 2026-06-19, In progress, OVERDUE. [Action SM-0145]
- SM-0146 vibration point on the fan, done 2026-07-10. [Action SM-0146]
- BUS: SM-0144 failure follow-up (completed 2026-06-03); "Hood exhaust humidity high" SM-0210 (completed 2026-09-08) and SM-0248 (Fenna Gallagher, due 2026-11-21, Not started). [Action SM-0144] [Action SM-0210] [Action SM-0248]
- See [[hood-fan-failures]], [[hood-supply-fan]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO 26109198 "Hood fan belt check" (asset 00072756, preventive, completed 2026-10-31, 1.7 h). [WO 26109198]

## What crews saw in Nov 2025 (shift reports; 6 months before the May 2026 failure)
- "Hood exhaust fan: hood exhaust humidity high → check exhaust fan damper" on 2025-11-17 (Day and Night); "→ damper linkage repaired" on 11-18 (Day and Night). [Shift Report PM1-SHIFT-2025-11-17-D] [Shift Report PM1-SHIFT-2025-11-18-D]
- Humidity was handled as a damper problem; no bearing or belt item for this fan appears in the Nov 2025 reports. [Shift Report PM1-SHIFT-2025-11-18-N]
- See [[shift-handover-signals-2025-11]], [[hood-fan-failures]].

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- "Hood exhaust humidity high": 5 issues, Fenna Gallagher, "Check exhaust fan damper" then "Damper linkage repaired": 2025-11-16 (WO 26100735), 12-01, 2026-01-29 (7 days), 03-08 (WO 26103388), 04-06 (WO 26104179). All five precede the 2026-05-28 bearing and belt failure and were fixed at the damper linkage. [BUS 2025-11-16 issue 3aee4c4852d28461] [BUS 2026-04-06 issue 60d7f23170bde803]

## Keel vibration route (reports library; see [[vibration-routes]])
- "Hood exhaust fan (portable)" readings in/s on the 12 routes: 0.069, 0.073, 0.063, 0.057, 0.073, 0.056, 0.059, 0.075, 0.074, 0.057, 0.058, 0.065 (10/14/2026); no alert; 0.059 on 05/13/2026, 15 days before the 05/28 failure [DOC KV-VR-251112 p.1] [DOC KV-VR-260513 p.1] [DOC KV-VR-261014 p.1]
- The failure was belt and bearing with a temperature trend (PM1:HOOD_EXH_TEMP) rather than a vibration rise; SM-0146 "Vibration point on Hood exhaust fan" (done 07/10/2026) although the portable point already existed on the routes [RCFA-SM-26-017] [Action SM-0146]

## Shift reports Dec 2025
- "Hood exhaust fan: hood exhaust humidity high → check exhaust fan damper" in handovers Dec 1 D to Dec 3 D (Dec 3: "damper linkage repaired"); before the 2026-05-28 failure, the same humidity subject recurs on BUS (SM-0210, SM-0248). [Shift Report PM1-SHIFT-2025-12-01-D] [Shift Report PM1-SHIFT-2025-12-03-D] [Action SM-0210]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072756, section 4)
- "Hood exhaust humidity high" corrective prio 3, INST Fenna Gallagher: 7 WOs completed 2026-06-06 [WO 26105838], 06-27 [WO 26106223], 06-27 [WO 26106300], 07-16 [WO 26106685], 07-24 [WO 26106762], 09-04 [WO 26107945], 09-06 [WO 26108057]; same symptom as the open Oct 2026 BUS issue below. No RCFA.
- "Hood fan belt check" preventive (1.5 h est, MECH Beatrix Hale): 4 WOs completed 2026-07-01, 07-31, 08-30, 09-30 (monthly), i.e. belts are checked monthly after the 05-28 belt failure. [WO 26106265] [WO 26107042] [WO 26107665] [WO 26108456]
- See [[hood-fan-failures]], [[work-orders-jun-sep-2026]].

## Asset and Pi tags (from equipment/Pi tag listing)
- Hood exhaust fan is asset 00072756 (kind fan, section sec-dryer-4). Pi tag: PM1:HOOD_EXH_TEMP hood exhaust temperature (degF). [equipment 00072756] [Pi tag PM1:HOOD_EXH_TEMP]

## BUS issues May-Sep 2026 (list in [[bus-issue-sheet]])
- 2026-05-28 exhaust fan failure 5.1 h, "hood exhaust temperature up and moisture drifting for 23 days before", WO 26105509, Gloria Nakamura, closed 05-31. [BUS 2026-05-28 .. BUS 2026-05-31 | issue 61439c7e8299997d]
- "Hood exhaust humidity high" (Fenna Gallagher, "Check exhaust fan damper" then "Damper linkage repaired"): 8 issues, 05-05 (WO 26104977), 05-30 (WO 26105544), 06-04 (WO 26105838), 06-10 (no WO), 06-23 (WOs 26106223, 26106300), 07-14 (WOs 26106685, 26106762; 13 days), 08-29 (WOs 26107945, 26108057; 11 days), 09-19 (7 days). The same damper linkage fix about every 2-4 weeks. [BUS 2026-05-05 .. BUS 2026-05-09 | issue 0b37b1dd73f72473] [BUS 2026-07-14 .. BUS 2026-07-24 | issue 8c1ddd48fecc6799] [BUS 2026-08-29 .. BUS 2026-09-06 | issue ef5217b951204afa]

## BUS issue Oct 2026
- Issue 3f1bc97ee9c0ad9c: hood exhaust humidity high, New 2026-10-31, Fenna Gallagher, "Check exhaust fan damper"; the only status at 10-31 (open); follow-up SM-0248. See [[bus-issues-2026-10-late]]. [BUS 2026-10-31]

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- Emergency WO 26105509 "Hood exhaust fan failure", 2026-05-28, MECH Beatrix Hale, est 15.3 h act 16.8 h: "hood exhaust temperature up and moisture drifting for 23 days before." RCFA-SM-26-017. [WO 26105509]
- 4 "Hood exhaust humidity high" WOs, INST Fenna Gallagher, type 1 prio 3, Closed (requested -> done, actual h): 26103388 (03-08 -> 03-12, 4.4), 26104179 (04-06 -> 04-08, 3.3), 26104977 (05-05 -> 05-09, 2.2), 26105544 (05-30 -> 05-31, 6.6); 16.5 h (computed). Requests about 29 days apart (03-08, 04-06, 05-05) then 05-30, two days after the failure. [WO 26103388] [WO 26104179] [WO 26104977] [WO 26105544]
- WO 26104977 (requested 05-05) is exactly 23 days before the 05-28 failure, matching the "moisture drifting for 23 days" note (computed from dates); the RCFA quotes only about 12 days of Pi trend. [WO 26104977] [WO 26105509] [RCFA-SM-26-017]
- Monthly PM "Hood fan belt check" (MECH, 1.5 h est): 26103164 (done 03-03), 26103934 (04-04), 26104725 (05-03), 26105432 (06-01). CONFLICT: RCFA-SM-26-017 action SM-0145 says belts are not on the PM, yet these monthly WOs exist before the 05-28 failure; the last one before it was completed 05-03, 25 days earlier. [WO 26104725] [Action SM-0145]
- Outage "Hood fan inspection" WOs are booked on the supply fan asset: [[hood-supply-fan]]. [WO 26103528]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Corrective WO 26100735 "Hood exhaust humidity high" (asset 00072756, type 1, prio 3, INST Fenna Gallagher, requested 2025-11-16, done 11-18, 3.3 h). [WO 26100735]
- Preventive "Hood fan belt check" (MECH, 1.7 h act), about monthly: 26100210 (done 2025-11-03), 26101001 (12-04), 26101743 (2026-01-03), 26102401 (02-01). [WO 26100210] [WO 26101001] [WO 26101743] [WO 26102401]
- See [[routine-pm-work-orders]], [[hood-fan-failures]].
