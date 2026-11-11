---
name: reel-drum
description: Reel drum DS bearing (PM1 Reel): known bearing defect found on the Aug 12 2026 vibration route, above the Danger limit 0.4 in/s at end of Oct 2026 but NOT flagged by Bonvoy (baseline moved); two vibration/temperature ramps; read for any reel drum / reel bearing question
type: equipment
aliases: ["Reel drum DS bearing", "reel drum", "PM1:REEL_DRUM_DS_VIB", "PM1:REEL_DRUM_DS_TEMP", "reel bearing", "story F2", "PM1:REEL_BW", "PM1:REEL_MOIST"]
---
Tags: PM1:REEL_DRUM_DS_VIB (in/s, 52 tag-days), PM1:REEL_DRUM_DS_TEMP (degF, 48 tag-days), PM1:REEL_BW, PM1:REEL_MOIST. Tool: bonvoy_exceptions; bonvoy_report ("watch" block). See [[bonvoy]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]] (asset 00072763): WO 26108834 "Reel drum bearing inspection" (MECH Beatrix Hale, 4 h, Reserved) and WO 26108736 "Calibrate reel scanner" (INST Fenna Gallagher, 6 h, Reserved). The bearing CHANGE WO 26107420 (Waiting on parts, parts On order, outage 2026-11-11) is a separate record, not in this extract's 19; confirm bearing receipt in outage_scope. [WO 26108834] [WO 26108736]
- Weekly "Clean reel scanner heads" (INST, 1 h): 26108610, 26108869, 26109009, 26109191 done; 26109366 Approved (planned 11-05). "Reel spool inspection" WO 26109233 In progress (planned 10-30, OPS). [WO 26109366] [WO 26109233]
- Reel drive (asset 00072777) "Reel turn-up missed twice on nights": WO 26109107 (completed 10-20) and WO 26109317 (completed 10-30), E&I Omar Szabo. [WO 26109107] [WO 26109317]

## Current picture (as of 2026-10-31)
- "Known bearing defect on the Reel drum DS bearing, found on the Aug 12 vibration route." Story tag F2. [Bonvoy Report 2026-10-25]
- Above the Danger limit (0.4 in/s) but flagged false, because "its baseline has moved up with it": 0.411 (10-25), 0.416, 0.418, 0.424 (10-28), 0.359 (10-29, Alert level), 0.423 (10-30), 0.426 (10-31). [Bonvoy Report 2026-10-25] [Bonvoy Report 2026-10-28] [Bonvoy Report 2026-10-29] [Bonvoy Report 2026-10-31]
- No RCFA, no WO listed on the watch entry in these reports. The bearing itself: WO 26107420, reel drum DS bearing 22238 CCK/W33, deferred from [[out-2026-08-19]] because not in stores; expedite action SM-0201 (ETA Nov 5, due 2026-10-15, In progress, overdue); intended for [[out-2026-11-11]] (facts from other wiki pages, not this batch). [Action SM-0201] [Action SM-0215]

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]], [[reel-drive]])
- 2025-11-24 BUS issue: Reel drum DS bearing (asset 00072770) failure 2.8 h, "failed (not caught on the route)", WO 26100945, Gloria Nakamura; repaired, closed 2025-11-25. [BUS 2025-11-24 issue 7a592842197786e7]
- "Spool bar damage at the reel": 7 issues, Harlan Mbeki, "Pull damaged spool" then "Spool sent for repair": 2025-11-10 (12 days, sent twice), 12-17, 2026-01-20, 01-31 (11 days), 02-24, 03-06, 04-06. No WO on any. [BUS 2025-11-10 issue 2bd5e06e60ac8fb4] [BUS 2026-04-06 issue f52569eff12bc227]
- Break-review issues "mostly at the reel", Tobias Renner, closed "Watching": 5 breaks in 24 h 2025-12-02 and 12-20, 4 breaks 12-09 and 2026-04-01. [BUS 2025-12-02 issue 5d58afca060eaaf1] [BUS 2026-04-01 issue 35c28d21a2db0f7a]

