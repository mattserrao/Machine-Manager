---
name: form-bottom
description: PM1 forming fabric (asset 00072245), 84 d target; run history incl. 2025-04-02 early pull for drainage and the 2026-02-09 damaged-fabric 9.5 h unplanned shut
type: position
aliases: ["Forming fabric", "forming wire", "asset 00072245", "NX-1850"]
---
## Run history (tool: position_life form-bottom)
- Installed 2025-01-08, removed 2025-04-02: 83 d vs target 84 d, reason performance, worn, serial NF-39534; pulled a cycle early, drainage falling off, couldn't hold speed on 34 Super. [position_life form-bottom]
- 2025-04-02 to 2025-06-25 (83 d, serial NF-39829) normal wear, edge wear at the TS. [position_life form-bottom]
- 2025-06-25 to 2025-09-17 (83 d, serial NF-39880) ran to target; vac box loads crept up over the last two weeks. [position_life form-bottom]
- 2025-09-17 to 2025-12-10 (83 d, serial NF-40204) normal wear, changed at [[out-2025-12-10]]. [position_life form-bottom]
- Installed 2025-12-10, removed 2026-02-09: 60 d vs target 84 d, reason damaged, serial NF-40212; 5-inch hole at the TS from a wad off the headbox approach, 9.5 h unplanned shut, spare off the floor. [position_life form-bottom]
- 2026-02-09 to 2026-04-15 (64 d, serial NF-40235) planned, wear; 64 d vs target 84 d (follows the 2026-02-09 damage change), changed at [[out-2026-04-15]]. [position_life form-bottom]
- 2026-04-15 to 2026-07-08 (83 d, serial NF-40272) normal wear, changed at [[out-2026-07-08]]. [position_life form-bottom]
- 2026-07-08 to 2026-09-30 (83 d, serial NF-40307) normal wear, changed at [[out-2026-09-30]]. [position_life form-bottom]

## Current run
- Installed 2026-09-30, running: 30 d vs target 84 d, serial NF-40312 (as of 2026-10-30). [position_life form-bottom]
- Computed: target reached about 2026-12-23 (84 d from 2026-09-30); the outage after [[out-2026-11-11]] is the likely change point, WO scope not in this batch.

## Details
- Fabric: Northbank Fabrics NX-1850 double layer ([[northbank-fabrics]]). [position_life form-bottom]
- Section: [[equipment-tree]]. Pi tags mapped to this position: PM1:FLATBOX_VAC, PM1:COUCH_VAC, PM1:COUCH_SOLIDS (see [[pi-tag-map]]). [Pi tag PM1:FLATBOX_VAC]
- Failure modes: [[forming-fabric-damage]] (hole 2026-02-09), early pull for drainage (2025-04-02). [position_life form-bottom]

## Vendor surveys and RCFA-SM-26-006 (reports library)
- Spec/target: 12 weeks, Northbank NX-1850 double layer [DOC SM-REF-02 p.1]
- Northbank survey wear at 11.9 wk (end of life, 89% wear layer): 12/10/2025 (0.77 mm, 452 cfm) [DOC NF-SV-251210 p.1]; 07/08/2026 (0.82 mm, 441 cfm) [DOC NF-SV-260708 p.1]; 09/30/2026 (0.83 mm, 453 cfm) [DOC NF-SV-260930 p.1]
- Mid-life: 5.9 wk 54% wear, 0.84-0.88 mm, 479-490 cfm [DOC NF-SV-260121 p.1] [DOC NF-SV-260527 p.1] [DOC NF-SV-260819 p.1]; 3.1 wk 38% wear [DOC NF-SV-260304 p.1]
- 04/15/2026: fabric installed 02/09/2026 at 9.1 wk, 73% wear, 457 cfm, "Normal wear. Change at this outage (planned)": "9 weeks against a 12-week target; changed at this outage" [DOC NF-SV-260415 p.1]
- RCFA-SM-26-006: forming fabric hole 02/09/2026 14:20, 5-inch hole at the TS from a wad off the headbox approach piping; spare off the floor; 9.5 h, 294 t, WO 26102842; lead Tobias Renner; status Open - actions pending [RCFA-SM-26-006]
- Root cause: wad of stock off the headbox approach piping; contributing: stock build-up in the approach piping, no wad detection at the breast roll [RCFA-SM-26-006]
- Actions: SM-0057 clean headbox approach piping at the Mar 4 outage (Tobias Renner, 03/03/2026, Completed); SM-0056 add approach piping to outage clean list (Sunniva Brooks, 04/14/2026, Completed); SM-0059 wad detector camera at the breast roll (Fenna Gallagher, due 04/30/2026, In progress, past due at 10/31) [Action SM-0059]
- Fabric installed 09/30/2026 is 6 weeks old on 11/11/2026 (computed), not due; see [[out-2026-11-11]], [[headbox]]
- Related: [[outage-clothing-changes]], [[rcfa-register]]

