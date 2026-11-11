---
name: rectifier-fault-mcc-dc-bus
description: Failure mode - rectifier fault, MCC DC bus down; 3 RCFAs (dryer drive lineup, pulper rotor twice), root cause still "under review"
type: failure-mode
aliases: ["rectifier fault", "MCC DC bus down", "MCC-1 DC bus", "MCC-2 DC bus"]
---
## Events
- 2026-03-22 [[dryer-drive-lineup]] MCC-2 DC bus down, 3.7 h, 116 t; RCFA-SM-26-011, closed 2026-04-04. [RCFA-SM-26-011]
- 2026-07-06 [[pulper-rotor]] MCC-1 DC bus down, 3.9 h, 121 t; RCFA-SM-26-019, closed 2026-07-21. [RCFA-SM-26-019]
- 2026-09-07 [[pulper-rotor]] 3.4 h, 104 t; RCFA-SM-26-027, closed 2026-09-26. [RCFA-SM-26-027]
- Totals about 11 h and 341 t (computed from the three headers).

## BUS issue
- 2026-03-22 dryer drive lineup (asset 00072742): "MCC-2 DC bus down: rectifier fault, dryer drive lineup and everything on the bus stopped", 3.7 h, WO 26103836, Gloria Nakamura, closed 2026-03-25. [BUS 2026-03-22 issue c98cfe8be4bebedc] See [[dryer-drive-lineup]], [[bus-sheet-issues-2025-11-to-2026-05]].

## Cause and actions
- Root cause on all three: "Rectifier fault (MCC DC bus down)"; contributing: "Under review". [RCFA-SM-26-011] [RCFA-SM-26-019] [RCFA-SM-26-027]
- Only action each time: "Review with the vendor" (Gloria Nakamura), completed 2026-04-04, 2026-07-21, 2026-09-26. [Action SM-0098] [Action SM-0172] [Action SM-0216]
- No corrective action beyond the vendor review is filed in this batch; the repeat on the pulper rotor (Jul, Sep) came after the first review. [Action SM-0172] [Action SM-0216]
- BUS follow-ups: SM-0094 (dryer drive lineup, Mar 22) and SM-0169 (pulper, Jul 6), both completed. [Action SM-0094] [Action SM-0169]
- Related electrical event on the pulper: drive IGBT trip, RCFA-SM-26-021 ([[pulper-rotor]]).
- Tool: rcfa_status; downtime_summary group=equipment. See [[rcfa-register]].

## Downtime log events
- 2026-03-22 20:15 2nd dryer section Dryer drive lineup, 224 min, WO 26103836, RCFA-SM-26-011: "MCC-2 DC bus down: rectifier fault, dryer drive lineup and everything on the bus stopped." Grade 34 Super, crew D. [downtime DT-260322-0219] [Shift Report PM1-SHIFT-2026-03-22-D]
- 2026-07-06 13:00 Stock prep Pulper rotor, 235 min, WO 26106545, RCFA-SM-26-019: "MCC-1 DC bus down: rectifier fault, pulper rotor and everything on the bus stopped." Grade 34 Super, crew C. [downtime DT-260706-0424] [Shift Report PM1-SHIFT-2026-07-06-D]
- 2026-09-07 06:45 Stock prep Pulper rotor, 201 min, WO 26108148, RCFA-SM-26-027: "MCC-1 DC bus down: rectifier fault, pulper rotor and everything on the bus stopped." Grade 34 Super, crew C. [downtime DT-260907-0534] [Shift Report PM1-SHIFT-2026-09-06-N]
- Three rectifier stops in the downtime log total 660 min (224 + 235 + 201); the Sep event is the second on MCC-1 (after 07-06). [downtime DT-260322-0219] [downtime DT-260706-0424] [downtime DT-260907-0534]
- What crews saw around 2026-03-22 (shift reports; see [[shift-handover-signals-2026-03]]): no electrical, MCC or drive item in any handover 03-01 to 03-21; the DC bus fault came without a logged precursor. [Shift Report PM1-SHIFT-2026-03-21-N]
- The day: 03-22 Day, crew D (Wynn Castellano): "Dryer drive lineup: rectifier fault (MCC DC bus down) at 16:15, 3.7 h down. Area barricaded while maintenance worked. WO 26103836"; stop line "Unplanned 224 min"; 286 t, sheet on 80.8%. CONFLICT on time: shift report 16:15, downtime log 20:15 (same 4 h offset as other March stops). [Shift Report PM1-SHIFT-2026-03-22-D] [downtime DT-260322-0219]
- Earlier that shift (06:01) a 33 min break at dryer can 6 (2nd dryer section, the section of the dryer drive lineup), 10 h before the fault; grade changes to 31# and 34 Super in the same shift. The shift report does not link the two. [Shift Report PM1-SHIFT-2026-03-22-D]
- Handovers after: 03-23 Day and Night "MCC-2 DC bus down: rectifier fault, dryer drive lineup and everything on the bus stopped. → repaired; running"; 03-24 Day and Night "→ watching after restart". [Shift Report PM1-SHIFT-2026-03-23-D] [Shift Report PM1-SHIFT-2026-03-24-D]
- WO labour hours on the two pulper events (not downtime): WO 26106545 (2026-07-06) 11.8 h est / 13 h act; WO 26108148 (2026-09-07) 10.1 h est / 11.1 h act; both Emergency prio 1, MECH Beatrix Hale. Between them a pulper drive trip WO 26106867 (2026-07-18) was done by E&I Omar Szabo. [WO 26106545] [WO 26108148] [WO 26106867]
- All three events were on 34 Super. None of the three log rows gives a precursor lead time (no "days before" text). [downtime DT-260322-0219] [downtime DT-260706-0424] [downtime DT-260907-0534]

## Work orders Feb-Jun 2026 (work-orders-2)
- WO 26103836 "Rectifier fault (MCC DC bus down): Dryer drive lineup", type 3 Emergency prio 1, 2026-03-22, MECH Beatrix Hale, est 11.2 h act 12.3 h: "MCC-2 DC bus down: rectifier fault, dryer drive lineup and everything on the bus stopped." RCFA-SM-26-011. [WO 26103836]
- Electrical PM on that lineup before and after: monthly "MCC thermography" (E&I Omar Szabo, 3 h est) WO 26103045 (done 02-26), 26103787 (03-28, six days after the fault), 26104473 (04-27), 26105320 (05-27); outage "MCC lineup clean and torque check" WO 26103556 ([[out-2026-04-15]], 8/8.8 h) and WO 26104613 ([[out-2026-05-27]], 6/6.6 h). [WO 26103045] [WO 26103787] [WO 26103556] [WO 26104613]
- See [[dryer-drive-lineup]], [[emergency-work-orders-feb-jun-2026]].