## Ramp 1 (Nov 2025)
- Vibration High 2025-11-07 -> 2025-11-24 (18 d): daily max 0.087 -> 0.396; temperature High 2025-11-09 -> 2025-11-24 (16 d): daily max 137.4 -> 164.6 degF (band mean ~133). [Bonvoy PM1:REEL_DRUM_DS_VIB 2025-11-07] [Bonvoy PM1:REEL_DRUM_DS_VIB 2025-11-24] [Bonvoy PM1:REEL_DRUM_DS_TEMP 2025-11-24]
- Ramp ended with the bearing failure DT-251124-0032 (165 min, stop 2025-11-25 04:30, WO 26100945), no RCFA filed; logged "not caught on the route" although Bonvoy had flagged the tag for 18 days. [downtime DT-251124-0032] [Bonvoy PM1:REEL_DRUM_DS_VIB 2025-11-07]
- Same start day as the couch roll ramp (2025-11-07), which failed 2025-11-19 ([[couch-roll]]). [Bonvoy PM1:COUCH_DS_VIB 2025-11-07]

## Ramp 2 (Jul-Aug 2026)
- Vibration High 2026-07-21 -> 2026-08-23 (34 d listed): daily max 0.074 -> 0.219; the tag stopped being flagged after 08-23 while the value kept rising (watch values 0.41-0.43 in Oct). [Bonvoy PM1:REEL_DRUM_DS_VIB 2026-07-21] [Bonvoy PM1:REEL_DRUM_DS_VIB 2026-08-23]
- Temperature High: 2026-04-12, 04-28, 05-29 (3-6 h), then 2026-07-23 -> 2026-08-20 (29 d), daily max 138.5 -> 149.4 degF; band mean 132.7 -> 136. [Bonvoy PM1:REEL_DRUM_DS_TEMP 2026-07-23] [Bonvoy PM1:REEL_DRUM_DS_TEMP 2026-08-20]
- The defect was not fixed at the 2026-08-19 outage ([[out-2026-08-19]]; bearing not in stores) and was still above Danger on 10-25..31. [Bonvoy Report 2026-10-25] [Action SM-0201]
- Compare Ramp 1 ending at ~0.40 in/s: the same level has now been exceeded for over a week. Pattern page: [[bearing-failed-between-vibration-routes]].

## Keel vibration route and bearing parts (reports library; see [[vibration-routes]])
- Route readings PM1:REEL_DRUM_DS_VIB in/s: 0.133 (11/12/2025), 0.023, 0.059, 0.059, 0.061, 0.063, 0.057, 0.060, 0.023 (07/08), 0.173 (08/12 Alert), 0.274 (09/09 Alert), 0.389 (10/14 Alert) [DOC KV-VR-251112 p.1] [DOC KV-VR-260812 p.1] [DOC KV-VR-260909 p.1] [DOC KV-VR-261014 p.1]
- Defect type: "Outer race defect frequency (BPFO) with harmonics" on 08/12, 09/09 and 10/14/2026 [DOC KV-VR-261014 p.1]
- 08/12/2026: "Change at the next outage (Aug 19). Plan the bearing now." [DOC KV-VR-260812 p.1]
- 09/09/2026: "Deferred from Aug 19 (no bearing in stores). Rate of rise is accelerating: change no later than the Nov 11 outage; consider a planned stop if it passes 0.50 in/s." [DOC KV-VR-260909 p.1]
- 10/14/2026: 0.39 in/s, same wording; Danger limit is 0.40 [DOC KV-VR-261014 p.1]
- Bonvoy watch values were 0.411-0.426 in/s on 10/25-10/31 (above Danger, below the 0.50 stop trigger the vendor named) [Bonvoy Report 2026-10-31]; a planned stop before 11/11 is the vendor's contingency
- Parts and WO: bearing 22238 CCK/W33, WO 26107420, ETA Nov 5, SM-0201 overdue; see [[out-2026-11-11]]
- Earlier history: the 11/12/2025 route already read 0.133 (Good); the bearing failure of 11/25/2025 (165 min, WO 26100945) followed 13 days later with no RCFA [DOC KV-VR-251112 p.1]
- Why the 08/19 change slipped: no bearing in stores [DOC KV-VR-260909 p.1]