## BUS issues
- 2026-02-09 hole issue 9.5 h, WO 26102842 and the 02-10 follow-up (RCFA opened; clean headbox approach piping): [[forming-fabric-damage]], [[bus-sheet-issues-2025-11-to-2026-05]]. Forming-section nuisance items on the same sheet: [[wire-guide]], [[flat-boxes]], [[forming-hp-shower]], [[headbox]]. [BUS 2026-02-09 issue 65f60ced9e687df2]

## Work order for the 2026-09-30 change
- WO 26107777 "Change Forming fabric" (asset 00072245), type 4, MILL Beatrix Hale, requested 2026-08-26, planned and completed 2026-09-30, 10 h est / 11 h act: "Removed after 83 days. Normal wear at removal." [WO 26107777] The 07-08 change WO is not in the Jun-Sep extract. Related forming-section corrective WOs: [[flat-boxes]], [[wire-guide]], [[forming-hp-shower]], [[vacuum-pump]].

## Downtime log event
- 2026-02-09 19:20 Forming / Forming fabric, cause "Forming fabric hole", 570 min, WO 26102842, RCFA-SM-26-006, grade 24#, crew D: "5-inch hole at the TS from a wad off the headbox approach; fabric changed (spare off the floor)". Largest single unplanned stop in the Nov 2025 - Sep 2026 downtime log. [downtime DT-260209-0163] [Shift Report PM1-SHIFT-2026-02-09-D]

## Work orders Feb-Jun 2026 (work-orders-2)
- "Change Forming fabric" (asset 00072245, MILL Beatrix Hale, type 4 prio 2, est 10 h act 11 h): WO 26103472 at [[out-2026-04-15]], note "Removed after 64 days. Normal wear at removal." (the fabric put in after the 02-09 hole); WO 26105684 at [[out-2026-07-08]], note "Removed after 83 days. Normal wear at removal." Not changed at [[out-2026-05-27]]. [WO 26103472] [WO 26105684]
- The 02-09 hole emergency itself is WO 26102842 (other extract): [[repeat-corrective-work-orders]]. Forming-section repeats in Feb-Jun: [[flat-boxes]], [[forming-hp-shower]], [[wire-guide]], [[vacuum-pump]], [[fan-pump]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Planned change WO 26100427 "Change Forming fabric" (asset 00072245, type 4, MILL Beatrix Hale, est 10 h act 11 h) at [[out-2025-12-10]]: "Removed after 83 days. Normal wear at removal." [WO 26100427]
- Emergency WO 26102842 "Forming fabric hole: Forming fabric" (type 3, prio 1, requested and completed 2026-02-09, MILL Beatrix Hale, est 28.5 h act 31.4 h, the longest job in the batch): "5-inch hole at the TS from a wad off the headbox approach; fabric changed (spare off the floor)." [WO 26102842]
- Same day a "Forming HP shower oscillator stalling" WO 26102807 was completed; the WOs do not link it to the hole ([[forming-hp-shower]]). [WO 26102807]
