---
name: fan-pump
description: Fan pump (asset 00072196, Forming) - impeller eroded by cavitation Jan 2026 (RCFA-SM-26-004 closed); silo low level on heavy grades; recurring packing-leak BUS follow-ups
type: equipment
aliases: ["asset 00072196", "fan pump impeller", "PM1:FAN_PUMP_FLOW", "PM1:FAN_PUMP_VIB", "PM1:HB_P"]
---
- 2026-01-02 impeller failure, 6 h, 187 t; root cause "Fan pump impeller eroded by cavitation"; contributing "Silo level run low on heavy grades"; RCFA-SM-26-004 closed 2026-02-05; lead Mei Fairbanks. [RCFA-SM-26-004]
- Pi trend about 8 days before the stop in PM1:FAN_PUMP_FLOW, PM1:HB_P, PM1:FAN_PUMP_VIB. [RCFA-SM-26-004]
- Actions done: raise the silo low-level alarm SM-0034 (2026-01-15); impeller inspection at every second outage SM-0033 (2026-02-05); Gloria Nakamura. [Action SM-0034] [Action SM-0033]
- BUS follow-ups "Fan pump packing leaking": SM-0020 (2025-12-13), SM-0078 (2026-03-08), SM-0097 (2026-03-25), SM-0150 (2026-06-03), all completed. [Action SM-0020] [Action SM-0078] [Action SM-0097] [Action SM-0150]
- Impeller inspection is "every second outage": which outage is next is not in this batch; check outage pages (e.g. [[out-2026-11-11]]).

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO 26109338 "Fan pump impeller change (planned)", prio 1, planned and completed 2026-10-29, est 10.8 h act 11.9 h. [WO 26109338]
- WO 26109170 "Fan pump seal inspection" (preventive, completed 2026-10-28). [WO 26109170]

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2026-01-02 BUS issue: impeller failure 6.0 h, WO 26101925, Gloria Nakamura, "fan pump flow and headbox pressure dipping in bursts for 16 days before"; closed 2026-01-04 after "Watching after restart". [BUS 2026-01-02 issue de3328eda72ee7e0]
- "Fan pump packing leaking": 10 issues, always "Adjust packing gland" then "Leak down to a drip": 2025-11-14, 12-02 (WO 26101134), 12-13, 2026-01-14 (WO 26102156), 01-20, 02-14 (WO 26102926; 12 days, re-closed 02-25), 03-08 (WO 26103381), 03-18 (WO 26103710), 03-25 (WO 26103899), 04-11 (WO 26104263). The leak recurs every 1-4 weeks before and after the impeller repair. [BUS 2025-11-14 issue 4ef8c66a5ede7f58] [BUS 2026-02-14 issue 171deecd52321852] [BUS 2026-04-11 issue bcc713697c25f13b]

## Downtime log event
- 2026-01-02 (event timestamp 2026-01-02T19:25) Forming / Fan pump, cause "Fan pump impeller failure", 362 min, WO 26101925, RCFA-SM-26-004, grade 31#, crew C: "fan pump flow and headbox pressure dipping in bursts for 16 days before" (RCFA says about 8 days of Pi trend; both kept). [downtime DT-260102-0094] [Shift Report PM1-SHIFT-2026-01-02-D]

## Shift reports around the Jan 2026 failure (tool: shift_reports)
- 2026-01-02 Day: "Lost 6.0 h (187 t) to fan pump impeller failure on the Fan pump at 14:25. WO 26101925. Grade change to 31#."; shift-level unplanned 215 min, the 362 min stop runs into the night. [Shift Report PM1-SHIFT-2026-01-02-D]
- Handover after restart: 01-03 "fan pump flow and headbox pressure dipping in bursts for 16 days before -> watching after restart"; 01-04 Day and Night "closed". [Shift Report PM1-SHIFT-2026-01-03-D] [Shift Report PM1-SHIFT-2026-01-04-D]
- The 16-day dip pattern (flow and headbox pressure in bursts) is only in the post-failure handover; the batch starts 01-02, so pre-failure crew notes are not in it. [Shift Report PM1-SHIFT-2026-01-03-N]
- Packing: 01-15 Day/Night "Fan pump: packing leaking -> leak down to a drip"; 01-21 Day/Night "adjust packing gland"; 01-22 Day/Night "leak down to a drip". Matches BUS "Fan pump packing leaking" SM-0020 series. [Shift Report PM1-SHIFT-2026-01-15-D] [Shift Report PM1-SHIFT-2026-01-21-D] [Shift Report PM1-SHIFT-2026-01-22-D]

