---
name: press-felt-plugging
description: Recurring failure mode - press felts plug mid-life and HP shower nozzles/strainers blind (emergency felt wash, unplanned felt change); 6 RCFAs May-Aug 2026 on all four press felts, 4 open per the RCFA register; read with Uhle vacuum actions
type: failure-mode
aliases: ["press felt plugged", "emergency felt wash", "unplanned felt change", "press shower nozzles plugged", "HP shower strainer", "Uhle vacuum rate-of-rise"]
---
## Current picture (as of 2026-11-10; tool: rcfa_status, overdue_actions)
- Six RCFAs May-Aug 2026 on all four press felts, about 28.4 h and 883 t (computed); 4 open (014, 015, 016, 024), 2 closed (023, 025). CONFLICT: an earlier description said 5 open; the register lists four. [RCFA-SM-26-014] [RCFA-SM-26-015] [RCFA-SM-26-016] [RCFA-SM-26-024] [[rcfa-register]]
- Overdue actions: SM-0135 Uhle rate-of-rise shift check (p1 bottom, due 2026-06-04), SM-0133 felt design review (p2 bottom, due 06-24), SM-0138 Bonvoy watch list (due 07-15), SM-0195 strainer on every outage clean list (due 08-27). [Action SM-0135] [Action SM-0133] [Action SM-0138] [Action SM-0195]
- Completed: SM-0132, SM-0187, SM-0199 (Uhle checks); SM-0136, SM-0189, SM-0200 (vendor design reviews); SM-0139, SM-0141, SM-0196 (strainer, nozzle checks). [Action SM-0139] [Action SM-0141] [Action SM-0196]
- Only the 2026-05-13 Spraywell audit found a badly plugged shower (2nd press top, 22%); 08/05 and 10/21 audits 0-5%. [DOC SW-SA-260513 p.1] [DOC SW-SA-261021 p.1]
- Early-warning rule: Uhle vacuum rising more than 0.1 inHg a day before week 4 of the felt means it is filling. [DOC MP-FA-260526 p.1]
- Nov 11 outage: 1st press bottom and 2nd press top felts are changed (WO 26109296, WO 26108953); the strainer clean is not in the scoped WOs. [WO 26109296] [WO 26108953] [[out-2026-11-11]]
- No plugging RCFA after 2026-08-14 in the RCFA list. [RCFA-SM-26-025]

## Events (tool: rcfa_status; downtime_summary group=equipment)
- 2026-05-12 [[p2-felt-bottom]] plugged, 5.3 h, 166 t; Pi PM1:UHLE_P2B_VAC, PM1:PRESS_SOLIDS about 8 days before; RCFA-SM-26-014, OPEN. [RCFA-SM-26-014]
- 2026-05-13 [[p1-felt-bottom]] plugged, 3.6 h, 112 t; PM1:UHLE_P1B_VAC about 13 days; RCFA-SM-26-015, OPEN. [RCFA-SM-26-015]
- 2026-05-19 [[p2-felt-top]] unplanned felt change, 7.5 h, 232 t; RCFA-SM-26-016, OPEN. [RCFA-SM-26-016]
- 2026-07-21 [[p1-felt-top]] plugged, 5.8 h, 179 t; PM1:UHLE_P1T_VAC about 11 days; RCFA-SM-26-023, closed 2026-08-27. [RCFA-SM-26-023]
- 2026-08-05 [[p1-felt-top]] HP shower nozzles plugged (asset 00072266 1st press top felt HP shower), 2.8 h, 88 t; about 14 days; RCFA-SM-26-024, OPEN. [RCFA-SM-26-024]
- 2026-08-14 [[p1-felt-bottom]] plugged again, 3.4 h, 106 t; PM1:UHLE_P1B_VAC about 10 days; RCFA-SM-26-025, closed 2026-09-25. [RCFA-SM-26-025]
- Six RCFAs total about 28.4 h and 883 t (computed from headers).

## Causes
- Plugging cases (014, 015, 023, 025): "Press felt plugged mid-life; conditioning could not keep it open, so the sheet would not hold". [RCFA-SM-26-014]
- Contributing on those: "Uhle vacuum trend not acted on; shower nozzle checks overdue". [RCFA-SM-26-015]
- 2nd press top felt (026): "filled early: HP shower nozzles plugged (22%) so the felt wasn't conditioned"; contributing: shower nozzles not checked since the Feb audit, heavier 34 Super run in May, strainer on the shower supply not cleaned. [RCFA-SM-26-016]
- 1st press top HP shower (024): "HP shower nozzles plugged: strainer on the shower supply blinded"; contributing: strainer not on the outage clean list. [RCFA-SM-26-024]
- Link to specifics: [[uhle-box-vacuum]], [[press-hp-showers]], [[syphon-differential]] is a different trend (dryers).