## What crews saw before the 2025-11-24 bearing failure (shift reports Nov 2025)
- Reel drum DS bearing stop: 11-24 Night (crew B, Lucille Brandt): "Unplanned stop at 23:30: bearing failure on the Reel drum DS bearing, 2.8 h down ... (not caught on the route). WO 26100945"; stop line 165 min. Sheet on 65.1%, 241 t. [Shift Report PM1-SHIFT-2025-11-24-N]
- CONFLICT on start time: the shift report says 23:30 on 11-24; the downtime log stop is 2025-11-25 04:30 (DT-251124-0032, above). Both kept. [Shift Report PM1-SHIFT-2025-11-24-N] [downtime DT-251124-0032]
- Handover items on the reel in the 14 days before the failure (these are the crew-visible signs; none names the DS bearing):
  - "Reel drum: spool bar damage at the reel → pull damaged spool" first on 11-10 (Day and Night), "spool sent for repair" 11-11, and repeated 11-12 to 11-15 (BUS action SM-0006, completed 2025-11-13). [Shift Report PM1-SHIFT-2025-11-10-D] [Shift Report PM1-SHIFT-2025-11-11-D] [Shift Report PM1-SHIFT-2025-11-14-D]
  - "Reel drive: reel turn-up missed twice on nights → check turn-up sequence timing" on 11-12, 11-13 and again 11-20, 11-21 (a recurring reel-drive BUS subject, see below). [Shift Report PM1-SHIFT-2025-11-12-N] [Shift Report PM1-SHIFT-2025-11-20-D]
  - Reel sheet breaks in Nov 2025 (all short): 11-03 16 min, 11-04 21, 11-07 19, 11-09 19, 11-15 10, 11-18 17, 11-19 16, 11-22 13, 11-28 12, 11-30 17 and 16 min. Typical 10-22 min, consistent with the 122-break summary above. [Shift Report PM1-SHIFT-2025-11-03-D] [Shift Report PM1-SHIFT-2025-11-30-N]
- Bonvoy had the vibration tag High from 2025-11-07 (see Ramp 1) but no handover line in the Nov reports mentions bearing vibration or temperature at the reel. [Bonvoy PM1:REEL_DRUM_DS_VIB 2025-11-07]
- After the failure, the 11-25 to 11-30 handovers do not list the reel drum. [Shift Report PM1-SHIFT-2025-11-25-D]
- Pattern: [[shift-handover-signals-2025-11]], [[bearing-failed-between-vibration-routes]].

## Shift reports Jan 2026 (reel items; not the bearing failure mode)
- Reel turn-up missed twice on nights: handover 01-02 and 01-03 "check turn-up sequence timing"; 01-04 "timing adjusted". [Shift Report PM1-SHIFT-2026-01-02-D] [Shift Report PM1-SHIFT-2026-01-04-D]
- Spool bar damage at the reel: handover 01-21 "pull damaged spool", repeated to 01-24; 01-25 "spool sent for repair". [Shift Report PM1-SHIFT-2026-01-21-D] [Shift Report PM1-SHIFT-2026-01-25-D]
- Reel sheet breaks in the Jan reports: 9 breaks, 145 min (10-22 min each) counted from the Stops lists of the 62 shift reports. [Shift Report PM1-SHIFT-2026-01-02-N] [Shift Report PM1-SHIFT-2026-01-24-N]
- No DS bearing sign appears in the January reports. [Shift Report PM1-SHIFT-2026-01-31-N]

## Work orders on the reel drum, Jun-Sep 2026 (tool: search_records / outage_scope; asset 00072763 Reel drum, DS bearing asset 00072770)
- Bearing change WO 26107420 "Change reel drum DS bearing (outer race defect, Keel route Aug 12)": corrective prio 2, requested 2026-08-12, status "Waiting on parts", parts "On order", planned 2026-11-11, outage 2026-11-11, 10 h est, MECH Beatrix Hale; "Aug 18: bearing not in stores (22238 CCK/W33). Deferred from the Aug 19 outage; ordered, ETA Nov 5. Rescheduled for Nov 11." The WO was first aimed at 2026-08-19 ([[out-2026-08-19]]). [WO 26107420]
- Bearing inspection WOs (inspection only, not a change): 2026-07-08 6 h est [WO 26105796]; 2026-08-19 8 h est [WO 26106811]; 2026-09-30 4 h est [WO 26107875]. Nov 11 has another inspection WO 26108834 (see [[out-2026-11-11]]).
- Reel scanner calibration at outages: 2026-08-19 [WO 26106699]; 2026-09-30 [WO 26107742]. Corrective "Calibrate: moisture scanner drift on Reel drum", INST Fenna Gallagher, completed 2026-07-05, matches the REEL_MOIST High 07-01 to 07-05 and action SM-0167. [WO 26106489] [Action SM-0167]
- Routine PM on the reel: "Clean reel scanner heads" weekly (17 WOs 2026-06-11 to 2026-10-01, INST Fenna Gallagher, 1 h est each); "Reel spool inspection" (4 WOs 2026-07-04 to 2026-10-01, OPS, 2 h est). Detail in [[work-orders-jun-sep-2026]].
- The reel drive "turn-up missed twice on nights" corrective WOs are on [[reel-drive]] (8 WOs 2026-06-19 to 2026-09-01).
- Note: no corrective WO between 2026-08-12 and 2026-09-30 changed this bearing; the defect was still present on the Keel 10/14 route (0.389 in/s). [WO 26107420] [DOC KV-VR-261014 p.1]

