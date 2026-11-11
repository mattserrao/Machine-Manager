---
name: forming-fabric-damage
description: Failure mode - forming fabric holed by a wad of stock off the headbox approach piping (2026-02-09, 9.5 h, 294 t); RCFA-SM-26-006 open on the wad detector camera (SM-0059 overdue)
type: failure-mode
aliases: ["forming fabric hole", "wad off the headbox approach", "wad detector camera"]
---
## Event
- 2026-02-09 forming fabric hole on [[form-bottom]] (asset 00072245), 9.5 h, 294 t, category Clothing, area Forming; RCFA-SM-26-006 opened 2026-02-10, OPEN, lead Tobias Renner. [RCFA-SM-26-006]
- Root cause: "A wad of stock off the headbox approach piping holed the forming fabric"; contributing: "Stock build-up in the approach piping; no wad detection at the breast roll". [RCFA-SM-26-006]
- BUS follow-ups: SM-0053 (5-inch hole at the TS from a wad off..., Gloria Nakamura, completed 2026-02-12) and SM-0054 (Tobias Renner, completed 2026-02-13). [Action SM-0053] [Action SM-0054]
- Largest single-event downtime and loss among the 29 RCFAs in this batch (9.5 h, 294 t; computed comparison, see [[rcfa-register]]).

## Shift reports Feb 2026 (what crews saw; tool: shift_reports)
- No early sign in the 02-01 to 02-08 reports: no forming-fabric or headbox item in any handover or note before the hole (wad events are sudden). Forming HP shower "oscillator stalling" 02-03 to 02-05 is a different item. [Shift Report PM1-SHIFT-2026-02-08-N] [Shift Report PM1-SHIFT-2026-02-03-D]
- 02-09 Day: "forming fabric hole at 14:20, 9.5 h down. Area barricaded while maintenance worked. WO 26102842"; stop 570 min = 220 min on Day + 350 min on Night, so restart about 23:50. Handover: "5-inch hole at the TS from a wad off the headbox approach; fabric changed (spare off the floor)". [Shift Report PM1-SHIFT-2026-02-09-D] [Shift Report PM1-SHIFT-2026-02-09-N]
- CONFLICT on start time: shift report 14:20; the position/downtime row on [[form-bottom]] says 19:20 (+5 h, same offset as the 2nd press drive and dryer drive rows). [Shift Report PM1-SHIFT-2026-02-09-D]
- Status trail in handovers: 02-09 "repaired; running"; 02-10 "spare fabric on; RCFA opened; crew briefed"; 02-11 "watching after restart"; 02-12 "closed"; 02-13 Day/Night "clean headbox approach piping at the outage" (became SM-0057 for [[out-2026-03-04]]). [Shift Report PM1-SHIFT-2026-02-10-D] [Shift Report PM1-SHIFT-2026-02-12-D] [Shift Report PM1-SHIFT-2026-02-13-D]
- Output: 02-09 Day 223 t (63.3% sheet on), Night 209 t (51.4%). [Shift Report PM1-SHIFT-2026-02-09-N]

## BUS issues (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2026-02-09 issue: 5-inch hole at the TS from a wad off the headbox approach; 9.5 h down; fabric changed (spare off the floor); WO 26102842, Gloria Nakamura, closed 2026-02-12. [BUS 2026-02-09 issue 65f60ced9e687df2]
- 2026-02-10 issue (Tobias Renner): "Spare fabric on; RCFA opened", closed 2026-02-13 "Clean headbox approach piping at the outage". [BUS 2026-02-10 issue d151cdf7fb993975]

## Actions
- SM-0057 clean headbox approach piping at the Mar 4 outage, Tobias Renner, done 2026-03-03. [Action SM-0057]
- SM-0056 add the approach piping to the outage clean list, Sunniva Brooks, done 2026-03-04. [Action SM-0056]
- SM-0059 install a wad detector camera at the breast roll, Fenna Gallagher, due 2026-04-30, In progress, OVERDUE as of 2026-11-10 (about 6 months); this is the only open action on the RCFA. [Action SM-0059]
- Related: [[headbox]] (approach piping), [[out-2026-03-04]].

## Position record (position_life form-bottom)
- Fabric NF-40212 (Northbank NX-1850) installed 2025-12-10 at [[out-2025-12-10]], removed 2026-02-09 after 60 d vs target 84 d, reason damaged: "5-inch hole at the TS from a wad off the headbox approach. 9.5 h unplanned shut; spare off the floor." [position_life form-bottom]
- Next fabric NF-40235 ran 64 d (2026-02-09 to 2026-04-15, [[out-2026-04-15]]). See [[form-bottom]]. [position_life form-bottom]

## Work order (WO extract work-orders-1)
- WO 26102842 "Forming fabric hole: Forming fabric" (type 3, prio 1, 2026-02-09, MILL Beatrix Hale, est 28.5 h act 31.4 h): "5-inch hole at the TS from a wad off the headbox approach; fabric changed (spare off the floor)." [WO 26102842]
- Headbox slice inspection and clean was a standing outage WO before (26101477 on 2026-01-21) and after (26102541 on 2026-03-04). [WO 26101477] [WO 26102541] See [[headbox]].