## What crews saw in Nov 2025 (shift reports)
- "Fan pump: packing leaking → adjust packing gland" 2025-11-14 (Day, Night) and 11-15 (Day, Night); "→ leak down to a drip" 11-16 (Day, Night). Not on later handovers in November. [Shift Report PM1-SHIFT-2025-11-14-D] [Shift Report PM1-SHIFT-2025-11-16-D]
- This is the earliest packing-leak item; the first BUS action of that wording is SM-0020 (2025-12-13). The 2026-01-02 impeller failure was cavitation, not packing. [Action SM-0020] [RCFA-SM-26-004]

## What crews saw in Dec 2025 (shift reports)
- Day shift Dec 24: "Fan pump: headbox pressure bouncing now and then (FAN_PUMP_FLOW, HB_P, FAN_PUMP_VIB)", the same three tags as RCFA-SM-26-004; 9 days before the 2026-01-02 impeller failure and the only such note in the Dec 2025 reports. [Shift Report PM1-SHIFT-2025-12-24-D]
- Packing leak handover "Fan pump: packing leaking → adjust packing gland" Dec 2 to Dec 15; status "leak down to a drip" Dec 4; leaked again Dec 14 and 15; the BUS follow-up SM-0020 was created 2025-12-13. Packing, not the impeller; no link to the failure is stated. [Shift Report PM1-SHIFT-2025-12-02-D] [Shift Report PM1-SHIFT-2025-12-04-D] [Shift Report PM1-SHIFT-2025-12-15-D] [Action SM-0020]

## Downtime log events Sep-Oct 2026 (planned, both caught early)
- 2026-09-11 12:00 planned 180 min, cause "Bearing change (found on the vibration route)", no WO on the row, grade 24#, crew C: "Fan pump bearing changed: found on the Sep 09 vibration route." This closes the open question below: the bearing was changed 2 days after the 09/09 Keel Alert (0.265) and the Bonvoy ramp ends the same day (09-11). No RCFA. [downtime DT-260911-0541] [Shift Report PM1-SHIFT-2026-09-11-D] [DOC KV-VR-260909 p.1]
- 2026-10-29 12:00 planned 216 min, cause "Fan pump impeller change (planned)", WO 26109338, grade 24#, crew D: "found Oct 28 (fan pump flow and headbox pressure dipping in bursts)". Same precursor pattern as the 2026-01-02 impeller failure (RCFA-SM-26-004, 6 h unplanned), this time handled planned one day after it was seen; 216 min planned vs 362 min unplanned. No RCFA. [downtime DT-261029-0626] [WO 26109338] [downtime DT-260102-0094]
- Bonvoy flow Low days 2026-09-21 and 2026-10-06 (listed below) precede the Oct 28 observation; whether the impeller change was the "every second outage" inspection (SM-0033) is not stated. [Bonvoy PM1:FAN_PUMP_FLOW 2026-10-06]
- Tool: downtime_events equipment="Fan pump". See also [[precursor-lead-times]].

## Shift reports Feb 2026 (packing)
- Handover "Fan pump: packing leaking": 02-15 Day/Night "leak down to a drip"; 02-16 Day to 02-18 Night "adjust packing gland". Matches the BUS SM-0078 series (03-08 first listed). No stop; no impeller or vibration remark. [Shift Report PM1-SHIFT-2026-02-15-D] [Shift Report PM1-SHIFT-2026-02-16-D] [Shift Report PM1-SHIFT-2026-02-18-N]