## Shift reports Feb 2026 (reel items; no DS bearing sign)
- Spool bar damage at the reel, handover "pull damaged spool": 02-01 to 02-02 (Day/Night each), 02-05 Day to 02-07 Night, and again 02-24 Day to 02-26 Night. No close-out wording ("spool sent for repair") in the February reports. [Shift Report PM1-SHIFT-2026-02-01-D] [Shift Report PM1-SHIFT-2026-02-07-N] [Shift Report PM1-SHIFT-2026-02-26-N]
- Reel sheet breaks in the Feb reports: 4 breaks, 81 min (18, 22, 22, 19 min): 02-06 14:09, 02-07 22:53, 02-21 06:19, 02-28 16:57. [Shift Report PM1-SHIFT-2026-02-06-D] [Shift Report PM1-SHIFT-2026-02-07-N] [Shift Report PM1-SHIFT-2026-02-21-D] [Shift Report PM1-SHIFT-2026-02-28-D]
- Reel drive "reel turn-up missed twice on nights -> check turn-up sequence timing": 02-06 Day to 02-08 Night; "timing adjusted" 02-09 Day/Night. [Shift Report PM1-SHIFT-2026-02-06-D] [Shift Report PM1-SHIFT-2026-02-09-D]
- Neither item is the Aug-Oct 2026 bearing defect; no DS bearing, vibration or temperature remark in the February reports. [Shift Report PM1-SHIFT-2026-02-28-N]

## Shift reports Mar 2026 (reel items; no DS bearing sign)
- 10 reel drum breaks of 11-19 min, 154 min (computed): 03-01 D 15, 03-02 D 16, 03-05 D 13, 03-15 D 17, 03-15 N 12, 03-16 D 16, 03-29 D 19, 03-29 N 19, 03-30 N 11, 03-31 N 16. [Shift Report PM1-SHIFT-2026-03-01-D] [Shift Report PM1-SHIFT-2026-03-15-D] [Shift Report PM1-SHIFT-2026-03-29-N] [Shift Report PM1-SHIFT-2026-03-31-N]
- Spool bar damage: "Reel drum: spool bar damage at the reel → pull damaged spool" 03-07 Day/Night, "→ spool sent for repair" 03-08 Day/Night. No reel bearing or vibration item in March handovers (the DS bearing ramps are Nov 2025 and Jul-Aug 2026). [Shift Report PM1-SHIFT-2026-03-07-D] [Shift Report PM1-SHIFT-2026-03-08-D]
- See [[shift-handover-signals-2026-03]].

## BUS issues (Aug-Oct 2026; owner Mei Fairbanks; list in [[bus-issue-sheet]])
- Issue 0f6e407b3446a3de, "Reel drum DS bearing" (asset 00072770): Alert on the Aug 12 route (0.17 in/s, outer race defect); 08-13 WO 26107420 raised for the Aug 19 outage -> 08-14 Waiting parts -> 08-17 "Bearing not in stores; ordering" -> 08-20 Closed "Deferred from Aug 19: rescheduled Nov 11, parts on order". [BUS 2026-08-13 .. BUS 2026-08-20 | issue 0f6e407b3446a3de]
- Issue 485d30ef457a8764 (2026-09-09 -> 10-31, 53 days open, still Waiting parts): 09-09 "Daily vibration readings by the shift; grease per Keel"; 09-27 "Keel to re-check weekly"; 10-15 "Danger at 0.40 in/s: decide run or stop"; header "bearing for Nov 11 on order, ETA Nov 5". [BUS 2026-09-09 .. BUS 2026-10-31 | issue 485d30ef457a8764]
- Reel drum (asset 00072763) other issues: spool bar damage 4 (06-24, 07-06 two cycles, 08-23, 08-29; Harlan Mbeki; "Spool sent for repair"); moisture reading high vs lab 07-04 (WO 26106489, scanner standardization); break-tape reviews 05-03, 05-07 (8 breaks), 05-16, 06-07. [BUS 2026-07-06 .. BUS 2026-07-16 | issue d81f9b2fa2b2b1d9] [BUS 2026-07-04 .. BUS 2026-07-05 | issue e9abdff6db41c5c2] [BUS 2026-05-07 .. BUS 2026-05-08 | issue c74e35155781f3f4]
- Reel drive turn-up misses: [[reel-drive]].