## Actions
- Add Uhle vacuum rate-of-rise to shift checks: SM-0132 p2 bottom (Sunniva Brooks) done 2026-06-03; SM-0135 p1 bottom (Tobias Renner) due 2026-06-04 In progress OVERDUE; SM-0187 p1 top done 2026-08-04; SM-0199 p1 bottom done 2026-08-31. [Action SM-0132] [Action SM-0135] [Action SM-0187] [Action SM-0199]
- Review felt design with the felt vendor: SM-0133 p2 bottom (Sunniva Brooks) due 2026-06-24 In progress OVERDUE; SM-0136 p1 bottom done 2026-06-19; SM-0189 p1 top done 2026-08-27; SM-0200 p1 bottom done 2026-09-25. [Action SM-0133] [Action SM-0136] [Action SM-0189] [Action SM-0200]
- Weekly press shower nozzle check by operations (Tobias Renner) done 2026-06-03. [Action SM-0141]
- Clean the HP shower supply strainer every outage (Sunniva Brooks) done 2026-07-01. [Action SM-0139]
- Add Uhle vacuum rate-of-rise to the Bonvoy watch list: SM-0138 (Mei Fairbanks) due 2026-07-15 In progress OVERDUE. [Action SM-0138]
- Add the shower strainer to every outage clean list: SM-0195 (Tobias Renner) due 2026-08-27 In progress OVERDUE. [Action SM-0195]
- Weekly nozzle check for 1st press top felt HP shower: SM-0196 (Ingrid Solberg) done 2026-09-10. [Action SM-0196]

## Vendor evidence (reports library)
- Spraywell audits of the five HP showers: only the 05/13/2026 audit found a shower badly plugged (2nd press top, 22%, strainer packed solid); 02/04, 08/05 and 10/21/2026 showed 0-5% everywhere; see [[press-hp-showers]] [DOC SW-SA-260513 p.1]
- Marlow used-felt analysis MP-FA-260526 of the 2nd press top felt (34 d): fill 71% vs 40-45% typical, 9 cfm vs 19, contaminant stickies, filler and fines; fix "Check the HP shower nozzles weekly and clean the shower supply strainer at every outage" [DOC MP-FA-260526 p.1]; detail [[rcfa-sm-26-016]]
- Early-warning rule: Uhle vacuum rising more than 0.1 inHg a day before week 4 of the felt means it is filling [DOC MP-FA-260526 p.1]; see [[uhle-box-vacuum]]
- Survey view of the plugged felts: the 1st press bottom felt reads 18-19 cfm and 853-891 gsm water at its 12-week end of life, but the stops hit it at about 10-11 weeks (05/13, 08/14) [DOC HF-SV-260304 p.1] [DOC HF-SV-260527 p.1] [RCFA-SM-26-015] [RCFA-SM-26-025]
- Date check on RCFA-SM-26-023: the 1st press top felt was changed 07/08/2026, 13 days before its 07/21 "plugged" stop, although the event text counts a 21-day Uhle climb [DOC HF-SV-260708 p.1] [RCFA-SM-26-023]
- Vendor felt-design reviews (SM-0133 open, SM-0136/0189/0200 completed): the outcome of the completed reviews is not recorded in the vendor surveys, which show no design change; Marlow and Halden keep the same styles (1400/1600 gsm, 1300/1500 gsm) through Sep 2026 [DOC MP-SV-260930 p.1] [DOC HF-SV-260930 p.1]

## Recurrence
- 1st press bottom felt plugged twice (May 13 and Aug 14) and the Uhle shift-check action for it (SM-0135) was still open when the Aug 14 event hit (SM-0199 filed anew, done 2026-08-31). [RCFA-SM-26-015] [RCFA-SM-26-025]
- 1st press top felt: plugged (Jul 21) then HP shower strainer blinded (Aug 5), 15 days apart. [RCFA-SM-26-023] [RCFA-SM-26-024]
- BUS follow-ups on press felts: see [[bus-follow-up-actions]] (1st press top felt conditioning low, 2nd press bottom felt guide hunting, 2nd press top felt sheet breaks).