## Keel vibration route (reports library; see [[vibration-routes]])
- PM1:FAN_PUMP_VIB route readings in/s: 11/12/2025 0.065; 12/10/2025 0.023; 01/14/2026 0.062; 02/11 0.065; 03/11 0.060; 04/08 0.053; 05/13 0.065; 06/10 0.067; 07/08 0.022; 08/12 0.061; 09/09 0.265 Alert; 10/14 0.061 [DOC KV-VR-251112 p.1] [DOC KV-VR-260909 p.1] [DOC KV-VR-261014 p.1]
- 09/09/2026: "Fan pump: 0.27 in/s (Alert). Plan a bearing change." with "Bearing defect frequencies present" [DOC KV-VR-260909 p.1]
- Back to 0.061 on 10/14/2026, so the bearing was presumably changed between the routes (no WO or doc says so here; check outage_scope for [[out-2026-09-30]]). No RCFA for this alert [DOC KV-VR-261014 p.1]
- The Jan 2026 impeller failure (cavitation) was not a bearing alert: 01/14 reading 0.062 Good, failure 01/02 earlier [DOC KV-VR-260114 p.1]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072196)
- Bearing change: WO 26108169 "Change Fan pump bearing (found on the Sep 09 vibration route)", corrective prio 1, requested 2026-09-09, completed 2026-09-11, no outage link, 6 h est / 6.6 h act, MECH Beatrix Hale. This answers the question above: the bearing was changed on 2026-09-11 (not at an outage), two days after the Keel 09/09 Alert (0.265 in/s); the Bonvoy ramp ends the same day (2026-09-11). [WO 26108169] [DOC KV-VR-260909 p.1] [Bonvoy PM1:FAN_PUMP_VIB 2026-09-11]
- Packing leaking (corrective prio 3, MECH Beatrix Hale): 4 WOs, completed 2026-06-05 [WO 26105712], 06-15 [WO 26105852], 06-18 [WO 26106055], 08-15 [WO 26107455]; 26105712 was requested 2026-06-03, the same day as BUS follow-up SM-0150. [Action SM-0150]
- Preventive "Fan pump seal inspection" (1.5 h est, MECH): 4 WOs completed 2026-06-30, 07-31, 08-31 and 09-28 (about monthly). [WO 26106209] [WO 26107014] [WO 26107630] [WO 26108435]
- No impeller inspection WO appears in the Jun-Sep records; the "every second outage" impeller check (SM-0033) is not visible as a WO here. See [[work-orders-jun-sep-2026]].

## Shift reports Mar 2026 (packing leak; no stop; see [[shift-handover-signals-2026-03]])
- "Fan pump: packing leaking → adjust packing gland" in handovers 03-09 Day through 03-10 Night, and 03-19 Day/Night; "→ leak down to a drip" 03-20 Day/Night; again "adjust packing gland" 03-25 Day to 03-26 Night, "→ leak down to a drip" 03-27 Day/Night. [Shift Report PM1-SHIFT-2026-03-09-D] [Shift Report PM1-SHIFT-2026-03-19-D] [Shift Report PM1-SHIFT-2026-03-20-D] [Shift Report PM1-SHIFT-2026-03-27-N]
- Matches BUS follow-ups SM-0078 (2026-03-08) and SM-0097 (2026-03-25); the 03-19 run has no follow-up id in [[bus-follow-up-actions]]. [Action SM-0078] [Action SM-0097]

## BUS issues Apr-Oct 2026 (owner Gloria Nakamura unless noted; list in [[bus-issue-sheet]])
- "Packing leaking" 5 issues, all "Adjust packing gland" then "Leak down to a drip": 04-27 (WO 26104788), 06-03 -> 06-18 (16 days on the sheet, three cycles: WO 26105712, 26105852, 26106055), 07-19, 08-14 (WO 26107455), 09-27 -> 10-01. [BUS 2026-04-27 .. BUS 2026-04-28 | issue 7473732ffea09473] [BUS 2026-06-03 .. BUS 2026-06-18 | issue 78ab1bd1094035f8] [BUS 2026-08-14 .. BUS 2026-08-15 | issue 8c6d5cda93401ca3] [BUS 2026-09-27 .. BUS 2026-10-01 | issue a4e0b10671bfa573]
- 2026-09-10 "Fan pump bearing in Alert on the vibration route": WO 26108169 "Planned stop to change it" (Mei Fairbanks); 09-11 closed "Monitoring daily". Matches the 09/09 route 0.27 in/s and the Aug-Sep Bonvoy ramp above. [BUS 2026-09-10 .. BUS 2026-09-11 | issue 376e6717b36f4ba6]

## Asset and Pi tags (from equipment/Pi tag listing)
- Fan pump is asset 00072196 (kind pump, section sec-forming). Pi tags: PM1:FAN_PUMP_FLOW (gpm) and PM1:FAN_PUMP_VIB bearing vibration (in/s). [equipment 00072196] [Pi tag PM1:FAN_PUMP_FLOW] [Pi tag PM1:FAN_PUMP_VIB]
- See [[pi-tag-map]].

