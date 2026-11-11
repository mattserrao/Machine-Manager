---
name: p1-felt-bottom
description: 1st press bottom felt (asset 00072273), 84 d target; changed every outage; current run 72 d, reaches target at the 2026-11-11 outage
type: position
aliases: ["1st press bottom felt", "asset 00072273", "P1 bottom felt"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26109296 "Change 1st press bottom felt" (asset 00072273, MILL Beatrix Hale, 8 h, parts Reserved, Scheduled); reaches its 84 d target on 2026-11-11. [WO 26109296]
- Planned chemical wash WO 26108876 "Press felt chemical wash (planned): 1st press bottom felt", prio 1, planned and completed 2026-10-09, est 8.4 h act 9.2 h. [WO 26108876]

## Run history (tool: position_life p1-felt-bottom)
- Eight consecutive planned runs of 83 d vs target 84 d, 2025-01-08 to 2026-08-19, all "worn". [position_life p1-felt-bottom]
- 2025-01-08 to 2025-04-02 (HFC-39981): some filling at the edges, cleaned with the HP shower at mid-life. [position_life p1-felt-bottom]
- 2025-06-25 to 2025-09-17 (HFC-40303): ran to target; caliper and air perm within the vendor's end-of-life range. [position_life p1-felt-bottom]
- 2025-12-10 to 2026-03-04 (HFC-40466, [[out-2025-12-10]] to [[out-2026-03-04]]) and 2026-03-04 to 2026-05-27 (HFC-40484): some filling at the edges, HP shower cleaned at mid-life. [position_life p1-felt-bottom]
- 2026-05-27 to 2026-08-19 (HFC-40522, [[out-2026-05-27]] to [[out-2026-08-19]]): normal wear. [position_life p1-felt-bottom]
- Changeover dates: 2025-01-08, 2025-04-02, 2025-06-25, 2025-09-17, 2025-12-10, 2026-03-04, 2026-05-27, 2026-08-19. [position_life p1-felt-bottom]

## Current run
- Installed 2026-08-19, running: 72 d vs target 84 d, serial HFC-40543 (as of 2026-10-30). [position_life p1-felt-bottom]
- Computed: 84 d is reached 2026-11-11, the date of [[out-2026-11-11]]; expect it to be due for change there (WO scope not in this batch).

## Details
- Felt: Halden Felt Co. endless felt, 1500 gsm ([[halden-felt-co]]). [position_life p1-felt-bottom]
- Linked equipment: [[uhle-box-vacuum]] (Pi PM1:UHLE_P1B_VAC), [[equipment-tree]]. [equipment 00072280] [equipment 00072287]

## Vendor surveys and RCFAs (reports library)
- Spec/target: 12 weeks, Halden endless felt 1500 gsm [DOC SM-REF-02 p.1]
- Halden survey 12/10/2025: felt installed 09/17/2025 at 11.9 wk, 889 gsm, 19 cfm, "End of life. Change at this outage as planned" [DOC HF-SV-251210 p.1]
- Same pattern at 03/04/2026 (installed 12/10/2025, 853 gsm, 18 cfm) [DOC HF-SV-260304 p.1], 05/27/2026 (installed 03/04, 891 gsm, 18 cfm) [DOC HF-SV-260527 p.1], 08/19/2026 (installed 05/27, 871 gsm, 19 cfm) [DOC HF-SV-260819 p.1]; each "12 weeks against a 12-week target; changed at this outage"
- Mid-life surveys at 5.9 wk are "Good. Continue" (2.80 mm, 25-26 cfm) [DOC HF-SV-260121 p.1] [DOC HF-SV-260415 p.1] [DOC HF-SV-260708 p.1] [DOC HF-SV-260930 p.1]
- Installed 08/19/2026 and 5.9 wk "Good. Continue" at 09/30/2026 [DOC HF-SV-260930 p.1]; reaches 12 weeks on 11/11/2026 (computed: 08/19 + 84 d), see [[out-2026-11-11]]
- RCFA-SM-26-015: emergency felt wash 05/13/2026 14:16, 3.6 h, 112 t, WO 26105159; Uhle vacuum climbing and press solids falling for 26 days (Pi trend about 13 days: PM1:UHLE_P1B_VAC, PM1:PRESS_SOLIDS); status Open; SM-0135 Uhle rate-of-rise shift checks (Tobias Renner, due 06/04/2026, In progress); SM-0136 felt design review (Ingrid Solberg, Completed) [RCFA-SM-26-015]
- RCFA-SM-26-025: emergency felt wash 08/14/2026 18:54, 3.4 h, 106 t, WO 26107469; trend 19 days (Pi about 10 days); status Closed; SM-0199 and SM-0200 Completed [RCFA-SM-26-025]
- Both stops hit this felt late in its run (about 10 and 11 weeks); the same felt ran to 12 weeks in the other cycles [RCFA-SM-26-015] [RCFA-SM-26-025]
- Shower audits: 1st press bottom HP shower 4% plugged 02/04, 05/13, 08/05, 10/21/2026, all OK [DOC SW-SA-260204 p.1] [DOC SW-SA-260513 p.1] [DOC SW-SA-260805 p.1] [DOC SW-SA-261021 p.1]
- Related: [[press-felt-plugging]], [[press-hp-showers]], [[outage-clothing-changes]], [[rcfa-register]]

## BUS issues Apr-Oct 2026 (owner Gloria Nakamura unless noted; list in [[bus-issue-sheet]])
- 2026-05-03 felt blown 2.2 h, WO 26104942 ("Crew pulling a new felt"). [BUS 2026-05-03 .. BUS 2026-05-05 | issue d1aaf49038fbf64d]
- 2026-05-13 felt plugged (emergency felt wash) 3.6 h, "Uhle vacuum climbing and press solids falling for 26 days before", WO 26105159. [BUS 2026-05-13 .. BUS 2026-05-15 | issue dc941602601e3655]
- 2026-07-20 felt blown 2.6 h, WO 26106944. [BUS 2026-07-20 .. BUS 2026-07-22 | issue 73a73a0256a1c4b0]
- 2026-08-14 felt plugged 3.4 h, 19 days before, WO 26107469. [BUS 2026-08-14 .. BUS 2026-08-16 | issue a6fc5c5accc64e71]
- 2026-10-08 "felt is filling" (Uhle vacuum climbing, solids falling): raise HP shower pressure and check the nozzles, WO 26108876, owner Sunniva Brooks, closed 10-09 "Done; running normal" (before the 10-09 chemical wash below). [BUS 2026-10-08 .. BUS 2026-10-09 | issue 8ae05bd2913c8b62]

## BUS follow-ups
- SM-0125 press felt blown, 2.2 h down, "Crew pulling a new fel..." (created 2026-05-03, Gloria Nakamura, Completed 2026-05-08), 10 days before RCFA-SM-26-015; SM-0130 follow-up of the 2026-05-13 plugging stop (Completed 2026-05-18). [Action SM-0125] [Action SM-0130] See [[bus-follow-up-actions]].

## Work orders Jun-Sep 2026 (WO extract work-orders-3)
- Change at [[out-2026-08-19]]: WO 26106706 "Change 1st press bottom felt" (asset 00072273), type 4, MILL Beatrix Hale, 10 h est / 11 h act: "Removed after 83 days. Normal wear at removal." Even though the felt was emergency-washed on 08-14 (WO 26107469) and blown on 07-20 (WO 26106944), the removal note says normal wear. [WO 26106706] [WO 26107469] [WO 26106944]
- Emergency WOs in this run (type 3, prio 1; hours are labour hours): WO 26106944 press felt blows, 2026-07-20, 7.7 h est / 8.5 h act, "Press felt blown. Crew pulling a new felt." [WO 26106944]; WO 26107469 press felt plugged (emergency felt wash), 2026-08-14, 10.3 h est / 11.3 h act, "uhle vacuum climbing and press solids falling for 19 days before". [WO 26107469]
- CONFLICT: a new felt was being pulled on 2026-07-20 per WO 26106944, yet the 08-19 WO says the removed felt had run 83 days (installed about 2026-05-28); see [[press-felt-blows]]. Check position_life p1-felt-bottom for the install dates.
- Next change due: [[out-2026-11-11]] (WO 26109296 in that outage's scope). See [[work-orders-jun-sep-2026]].

## Bonvoy (tag PM1:UHLE_P1B_VAC, 23 tag-days; see [[uhle-box-vacuum]])
- Uhle vacuum episodes: 2026-02-17 (5 h, max 11.5); 2026-05-05 -> 2026-05-13 (9 d, max 12.37 -> 13.98); 2026-08-02 -> 2026-08-14 (13 d, max 11.89 -> 14.29, 18-24 h/day). [Bonvoy PM1:UHLE_P1B_VAC 2026-05-13] [Bonvoy PM1:UHLE_P1B_VAC 2026-08-14]
- Both big episodes end on the RCFA plugging dates (05-13 RCFA-SM-26-015, 08-14 RCFA-SM-26-025); Bonvoy shows 9 and 13 flagged days vs the RCFAs' 13 and 10 days. The Aug episode ends 5 days before the 2026-08-19 change. [RCFA-SM-26-015] [RCFA-SM-26-025] [position_life p1-felt-bottom]
- Mode: [[press-felt-plugging]].

## Mid-run chemical wash 2026-10-09 (downtime log)
- 2026-10-09 17:00 planned "Press felt chemical wash (planned)" 169 min, WO 26108876, grade 24#, crew C: "found Oct 08 (uhle vacuum climbing and press solids falling)". On the felt installed 2026-08-19, day 51 of the 84 d target (computed). [downtime DT-261009-0585] [WO 26108876] [Shift Report PM1-SHIFT-2026-10-09-D]
- The two earlier plugging events on this position (2026-05-13, 2026-08-14) were unplanned emergency washes (217 and 206 min, RCFA-SM-26-015 and -025); this one was planned and 169 min. [downtime DT-260513-0327] [downtime DT-260814-0496]
- Whether the wash relieved the vacuum climb (Bonvoy UHLE_P1B_VAC after 2026-10-09) is not in this batch; tool: bonvoy_exceptions tag=UHLE_P1B_VAC. See [[uhle-box-vacuum]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Outage change WOs (type 4, MILL Beatrix Hale, est 10 h act 11 h): 26100413 at [[out-2025-12-10]] "Removed after 83 days. Normal wear at removal." and 26102485 at [[out-2026-03-04]] "Removed after 83 days. Some filling at the edges; cleaned with the HP shower at mid-life." Both Closed on the outage date. [WO 26100413] [WO 26102485]

## Work orders Feb-Jun 2026 (work-orders-2)
- "Change 1st press bottom felt" WO 26104529 (asset 00072273, [[out-2026-05-27]], MILL Beatrix Hale, type 4 prio 2, est 10 h act 11 h): "Removed after 83 days. Some filling at the edges; cleaned with the HP shower at mid-life." No change WO for this position at 04-15 or in the 07-08 WOs of this extract (it changes at the 05-27 / 08-19 cycle). [WO 26104529]
- Emergency WOs: 26104942 press felt blown 2026-05-03 (6.8 / 7.5 h) and 26105159 press felt plugged, emergency wash 2026-05-13 (10.8 / 11.9 h, "uhle vacuum climbing and press solids falling for 26 days before"; RCFA-SM-26-015). The felt (installed 03-04) was 70 days old on 05-13 and was changed 14 days later (computed). See [[press-felt-blows]], [[emergency-work-orders-feb-jun-2026]]. [WO 26104942] [WO 26105159]
