---
name: routine-pm-work-orders
description: The weekly/monthly preventive (type 2) WO series Oct 2025 - Feb 2026: title, asset, craft, hours, cadence and count; read to know what PM exists on which asset and how late routes run
type: topic
aliases: ["PM routes", "lube route", "operator rounds", "preventive work orders", "type 2 WOs", "weekly routes"]
---
Source: WO extract work-orders-1 (WO 26100000 to 26102842, requested 2025-10-18 to 2026-02-09). All preventive WOs are type 2, prio 4, Closed. Actual hours are 1.1 x estimate on every one of them. Later period: [[work-order-routes-and-corrective]]. Tool: search_records (WO).

## Weekly routes (one WO per week unless noted; count = WOs in this batch)
- Lube route: wet end and press (couch roll asset 00072210, MILL Beatrix Hale, 3 h est): 17 WOs, 26100000 (done 2025-10-25) ... 26102779 (done 2026-02-14). [WO 26100000] [WO 26102779] See [[couch-roll]].
- Lube route: stock prep (Pulper 00072077, MILL, 3 h): 16 WOs, 26100133 ... 26102758. [WO 26100133] See [[pulper-rotor]].
- Lube route: dryers and reel (Dryer drive lineup 00072742, MILL, 4 h): 17 WOs, 26100021 ... 26102814. [WO 26100021] See [[dryer-drive-lineup]].
- Operator rounds: wet end (Headbox 00072189, OPS, 1 h): 17 WOs. [WO 26100028] See [[headbox]].
- Operator rounds: dry end (Dryer can 10 00072504, OPS, 1 h): 16 WOs. [WO 26100056]
- Operator rounds: stock prep (Pulper, OPS, 1 h): 17 WOs. [WO 26100007]
- Doctor blade check: dryers (Dryer can 1 00072385, OPS, 2 h): 17 WOs. [WO 26100049]
- Grease felt roll bearings, 1st and 2nd sections (d1-froll-1 asset 00072420, MILL, 2 h): 16 WOs, [[d1-froll-1]]. [WO 26100063]
- Grease felt roll bearings, 3rd and 4th sections (d3-froll-1 asset 00072602, MILL, 2 h): 16 WOs, [[d3-froll-1]]. [WO 26100084]
- Felt roll bearing grease, all sections (d2-froll-1 asset 00072511, MILL, 4 h): 4 WOs, about every 5 weeks (26100112 done 2025-10-30, 26100896 done 11-29, 26101659 done 12-29, 26102296 done 2026-01-28); [[d2-froll-1]]. [WO 26100112] [WO 26102296]
- Press shower nozzle check (2nd press top felt HP shower 00072329, position p2-felt-top, OPS, 1 h): 16 WOs, [[p2-felt-top]], [[press-hp-showers]]. [WO 26100070]
- Winder slitter blade change (Winder slitters 00072798, OPS, 1.5 h): 16 WOs, [[winder-drums]]. [WO 26100098]
- Clean reel scanner heads (Reel drum 00072763, INST Fenna Gallagher, 1 h): 16 WOs, [[reel-drum]]. [WO 26100105]
- Rotary joint inspection, all sections (3rd section rotary joint 00072637, MECH, 2 h): 9 WOs (about every 2 weeks), [[3rd-section-rotary-joint]]. [WO 26100035]
- Screen basket ΔP check (Fine screens 00072105, OPS, 1 h): 9 WOs, [[fine-screens]]. [WO 26100014]
- Press hydraulic unit inspection (1st press drive 00072308, MECH, 2 h): 8 WOs, [[1st-press-drive]]. [WO 26100287]
- Vacuum pump seal water check (Vacuum pump 00072238, MECH, 1 h): 8 WOs, [[vacuum-pump]]. [WO 26100301]

## Monthly / less frequent
- Monthly vibration route (Keel Vibration Services; asset Dryer drive lineup, MECH, 6 h): 4 WOs, 26100511 (done 2025-11-12), 26101162 (12-10), 26102023 (2026-01-14), 26102730 (02-11); dates match the Keel route reports in [[vibration-routes]]. [WO 26100511] [WO 26102730]
- MCC thermography (Dryer drive lineup, E&I Omar Szabo, 3 h): 4 WOs, 26100091 (done 2025-10-29), 26100882 (11-29), 26101631 (12-29), 26102282 (2026-01-27). [WO 26100091] [WO 26102282]
- ADX motor test round (REF 1 refiner motor 00072168, position ref-refa, E&I, 6 h): 4 WOs, 26100042, 26100826, 26101575, 26102219; [[ref-refa]]. [WO 26100042] [WO 26102219]
- Refiner plate gap check REF 1 (00072161) and REF 2 (00072175), MECH 1 h: 4 each, monthly; [[ref-refa]], [[ref-refb]]. [WO 26100140] [WO 26100161]
- Fan pump seal inspection (MECH, 1.5 h): 4 WOs; [[fan-pump]]. [WO 26100168]
- Hood fan belt check (Hood exhaust fan 00072756, MECH, 1.5 h): 4 WOs; [[hood-exhaust-fan]]. [WO 26100210]
- Steam trap survey (Steam header, MECH, 4 h): 4 WOs; [[steam-header]]. [WO 26100077]
- Thickener wire wash (Thickener 00072126, OPS, 3 h): 4 WOs. [WO 26100259]
- Reel spool inspection (Reel drum, OPS, 2 h): 4 WOs. [WO 26100238]

## Lateness
- Of the 275 preventive WOs, 178 were completed on the planned date, 54 one day late and 43 two days late; none later than 2 days (computed from planned vs completed dates). Examples ( WO 26100063 planned 2025-10-28, done 10-30; WO 26100217 planned 11-03, done 11-05; WO 26100343 planned 11-09, done 11-11; WO 26101834 planned 2026-01-05, done 01-07). [WO 26100063] [WO 26100217] [WO 26100343] [WO 26101834]
- No PM WO in this batch is open or cancelled. [WO 26102835]
- Continuation Feb-Jun 2026 (WO 26102849 on): the same series with ids, counts and timeliness are in [[work-orders-feb-jun-2026]]; Jun-Sep 2026 in [[work-orders-jun-sep-2026]].