## Downtime log events (tool: downtime_events; WO and shift report per row)
- Emergency felt washes (cause "Press felt plugged (emergency felt wash)"): 2026-05-12 2nd press bottom felt 321 min WO 26105138 RCFA-SM-26-014, Uhle vacuum climbing and press solids falling for 16 days before [downtime DT-260512-0322]; 2026-05-13 1st press bottom felt 217 min WO 26105159 RCFA-SM-26-015, 26 days before [downtime DT-260513-0327]; 2026-07-21 1st press top felt 347 min WO 26106958 RCFA-SM-26-023, 21 days [downtime DT-260721-0462]; 2026-08-14 1st press bottom felt 206 min WO 26107469 RCFA-SM-26-025, 19 days [downtime DT-260814-0496].
- Unplanned felt change 2026-05-19 2nd press top felt 450 min WO 26105306 RCFA-SM-26-016: "filled at 3 weeks: changed early (Uhle vacuum up 4.6 inHg, 4th section steam at its limit)" [downtime DT-260519-0344]; see [[p2-felt-top]].
- Planned chemical wash 2026-02-21 1st press top felt 164 min WO 26103017: "found Feb 18 (uhle vacuum climbing and press solids falling)", so the precursor was caught and handled planned once, before the May-Aug emergencies [downtime DT-260221-0177].
- HP shower nozzle plugging stops (cause "Press shower nozzles plugged"): 2026-02-07 2nd press bottom felt HP shower 114 min WO 26102793, 25 days of nozzle plugging [downtime DT-260207-0157]; 2026-04-02 1st press top felt HP shower 136 min WO 26104067, 14 days [downtime DT-260401-0236 timestamp 2026-04-02T03:49]; 2026-06-30 1st press top felt HP shower 179 min WO 26106440, 24 days [downtime DT-260630-0417]; 2026-08-05 1st press top felt HP shower 170 min WO 26107287 RCFA-SM-26-024, 27 days [downtime DT-260805-0485]. The first three had no RCFA.
- The 1st press top felt HP shower stopped the machine three times (Apr 2, Jun 30, Aug 5; 485 min total) and an RCFA was only opened on the third. [downtime DT-260401-0236] [downtime DT-260630-0417] [downtime DT-260805-0485]
- Planned chemical wash 2026-10-09 17:00 1st press bottom felt 169 min WO 26108876: "found Oct 08 (uhle vacuum climbing and press solids falling)"; second planned catch after 2026-02-21 (1st press top), and the first on a 1st press bottom felt after the unplanned plugs of 2026-05-13 and 2026-08-14. Washed 1 day after the signal, on day 51 of the felt's run (installed 2026-08-19, target 84 d; computed), see [[p1-felt-bottom]]. No RCFA. [downtime DT-261009-0585] [WO 26108876] [Shift Report PM1-SHIFT-2026-10-09-D]
- No emergency felt wash, felt blow or HP shower stop in the downtime log 2026-09-02 to 2026-10-31; the 2nd press top felt kept breaking (38 breaks) without a plugging stop. [downtime DT-260901-0523 to DT-261030-0629] [[p2-felt-top]]
- Sibling mode (felt blown, not plugged): [[press-felt-blows]].