## Reel quality tags
- REEL_BW (basis weight lb/1000 ft2) Low 4 h on 2026-05-20 (mean 25.5, min 24.61). REEL_MOIST (%) High 2026-04-10 and 2026-07-01 -> 07-05 (mean ~7.96, max 8.91). [Bonvoy PM1:REEL_BW 2026-05-20] [Bonvoy PM1:REEL_MOIST 2026-07-02]

## Actions (from the action register; as of 2026-11-10)
- SM-0201 "Expedite the reel drum DS bearing (22238 CCK/W33), ETA Nov 5": Quentin Adeyemi, bucket Reliability, created 2026-08-20, due 2026-10-15, In progress, OVERDUE; note "Deferred from Aug 19: not in stores. WO 26107420." [Action SM-0201]
- The bearing was deferred from [[out-2026-08-19]] because it was not in stores; ETA Nov 5 is before [[out-2026-11-11]] but receipt is not confirmed in the action record.
- SM-0215 BUS follow-up "Reel drum DS bearing vibration rising (Bonvoy); bearing for Nov 11 on", Mei Fairbanks, created 2026-09-09, completed 2026-09-28. [Action SM-0215]
- SM-0014 follow-up on a reel drum DS bearing failure (2.8 h down), created 2025-11-24, completed 2025-11-26. [Action SM-0014]
- Other reel BUS follow-ups: spool bar damage SM-0006 (Harlan Mbeki, completed 2025-11-13); 4 sheet breaks in 24 h mostly at the reel SM-0153 (Tobias Renner, completed 2026-06-09); reel moisture reading high but sheet tests dry SM-0167 (Fenna Gallagher, completed 2026-07-05). [Action SM-0006] [Action SM-0153] [Action SM-0167]
- Reel drive "turn-up missed twice on nights" (Desmond Pike): SM-0029, 0148, 0158, 0161, 0188, 0203, all completed; see [[bus-follow-up-actions]].

## Sheet breaks at the reel (restored from [[breaks-by-location]]; the original lines of this page were overwritten in error and should be re-checked by the downtime agent)
- Reel drum: 122 breaks, 2,267 min; typical break 10-22 min; one reel break was 318 min (DT-260711-0440, same day as the headbox slime stop DT-260711-0439, see [[slime-buildup]]). Tool: downtime_summary group=location. [downtime DT-260711-0440]
- Reel breaks by crew: A 31, B 29, C 30, D 32 (evenly spread). [downtime DT-251103-0002 to DT-260901-0522]

