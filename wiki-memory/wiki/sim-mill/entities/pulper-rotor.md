---
name: pulper-rotor
description: Pulper rotor (asset 00072084, Stock prep) - the worst repeat RCFA asset: 6 RCFAs in 2026 (3 bearing, 2 rectifier, 1 drive IGBT trip); RCFA-SM-26-013 still open
type: equipment
aliases: ["asset 00072084", "Pulper", "pulper drive", "PM1:PULPER_VIB"]
---
## Current picture (as of 2026-11-10; tool: rcfa_status)
- Worst repeat-RCFA asset: 6 RCFAs in 2026 (3 bearing, 2 rectifier, 1 drive IGBT trip), about 27.3 h and 849 t (computed). [RCFA-SM-26-005] [RCFA-SM-26-027]
- Only RCFA-SM-26-013 (bearing, 2026-04-28) is open; its grease review SM-0124 is In progress, overdue since 2026-07-01. [RCFA-SM-26-013] [Action SM-0124]
- Last event: 2026-09-07 rectifier fault, 3.4 h, 104 t, closed 2026-09-26. [RCFA-SM-26-027]
- Bearing cases had Pi PM1:PULPER_VIB lead times of about 15, 22 and 18 days. [RCFA-SM-26-005] [RCFA-SM-26-013] [RCFA-SM-26-022]
- Note: the online sensor was recorded done 2026-02-25, yet RCFA-013 and -022 again list "no online vibration". [Action SM-0044] [RCFA-SM-26-022]
- Scoped for 11/11: WO 26108827 pulper extraction plate inspection (4 h, Reserved). [WO 26108827]
- WO asset is "Pulper" 00072077, not the rotor 00072084; "amps swinging with bale feed" BUS subject is separate. [BUS 2026-06-05]
- See [[bearing-failed-between-vibration-routes]], [[rectifier-fault-mcc-dc-bus]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO assets say "Pulper" (asset 00072077), not the rotor (00072084). Scoped for [[out-2026-11-11]]: WO 26108827 "Pulper extraction plate inspection" (MECH Beatrix Hale, 4 h, Reserved). [WO 26108827]
- Weekly "Lube route: stock prep" (3 h) and "Operator rounds: stock prep" (1 h): 26108631, 26108883, 26109037 and 26108666, 26108897, 26109072 done; 26109226 and 26109247 In progress; 26109394 and 26109415 Entered. See [[work-order-routes-and-corrective]]. [WO 26109226] [WO 26109394]

## RCFAs on this asset (tool: rcfa_status; downtime_summary group=equipment)
- 2026-01-22 bearing failure, 5 h, 157 t, Pi PM1:PULPER_VIB about 15 days before; RCFA-SM-26-005 closed 2026-03-22. [RCFA-SM-26-005]
- 2026-04-28 bearing failure, 4.5 h, 139 t, PM1:PULPER_VIB about 22 days before; RCFA-SM-26-013 OPEN. [RCFA-SM-26-013]
- 2026-07-06 rectifier fault (MCC-1 DC bus down), 3.9 h, 121 t; RCFA-SM-26-019 closed 2026-07-21. [RCFA-SM-26-019]
- 2026-07-18 drive trip: overcurrent, IGBT module failed, 4.6 h, 144 t, category Electrical; RCFA-SM-26-021 closed 2026-08-22. [RCFA-SM-26-021]
- 2026-07-20 bearing failure, 5.9 h, 184 t, PM1:PULPER_VIB about 18 days before; RCFA-SM-26-022 closed 2026-09-22. [RCFA-SM-26-022]
- 2026-09-07 rectifier fault, 3.4 h, 104 t; RCFA-SM-26-027 closed 2026-09-26. [RCFA-SM-26-027]
- Six RCFAs total about 27.3 h and 849 t (computed from the headers). Lead on all: Mei Fairbanks.

## Causes and actions
- Bearing: "failed between vibration routes" - see [[bearing-failed-between-vibration-routes]]; two-weekly route done (SM-0043 2026-02-07, SM-0121 2026-05-14, SM-0183 2026-08-08), online sensor installed (SM-0044 2026-02-25, SM-0123 2026-06-10, SM-0185 2026-08-26), grease review SM-0045 and SM-0186 done, SM-0124 In progress, due 2026-07-01, OVERDUE. [Action SM-0043] [Action SM-0123] [Action SM-0185] [Action SM-0124]
- Observation: the online sensor was first listed as done 2026-02-25 yet RCFA-SM-26-013 (Apr) and -022 (Jul) again list "no online vibration on this asset" as contributing.
- Rectifier: see [[rectifier-fault-mcc-dc-bus]]; vendor reviews SM-0172, SM-0216 done. [Action SM-0172] [Action SM-0216]
- Drive IGBT trip: "Drive at 95%+ load on heavy grades"; load study on 34 Super SM-0181 done 2026-08-09; spare drive module to stores SM-0182 done 2026-08-22 (Desmond Pike). [Action SM-0181] [Action SM-0182]

## BUS issues Dec 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]], [[stock-prep-recurring-issues]])
- 2026-01-22 BUS issue: pulper rotor (asset 00072084) bearing failure 5.0 h, WO 26102317, Gloria Nakamura, "bearing vibration rising (bonvoy) for 31 days before"; closed 2026-01-24. [BUS 2026-01-22 issue ce84ad5c53467465]
- "Pulper rotor amps swinging with bale feed" (Pulper, asset 00072077; Ingrid Solberg, "Operators checking bale breaker feed rate" then "Feed rate steadied; watch"): 7 issues, 2025-12-01, 12-13 (10 days), 12-25, 2026-01-20, 02-09 (14 days), 02-25, 04-10. Three of them (12-13, 12-25, 01-20) fall in the 6 weeks before the 01-22 bearing failure. [BUS 2025-12-13 issue d835ed43b5756866] [BUS 2026-04-10 issue 792fead1ecc70f81]

## BUS follow-ups
- "Pulper rotor amps swinging with bale feed" (asset "Pulper"): SM-0023 (2025-12-25), SM-0042 (2026-01-20), SM-0072 (2026-02-25), all completed; Ingrid Solberg. [Action SM-0023] [Action SM-0042] [Action SM-0072]

## What crews saw before the 2026-01-22 bearing failure (shift reports; tool: shift_reports)
- First crew flag: 2026-01-08 Day (crew B): "Something to look at on the Pulper rotor: bearing sounds rough on rounds. Not sure yet; flagging it." 14 days before the failure. [Shift Report PM1-SHIFT-2026-01-08-D]
- Repeated in the notes of 13 more shifts through 01-20 Night, wording "bearing sounds rough on rounds" (sometimes with "?"): 01-10-N, 01-11-D, 01-11-N, 01-12-D, 01-13-N, 01-14-D, 01-14-N, 01-16-D, 01-17-N, 01-18-D, 01-19-N, 01-20-D, 01-20-N. [Shift Report PM1-SHIFT-2026-01-10-N] [Shift Report PM1-SHIFT-2026-01-12-D] [Shift Report PM1-SHIFT-2026-01-20-N]
- From 01-13 Night the note carries the Pi tag "(PULPER_VIB)", i.e. crews were looking at PM1:PULPER_VIB. [Shift Report PM1-SHIFT-2026-01-13-N] [Shift Report PM1-SHIFT-2026-01-20-D]
- The rough-bearing remark is in the free-text Notes only; it is not in the Handover lists of the 01-08 to 01-20 reports, which carry other items. [Shift Report PM1-SHIFT-2026-01-14-D]
- Keel route 01/14/2026 read 0.275 Alert (see below), the same day the notes said "Operators mentioned the Pulper rotor: bearing sounds rough on rounds". [Shift Report PM1-SHIFT-2026-01-14-D]
- Day before the stop (outage day): handover "Pulper: rotor amps swinging with bale feed -> operators checking bale breaker feed rate" on 01-21 Day and Night; 01-22 Day "feed rate steadied; watch" (BUS SM-0042 above). [Shift Report PM1-SHIFT-2026-01-21-D] [Shift Report PM1-SHIFT-2026-01-22-D]
- Failure: 2026-01-22 06:06, "Pulper rotor: bearing failure at 06:06, 5.0 h down. Area barricaded while maintenance worked. WO 26102317"; stop logged as Unplanned 303 min. The outage window in [[out-2026-01-21]] ended 07:00 that morning, but the report logs the stop as unplanned. [Shift Report PM1-SHIFT-2026-01-22-D]
- Aftermath: 01-23 handover "bearing vibration rising (bonvoy) for 31 days before -> watching after restart", closed 01-24. [Shift Report PM1-SHIFT-2026-01-23-D] [Shift Report PM1-SHIFT-2026-01-24-D]
- Not in the 29 shifts from 01-08 to 01-22: any note that the bearing was inspected or a stop planned for it; the remark stayed "not sure yet" for 14 days. [Shift Report PM1-SHIFT-2026-01-08-D] [Shift Report PM1-SHIFT-2026-01-20-N]
- See [[bearing-failed-between-vibration-routes]], [[precursor-lead-times]].

## Shift reports Feb 2026 (amps swinging; 2 months before the 2026-04-28 bearing failure)
- Handover "Pulper: rotor amps swinging with bale feed -> operators checking bale breaker feed rate": 02-10 Day to 02-11 Night, 02-13 Day to 02-14 Night, 02-27 Day to 02-28 Night; 02-28 Day/Night add "feed rate steadied; watch". Matches BUS SM-0072 (02-25). [Shift Report PM1-SHIFT-2026-02-10-D] [Shift Report PM1-SHIFT-2026-02-14-N] [Shift Report PM1-SHIFT-2026-02-28-D] [Action SM-0072]
- Process item (feed rate), not a bearing sign: no "bearing sounds rough" remark and no PULPER_VIB mention in the February reports, unlike 01-08 to 01-20. The Bonvoy ramp before RCFA-SM-26-013 starts 2026-03-30. [Shift Report PM1-SHIFT-2026-02-13-D] [Bonvoy PM1:PULPER_VIB 2026-04-28]
- No pulper stop in the February reports. The same amps item preceded the 2026-01-22 failure by one day (above). [Shift Report PM1-SHIFT-2026-02-28-N]

## Shift reports Mar 2026 (before the 2026-04-28 bearing failure; see [[shift-handover-signals-2026-03]])
- Only pulper item in March: "Pulper: rotor amps swinging with bale feed → feed rate steadied; watch" on 03-01 Day and Night. No pulper rotor item in handovers 03-02 to 03-31. [Shift Report PM1-SHIFT-2026-03-01-D] [Shift Report PM1-SHIFT-2026-03-01-N]
- The downtime log says bearing vibration was rising for 43 days before the 04-28 failure, i.e. from about 03-16 (computed); none of the March handovers mention vibration or the pulper after 03-01, and the Keel 03-11 route read 0.064 Good. [downtime DT-260428-0277] [DOC KV-VR-260311 p.1]

## Downtime log events (tool: downtime_events; minutes from the log)
- 2026-01-22 bearing failure 303 min, WO 26102317, RCFA-SM-26-005; "bearing vibration rising (bonvoy) for 31 days before". CONFLICT on lead time: RCFA says about 15 days in Pi PM1:PULPER_VIB, the log text says 31 days. [downtime DT-260122-0130]
- 2026-04-28 bearing failure 269 min, WO 26104816, RCFA-SM-26-013; log says 43 days of rising vibration (RCFA says about 22). [downtime DT-260428-0277]
- 2026-07-06 rectifier fault, MCC-1 DC bus down, 235 min, WO 26106545, RCFA-SM-26-019. [downtime DT-260706-0424]
- 2026-07-18 drive trip 278 min, WO 26106867, RCFA-SM-26-021. [downtime DT-260718-0455]
- 2026-07-20 bearing failure 356 min, WO 26106916, RCFA-SM-26-022; log says 35 days of rising vibration (RCFA about 18). Only two days after the drive trip. [downtime DT-260720-0461]
- 2026-09-07 06:45 rectifier fault, MCC-1 DC bus down, 201 min, WO 26108148, RCFA-SM-26-027, grade 34 Super, crew C; log says nothing about a vibration precursor. [downtime DT-260907-0534] [Shift Report PM1-SHIFT-2026-09-06-N]
- Downtime-log total for the four pulper rotor stops Jan-Jul 2026: 3 bearing (928 min) plus rectifier 235 and drive trip 278. [downtime DT-260122-0130 to DT-260720-0461]
- Before this batch's RCFAs: the log has no other pulper rotor stop Nov 2025 - Sep 1 2026 beyond these five rows (the Sep 7 rectifier event is after the batch).

## BUS issues for the stops (Apr-Sep 2026; list in [[bus-issue-sheet]])
- 2026-04-28 bearing 4.5 h, WO 26104816, "bearing vibration rising (bonvoy) for 43 days before"; owner Gloria Nakamura; New -> Open "Watching after restart" -> Closed 04-30. [BUS 2026-04-28 .. BUS 2026-04-30 | issue d10840ea9aa2dae8]
- 2026-07-06 rectifier fault 3.9 h, WO 26106545. [BUS 2026-07-06 .. BUS 2026-07-08 | issue 6409159f2529c7a1]
- 2026-07-18 drive trip 4.6 h, WO 26106867, owner Desmond Pike (not Gloria Nakamura). [BUS 2026-07-18 .. BUS 2026-07-19 | issue a029410d8bc231f8]
- 2026-07-20 bearing 5.9 h, WO 26106916, 35 days of rising vibration per the sheet. [BUS 2026-07-20 .. BUS 2026-07-22 | issue 0afa4d3eb95b62d6]
- 2026-09-07 rectifier fault again, 3.4 h, WO 26108148 (RCFA-SM-26-027), closed 09-09. [BUS 2026-09-07 .. BUS 2026-09-09 | issue 6aa5467cf4d982bf]
- Pulper (asset 00072077) "rotor amps swinging with bale feed", Ingrid Solberg: issues 06-05, 07-13 (14 days on the sheet, two cycles), 09-13, each closed "Feed rate steadied; watch". [BUS 2026-07-13 .. BUS 2026-07-24 | issue 1a5bc459509ce230]

## Keel vibration route (reports library; see [[vibration-routes]])
- PM1:PULPER_VIB route readings in/s: 11/12/2025 0.068; 12/10/2025 0.024; 01/14/2026 0.275 Alert; 02/11 0.076; 03/11 0.064; 04/08 0.169 Alert; 05/13 0.070; 06/10 0.070; 07/08 0.062; 08/12 0.073; 09/09 0.075; 10/14 0.072 [DOC KV-VR-260114 p.1] [DOC KV-VR-260408 p.1] [DOC KV-VR-261014 p.1]
- Both route alerts preceded a bearing failure: 0.275 on 01/14 then failure 01/22 (8 d, RCFA-SM-26-005); 0.169 on 04/08 then failure 04/28 (20 d, RCFA-SM-26-013). Neither alert row carries a note or finding text [DOC KV-VR-260114 p.1] [DOC KV-VR-260408 p.1]
- The 01/14 report's findings read "No new findings. All points within limits." despite the 0.275 Alert reading (CONFLICT inside the report) [DOC KV-VR-260114 p.1]
- 07/08/2026 route 0.062 Good; the July bearing failure came 12 days later (RCFA-SM-26-022) [DOC KV-VR-260708 p.1]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072084 Pulper rotor, parent Pulper 00072077)
- All four are type 3 Emergency, prio 1, requested and completed the same day; hours are WO labour hours (est / act), not downtime minutes:
  - 2026-07-06 Rectifier fault (MCC DC bus down): 11.8 h / 13 h, MECH Beatrix Hale. [WO 26106545]
  - 2026-07-18 Drive trip: 13.9 h / 15.3 h, E&I Omar Szabo. [WO 26106867]
  - 2026-07-20 Bearing failure: 17.8 h / 19.6 h, MECH Beatrix Hale; "bearing vibration rising (bonvoy) for 35 days before". [WO 26106916]
  - 2026-09-07 Rectifier fault (MCC DC bus down): 10.1 h / 11.1 h, MECH Beatrix Hale. [WO 26108148]