## Shift reports Feb 2026 (what crews saw before the two February press-felt events; tool: shift_reports)
- 2nd press bottom felt HP shower, stop 2026-02-07 10:26 (114 min unplanned, WO 26102793, no RCFA): the same remark "2nd press bottom felt HP shower: felt looks wet coming out of the nip" was written in the Notes of six shifts first: 02-03 Day (as a question "?"), 02-03 Night, 02-04 Night, 02-05 Day ("Not sure yet; flagging it"), 02-05 Night, 02-06 Day (again "Not sure yet; flagging it"). [Shift Report PM1-SHIFT-2026-02-03-D] [Shift Report PM1-SHIFT-2026-02-05-D] [Shift Report PM1-SHIFT-2026-02-06-D]
- The wet-felt remark was in the Notes only, never in a Handover item, so it did not carry to the next crew's action list; the handovers of those shifts list other items (forming shower oscillator, PV fan, coarse screen, guide hunting). [Shift Report PM1-SHIFT-2026-02-04-N] [Shift Report PM1-SHIFT-2026-02-06-D]
- First sign to stop: about 3.5 days (02-03 day shift to 02-07 10:26). The stop note: "Press shower nozzles plugged: hp shower nozzles plugging for 25 days before"; Day shift 02-07 was 251 t with 3 breaks (crew B, 1.9 h down). [Shift Report PM1-SHIFT-2026-02-07-D]
- The wet-felt remark does not appear after the stop (02-07 Night, 02-08 onward). [Shift Report PM1-SHIFT-2026-02-07-N]
- 1st press top felt, planned chemical wash 2026-02-21 13:00 (164 min, WO 26103017): first handover item 02-18 Day "uhle vacuum climbing and press solids falling: the felt is filling -> raise HP shower pressure and check the nozzles" (repeated 02-18 N, 02-19 D and N). [Shift Report PM1-SHIFT-2026-02-18-D] [Shift Report PM1-SHIFT-2026-02-19-N]
- 02-20 Day/Night: WO 26103017 added and "chemical felt wash planned"; 02-20 Night notes "trend still moving". [Shift Report PM1-SHIFT-2026-02-20-D] [Shift Report PM1-SHIFT-2026-02-20-N]
- 02-21 Day: wash done as a 2.7 h planned stop, "lockouts verified before work started" (crew D); 285 t, 74.2% sheet on. 02-22 onward the item is not in the handovers. [Shift Report PM1-SHIFT-2026-02-21-D]
- Lead time first handover to wash: about 3 days (02-18 to 02-21); the felt was installed 2026-01-21 so about 28 d old at the first sign (computed) of an 84 d target. [Shift Report PM1-SHIFT-2026-02-18-D] [position_life p1-felt-top]
- After the wash the item turned into "1st press top felt: conditioning low -> raise Uhle vacuum setpoint 0.5 inHg" (02-23 Day to 02-25 Night); earlier "conditioning low -> holding" on 02-01 and 02-02 and again 02-27/02-28 Night. BUS follow-up SM-0073 (2026-02-26). [Shift Report PM1-SHIFT-2026-02-23-D] [Shift Report PM1-SHIFT-2026-02-27-D] [Action SM-0073]
- Contrast: the Feb 7 shower stop had crew remarks but no Uhle trend item; the Feb 21 wash had the Uhle/solids trend in handover and a WO two days before. See [[p1-felt-top]], [[p2-felt-bottom]], [[press-hp-showers]], [[uhle-box-vacuum]].

## Shift reports Mar 2026 (flag before the 2026-04-02 1st press top HP shower stop; detail [[p1-felt-top]])
- 03-25 Day to 03-31 Day the crews flagged "1st press top felt HP shower: felt looks wet coming out of the nip" six times (03-27 naming UHLE_P1T_VAC and PRESS_SOLIDS) and ran "conditioning low → raise Uhle vacuum setpoint 0.5 inHg" 03-26 to 03-28; the stop followed on 2026-04-02 (136 min, WO 26104067, no RCFA). [Shift Report PM1-SHIFT-2026-03-25-D] [Shift Report PM1-SHIFT-2026-03-27-D] [downtime DT-260401-0236]
- Blown 2nd press bottom felt 03-21 had a guide-hunting flag 03-12/13: see [[press-felt-blows]].

## WO hours for the Jun-Aug 2026 events (WO extract work-orders-3; labour hours est / act, not downtime; all type 3 Emergency, prio 1)
- 2026-06-30 1st press top felt HP shower nozzles plugged: 8.9 h / 9.8 h, "hp shower nozzles plugging for 24 days before". [WO 26106440]
- 2026-07-21 (done 07-22) 1st press top felt emergency felt wash: 17.4 h / 19.1 h, "uhle vacuum climbing and press solids falling for 21 days before". [WO 26106958]
- 2026-08-05 1st press top felt HP shower nozzles plugged: 8.5 h / 9.4 h, "...for 27 days before". [WO 26107287]
- 2026-08-14 1st press bottom felt emergency felt wash: 10.3 h / 11.3 h, "...for 19 days before". [WO 26107469]
- Lead times in these WO notes (24, 21, 27, 19 d) are the log-text values; RCFAs quote Pi trends that are shorter or longer, see [[precursor-lead-times]].
- Weekly "Press shower nozzle check" on the 2nd press top felt HP shower ran every week through these events (16 WOs 06-18 to 09-29, [[p2-felt-top]]); no equivalent weekly check WO on the 1st press top felt HP shower (asset 00072266) in the Jun-Sep extract, where all three nozzle/plugging emergencies happened ([[p1-felt-top]]). Outage WOs "Change HP shower nozzles, press section" were on asset 00072329 only: 2026-08-19 [WO 26106720], 2026-09-30 [WO 26107784]. [WO 26105922] [WO 26107784]

