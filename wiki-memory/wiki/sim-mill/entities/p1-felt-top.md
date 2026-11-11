---
name: p1-felt-top
description: 1st press top felt (asset 00072252), 84 d target; one early pull 2025-08-06 for drainage; current run 30 d
type: position
aliases: ["1st press top felt", "asset 00072252", "P1 top felt"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108792 "Inspect and clean Uhle box covers" (asset 00072259, 1st press top felt Uhle box, OPS, 8 h, parts Reserved). The felt itself is not due (30 d of 84 d); no felt change WO. See [[uhle-box-vacuum]]. [WO 26108792]

## Run history (tool: position_life p1-felt-top)
- 2025-02-19 to 2025-05-14: 83 d vs target 84 d, planned, HFC-39748. [position_life p1-felt-top]
- 2025-05-14 to 2025-08-06: 83 d vs target 84 d, reason performance, HFC-40139; pulled a cycle early, drainage falling off, couldn't hold speed on 34 Super. [position_life p1-felt-top]
- 2025-08-06 to 2025-10-29 (HFC-40212) and 2025-10-29 to 2026-01-21 (HFC-40349) and 2026-04-15 to 2026-07-08 (HFC-40400): some filling at the edges, HP shower cleaned at mid-life. [position_life p1-felt-top]
- 2026-01-21 to 2026-04-15 (HFC-40368, [[out-2026-01-21]] to [[out-2026-04-15]]); 2026-07-08 to 2026-09-30 (HFC-40440, [[out-2026-07-08]] to [[out-2026-09-30]]): normal wear. [position_life p1-felt-top]
- Changeover dates: 2025-02-19, 05-14, 08-06, 10-29, 2026-01-21, 04-15, 07-08, 09-30. [position_life p1-felt-top]

## Shift reports Feb 2026 (felt installed 2026-01-21; filling at about 4 weeks)
- 02-18 Day first handover "uhle vacuum climbing and press solids falling: the felt is filling -> raise HP shower pressure and check the nozzles"; WO 26103017 and "chemical felt wash planned" on 02-20; wash done 02-21 13:00, 164 min planned. Detail and lead time in [[press-felt-plugging]]. [Shift Report PM1-SHIFT-2026-02-18-D] [Shift Report PM1-SHIFT-2026-02-20-D] [Shift Report PM1-SHIFT-2026-02-21-D]
- "conditioning low": 02-01 Day/Night "holding"; 02-23 Day to 02-25 Night "raise Uhle vacuum setpoint 0.5 inHg"; 02-27 Day/Night "holding". BUS SM-0073 (02-26). [Shift Report PM1-SHIFT-2026-02-01-D] [Shift Report PM1-SHIFT-2026-02-23-D] [Shift Report PM1-SHIFT-2026-02-27-N]

## Current run
- Installed 2026-09-30, running: 30 d vs target 84 d, serial HFC-40451 (as of 2026-10-30). [position_life p1-felt-top]
- Computed: 84 d reached about 2026-12-23; not due at [[out-2026-11-11]].

## Details
- Felt: Halden Felt Co. seamed felt, 1300 gsm ([[halden-felt-co]]). [position_life p1-felt-top]
- Linked equipment: [[uhle-box-vacuum]] (Pi PM1:UHLE_P1T_VAC), [[equipment-tree]]. [equipment 00072259] [equipment 00072266]
- Failure mode: early pull for drainage, see [[press-felt-plugging]].

## Vendor surveys and RCFAs (reports library)
- Spec/target in the clothing-life table: 12 weeks, Halden seamed felt 1300 gsm [DOC SM-REF-02 p.1]
- Halden surveys at each outage (analyst Joel Abernathy): felt at 5.9 wk is "Good. Continue" (caliper about 2.79-2.84 mm, 24-25 cfm, 725-761 gsm water) [DOC HF-SV-260304 p.1] [DOC HF-SV-260527 p.1] [DOC HF-SV-260819 p.1]
- Felt at 11.9 wk is "End of life. Change at this outage as planned": 01/21/2026 (875 gsm, 19 cfm) [DOC HF-SV-260121 p.1]; 04/15/2026 (871 gsm, 18 cfm) [DOC HF-SV-260415 p.1]; 07/08/2026 (896 gsm, 18 cfm) [DOC HF-SV-260708 p.1]; 09/30/2026 (900 gsm, 18 cfm) [DOC HF-SV-260930 p.1]
- Felt installed 10/29/2025 was 5.9 wk at 12/10/2025 and "Good. Continue" [DOC HF-SV-251210 p.1]
- RCFA-SM-26-023: 1st press top felt plugged, emergency felt wash 07/21/2026 20:33, 5.8 h, 179 t, WO 26106958; Pi trend (PM1:UHLE_P1T_VAC, PM1:PRESS_SOLIDS) about 11 days, event text says Uhle vacuum climbing and press solids falling for 21 days; status Closed [RCFA-SM-26-023]
- Date check: the felt had been changed 07/08/2026, 13 days before this stop (computed), yet the event text puts the Uhle climb 21 days back, i.e. before the change; not explained in [RCFA-SM-26-023]
- RCFA-SM-26-023 actions: SM-0187 Uhle rate-of-rise in shift checks (Ingrid Solberg, 08/12/2026, Completed); SM-0189 felt design review with vendor (Sunniva Brooks, 09/02/2026, Completed) [RCFA-SM-26-023]
- RCFA-SM-26-024: 1st press top felt HP shower nozzles plugged, 08/05/2026 14:37, 2.8 h, 88 t, WO 26107287, root cause shower supply strainer blinded and not on the outage clean list; status Open; SM-0195 add strainer to every outage clean list (Tobias Renner, due 08/27/2026, In progress) [Action SM-0195]; SM-0196 weekly nozzle check (Ingrid Solberg, Completed) [RCFA-SM-26-024]
- Shower audit shows 1st press top HP shower 5% plugged 02/04/2026, 0% 05/13, 4% 08/05 and 0% 10/21/2026. CONFLICT: the Spraywell audit on 08/05/2026 found this shower OK at 4%, the same day RCFA-SM-26-024 logged the 1st press top HP shower nozzles plugged (stop 14:37) [DOC SW-SA-260204 p.1] [DOC SW-SA-260513 p.1] [DOC SW-SA-260805 p.1] [DOC SW-SA-261021 p.1]; see [[press-hp-showers]]
- Related: [[press-felt-plugging]], [[outage-clothing-changes]], [[rcfa-register]]

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- "1st press top felt conditioning low": 5 issues, Sunniva Brooks, "Raise Uhle vacuum setpoint 0.5 inHg" then "Holding": 2025-11-13 (7 days), 2026-01-15 (12 days), 01-30, 02-22 (11 days), 03-26 (7 days). No WO. [BUS 2025-11-13 issue 06a352e6794f52bf] [BUS 2026-03-26 issue 923bbc1aacb655d9]
- 2026-02-18 issue (felt installed 2026-01-21, about 4 weeks old): "Uhle vacuum climbing and press solids falling: the felt is filling", WO 26103017, "Raise HP shower pressure and check the nozzles", chemical felt wash planned 02-20, closed 02-21 "Done; running normal". [BUS 2026-02-18 issue 7fb0a0196a496e16]
- 2026-04-01 issue: 1st press top felt HP shower (asset 00072266) nozzles plugged, 2.3 h down, WO 26104067, "hp shower nozzles plugging for 14 days before"; closed 04-03. See [[press-felt-plugging]]. [BUS 2026-04-01 issue cb3f9c18e38705ae]

## BUS issues Jun-Oct 2026 (Gloria Nakamura for stops, Sunniva Brooks for conditioning; list in [[bus-issue-sheet]])
- 2026-06-30 press shower nozzles plugged 3.0 h ("hp shower nozzles plugging for 24 days before"), WO 26106440; 2026-08-05 again 2.8 h (27 days before), WO 26107287; asset 00072266 "1st press top felt HP shower". [BUS 2026-06-30 .. BUS 2026-07-01 | issue c322abd4b9113a6e] [BUS 2026-08-05 .. BUS 2026-08-06 | issue 42ca6aa845d8c9e4] See [[press-hp-showers]].
- 2026-07-21 felt plugged (emergency felt wash) 5.8 h, 21 days of Uhle vacuum climbing, WO 26106958. [BUS 2026-07-21 .. BUS 2026-07-24 | issue 7608f66831922b8a]
- "1st press top felt conditioning low" (asset 00072252): 7 issues 07-12 (4 days), 07-20 (19 days, three cycles), 08-12 (15 days), 09-01 (7 days), 09-10, 10-06, 10-10; each "Raise Uhle vacuum setpoint 0.5 inHg" then "Holding"; the setpoint was raised repeatedly rather than the cause fixed. [BUS 2026-07-20 .. BUS 2026-08-04 | issue 8b6fd3b508a6179a] [BUS 2026-08-12 .. BUS 2026-08-21 | issue ef61364b82a744c8]

## BUS follow-ups (see [[bus-follow-up-actions]])
- "1st press top felt conditioning low", Sunniva Brooks: SM-0073 (2026-02-26), SM-0099 (2026-03-26), SM-0197 (2026-08-13), SM-0231 (2026-10-06), SM-0237 (2026-10-16), all Completed; SM-0179 (2026-07-21, follow-up of the plugging stop, Gloria Nakamura) Completed; SM-0104 (2026-04-01, press shower nozzles plugged 2.3 h, Gloria Nakamura) Completed. Conditioning-low follow-ups continued after RCFA-SM-26-023/-024. [Action SM-0237] [Action SM-0179] [Action SM-0104]

## What crews saw in Nov 2025 (shift reports; felt installed 2025-10-29)
- "1st press top felt: conditioning low → raise Uhle vacuum setpoint 0.5 inHg" on every handover 2025-11-13 Day to 2025-11-15 Night (6 shifts), the first such conditioning item at week 2 of the run. Action taken: raise the Uhle setpoint 0.5 inHg; outcome not recorded after 11-15. [Shift Report PM1-SHIFT-2025-11-13-D] [Shift Report PM1-SHIFT-2025-11-15-N]
- Same wording recurs as BUS actions from 2026-02-26 (SM-0073); see list above and [[uhle-box-vacuum]]. [Action SM-0073]

## Shift reports Jan 2026
- Handover "1st press top felt: conditioning low -> raise Uhle vacuum setpoint 0.5 inHg" on 01-17 (Day/Night), 01-22 (Day/Night), 01-30 and 01-31 (Day/Night); 01-23 "holding". Run HFC-40349 ended at the 01-21 change; the same item reappears on the new felt HFC-40368 from 01-22. [Shift Report PM1-SHIFT-2026-01-17-D] [Shift Report PM1-SHIFT-2026-01-23-D] [Shift Report PM1-SHIFT-2026-01-30-D]

## Shift reports Mar 2026: early signs before the 2026-04-02 HP shower stop (see [[shift-handover-signals-2026-03]])
- 03-25 Day (crew B): "Something to look at on the 1st press top felt HP shower: felt looks wet coming out of the nip. Not sure yet; flagging it." Repeated 03-25 Night, 03-27 Day (naming UHLE_P1T_VAC and PRESS_SOLIDS), 03-28 Night, 03-29 Night and 03-31 Day. [Shift Report PM1-SHIFT-2026-03-25-D] [Shift Report PM1-SHIFT-2026-03-27-D] [Shift Report PM1-SHIFT-2026-03-31-D]
- Handover items "1st press top felt: conditioning low → raise Uhle vacuum setpoint 0.5 inHg" 03-26 Day through 03-28 Night (matches BUS SM-0099, 2026-03-26). [Shift Report PM1-SHIFT-2026-03-26-D] [Shift Report PM1-SHIFT-2026-03-28-N] [Action SM-0099]
- The flags line up with the Bonvoy UHLE_P1T_VAC episode 2026-03-27 to 04-01 and came 8 days (03-25) before the 1st press top felt HP shower stop of 2026-04-02 (136 min, WO 26104067, no RCFA; log says nozzle plugging for 14 days). The crews' "felt looks wet" flag is the earliest human sign in the record for that stop. [Bonvoy PM1:UHLE_P1T_VAC 2026-04-01] [downtime DT-260401-0236]
- Related BUS follow-up after the stop: SM-0104 (2026-04-01, press shower nozzles plugged 2.3 h). [Action SM-0104] See [[press-felt-plugging]], [[press-hp-showers]].

## Work orders Jun-Sep 2026 (WO extract work-orders-3)
- Emergencies on this position (type 3, prio 1, requested and completed the same day; labour hours est / act): 2026-06-30 "Press shower nozzles plugged: 1st press top felt HP shower" (asset 00072266) 8.9 h / 9.8 h, "hp shower nozzles plugging for 24 days before" [WO 26106440]; 2026-07-21 (completed 07-22) "Press felt plugged (emergency felt wash): 1st press top felt" (asset 00072252) 17.4 h / 19.1 h, "uhle vacuum climbing and press solids falling for 21 days before" [WO 26106958]; 2026-08-05 "Press shower nozzles plugged" again 8.5 h / 9.4 h, "...for 27 days before" [WO 26107287]. All MECH/MILL Beatrix Hale.
- Dates against runs: the 06-30 nozzle event fell in the previous felt's run (HFC-40400, out 07-08); the 07-21 wash and the 08-05 nozzle event fell in the felt installed 07-08 and removed 09-30 (HFC-40440, 83 d). [position_life p1-felt-top] [WO 26106440] [WO 26106958] [WO 26107287]
- Change at [[out-2026-09-30]]: WO 26107749 "Change 1st press top felt", MILL, 10 h est / 11 h act, "Removed after 83 days. Normal wear at removal." [WO 26107749]
- Uhle box: outage "Inspect and clean Uhle box covers" (asset 00072259 1st press top felt Uhle box, OPS Operations, type 4): 2026-07-08 8 h est [WO 26105747]; 2026-08-19 6 h est [WO 26106776]; 2026-09-30 4 h est [WO 26107840]. The hours fall at each outage even though plugging recurred. See [[press-felt-plugging]], [[work-orders-jun-sep-2026]].

## Bonvoy (tag PM1:UHLE_P1T_VAC, 20 tag-days; see [[uhle-box-vacuum]])
- Episodes: 2026-01-09 (9 h, max 11.76, 12 days before the 01-21 change); 2026-03-27 -> 2026-04-01 (6 d, max 12.65; change 04-15); 2026-06-19 -> 2026-06-30 (12 d, max 11.91 -> 12.86; change 07-08); 2026-09-29 (5 h, max 12.25, day before the 09-30 change). [Bonvoy PM1:UHLE_P1T_VAC 2026-04-01] [Bonvoy PM1:UHLE_P1T_VAC 2026-06-30] [Bonvoy PM1:UHLE_P1T_VAC 2026-09-29]
- Nothing flagged on this tag in July-August, although RCFA-SM-26-023 (2026-07-21) cites PM1:UHLE_P1T_VAC about 11 days before; the 06-19..30 episode is the nearest (plugging 3 weeks before). [RCFA-SM-26-023]
- Nothing flagged on the current felt (installed 2026-09-30) through 2026-10-31. [Bonvoy PM1:UHLE_P1T_VAC 2026-09-29]

## BUS issue Oct 2026
- Issue 82ff70c222af914a (10-16 to 10-22, Sunniva Brooks): conditioning low; "Raise Uhle vacuum setpoint 0.5 inHg" (10-16/17), closed 10-22 "Holding". Matches SM-0237. See [[uhle-box-vacuum]], [[bus-issues-2026-10-late]]. [BUS 2026-10-16] [BUS 2026-10-22]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- 26101421 "Change 1st press top felt" at [[out-2026-01-21]] (type 4, MILL Beatrix Hale, est 10 h act 11 h): "Removed after 83 days. Some filling at the edges; cleaned with the HP shower at mid-life." [WO 26101421]
- "Inspect and clean Uhle box covers" (asset 00072259, 1st press top felt Uhle box, OPS) at each outage: 26100483 (2025-12-10, 8.8 h), 26101491 (2026-01-21, 6.6 h), 26102555 (2026-03-04, 8.8 h). [WO 26100483] [WO 26101491] [WO 26102555]
- The felt was not changed at 12-10 or 03-04 (those outages changed the 1st press bottom felt, [[p1-felt-bottom]]); see [[outage-standard-wo-package]]. [WO 26100413] [WO 26102485]

## Work orders Feb-Jun 2026 (work-orders-2)
- "Change 1st press top felt" (asset 00072252, MILL Beatrix Hale, type 4 prio 2, est 10 h act 11 h): WO 26103451 at [[out-2026-04-15]], note "Removed after 83 days. Normal wear at removal."; WO 26105656 at [[out-2026-07-08]], note "Removed after 83 days. Some filling at the edges; cleaned with the HP shower at mid-life." Same as position_life. [WO 26103451] [WO 26105656]
- Planned chemical wash WO 26103017 (done 2026-02-21, 9 h) and emergency HP shower plugging WO 26104067 (04-01, "14 days before"): [[press-felt-plugging]], [[emergency-work-orders-feb-jun-2026]]. [WO 26103017] [WO 26104067]
- Uhle box cover clean on this felt's Uhle box (asset 00072259), OPS, est 6 h act 6.6 h: WO 26103535 (04-15) and WO 26104592 (05-27). [WO 26103535] [WO 26104592]
