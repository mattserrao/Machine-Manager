---
name: ref-refa
description: REF 1 refiner plates (asset 00072161), 84 d target, 34" LC plates; all runs 83 d; current run 72 d, reaches target at the 2026-11-11 outage
type: position
aliases: ["REF 1 refiner", "refiner A", "asset 00072161", "PM1:REF_A_KW", "REF_A_SE"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108904 "Change REF 1 refiner plates" (asset 00072161, MILL Beatrix Hale, 8 h), status "Planned - parts not reserved", parts Not reserved as of the extract; only one Ridgeway set on hand for two refiners (SM-0241). [WO 26108904] [Action SM-0241]
- Plate gap check WO 26109142 (completed 2026-10-28); ADX motor test round on the REF 1 motor (asset 00072168) WO 26109002 (E&I Omar Szabo, completed 10-22). [WO 26109142] [WO 26109002]

## Run history (tool: position_life ref-refa)
- Seven planned runs of 83 d vs target 84 d, 2025-01-08 to 2026-08-19, all worn. [position_life ref-refa]
- Changeover dates: 2025-01-08, 2025-04-02, 2025-06-25, 2025-09-17, 2025-12-10, 2026-03-04, 2026-05-27, 2026-08-19. [position_life ref-refa]
- Bars worn as expected, energy per ton steady to the end: RR-38926, RR-39687, RR-40036, RR-40059, RR-40065, RR-40074. [position_life ref-refa]
- 2025-04-02 to 2025-06-25 (RR-39290): normal wear; Ridgeway plate report on file. [position_life ref-refa]

## Current run
- Installed 2026-08-19, running: 72 d vs target 84 d, serial RR-40082 (as of 2026-10-30). [position_life ref-refa]
- Computed: 84 d is reached 2026-11-11, the date of [[out-2026-11-11]]; expect plates due for change there (WO scope not in this batch).

## Details
- Plates: Ridgeway Refining 34" LC plate, 3.0/4.0 bar/groove ([[ridgeway-refining]]). [position_life ref-refa]
- Pi tags: PM1:REF_A_KW (motor load kW), PM1:REF_A_SE (specific energy kWh/t) on asset 00072161; PM1:REF_A_VIB (bearing vibration) on motor 00072168. [Pi tag PM1:REF_A_SE] [Pi tag PM1:REF_A_VIB]
- Compare [[ref-refb]], which showed premature plate wear in the 2026-07-08 run. Plate life here is in days; do not mix with kWh. [position_life ref-refb]

## Ridgeway plate reports and 11/11 change (reports library)
- Target 12 weeks (84 d), Ridgeway 34" LC plate, 3.0/4.0 bar/groove [DOC SM-REF-02 p.1]
- Each REF 1 plate report (all 83 d, "Even wear", "Normal wear for the run length"): 09/17 to 12/10/2025 bar wear 53%, 62.3 kWh/t [DOC RR-PL-251210-A p.1]; 12/10/2025 to 03/04/2026 64%, 62.9 kWh/t [DOC RR-PL-260304-A p.1]; 03/04 to 05/27/2026 62%, 62.6 kWh/t [DOC RR-PL-260527-A p.1]; 05/27 to 08/19/2026 62%, 62.7 kWh/t [DOC RR-PL-260819-A p.1]
- Bar wear is in % of height and specific energy at removal in kWh/t; do not mix with plate life in days
- REF 1 specific energy was 61.8 kWh/t on 10/25/2026 at 10 weeks, used by Ridgeway as the comparison for REF 2 [DOC RR-FV-261026 p.1]
- Ridgeway field visit 10/26/2026 (rep Corinne Batista) recommends changing REF 2 plates at the 11/11/2026 outage together with REF 1 "(due)"; the mill has one set on hand, order a second set now (lead time 10 days) [DOC RR-FV-261026 p.1]
- Parts risk for [[out-2026-11-11]]: two plate sets needed (REF 1 due, REF 2 early) against one on hand as of 10/26/2026; whether the second is ordered/received: tool outage_scope or search_records
- Vibration: PM1:REF_A_VIB 0.057-0.073 in/s on every monthly Keel route 11/2025-10/2026 except 0.024-0.025 on 12/10/2025 and 07/08/2026; no alert [DOC KV-VR-261014 p.1]; see [[vibration-routes]]
- Related: [[ref-refb]], [[refiner-plate-wear]], [[outage-clothing-changes]]

## Work orders Jun-Sep 2026 (WO extract work-orders-3; asset 00072161 REF 1 refiner, motor 00072168)
- Change at [[out-2026-08-19]]: WO 26106727 "Change REF 1 refiner" (type 4, MILL Beatrix Hale, 6 h est / 6.6 h act): "Removed after 83 days. Bars worn as expected; energy per ton steady to the end." [WO 26106727]
- Preventive: "Refiner plate gap check, REF 1" (MECH, 1 h est): 4 WOs completed 2026-06-28 [WO 26106174], 07-28 [WO 26106972], 08-27 [WO 26107602], 09-28 [WO 26108379]. "ADX motor test round" (REF 1 refiner motor, E&I Omar Szabo, 6 h est / 6.6 h act): completed 2026-06-25 [WO 26106076], 07-24 [WO 26106853], 08-23 [WO 26107497], 09-22 [WO 26108253]. Both monthly.
- Next change: WO 26108904 for [[out-2026-11-11]], parts not reserved. See [[work-orders-jun-sep-2026]].

## Bonvoy (tags PM1:REF_A_SE 14 tag-days, REF_A_KW 4, REF_A_VIB 2; see [[refiner-plate-wear]])
- 2026-10-31: REF_A_SE High 3 h (mean 60.12, max 67.6), rank 4 in the daily report: "More energy per ton for the same work: refiner plates wearing"; REF 1 is 72 days into the 84-day target; WO 26108904 "Change REF 1 refiner plates" status 30. [Bonvoy Report 2026-10-31]
- Specific energy history: High 2025-11-29, 12-04, 2026-02-14, 02-17, 02-23, 02-24, 04-29, 05-23, 05-24, 08-11, 08-12, 10-31; Low 2025-12-12, 2026-06-02 (3-4 h each). Normal mean ~60 kWh/t. [Bonvoy PM1:REF_A_SE 2026-02-24] [Bonvoy PM1:REF_A_SE 2026-10-31]
- Motor load Low 3-5 h on 2026-03-02, 04-02, 08-25, 10-06 (stop-like days, [[bonvoy-multi-tag-dips]]); bearing vibration 2 isolated flags (2025-11-20 Low, 2025-12-08 High, max 0.081). [Bonvoy PM1:REF_A_KW 2026-10-06] [Bonvoy PM1:REF_A_VIB 2025-12-08]

## Work orders Feb-Jun 2026 (work-orders-2)
- "Change REF 1 refiner" WO 26104550 at [[out-2026-05-27]] (asset 00072161, MILL Beatrix Hale, type 4 prio 2, est 6 h act 6.6 h): "Removed after 83 days. Bars worn as expected; energy per ton steady to the end." [WO 26104550]
- Monthly PM "Refiner plate gap check, REF 1" (MECH, 1 h est): 26103094 (done 03-01), 26103864 (03-30), 26104634 (04-30), 26105362 (05-30). Monthly "ADX motor test round" on the REF 1 refiner motor (asset 00072168, E&I Omar Szabo): 26102989, 26103731, 26104389, 26105264. [WO 26103094] [WO 26105362] [WO 26102989] [WO 26105264]
- See [[refiner-plate-wear]], [[work-orders-feb-jun-2026]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Plate changes (type 4, MILL Beatrix Hale, est 6 h act 6.6 h; asset "REF 1 refiner" 00072161): 26100441 at [[out-2025-12-10]] and 26102513 at [[out-2026-03-04]], both "Removed after 83 days. Bars worn as expected; energy per ton steady to the end." [WO 26100441] [WO 26102513]
- Preventive: refiner plate gap check REF 1 (MECH, 1.1 h) 4 times monthly, 26100140 (done 2025-10-31), 26100931 (12-02), 26101687 (12-30), 26102338 (2026-01-29) [WO 26100140] [WO 26102338]; ADX motor test round on the REF 1 refiner motor (asset 00072168, E&I Omar Szabo, 6.6 h) 4 times: 26100042, 26100826, 26101575, 26102219. [WO 26100042] [WO 26102219]
- See [[routine-pm-work-orders]], [[outage-standard-wo-package]].