## Run-history evidence (position_life; added from the positions batch)
- [[p2-felt-top]] run 2026-04-15 to 2026-05-19 ended at 33 d vs target 42 d, reason performance: "Filled at 3 weeks: Uhle vacuum up 4.6 inHg, press solids down 1.8 points, 4th section steam at its limit on 34 Super. Changed early in a 7.5 h shut. 22% of the HP shower nozzles were plugged (Spraywell audit May 13)." [position_life p2-felt-top]
- Earlier performance pull: [[p1-felt-top]] run 2025-05-14 to 2025-08-06 (83 d vs 84 d, reason performance): "Pulled a cycle early: drainage falling off, couldn't hold speed on 34 Super." The same wording is on the [[form-bottom]] run 2025-01-08 to 2025-04-02. [position_life p1-felt-top] [position_life form-bottom]
- Mild edge filling cleaned by the HP shower at mid-life is a routine remark on many 83 d / 41 d felt runs (p1-felt-bottom, p1-felt-top, p2-felt-bottom, p2-felt-top). [position_life p1-felt-bottom] [position_life p2-felt-bottom]

## Bonvoy evidence (tool: bonvoy_exceptions tag=UHLE_P*_VAC; detail in [[uhle-box-vacuum]])
- Matches: 1st press bottom felt 05-05 -> 05-13 (daily max 13.98) and 08-02 -> 08-14 (14.29); 2nd press top felt 05-10 -> 05-19 (14.59). [Bonvoy PM1:UHLE_P1B_VAC 2026-08-14] [Bonvoy PM1:UHLE_P2T_VAC 2026-05-19]
- Not found in Bonvoy exceptions: UHLE_P2B_VAC around 2026-05-12 (RCFA-SM-26-014) and UHLE_P1T_VAC around 2026-07-21 / 08-05 (RCFA-SM-26-023 / -024); nearest P1T episode was 06-19 -> 06-30. [Bonvoy PM1:UHLE_P1T_VAC 2026-06-30]
- Uhle vacuum also rises before planned changes (P2B 2026-01-07..21 to the 01-21 change; P1T 2026-06-19..30 before 07-08): not every episode is an unplanned plug. [Bonvoy PM1:UHLE_P2B_VAC 2026-01-21]
- Marlow's rule of thumb (more than 0.1 inHg a day before week 4 = filling) is in [[p2-felt-top]]; the May P2T episode rose about 0.2 inHg/day in daily max. [Bonvoy PM1:UHLE_P2T_VAC 2026-05-19]

## Work orders Feb-Jun 2026 (work-orders-2; see [[emergency-work-orders-feb-jun-2026]])
- Planned chemical wash WO 26103017 "Press felt chemical wash (planned): 1st press top felt", type 1 Corrective prio 1, requested 2026-02-18, planned and completed 02-21, MILL Beatrix Hale, est 8.2 h act 9 h. [WO 26103017]
- Emergency WOs: 26104067 1st press top felt HP shower nozzles plugged (04-01, est 6.8 h act 7.5 h, "hp shower nozzles plugging for 14 days before"); 26105138 2nd press bottom felt plugged (05-12, 16 / 17.6 h, "16 days before"); 26105159 1st press bottom felt plugged (05-13, 10.8 / 11.9 h, "26 days before"); 26105306 2nd press top felt changed early (05-19, 22.5 / 24.8 h). [WO 26104067] [WO 26105138] [WO 26105159] [WO 26105306]
- Weekly "Press shower nozzle check" WOs (asset 00072329, 2nd press top felt HP shower, OPS Operations, 1 h) were Closed on 17 dates 2026-02-17 to 06-09, so the RCFA-SM-26-016 statement that nozzles were not checked conflicts with the WO record (details in [[work-orders-feb-jun-2026]]). [WO 26104984] [RCFA-SM-26-016]
- Outage jobs that condition the press felts: "Change HP shower nozzles, press section" WO 26103479 ([[out-2026-04-15]], 6/6.6 h), WO 26104543 ([[out-2026-05-27]], 8/8.8 h), WO 26105691 ([[out-2026-07-08]], 4/4.4 h), all OPS; "Inspect and clean Uhle box covers" (1st press top felt Uhle box) WO 26103535 and WO 26104592 (6/6.6 h each). The 2nd press bottom felt shower and the 1st press shower have no check WO in the extract. [WO 26103479] [WO 26104543] [WO 26105691] [WO 26103535] [WO 26104592]
