---
name: p2-felt-top
description: 2nd press top felt (Marlow, seamed 1400 gsm, 6-week target): run history Oct 2025-Sep 2026, the early 5/19 change (RCFA-SM-26-016), current run. Read for felt-life, plugging and Uhle questions on the 2nd press top.
type: position
aliases: ["2nd press top felt", "P2 top felt", "p2-felt-top", "MPF-40661", "Seamed felt 1400 gsm"]
---
## Current picture (as of 2026-10-31; wiki may lag, re-fetch position_life p2-felt-top)
- Current felt installed 09/30/2026 (assumed from "change at this outage"); reaches its 6-week (42 d) target on 11/11/2026. [position_life p2-felt-top] [outage OUT-2026-11-11]
- Scoped for 11/11: WO 26108953 change felt (8 h, parts Reserved) and WO 26108743 change HP shower nozzles (6 h, Reserved). [WO 26108953] [WO 26108743]
- Planned runs Dec 2025 - Sep 2026 were each 5.9 wk; the one early change was 05/19/2026 after 34 d (RCFA-SM-26-016, 7.5 h, 232 t). [DOC MP-SV-260930 p.1] [RCFA-SM-26-016]
- Cause of the early change: HP shower nozzles 22% plugged, strainer packed solid; Marlow fill 71% vs 40-45% typical. [DOC MP-FA-260526 p.1] [DOC SW-SA-260513 p.1]
- CONFLICT on age at the early change: RCFA text "3 weeks" vs Marlow 34 days. [RCFA-SM-26-016] [DOC MP-FA-260526 p.1]
- RCFA-SM-26-016 still open: SM-0138 (Uhle rate-of-rise on Bonvoy watch list) overdue since 07/15/2026; SM-0139 and SM-0141 completed. [Action SM-0138] [Action SM-0139] [Action SM-0141]
- Shower audits since the fix: 4% plugged 08/05/2026, 0% 10/21/2026. [DOC SW-SA-260805 p.1] [DOC SW-SA-261021 p.1]
- Sheet breaks at this location: 175 breaks, about 12,764 min Nov 2025 - Aug 2026 (peak May-Jun 2026, 24 and 26 a month); 38 breaks, 2,734 min Sep-Oct 2026; new felt broke as often as the old one (19 vs 19). [downtime DT-251106-0005 to DT-260901-0522] [downtime DT-260901-0523 to DT-261029-0628]
- Restart break 2026-10-01 06:00, 62 min, after the 09-30 outage. [downtime DT-261001-0574]
- Weekly shower nozzle check WOs done 10-07, 10-13, 10-20, 10-28; next WO 26109331 planned 11-03. [WO 26109331]
- Detail pages: [[rcfa-sm-26-016]], [[press-felt-plugging]], [[press-hp-showers]], [[uhle-box-vacuum]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108953 "Change 2nd press top felt" (asset 00072315, MILL Beatrix Hale, 8 h, parts Reserved, status Scheduled) and WO 26108743 "Change HP shower nozzles, press section" (asset 00072329 shower, OPS, 6 h, parts Reserved). Felt reaches its 42 d target on 2026-11-11, so it is scoped. [WO 26108953] [WO 26108743]
- Weekly "Press shower nozzle check" (OPS, 1 h) on the 2nd press top felt HP shower: WO 26108582, 26108729, 26108967, 26109156 done (10-07, 10-13, 10-20, 10-28); WO 26109331 Approved, planned 11-03. [WO 26109331] See [[press-hp-showers]].

## Work orders Jun-Sep 2026 (WO extract work-orders-3)
- Changes at outages (type 4, MILL Beatrix Hale, 10 h est / 11 h act each): 2026-08-19 WO 26106713 "Removed after 41 days. Normal wear at removal." [WO 26106713]; 2026-09-30 WO 26107763 "Removed after 41 days. Normal wear at removal." [WO 26107763]. The 07-08 change WO is not in this extract; the felt run installed 07-08 ended 08-19 (42 d vs 6-week target).
- HP shower nozzle changes on the 2nd press top felt HP shower (asset 00072329, OPS Operations): 2026-08-19 4 h est [WO 26106720]; 2026-09-30 8 h est [WO 26107784]; Nov 11: WO 26108743. See [[press-hp-showers]].
- Weekly preventive "Press shower nozzle check" (OPS, 1 h est / 1.1 h act, asset 00072329): 16 WOs completed 2026-06-18 to 2026-09-29 (first 26105922, last 26108463), including 2 days late on 26105922 (planned 06-16, done 06-18) and 26106433 (planned 07-07, done 07-09). [WO 26105922] [WO 26108463]
- CONFLICT note: RCFA-SM-26-016 says the nozzles were not checked since the Feb audit; the weekly check WOs continue to run every week through September anyway (see [[work-orders-feb-jun-2026]]). No 2nd press top felt emergency WO in Jun-Sep 2026 (the unplanned change was 05-19, WO 26105306).

## Spec and target
- 6-week target (shortest clothing target on PM1); vendor Marlow Press Fabrics; seamed felt, 1400 gsm [DOC SM-REF-02 p.1]
- Position sits in the 2nd press with [[p2-felt-bottom]], [[p2-roll-top]] and [[p2-roll-bottom]]; Uhle box on this felt (Pi PM1:UHLE_P2T_VAC pattern; see [[press-felt-plugging]]) [DOC SM-DWG-201 p.1]
- Marlow surveys it at each outage (analyst Ines Callaghan): caliper, air perm, fill; see [[outage-clothing-changes]]

## Run history (installed date -> removed; vendor survey doc)
- Installed 10/29/2025; 5.9 wk at 12/10/2025, caliper 2.52 mm, air perm 18 cfm, "End of life. Change at this outage as planned" [DOC MP-SV-251210 p.1]
- Installed 12/10/2025; changed 01/21/2026 at 5.9 wk (6 of 6) [DOC MP-SV-260121 p.1]
- Installed 01/21/2026; changed 03/04/2026 at 5.9 wk [DOC MP-SV-260304 p.1]
- Installed 03/04/2026; changed 04/15/2026 at 5.9 wk [DOC MP-SV-260415 p.1]
- Installed 04/15/2026; changed EARLY on 05/19/2026 after 34 days (target 42): emergency WO 26105306, 7.5 h down, 232 t lost [RCFA-SM-26-016] [WO 26105306]
- Installed 05/19/2026; survey 05/27/2026 at 1.0 wk "Good", Uhle vacuum 9.5 inHg the day before [DOC MP-SV-260527 p.1]
- Same felt ran to 07/08/2026: 7.0 wk against a 6-week target (1 wk over), 915 gsm water, 16 cfm, changed at that outage [DOC MP-SV-260708 p.1]
- Installed 07/08/2026; changed 08/19/2026 at 5.9 wk [DOC MP-SV-260819 p.1]
- Installed 08/19/2026; changed 09/30/2026 at 5.9 wk [DOC MP-SV-260930 p.1]
- Current run: installed 09/30/2026 (assumed from the "change at this outage" on 09/30); reaches the 6-week target on 11/11/2026 (computed: 09/30 + 42 d), the planned outage [[out-2026-11-11]]. Whether a felt is scoped: tool outage_scope.

## The 05/19/2026 early change (what happened, why)
- Used-felt analysis MP-FA-260526 (felt serial MPF-40661, 04/15 to 05/19/2026, 34 days, target 42): fill 71% vs 40-45% typical at 5 weeks; water 1,180 gsm vs 780; air perm 9 cfm vs 19; contaminant stickies, filler and fines [DOC MP-FA-260526 p.1]
- Uhle box vacuum (Pi) 14.4 inHg on 05/18 against about 10 inHg for a felt this age; press exit solids 42.1% [DOC MP-FA-260526 p.1]
- Cause: felt not conditioned; Spraywell audit 05/13/2026 found 22% of the 2nd press top HP shower nozzles plugged (fibre, stickies) and the supply strainer packed solid [DOC SW-SA-260513 p.1] [DOC MP-FA-260526 p.1]
- RCFA root cause: 2nd press top felt filled early because HP shower nozzles plugged (22%); contributing: nozzles not checked since the Feb audit, heavier 34 Super run in May, shower supply strainer not cleaned [RCFA-SM-26-016]
- CONFLICT on age: RCFA event text says "filled at 3 weeks ... Uhle vacuum up 4.6 inHg, 4th section steam at its limit" [RCFA-SM-26-016]; Marlow analysis says 34 days (about 4.9 wk) and 14.4 vs about 10 inHg (+4.4) [DOC MP-FA-260526 p.1]
- Marlow recommendation: check HP shower nozzles weekly, clean the shower supply strainer at every outage; watch Uhle vacuum rate of rise, "more than 0.1 inHg a day before week 4 means the felt is filling" [DOC MP-FA-260526 p.1]
- Shower audit after the fix: 2nd press top HP shower 4% plugged 08/05/2026 and 0% on 10/21/2026 [DOC SW-SA-260805 p.1] [DOC SW-SA-261021 p.1]; see [[press-felt-plugging]]

## RCFA actions (as of 10/31/2026)
- SM-0141 weekly press shower nozzle check by operations, Tobias Renner, due 06/10/2026, Completed [Action SM-0141]
- SM-0139 clean HP shower supply strainer every outage, Sunniva Brooks, due 07/01/2026, Completed [Action SM-0139]
- SM-0138 add Uhle vacuum rate-of-rise to the Bonvoy watch list, Mei Fairbanks, due 07/15/2026, In progress (past due at 10/31) [Action SM-0138]
- RCFA-SM-26-016 status: Open - actions pending [RCFA-SM-26-016]; detail page [[rcfa-sm-26-016]]
- Related: [[press-felt-plugging]], [[press-felt-plugging]], [[rcfa-register]]

## BUS break-review issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- "N sheet breaks in 24 h, mostly at the press" on the 2nd press top felt (Tobias Renner, "Shift leads to review break tapes", closed next day "Watching"): 5 breaks 2025-12-12, 4 breaks 2026-01-17, 03-28 and 04-17. No WO. [BUS 2025-12-12 issue ecaac74f334c57f6] [BUS 2026-01-17 issue 7c328d7f84b16052] [BUS 2026-03-28 issue 06a389a6f756bc51] [BUS 2026-04-17 issue 0ff4db9fd348e43c]

## BUS issues May-Sep 2026 (list in [[bus-issue-sheet]])
- 2026-05-04 -> 05-20 "felt filling: Uhle vacuum up, press solids down" (Sunniva Brooks): raise HP shower pressure, check nozzles; 05-10 spraywell audit pulled forward to May 13; 05-15 "22% nozzles plugged: cleaned; felt still filling"; closed "Felt changed May 19 (7.5 h shut)". [BUS 2026-05-04 .. BUS 2026-05-20 | issue b986516cc99abd78]
- 2026-05-19 unplanned felt change 7.5 h, "filled at 3 weeks: changed early (Uhle vacuum up 4.6 inHg, 4th section steam at its limit)", WO 26105306. [BUS 2026-05-19 .. BUS 2026-05-22 | issue e4a594dc109adcd9]
- Break-tape review issues (Tobias Renner, "Shift leads to review break tapes" then "Watching"): 7 issues, 4 breaks in 24 h on 05-02, 05-10, 06-17, 09-15; 5 on 05-14 and 06-25; 6 on 07-10. [BUS 2026-07-10 .. BUS 2026-07-11 | issue 3442e824c2530818] [BUS 2026-05-14 .. BUS 2026-05-15 | issue e82960db02f1195e]

## BUS sheet-break follow-ups (see [[bus-follow-up-actions]])
- "N sheet breaks in 24 h, mostly at the press (2nd press top felt)", Tobias Renner, all Completed: SM-0019 (2025-12-12, 5 breaks), SM-0115 (2026-04-17, 4), SM-0131 (2026-05-14, 5; five days before the 2026-05-19 unplanned change), SM-0173 (2026-07-10, 6). [Action SM-0131] [Action SM-0173] Tool: breaks-by-location topic [[breaks-by-location]].

## Sheet breaks and stops from the downtime log (2025-11-01 to 2026-09-01; tool: downtime_summary group=equipment kind=break)
- 175 sheet breaks ("Sheet break (press)") at the 2nd press top felt, about 12,764 min, average about 73 min; the most of any location (about 58% of all break minutes). [downtime DT-251106-0005 to DT-260901-0522]
- 144 of the 175 lasted 60 min or more; the longest were 94 min (DT-260321-0216, DT-260531-0359, DT-260622-0396). [downtime DT-260321-0216] [downtime DT-260531-0359] [downtime DT-260622-0396]
- Monthly count (minutes), by event timestamp: 2025-11 10 (707), 2025-12 16 (1178), 2026-01 19 (1408), 2026-02 12 (914), 2026-03 20 (1513), 2026-04 15 (1064), 2026-05 24 (1726), 2026-06 26 (1815), 2026-07 15 (1117), 2026-08 16 (1186). May-June 2026 are the peak. [downtime DT-251106-0005 to DT-260901-0522]
- By crew: A 36 (2,471 min), B 49 (3,650), C 46 (3,428), D 44 (3,215); by grade: 24# 120, 28# 7, 31# 16, 34 Super 32 (raw counts, see [[breaks-by-crew-and-grade]]). [downtime DT-251106-0005 to DT-260901-0522]
- Burst example: six breaks of 56-94 min between 2026-03-18 and 2026-03-22 (DT-260318-0208 to DT-260320-0213, plus DT-260321-0216 and DT-260321-0217). [downtime DT-260318-0208] [downtime DT-260321-0217]
- The first event after every planned outage restart is a break here of 60-88 min (7 of 7 outages); see [[planned-outage-history]]. [downtime DT-251211-0059] [downtime DT-260820-0502]
- Unplanned felt change 2026-05-19 10:00, 450 min, WO 26105306, RCFA-SM-26-016: "2nd press top felt filled at 3 weeks: changed early (Uhle vacuum up 4.6 inHg, 4th section steam at its limit)". [downtime DT-260519-0344] [Shift Report PM1-SHIFT-2026-05-19-D]
- After the 05-19 change the break rate did not drop: 26 in June, 15 in July, 16 in August 2026. [downtime DT-260603-0362 to DT-260831-0519]
- Failure mode: [[press-felt-plugging]]; all locations: [[breaks-by-location]].

## Sheet breaks 2026-09-02 to 2026-10-31 (new felt installed 2026-09-30; counted from the rows)
- 38 breaks, 2,734 min, average about 72 min: Sep 19 (1,352 min), Oct 19 (1,382 min). Same rate as Jun-Aug 2026 (15-26 a month). [downtime DT-260901-0523 to DT-261029-0628]
- Split at the outage: 19 breaks (1,352 min) on the old felt 2026-09-02 to 09-29 (28 days), 19 breaks (1,382 min) on the new felt 2026-10-01 to 10-29 (29 days); the fresh felt broke as often as the worn one. [downtime DT-260901-0523 to DT-261029-0628]
- First event after the 2026-09-30 outage was this felt's restart break 2026-10-01 06:00, 62 min, crew B: the 8th of 8 outages followed by a press break (see [[planned-outage-history]]). [downtime DT-261001-0574] [outage OUT-2026-09-30]
- By crew: A 8 (576 min), B 14 (972), C 7 (526), D 9 (660); by grade: 24# 28 (2,035 min), 28# 1, 31# 3, 34 Super 6 (451). [downtime DT-260901-0523 to DT-261029-0628]
- Longest: 93 min 2026-10-27 (crew C, 24#), 92 min 2026-10-29 (crew D), 91 min 2026-09-02 (crew B) and 2026-10-08 (crew A). [downtime DT-261027-0622] [downtime DT-261029-0628] [downtime DT-260902-0524] [downtime DT-261008-0581]
- Burst examples: 2026-09-04 two breaks of 66 and 68 min within 4 h; 2026-09-29 two of 64 and 85 min (plus a 15 min reel break); 2026-10-19 two of 82 and 61 min (10:18, 18:09), crew D. [downtime DT-260904-0527] [downtime DT-260929-0571] [downtime DT-261019-0601]

## What crews saw in Nov 2025 (shift reports; felt installed 10/29/2025, changed at [[out-2025-12-10]])
- 10 press breaks at this felt in Nov 2025, 707 min (matches the monthly count above): 11-06D 69, 11-06N 65, 11-15N 59, 11-16D 78, 11-19N 66, 11-22N 67, 11-24N 86, 11-25D 81, 11-28D 57, 11-30D 79 min. Every one is a 57-86 min event; none is under 57 min. [Shift Report PM1-SHIFT-2025-11-06-D] [Shift Report PM1-SHIFT-2025-11-24-N] [Shift Report PM1-SHIFT-2025-11-30-D]
- Back-to-back breaks: 11-06 Day and Night (69 then 65 min, 16 h apart); 11-24 Night 02:15 break (86 min) followed 11-25 Day by 81 min. [Shift Report PM1-SHIFT-2025-11-06-N] [Shift Report PM1-SHIFT-2025-11-25-D]
- The felt in place was installed 10/29/2025 (6-week target, changed 12-10), so the Nov breaks ran from week 1 (11-06) to week 4-5 (11-30): long breaks from the first week, not only late in life. The handover lists in these reports do not name the 2nd press top felt; the press items named are the 2nd press BOTTOM felt "guide hunting → check guide paddle" (11-23 to 11-30, 8 days, never recorded as fixed) and the 1st press top felt (see [[p1-felt-top]]). [Shift Report PM1-SHIFT-2025-11-23-D] [Shift Report PM1-SHIFT-2025-11-30-N]
- A felt-conditioning step was tried only on the 1st press: "1st press top felt: conditioning low → raise Uhle vacuum setpoint 0.5 inHg" 11-13 to 11-15 (see [[uhle-box-vacuum]]). Nothing similar is logged for the 2nd press top. [Shift Report PM1-SHIFT-2025-11-13-D] [Shift Report PM1-SHIFT-2025-11-15-N]
- See [[shift-handover-signals-2025-11]].

## Sheet breaks in the Jan 2026 shift reports (62 shifts, 2026-01-01 to 01-31; counted from the Stops lists)
- 19 breaks at the 2nd press top felt, 1,408 min (about 74 min each), the largest share of the 54 sheet breaks in the month; dryer cans 3/6/11/16 together 26 breaks, 983 min; reel 9 breaks, 145 min. [Shift Report PM1-SHIFT-2026-01-02-N] [Shift Report PM1-SHIFT-2026-01-29-D]
- Press breaks are long: 55-92 min, versus 10-30 min typical at the reel. Longest: 01-23 Night 90 min, 01-29 Day 92 min, 01-18 Night 89 min. [Shift Report PM1-SHIFT-2026-01-23-N] [Shift Report PM1-SHIFT-2026-01-29-D] [Shift Report PM1-SHIFT-2026-01-18-N]
- No handover item or note in January ties these to felt condition; the felt was changed 01-21 (MPF-40600 out, MPF-40606 in, [[out-2026-01-21]]) and breaks continued on the new felt: 01-21 Night 85 min at 02:00, 01-23 Night two, 01-26 Night, 01-29 Day, 01-30 Day, 01-31 Day. [Shift Report PM1-SHIFT-2026-01-21-N] [Shift Report PM1-SHIFT-2026-01-31-D]
- See [[breaks-by-location]].

## Shift reports Feb 2026 (felt installed 2026-01-21; 12 press breaks, 914 min, matches the monthly count above)
- Breaks (Sheet break (press)) by minutes: 02-01 82, 02-04 63, 02-05 89, 02-08 67, 02-10 67, 02-15 92, 02-16/17 82, 02-18 92, 02-19 71, 02-25 63 and 58, 02-27/28 88; sum 914 min. [Shift Report PM1-SHIFT-2026-02-01-D] [Shift Report PM1-SHIFT-2026-02-15-N] [Shift Report PM1-SHIFT-2026-02-18-N] [Shift Report PM1-SHIFT-2026-02-25-D]
- Reading note: breaks near shift change are split across the two shift headers (02-16 Night header says 1 break 2 min, the stop line says 82 min at 05:58, and 02-17 Day shows "0 breaks (80 min)"). Count breaks from the Stops lines, not the headers. [Shift Report PM1-SHIFT-2026-02-16-N] [Shift Report PM1-SHIFT-2026-02-17-D]
- The 02-15 22:03 break (92 min) came immediately after the 2nd press drive motor failure restart ([[2nd-press-drive]]). [Shift Report PM1-SHIFT-2026-02-15-N]
- No 2nd press top felt item (conditioning, Uhle, shower) in any February handover: the press-side items were the 1st press top felt and 2nd press bottom felt ([[press-felt-plugging]]). 02-25 Day: two press breaks (63, 58 min) plus two dryer breaks, 262 t. [Shift Report PM1-SHIFT-2026-02-25-D]

## Shift reports Mar 2026 (press breaks as the crews logged them; see [[shift-handover-signals-2026-03]])
- 20 breaks at the 2nd press top felt in the March shift reports, 1,513 min (computed), equal to the downtime-log monthly count above (20, 1,513). 16 of the 20 were on night shifts; the four day-shift breaks were 03-18 D, 03-21 D, 03-27 D and 03-31 D (computed). [Shift Report PM1-SHIFT-2026-03-01-N] [Shift Report PM1-SHIFT-2026-03-31-D]
- Before the 03-18 2nd press drive bearing stop: 66 min (03-01 N), 83 (03-04 N, first break after the outage restart, see [[out-2026-03-04]]), 71 (03-11 N), 64 (03-14 N). [Shift Report PM1-SHIFT-2026-03-04-N] [Shift Report PM1-SHIFT-2026-03-14-N]
- Burst 03-18 to 03-22: 10 breaks, 804 min (94, 59, 91, 56, 90, 89, 66, 94, 73, 92), around the [[2nd-press-drive]] stop (03-18 06:30) and the [[press-felt-blows]] 2nd press bottom felt blow (03-21 12:02); the wiki line above counts six from the log. 03-18 Night alone had three (59, 91, 56). [Shift Report PM1-SHIFT-2026-03-18-N] [Shift Report PM1-SHIFT-2026-03-21-D]
- Later in March: 69 (03-24 N), 68 (03-26 N), 56 and 64 (03-27 D and N), 89 (03-28 N), 79 (03-31 D). Handover 03-29 Day and Night: "2nd press top felt: 4 sheet breaks in 24 h, mostly at the press → watching". [Shift Report PM1-SHIFT-2026-03-29-D] [Shift Report PM1-SHIFT-2026-03-29-N]
- Felt MPF-40641 was installed 2026-03-04 and changed 04-15 at 5.9 wk (see run history and [[out-2026-03-04]]); the 03-01 break was on the outgoing felt MPF-40606, the other 19 March breaks on MPF-40641 (computed from the dates). [position_life p2-felt-top]

## Bonvoy (tag PM1:UHLE_P2T_VAC, 10 tag-days; see [[uhle-box-vacuum]])
- Only episode: 2026-05-10 -> 2026-05-19, High 6-23 h/day, daily max 12.66 -> 14.59 inHg; 14.1-14.59 on 05-18, matching the 14.4 inHg in Marlow's analysis. Ends on the 05-19 unplanned change (RCFA-SM-26-016); Bonvoy shows 10 flagged days. [Bonvoy PM1:UHLE_P2T_VAC 2026-05-10] [Bonvoy PM1:UHLE_P2T_VAC 2026-05-18] [Bonvoy PM1:UHLE_P2T_VAC 2026-05-19]
- Rate: daily mean 10.21 -> 10.49 over 9 days; daily max rose about 0.2 inHg a day. [Bonvoy PM1:UHLE_P2T_VAC 2026-05-19]
- Press exit solids went Low at the same time: [[p2-roll-bottom]].

## December 2025 breaks seen by the crews (shift reports; tool: shift_reports; matches the 16 breaks / 1,178 min above)
- 16 breaks at the 2nd press top felt in Dec 2025 shift reports, 1,178 min (of 38 breaks total at all locations in the month in the reports: reel 18, dryer 12). Press breaks were 54 to 94 min each. [Shift Report PM1-SHIFT-2025-12-01-D] [Shift Report PM1-SHIFT-2025-12-14-N]
- Before the Dec 10 outage (old felt MPF-40569, 5.9 wk, "End of life"): Dec 1 D 92 min, Dec 2 N 69, Dec 6 N 89, Dec 7 D 65 and Dec 7 N 72. [Shift Report PM1-SHIFT-2025-12-01-D] [Shift Report PM1-SHIFT-2025-12-06-N] [Shift Report PM1-SHIFT-2025-12-07-N]
- After the Dec 10 change (new felt MPF-40600, installed [[out-2025-12-10]]): first break 78 min at 02:00 on the restart night, then Dec 11 D 82 and 69 (3 breaks, 165 min, sheet on 77.1%), Dec 12 N 77 (the report header says 7 min for that break, the event line says 77 min; CONFLICT, 77 used in the totals above), Dec 14 N 94, Dec 17 N 55, Dec 19 D 54, Dec 20 D 83 and 54, Dec 26 D 54, Dec 27 N 91. [Shift Report PM1-SHIFT-2025-12-10-N] [Shift Report PM1-SHIFT-2025-12-11-D] [Shift Report PM1-SHIFT-2025-12-12-N] [Shift Report PM1-SHIFT-2025-12-27-N]
- Handover item "5 sheet breaks in 24 h, mostly at the press → shift leads to review break tapes" on Dec 12 D and N, then "watching" Dec 13; BUS action SM-0019 dated 2025-12-12. Eight breaks followed on the new felt after that. No cause is written in the reports. [Shift Report PM1-SHIFT-2025-12-12-D] [Shift Report PM1-SHIFT-2025-12-13-D] [Action SM-0019]
- Related at the press: "2nd press bottom felt: guide hunting → check guide paddle" Dec 20 D to Dec 21 N ([[p2-felt-bottom]]); "1st press top roll doctor chatter" Dec 18 to Dec 20 ([[p1-roll-top]]). [Shift Report PM1-SHIFT-2025-12-20-D]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Changed at all three outages in the period, each "Removed after 41 days. Normal wear at removal." (type 4, MILL Beatrix Hale, est 10 h act 11 h): 26100420 ([[out-2025-12-10]]), 26101435 ([[out-2026-01-21]]), 26102499 ([[out-2026-03-04]]). [WO 26100420] [WO 26101435] [WO 26102499]
- HP shower on this felt (asset 00072329): "Change HP shower nozzles, press section" at each of the same outages: 26100434 (8.8 h), 26101442 (4.4 h), 26102506 (8.8 h) [WO 26100434] [WO 26101442] [WO 26102506]; weekly "Press shower nozzle check" (OPS, 1.1 h) 16 times in the batch, e.g. 26100070 (done 2025-10-28) ... 26102709 (done 2026-02-11). [WO 26100070] [WO 26102709]
- See [[outage-standard-wo-package]], [[routine-pm-work-orders]], [[press-hp-showers]].

## Work orders Feb-Jun 2026 (work-orders-2)
- "Change 2nd press top felt" (asset 00072315, MILL Beatrix Hale, type 4 prio 2, est 10 h act 11 h): WO 26103465 at [[out-2026-04-15]], note "Removed after 41 days. Some filling at the edges; cleaned with the HP shower at mid-life." (the run table above has 03-04 to 04-15 = 42 d, vendor 5.9 wk); WO 26105670 at [[out-2026-07-08]], note "Removed after 50 days. Normal wear at removal." (05-19 to 07-08). No change WO for this position at [[out-2026-05-27]]. [WO 26103465] [WO 26105670]
- Early change WO 26105306 "Unplanned felt change: 2nd press top felt", type 3, 2026-05-19, est 22.5 h act 24.8 h, MILL Beatrix Hale: "2nd press top felt filled at 3 weeks: changed early (Uhle vacuum up 4.6 inHg, 4th section steam at its limit)." [WO 26105306]
- Shower: weekly "Press shower nozzle check" WOs on its HP shower (asset 00072329) were Closed 17 times 02-17 to 06-09 (WO 26104830 on 05-07, WO 26104984 on 05-12), which conflicts with the RCFA wording "nozzles not checked since the Feb audit"; outage "Change HP shower nozzles, press section" WOs 26103479 (04-15), 26104543 (05-27), 26105691 (07-08). See [[press-felt-plugging]], [[work-orders-feb-jun-2026]]. [WO 26104830] [WO 26104984] [WO 26103479] [WO 26104543] [WO 26105691]

## Gaps (checked 2026-11-10)
- Not on this page: shift-report sections for Apr-Oct 2026 and BUS issues after 2026-09-30 (see [[bus-issues-2026-10-late]]); the Bonvoy section covers 10 tag-days only. Use tool: shift_reports for those months.
