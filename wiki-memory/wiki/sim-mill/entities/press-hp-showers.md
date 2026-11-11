---
name: press-hp-showers
description: PM1 high-pressure felt showers (forming + four press felts): Spraywell audit results Feb-Oct 2026 (pressure, % nozzles plugged), the 22% plugged 2nd press top shower in May, strainer actions; read for shower condition and nozzle-check questions
type: equipment
aliases: ["HP showers", "Spraywell audit", "shower audit", "nozzles plugged", "shower strainer", "forming HP shower", "press felt HP shower"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108743 "Change HP shower nozzles, press section" (2nd press top felt HP shower, asset 00072329, OPS, 6 h, Reserved). The strainer clean (SM-0139, SM-0195) is not a WO in the scope. [WO 26108743] [Action SM-0195]
- Forming HP shower (asset 00072224) oscillator stalling: WO 26109345 (completed 10-30), WO 26109380 (Entered 10-30, open). [WO 26109345] [WO 26109380]

## Audits (Spraywell Nozzle Supply, auditor Kiran Mehta; pressure psi / nozzles plugged / action)
- Audit 02/04/2026: forming 278 / 2% / OK; 1st press top 227 / 5% / OK; 1st press bottom 218 / 4% / OK; 2nd press top 216 / 4% / OK; 2nd press bottom 225 / 3% / OK; "Shower coverage good." [DOC SW-SA-260204 p.1]
- Audit 05/13/2026: forming 273 / 4%; 1st top 221 / 0%; 1st bottom 226 / 4%; 2nd top 224 / 22% "Clean nozzles; check strainer"; 2nd bottom 218 / 3% [DOC SW-SA-260513 p.1]
- 05/13 comment: "2nd press top felt HP shower: 22% of nozzles plugged (fibre and stickies). The supply strainer was packed solid. This felt is not being conditioned: expect it to fill. Nozzles cleaned during the audit; strainer to be cleaned at the next stop." [DOC SW-SA-260513 p.1]
- The felt filled 6 days later (05/19/2026, 34 d old): [[p2-felt-top]], [[rcfa-sm-26-016]]
- Audit 08/05/2026: forming 282 / 3%; 1st top 227 / 4%; 1st bottom 222 / 3%; 2nd top 223 / 4%; 2nd bottom 228 / 4%; all OK, "Shower coverage good." [DOC SW-SA-260805 p.1]
- Audit 10/21/2026: forming 279 / 4%; 1st top 215 / 0%; 1st bottom 223 / 4%; 2nd top 222 / 0%; 2nd bottom 219 / 0%; all OK [DOC SW-SA-261021 p.1]
- Only one audit (05/13) found a shower above 5% plugged; "Action" is OK on all other rows. Forming shower runs 273-282 psi; press showers 215-228 psi (range over the four audits)
- CONFLICT: the 08/05/2026 audit shows the 1st press top shower at 4% OK on the same day RCFA-SM-26-024 logged that shower's nozzles plugged and stopped the machine (14:37, 2.8 h); audit time of day is not stated [DOC SW-SA-260805 p.1] [RCFA-SM-26-024]
- The audits are infrequent (about quarterly: Feb, May, Aug, Oct); RCFA-SM-26-016 says nozzles were "not checked since the Feb audit" [RCFA-SM-26-016]

## BUS issues: shower nozzles plugged stops (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2026-02-07 2nd press bottom felt HP shower (asset 00072350) nozzles plugged, 1.9 h, WO 26102793, "hp shower nozzles plugging for 25 days before". [BUS 2026-02-07 issue 95651f898ec7733f]
- 2026-04-01 1st press top felt HP shower (asset 00072266) nozzles plugged, 2.3 h, WO 26104067, "for 14 days before". [BUS 2026-04-01 issue cb3f9c18e38705ae]
- Felt "filling" issues that asked to "Raise HP shower pressure and check the nozzles": 2nd press bottom felt WO 26102149 (2026-01-14) and 1st press top felt WO 26103017 (2026-02-18). [BUS 2026-01-14 issue 7f261d37ae97568b] [BUS 2026-02-18 issue 7fb0a0196a496e16]
- Not the Forming HP shower (oscillator stalling, 5 issues): [[forming-hp-shower]].

## Related actions (as of 10/31/2026)
- Weekly press shower nozzle check by operations: SM-0141 Completed [Action SM-0141]
- Clean the HP shower supply strainer every outage: SM-0139 Completed [Action SM-0139]
- Add the shower strainer to every outage clean list: SM-0195 (Tobias Renner, due 08/27/2026) In progress [Action SM-0195]
- Weekly nozzle check for the 1st press top felt HP shower: SM-0196 Completed [Action SM-0196]
- Marlow's rule of thumb: check the nozzles weekly and clean the strainer at every outage; Uhle vacuum rate of rise "more than 0.1 inHg a day before week 4 means the felt is filling" [DOC MP-FA-260526 p.1]

## Shift reports Feb 2026
- Forming HP shower "oscillator stalling -> check oscillator drive": handover 02-03 Day to 02-05 Night (6 shifts); not in later February handovers and not in a stop. The 02/04 audit had forming at 278 psi, 2% plugged, OK. [Shift Report PM1-SHIFT-2026-02-03-D] [Shift Report PM1-SHIFT-2026-02-05-N] [DOC SW-SA-260204 p.1]
- 2nd press bottom shower: crews wrote "felt looks wet coming out of the nip" 02-03 to 02-06; nozzles plugged 02-07 10:26 (114 min, WO 26102793), three days after the 02/04 audit gave it 3% "OK". See [[press-felt-plugging]]. [Shift Report PM1-SHIFT-2026-02-07-D] [DOC SW-SA-260204 p.1]
- 1st press top felt: handover 02-18 "raise HP shower pressure and check the nozzles" led to the 02-21 chemical wash. [Shift Report PM1-SHIFT-2026-02-18-D]

## Work orders Jun-Sep 2026 (WO extract work-orders-3)
- Weekly "Press shower nozzle check" is logged on the 2nd press top felt HP shower (asset 00072329): 16 WOs completed 2026-06-18 to 2026-09-29 ([[p2-felt-top]]). Outage "Change HP shower nozzles, press section" (same asset, OPS Operations): 2026-08-19 [WO 26106720]; 2026-09-30 [WO 26107784]; Nov 11 [WO 26108743]. Emergencies on the 1st press top felt HP shower (asset 00072266): 2026-06-30 [WO 26106440] and 2026-08-05 [WO 26107287], see [[press-felt-plugging]]. The 1st press shower has no weekly check WO and no nozzle-change WO in this extract. [WO 26106720] [WO 26107784]

## Links
- Failure mode [[press-felt-plugging]]; Uhle box trend [[uhle-box-vacuum]]; felts [[p1-felt-top]], [[p1-felt-bottom]], [[p2-felt-top]], [[p2-felt-bottom]]; forming fabric [[form-bottom]]
- Per-shower asset pages (from the equipment list): [[1st-press-top-felt-hp-shower]], [[1st-press-bottom-felt-hp-shower]], [[2nd-press-bottom-felt-hp-shower]]

## Work orders Feb-Jun 2026 (work-orders-2)
- Weekly "Press shower nozzle check" (asset 00072329, 2nd press top felt HP shower, OPS Operations, 1 h est): 17 WOs, 26102877 (done 02-17), 26103003, 26103171, 26103283, 26103437, 26103689, 26103885, 26104039, 26104207, 26104326, 26104515, 26104830 (05-07), 26104984 (05-12), 26105145 (05-20), 26105292, 26105453, 26105635 (06-09). The 05-13 Spraywell audit found this shower 22% plugged one day after WO 26104984 was Closed; see the CONFLICT in [[p2-felt-top]]. [WO 26102877] [WO 26104984] [WO 26105635]
- Emergency WO 26104067 (2026-04-01) on the 1st press top felt HP shower asset 00072266 ("plugging for 14 days before"; 6.8 / 7.5 h). Outage "Change HP shower nozzles, press section" (asset 00072329, OPS): WO 26103479 (04-15, 6/6.6 h), WO 26104543 (05-27, 8/8.8 h), WO 26105691 (07-08, 4/4.4 h). [WO 26104067] [WO 26103479] [WO 26104543] [WO 26105691]
- Forming HP shower oscillator stalling: [[forming-hp-shower]]. Overview [[work-orders-feb-jun-2026]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- The weekly "Press shower nozzle check" (OPS, 1.1 h act) is filed on the 2nd press top felt HP shower (asset 00072329, position p2-felt-top): 16 WOs, 26100070 (done 2025-10-28) ... 26102709 (done 2026-02-11). [WO 26100070] [WO 26102709]
- "Change HP shower nozzles, press section" (same asset, OPS, type 4) at three outages: 26100434 ([[out-2025-12-10]], 8.8 h), 26101442 ([[out-2026-01-21]], 4.4 h), 26102506 ([[out-2026-03-04]], 8.8 h). [WO 26100434] [WO 26101442] [WO 26102506]
- Emergency WO 26102793 "Press shower nozzles plugged: 2nd press bottom felt HP shower" (asset 00072350, 2026-02-07, 6.3 h act): "hp shower nozzles plugging for 25 days before". In this batch the weekly nozzle check WOs are all filed on the 2nd press top felt shower, none on this one. [WO 26102793] [WO 26102709]
- See [[p2-felt-bottom]], [[p2-felt-top]], [[press-felt-plugging]].
