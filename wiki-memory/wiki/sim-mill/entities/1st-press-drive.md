---
name: 1st-press-drive
description: 1st press drive (asset 00072308); Pi tags for nip load and drive bearing vibration; no stops or WOs in the positions batch
type: equipment
aliases: ["1st press drive", "asset 00072308", "PM1:PRESS1_LOAD", "PM1:PRESS1_DS_VIB"]
---
- Asset 00072308, kind drive, section sec-press, parent PM1 Press section 00072028. [equipment 00072308]
- Pi tags: PM1:PRESS1_LOAD 1st press nip load (pli) and PM1:PRESS1_DS_VIB 1st press drive bearing vibration (in/s). [Pi tag PM1:PRESS1_LOAD] [Pi tag PM1:PRESS1_DS_VIB]
- Stop history, WOs and RCFAs are not in this batch; see [[pi-tag-map]], [[equipment-tree]] and the 2nd press counterpart [[2nd-press-drive]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Weekly "Press hydraulic unit inspection" (MECH, 2 h): WO 26108624 (10-08), WO 26109023 (completed 10-24, two days late); WO 26109373 Approved (planned 11-05). [WO 26109023] [WO 26109373]

## Keel vibration route (reports library; see [[vibration-routes]])
- PM1:PRESS1_DS_VIB route readings in/s: 11/12/2025 0.058; 12/10/2025 0.022; 01/14/2026 0.071; 02/11 0.064; 03/11 0.067; 04/08 0.060; 05/13 0.055; 06/10 0.064; 07/08 0.024; 08/12 0.155 Alert; 09/09 0.056; 10/14 0.062 [DOC KV-VR-260812 p.1] [DOC KV-VR-260909 p.1]
- 08/12/2026: "1st press drive: 0.15 in/s (Alert). Plan a bearing change." with "Bearing defect frequencies present" [DOC KV-VR-260812 p.1]
- Route back to 0.056 on 09/09/2026 after the [[out-2026-08-19]] outage, so the bearing was presumably changed then (not stated in the Keel report); no RCFA, no failure [DOC KV-VR-260909 p.1]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072308)
- Bearing change: WO 26107413 "Change 1st press drive bearing (found on the Aug 12 vibration route)", corrective prio 2, requested 2026-08-12, planned 2026-08-19, completed 2026-08-19, outage 2026-08-19, 8 h est / 8.8 h act, MECH Beatrix Hale. This confirms the bearing was changed at [[out-2026-08-19]] (route fell from 0.155 to 0.056 by 09/09). No RCFA. [WO 26107413] [DOC KV-VR-260812 p.1] [DOC KV-VR-260909 p.1]
- Preventive "Press hydraulic unit inspection" (2 h est, MECH Beatrix Hale, asset 1st press drive): 8 WOs completed 2026-06-18, 07-03, 07-18, 08-01, 08-13, 08-29, 09-10, 09-24 (about every two weeks). [WO 26105957] [WO 26106307] [WO 26106594] [WO 26107028] [WO 26107308] [WO 26107595] [WO 26108064] [WO 26108330]
- The earlier line "no stops or WOs in the positions batch" is superseded: these WOs exist. See [[work-orders-jun-sep-2026]].

## BUS issue (list in [[bus-issue-sheet]])
- 2026-08-13 "1st press drive bearing in Alert on the vibration route": WO 26107413 "raised; scheduled" (owner Mei Fairbanks), closed 2026-08-19 "Monitoring daily" (outage day [[out-2026-08-19]]); 7 days on the sheet. [BUS 2026-08-13 .. BUS 2026-08-19 | issue 7d66d256db88d021]

## Bonvoy (tags PM1:PRESS1_DS_VIB 26 tag-days, PM1:PRESS1_LOAD 3 tag-days; tool: bonvoy_exceptions; see [[bonvoy]])
- Isolated 3 h flags: Low 2025-11-09 and 2026-01-17; High 2026-04-10, 2026-07-19, 2026-07-28 (max 0.077-0.080 in/s). [Bonvoy PM1:PRESS1_DS_VIB 2026-04-10] [Bonvoy PM1:PRESS1_DS_VIB 2026-07-28]
- Vibration ramp 2026-07-30 -> 2026-08-19 (21 d): High 16-24 h/day, daily max 0.089 -> 0.239 in/s; Alert 0.15 passed about 2026-08-14 (0.192); Danger 0.4 not reached. The record ends 2026-08-19, the day of [[out-2026-08-19]] (what ended it is not in this batch). No RCFA in the wiki; mode [[bearing-failed-between-vibration-routes]]. [Bonvoy PM1:PRESS1_DS_VIB 2026-07-30] [Bonvoy PM1:PRESS1_DS_VIB 2026-08-19]
- Nip load: High 3 h on 2026-03-31 (mean 557.7, max 572) and 2026-08-09 (mean 580.5, max 597, inside the vibration ramp); Low 5 h on 2026-06-18 (mean 520.2, min 504). [Bonvoy PM1:PRESS1_LOAD 2026-03-31] [Bonvoy PM1:PRESS1_LOAD 2026-08-09] [Bonvoy PM1:PRESS1_LOAD 2026-06-18]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Preventive "Press hydraulic unit inspection" (asset 00072308, MECH Beatrix Hale, type 2, 2.2 h act): 8 WOs about every 2 weeks, 26100287 (done 2025-11-06), 26100686 (11-21), 26101022 (12-05), 26101309 (12-18), 26101736 (2026-01-01), 26102051 (01-15), 26102331 (01-29), 26102751 (02-14). [WO 26100287] [WO 26102751]
- No corrective or emergency WO on the 1st press drive in this batch. See [[routine-pm-work-orders]].