## Bonvoy (tags PM1:FAN_PUMP_VIB 23 tag-days, PM1:FAN_PUMP_FLOW 4 tag-days; see [[bonvoy]])
- Vibration 2025-12-20 -> 2025-12-29: 6 scattered days (12-20, 21, 22, 25, 27, 29), 3-6 h each, daily max 0.088 -> 0.110; the impeller RCFA-SM-26-004 failure date is 2026-01-02. [Bonvoy PM1:FAN_PUMP_VIB 2025-12-20] [Bonvoy PM1:FAN_PUMP_VIB 2025-12-29]
- Vibration RAMP 2026-08-26 -> 2026-09-11 (17 d), daily max 0.076 -> 0.313 in/s (Alert passed ~2026-09-03, 0.168; Danger 0.4 not reached in the record). No RCFA for it in the wiki. [Bonvoy PM1:FAN_PUMP_VIB 2026-08-26] [Bonvoy PM1:FAN_PUMP_VIB 2026-09-11]
- Flow Low 3 h (gpm mean ~17,900, min 551 to 5,801): 2026-03-02, 08-25, 09-21, 10-06 - all stop-like days, see [[bonvoy-multi-tag-dips]]. [Bonvoy PM1:FAN_PUMP_FLOW 2026-10-06]
- Mode: [[bearing-failed-between-vibration-routes]] (Aug-Sep ramp only).

## BUS issue Oct 2026
- Issue 8759513b5205e0d6 (10-28 to 10-29, Gloria Nakamura, WO 26109338): "Fan pump flow and headbox pressure dipping in bursts: cavitation or impeller wear"; "Check silo level and the pump suction"; closed 10-29 "Done; running normal". Same symptoms as the Jan 2026 impeller RCFA-SM-26-004; Bonvoy flow Low on 2026-10-06 above. See [[bus-issues-2026-10-late]]. [BUS 2026-10-29] [WO 26109338]

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- 6 "Fan pump packing leaking" WOs, MECH Beatrix Hale, type 1 prio 3, all Closed (requested -> done, actual h): 26102926 (02-14 -> 02-15, 6.6), 26103381 (03-08 -> 03-14, 2.2), 26103710 (03-18 -> 03-20, 4.4), 26103899 (03-25 -> 03-27, 6.6), 26104263 (04-11 -> 04-13, 2.2), 26104788 (04-27 -> 04-28, 3.3); 25.3 h (computed). With the 2 WOs of Dec-Jan that is 8 packing WOs by 04-28; none 04-29 to 06-03 in the extract. [WO 26102926] [WO 26103381] [WO 26103710] [WO 26103899] [WO 26104263] [WO 26104788]
- WO request dates 03-08 and 03-25 equal the creation dates of BUS follow-ups SM-0078 and SM-0097. [Action SM-0078] [Action SM-0097]
- Monthly "Fan pump seal inspection" (MECH, 1.5 h est): 26103143 (done 03-02), 26103906 (04-02), 26104697 (05-03), 26105404 (05-31). [WO 26103143] [WO 26103906] [WO 26104697] [WO 26105404]
- Alert 09/09/2026 and the Oct 2026 impeller change come later; see above and [[work-order-routes-and-corrective]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26101925 "Fan pump impeller failure: Fan pump" (type 3, prio 1, requested and completed 2026-01-02, MECH Beatrix Hale, est 18.1 h act 19.9 h; third-longest job of the batch): "fan pump flow and headbox pressure dipping in bursts for 16 days before." [WO 26101925]
- Corrective "Fan pump packing leaking": WO 26101134 (requested 2025-12-02, done 12-04, 2.2 h) and WO 26102156 (2026-01-14, done 01-15, 6.6 h). [WO 26101134] [WO 26102156]
- Preventive "Fan pump seal inspection" (MECH, 1.7 h act): 4 WOs, 26100168 (done 2025-11-03), 26100973 (12-03), 26101729 (2026-01-01), 26102373 (01-31); about monthly, one fell on the failure week (2026-01-01 inspection, failure 01-02). [WO 26100168] [WO 26101729] [WO 26102373] [WO 26101925]