- Pulper (asset 00072077) routine WOs: "Lube route: stock prep" (MILL Beatrix Hale, 3 h est, 17 WOs 2026-06-13 to 2026-10-02), "Operator rounds: stock prep" (OPS, 1 h est, 17 WOs 2026-06-14 to 2026-10-03), outage "Pulper extraction plate inspection" 2026-07-08 [WO 26105789], 2026-08-19 [WO 26106804], 2026-09-30 [WO 26107868]. See [[work-orders-jun-sep-2026]].
- Other stock prep corrective WOs (INST Fenna Gallagher unless noted): [[machine-chest]] level hunting, [[hd-cleaners]] reject valve sticking, [[coarse-screen]] rejects high (MECH), [[steam-header]] pressure dips.

## Asset and Pi tags (from equipment/Pi tag listing)
- Pulper rotor is asset 00072084 (kind motor, section sec-stockprep), child of Pulper 00072077 (parent PM1 Stock prep 00072007). [equipment 00072084]
- Pi tags: PM1:PULPER_AMPS rotor current (A) and PM1:PULPER_VIB rotor bearing vibration (in/s) on 00072084; PM1:PULPER_CONS pulper consistency (%) on the pulper 00072077. [Pi tag PM1:PULPER_AMPS] [Pi tag PM1:PULPER_VIB] [Pi tag PM1:PULPER_CONS]
- See [[pi-tag-map]] and [[equipment-tree]].

