---
name: hood-fan-failures
description: Failure mode - 4th dryer section hood fans (supply fan bearing Mar 2026, exhaust fan bearing and belt May 2026); vibration monitoring gap; repeated BUS "bearing noisy" follow-ups
type: failure-mode
aliases: ["fog fan down", "hood supply fan", "hood exhaust fan", "hood fan bearing"]
---
## Events
- 2026-03-11 [[hood-supply-fan]] "Fog fan down", 4.7 h, 147 t; root cause "Hood supply fan bearing failure"; contributing "No vibration monitoring on the fan"; RCFA-SM-26-009 closed 2026-03-28. [RCFA-SM-26-009]
- 2026-05-28 [[hood-exhaust-fan]], 5.1 h, 159 t; root cause "Hood exhaust fan bearing and belt failure"; contributing "Exhaust temperature rose for weeks; belts not on the PM"; Pi PM1:HOOD_EXH_TEMP, PM1:REEL_MOIST about 12 days before; RCFA-SM-26-017 OPEN. [RCFA-SM-26-017]

## Actions
- Add the hood fans to the vibration route (Gloria Nakamura) SM-0084 done 2026-03-28. [Action SM-0084]
- Add hood exhaust fan belts to the monthly PM: SM-0145 due 2026-06-19, In progress, OVERDUE. [Action SM-0145]
- Vibration point on Hood exhaust fan: SM-0146 done 2026-07-10. [Action SM-0146]

## Warning signs before the failures
- Hood supply fan "bearing noisy" BUS follow-ups ran Feb 2026 to Oct 2026 (7 actions, see [[bus-follow-up-actions]]), including SM-0069 (2026-02-21) and SM-0071 before the Mar 11 failure. [Action SM-0069] [Action SM-0071]
- The last one, SM-0238 (created 2026-10-16, completed 2026-10-17), is after the vibration-route action was done. [Action SM-0238]
- Hood exhaust humidity high: SM-0210 (completed 2026-09-08) and SM-0248 (due 2026-11-21, Not started). [Action SM-0210] [Action SM-0248]
- Shift reports 2026-02-22 to 02-26 (8 shifts) carry "Hood supply fan: bearing noisy -> grease and monitor", the last handover appearance 13 days before the Mar 11 failure; details on [[hood-supply-fan]]. [Shift Report PM1-SHIFT-2026-02-22-D] [Shift Report PM1-SHIFT-2026-02-26-N]
- Related failure mode: [[bearing-failed-between-vibration-routes]].

## Shift reports Mar 2026 (before and after the supply fan stop; detail [[hood-supply-fan]])
- Handovers 03-09 Day, 03-09 Night and 03-10 Day carried "Hood exhaust fan: hood exhaust humidity high → check exhaust fan damper"; the supply fan then tripped at 00:39 on 03-11 (shift clock). The humidity item names the exhaust fan, not the supply fan; the link between them is not stated. [Shift Report PM1-SHIFT-2026-03-09-D] [Shift Report PM1-SHIFT-2026-03-10-N]
- After the stop: "Hood supply fan: bearing noisy → grease and monitor" 03-31 Day/Night (BUS SM-0103). [Shift Report PM1-SHIFT-2026-03-31-D] [Action SM-0103]

## Downtime log events
- 2026-03-11 04:39 4th dryer section Hood supply fan, cause "Fog fan down", 284 min, WO 26103507, RCFA-SM-26-009: "The fog remediation fan tripped! The machine keeps running, but the machine room is filling with wet-end fog." [downtime DT-260311-0197] [Shift Report PM1-SHIFT-2026-03-10-N]
- 2026-05-28 13:11 4th dryer section Hood exhaust fan failure, 307 min, WO 26105509, RCFA-SM-26-017: "hood exhaust temperature up and moisture drifting for 23 days before" (RCFA states about 12 days of Pi trend; both kept). [downtime DT-260528-0354]
- Tool: downtime_events equipment="Hood supply fan" or "Hood exhaust fan".

## Work order trail Feb-Jun 2026 (work-orders-2)
- Fog fan down WO 26103507 (03-11) and exhaust fan failure WO 26105509 (05-28); in between 6 supply fan "bearing noisy" WOs and 4 exhaust "humidity high" WOs, plus monthly "Hood fan belt check" PM WOs. Detail and ids: [[hood-supply-fan]], [[hood-exhaust-fan]], [[work-orders-feb-jun-2026]]. [WO 26103507] [WO 26105509]
