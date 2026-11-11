---
name: p2-roll-bottom
description: 2nd press bottom roll (asset 00072364), blind-drilled rubber 12 P&J, target 546 d; changed at 2026-09-30 outage; Pi PM1:PRESS_SOLIDS maps here
type: position
aliases: ["2nd press bottom roll", "asset 00072364", "P2 bottom roll", "press exit solids"]
---
## Run history (tool: position_life p2-roll-bottom)
- Installed 2023-10-04, removed 2025-03-12: 524 d vs target 546 d, planned, serial PRS-40569; cover hardness up 2 P&J, recovered and reground. [position_life p2-roll-bottom]
- Installed 2025-03-12, removed 2026-09-30 ([[out-2026-09-30]]): 566 d vs target 546 d, planned, worn, serial PRS-40911; sent out to recover and regrind. [position_life p2-roll-bottom]

## Current run
- Installed 2026-09-30, running: 30 d vs target 546 d, serial PRS-40949 (as of 2026-10-30). [position_life p2-roll-bottom]
- Computed: target about 2028-03-30; not due at [[out-2026-11-11]].

## Details
- Roll: blind-drilled rubber, 12 P&J, vendor [[pellham-roll-service]]. [position_life p2-roll-bottom]
- Pi tag PM1:PRESS_SOLIDS (press exit solids, %) is attached to this position. [Pi tag PM1:PRESS_SOLIDS]
- Pellham roll service report PR-RS-261009-p2bottom (service rep Hollis Drummond): roll PRS-40911 removed 09/30/2026, received 10/02, report 10/09/2026, in service 566 days [DOC PR-RS-261009-p2bottom p.1]
- As received/as shipped vs spec: cover hardness 9 P&J (hardened) to 12 P&J (spec 12 +/- 1); crown 0.0030 in (worn) to 0.0040 in (spec 0.0040); TIR 0.0024 in to 0.0010 in (spec <= 0.0015); 0.11 in on diameter removed in the grind; bearings worn, replaced with new sealed [DOC PR-RS-261009-p2bottom p.1]
- Findings: cover hardened 3 P&J in service and the crown wore flat in the centre, "normal for 80 weeks"; no cracks, blisters or bond failure; reground, bearings replaced, balanced and "returned to stores as the spare" [DOC PR-RS-261009-p2bottom p.1]
- Target here is 78 weeks (546 d) [DOC SM-REF-02 p.1]; 566 d is about 81 weeks (computed). The spare is now PRS-40911 in stores (the roll on the machine is PRS-40949 per position_life)
- Roll list: p2-roll-bottom is Pellham Roll Service, 78 wk target [DOC SM-DWG-101 p.1]; see [[machine-layout]]
- Serial PRS-40949 also appears on [[d1-froll-2]] for the run 2022-09-21 to 2025-04-18 (roll recovered and reground, possibly reused); not explained in the sources. [position_life d1-froll-2]

## Work order for the 2026-09-30 change
- WO 26107805 "Change out (send to roll shop) 2nd press bottom roll" (asset 00072364), type 4 Project / outage, prio 2, MILL Beatrix Hale, requested 2026-08-26, planned and completed 2026-09-30, 10 h est / 11 h act: "Removed after 566 days. Sent out to recover and regrind." [WO 26107805] Pellham service report follows in PR-RS-261009-p2bottom (above).

## Bonvoy (tag PM1:PRESS_SOLIDS, 27 tag-days; tool: bonvoy_exceptions; see [[bonvoy]])
- Low windows: 2026-01-13 -> 2026-01-21 (9 d, min 43.46 -> 43.04, band mean 44.1) and 2026-05-04 -> 2026-05-18 (15 d, daily min fell to 41.14 on 05-11 then recovered to 41.95; band mean 43.98 -> 43.77). [Bonvoy PM1:PRESS_SOLIDS 2026-01-21] [Bonvoy PM1:PRESS_SOLIDS 2026-05-11] [Bonvoy PM1:PRESS_SOLIDS 2026-05-18]
- High 3-7 h on 2026-08-21, 08-23, 08-24 (max 44.59). [Bonvoy PM1:PRESS_SOLIDS 2026-08-23]
- The May window precedes the 05-12 / 05-13 / 05-19 felt events ([[press-felt-plugging]], [[uhle-box-vacuum]]); the Jan window overlaps the 2nd press bottom felt Uhle episode. Nothing flagged after 2026-08-24. [Bonvoy PM1:PRESS_SOLIDS 2026-08-24]