## Bonvoy (tags PM1:PULPER_VIB 74 tag-days, PM1:PULPER_AMPS, PM1:PULPER_CONS; see [[bonvoy]])
- Three ramps, each ending on a bearing RCFA date: 2025-12-25 -> 2026-01-21 (28 d, daily max 0.086 -> 0.414); 2026-03-30 -> 2026-04-28 (30 d, 0.115 -> 0.413); 2026-07-05 -> 2026-07-20 (15 listed days, 0.192 -> 0.407). 74 tag-days = 28 + 30 + 15 + 1. [Bonvoy PM1:PULPER_VIB 2026-01-21] [Bonvoy PM1:PULPER_VIB 2026-04-28] [Bonvoy PM1:PULPER_VIB 2026-07-20]
- Longer than the RCFA "about 15/22/18 days" lead times: Bonvoy shows 28, 30 and 15 flagged days (see [[bearing-failed-between-vibration-routes]]).
- Single 2026-10-23 flag is Low (max 0.057), a quiet reading. Nothing High on this tag after 2026-07-20 in the record. [Bonvoy PM1:PULPER_VIB 2026-10-23]
- Shift reports Dec 2025: "Pulper: rotor amps swinging with bale feed → operators checking bale breaker feed rate" in handovers Dec 1 to Dec 14 and Dec 25 to Dec 27 (Dec 27 D: "feed rate steadied; watch"); about 4 to 7 weeks before the 2026-01-22 bearing failure (RCFA-SM-26-005); the reports attribute it to bale feed, not the bearing. [Shift Report PM1-SHIFT-2025-12-01-D] [Shift Report PM1-SHIFT-2025-12-14-D] [Shift Report PM1-SHIFT-2025-12-27-D] [RCFA-SM-26-005]
- Rotor current PULPER_AMPS Low on 2026-01-19 (mean 409.8, min 395.3) and 2026-03-08; consistency PULPER_CONS High 2026-01-20 (5.22%) and 2026-09-24. Both Jan dates fall inside the first vibration ramp. [Bonvoy PM1:PULPER_AMPS 2026-01-19] [Bonvoy PM1:PULPER_CONS 2026-01-20]

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- Emergency WO 26104816 "Bearing failure: Pulper rotor" (asset 00072084), type 3 prio 1, 2026-04-28, MECH Beatrix Hale, est 13.4 h act 14.7 h: "bearingfail: bearing vibration rising (bonvoy) for 43 days before." RCFA-SM-26-013. [WO 26104816]
- Pulper (asset 00072077) weekly PM: "Lube route: stock prep" (MILL Beatrix Hale, 3 h est) 16 WOs 26102919 to 26105530; "Operator rounds: stock prep" (OPS, 1 h) 16 WOs 26102947 to 26105558. The lube route WO 26104368 was completed 04-24, 4 days before the 04-28 bearing failure. [WO 26104368] [WO 26104816]
- Outage "Pulper extraction plate inspection" (MECH, 4 h est): WO 26103563 ([[out-2026-04-15]]) and WO 26104620 ([[out-2026-05-27]]). [WO 26103563] [WO 26104620]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26102317 "Bearing failure: Pulper rotor" (asset 00072084, type 3, prio 1, requested and completed 2026-01-22, MECH Beatrix Hale, est 15.1 h act 16.6 h): "bearingfail: bearing vibration rising (bonvoy) for 31 days before." [WO 26102317]
- The day before, the 2026-01-21 outage ran "Pulper extraction plate inspection" WO 26101519 (asset Pulper 00072077, 4.4 h act): [[out-2026-01-21]]. The same inspection also ran at 12-10 (WO 26100518, 8.8 h) and 03-04 (WO 26102583, 8.8 h). [WO 26101519] [WO 26100518] [WO 26102583]
- Preventive on the Pulper (asset 00072077): "Lube route: stock prep" (MILL, 3.3 h act) 16 WOs and "Operator rounds: stock prep" (OPS, 1.1 h) 17 WOs, roughly weekly. [WO 26100133] [WO 26100007] See [[routine-pm-work-orders]].