## December 2025 shift reports (tool: shift_reports)
- 18 reel breaks in the Dec 2025 reports, 298 min, each 13 to 21 min (longest Dec 8 N 21, Dec 23 D 21, Dec 27 N 20). Routine; no reel stop of the Nov 24 bearing kind in December. [Shift Report PM1-SHIFT-2025-12-23-D] [Shift Report PM1-SHIFT-2025-12-27-N]
- Spool bar damage: handover "Reel drum: spool bar damage at the reel → pull damaged spool" Dec 17 D to Dec 18 N, then "spool sent for repair" Dec 19 D to Dec 19 N. [Shift Report PM1-SHIFT-2025-12-17-D] [Shift Report PM1-SHIFT-2025-12-19-D]
- Reel drive (separate subject): "reel turn-up missed twice on nights → check turn-up sequence timing" in handovers Dec 4 to Dec 30 (also 11-12/11-13/11-20/11-21 above); Dec 30 D status "timing adjusted". Recurring BUS subject, see [[bus-follow-up-actions]]. [Shift Report PM1-SHIFT-2025-12-04-D] [Shift Report PM1-SHIFT-2025-12-30-D]
- 2026-09-02 to 2026-10-31: 30 reel breaks, 487 min, average about 16 min, range 10 to 22 min (Sep 18 / 304 min, Oct 12 / 183 min); none long. [downtime DT-260903-0525 to DT-261028-0625]
- Same window by crew: A 8 (counted), B 9, C 5, D 8 (reel breaks, counted from the rows). [downtime DT-260903-0525 to DT-261028-0625]
- Reel breaks cluster on 2026-09-15/16 (four of 17-22 min within about 17 h, crew D three then crew A, 34 Super) and 2026-10-19 (three of 13-18 min, 24#). [downtime DT-260915-0551] [downtime DT-260916-0554] [downtime DT-261019-0600]
- These reel breaks are all "Sheet break (reel)"; the 09/09 Keel route Alert on this bearing is in the vibration section above. [downtime DT-260903-0525]

## BUS issues Oct 2026
- Reel drive turn-up missed twice on nights (asset 00072777, Desmond Pike): issue 78f53783d6845608 (10-18 to 10-22, WO 26109107, "Timing adjusted" 10-20, text back 10-21, closed 10-22) and issue 58ccf65a1418a95c (10-26 to 10-30, WO 26109317, "Timing adjusted"). [BUS 2026-10-22] [BUS 2026-10-30]
- Spool bar damage: issue ce0af10c4b3f4801 10-20 "Pull damaged spool", 10-21 "Spool sent for repair" (Harlan Mbeki). [BUS 2026-10-21]
- Break flags "mostly at the reel": issue b4e74e9340a63f34 (5 breaks in 24 h, 10-20 to 10-21) and 84f05edde2c2487b (4 breaks in 24 h, 10-28 to 10-29), both Tobias Renner, "Watching". See [[bus-issues-2026-10-late]]. [BUS 2026-10-21] [BUS 2026-10-29]

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- Weekly PM "Clean reel scanner heads" (asset 00072763, INST Fenna Gallagher, 1 h est): 16 WOs, 26102898 (done 02-20) to 26105502 (06-04). Monthly "Reel spool inspection" (OPS, 2 h est): 26103192, 26103962, 26104774, 26105460 (done 03-05, 04-05, 05-05, 06-04). [WO 26102898] [WO 26105502] [WO 26103192] [WO 26105460]
- Outage jobs on the reel: "Calibrate reel scanner" (INST) WO 26103444 ([[out-2026-04-15]], 6/6.6 h), WO 26104522 ([[out-2026-05-27]], 8/8.8 h), WO 26105649 ([[out-2026-07-08]], 4/4.4 h); "Reel drum bearing inspection" (MECH) WO 26103570 (8/8.8 h) and WO 26104627 (8/8.8 h). No reel bearing failure in Feb-Jun in these WOs. [WO 26103444] [WO 26104522] [WO 26105649] [WO 26103570] [WO 26104627]
- Reel drive "turn-up missed" WOs are on [[reel-drive]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26100945 "Bearing failure: Reel drum DS bearing" is filed on the separate asset 00072770 "Reel drum DS bearing" (type 3, prio 1, requested 2025-11-24, completed 2025-11-25, MECH Beatrix Hale, est 8.2 h act 9 h): "Reel drum DS bearing bearing failed (not caught on the route)." [WO 26100945]
- Reel drum (asset 00072763) outage WOs: "Reel drum bearing inspection" 26100525 ([[out-2025-12-10]], 4.4 h), 26101526 ([[out-2026-01-21]], 4.4 h), 26102590 ([[out-2026-03-04]], 6.6 h); "Calibrate reel scanner" 26100406, 26101414, 26102478. [WO 26100525] [WO 26101526] [WO 26102590] [WO 26100406]
- Preventive on the reel drum: "Clean reel scanner heads" (INST Fenna Gallagher, 1.1 h) 16 WOs about weekly; "Reel spool inspection" (OPS, 2.2 h) 4 WOs: 26100238, 26101029, 26101792, 26102450. [WO 26100105] [WO 26102744] [WO 26100238] [WO 26102450]
- The reel drum bearing inspection was on the 2025-12-10 and later outages after the Nov 2025 failure; the Aug-Oct 2026 defect is a different bearing event (above). Reel drive WOs: [[reel-drive]]. [WO 26100525]

## Gaps (checked 2026-11-10)
- A parallel overwrite is already noted above (the "Sheet breaks at the reel" lines were restored from [[breaks-by-location]]). Not on this page: shift-report sections for Apr-Oct 2026, and the Sep 27 - Oct 31 Bonvoy ramp detail beyond the Current picture; see [[bonvoy-report-2026-10]].
- Nov 2025 failure date appears as 2025-11-24 (section title) and 2025-11-25 (index line); CONFLICT: confirm with tool: downtime_events for the reel drum DS bearing stop.
