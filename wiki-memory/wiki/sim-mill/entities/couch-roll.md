---
name: couch-roll
description: Couch roll (asset 00072210, Forming) - one bearing RCFA Nov 2025 (all actions done) and seal strip water follow-ups
type: equipment
aliases: ["asset 00072210", "couch roll seal strip", "PM1:COUCH_VAC"]
---
- 2025-11-19 bearing failure, 4 h, 126 t, "failed between vibration routes"; RCFA-SM-25-001 opened 2025-11-20, closed 2026-01-21; lead Mei Fairbanks. [RCFA-SM-25-001]
- Actions all done: two-weekly route SM-0010 (2025-12-07), online vibration sensor SM-0011 (2025-12-28), grease review SM-0012 (2026-01-21); Gloria Nakamura. [Action SM-0010] [Action SM-0011] [Action SM-0012]
- Not in this batch: a repeat bearing RCFA on this asset after Jan 2026.
- BUS follow-ups "Couch roll seal strip water low": SM-0066 (2026-02-19), SM-0151 (2026-06-04), SM-0171 (2026-07-09), all completed; Tobias Renner. [Action SM-0066] [Action SM-0151] [Action SM-0171]
- Shift report Dec 27 D: "Couch roll: seal strip water low → strainer cleaned" (first of the seal-strip-water items; BUS follow-ups start 2026-02-19); the same day the vacuum pump seal water was also an open item, see [[vacuum-pump]]. [Shift Report PM1-SHIFT-2025-12-27-D]
- Mode page: [[bearing-failed-between-vibration-routes]]. Couch vacuum Pi tags (PM1:COUCH_VAC, PM1:COUCH_SOLIDS) are mapped to [[form-bottom]] and appear in [[vacuum-pump]] RCFA.

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Weekly "Lube route: wet end and press" (asset 00072210, MILL, 3 h): 26108659, 26108890, 26109058 done; 26109240 In progress (planned 10-31); 26109408 Entered (11-07). [WO 26109240] [WO 26109408]

## Work orders Jun-Sep 2026 (WO extract work-orders-3; asset 00072210 Couch roll)
- Planned for [[out-2026-11-11]]: WO 26108274 "Rebuild couch roll seal strips", type 4 Project / outage, prio 2, requested 2026-09-15, status "Planned - parts not reserved", parts "Not reserved", 8 h est, MECH Beatrix Hale. The seal strip water-low issues keep recurring (see the BUS issues below); the parts are not reserved as of the extract. [WO 26108274]
- Weekly preventive "Lube route: wet end and press" (MILL Beatrix Hale, 3 h est / 3.3 h act): 17 WOs completed 2026-06-15 to 2026-10-04, first 26105859, last 26108519; four were 2 days late (e.g. 26106139 planned 06-27 done 06-29; 26107952 planned 09-05 done 09-07). [WO 26105859] [WO 26108519] See [[work-orders-jun-sep-2026]].

## Keel vibration route (reports library; see [[vibration-routes]])
- Route 11/12/2025: PM1:COUCH_DS_VIB 0.216 in/s Alert, "Bearing defect frequencies present", "Couch roll: 0.22 in/s (Alert). Plan a bearing change." [DOC KV-VR-251112 p.1]
- The roll failed 7 days later (11/19/2025). CONFLICT: the RCFA event text says "failed (not caught on the route)" although the 11/12 route had flagged the bearing [RCFA-SM-25-001] [DOC KV-VR-251112 p.1]
- Later routes Good: 0.024 (12/10/2025), 0.065, 0.062, 0.076, 0.062, 0.066, 0.068, 0.023 (07/08), 0.073, 0.067, 0.072 (10/14/2026) [DOC KV-VR-261014 p.1]; the Oct 2026 Bonvoy ramp below was not yet visible on the 10/14 route

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2025-11-19 BUS issue: bearing failure 4.0 h, "not caught on the route", WO 26100833, Gloria Nakamura; "Repaired; running", watching after restart, closed 2025-11-22. [BUS 2025-11-19 issue 19349fc9c1512936]
- "Couch roll seal strip water low": 8 issues, Tobias Renner, "Check seal water flow" then "Strainer cleaned": 2025-11-26, 12-26, 2026-01-06 (10 days), 01-17, 02-19, 02-27, 03-16, 04-12. [BUS 2025-11-26 issue 7fd05593133b68e3] [BUS 2026-04-12 issue 5b9ea60c488a3fad]

## Downtime log event
- 2025-11-19 19:30 Forming / Couch roll, cause Bearing failure, 243 min, WO 26100833, RCFA-SM-25-001, grade 34 Super, crew D: "Couch roll bearing failed (not caught on the route)". [downtime DT-251119-0024] [Shift Report PM1-SHIFT-2025-11-19-D]
- The same shift (19 Nov) also had 3 breaks: dryer can 11 (48 min), reel (16 min) before the stop and a 2nd press top felt break (66 min) after; see [[breaks-by-location]]. [downtime DT-251119-0022] [downtime DT-251119-0023] [downtime DT-251119-0025]

## What crews saw (shift reports Nov 2025)
- Before the failure: no couch roll item appears in any handover list 2025-11-01 to 2025-11-18, although Bonvoy was High from 11-07. Crews' handovers that fortnight were on the hood supply fan, thickener nozzles, ragger, winder rolls and reel spool bars instead. [Shift Report PM1-SHIFT-2025-11-18-N] [Shift Report PM1-SHIFT-2025-11-07-D]
- The day of the failure (11-19 Day, crew D, Wynn Castellano): "Couch roll: bearing failure at 14:30, 4.0 h down. Area barricaded while maintenance worked. WO 26100833"; stop line "Unplanned 243 min · Couch roll · Bearing failure". [Shift Report PM1-SHIFT-2025-11-19-D]
- CONFLICT on start time: the shift report stop line and notes say 14:30; the downtime log has 19:30 (DT-251119-0024, see above). Both kept. [Shift Report PM1-SHIFT-2025-11-19-D] [downtime DT-251119-0024]
- Same shift: a near miss at the wet end (slippery floor at the couch pit) was reported, and two breaks (dryer can 11, 48 min; reel 16 min) came before the stop. [Shift Report PM1-SHIFT-2025-11-19-D]
- Handover after the stop (11-21 Day and Night): "Couch roll: bearing failure: 4.0 h down. Couch roll bearing failed (not caught on the route). → watching after restart". [Shift Report PM1-SHIFT-2025-11-21-D] [Shift Report PM1-SHIFT-2025-11-21-N]
- Seal strip follow-up in the same month: "Couch roll: seal strip water low → check seal water flow" (11-26 Day and Night), then "→ strainer cleaned" (11-27 Day and Night). This is the first of the "seal strip water low" items later raised as BUS actions (SM-0066, SM-0151, SM-0171). [Shift Report PM1-SHIFT-2025-11-26-D] [Shift Report PM1-SHIFT-2025-11-27-D]
- Pattern: see [[shift-handover-signals-2025-11]] and [[bearing-failed-between-vibration-routes]].

## Shift reports Jan 2026 (seal strip water)
- Handover "Couch roll: seal strip water low -> check seal water flow" on 01-07 Day/Night, 01-08 Day/Night, 01-18 Day/Night and 01-19 Day/Night; no stop is logged against it in these reports. [Shift Report PM1-SHIFT-2026-01-07-D] [Shift Report PM1-SHIFT-2026-01-08-N] [Shift Report PM1-SHIFT-2026-01-18-D] [Shift Report PM1-SHIFT-2026-01-19-N]

## Shift reports Feb 2026 (seal strip water)
- Handover "Couch roll: seal strip water low -> check seal water flow" 02-19 Day to 02-20 Night; 02-21 Day/Night "strainer cleaned"; back 02-28 Day/Night "check seal water flow". Matches BUS SM-0066 (02-19). No stop logged against it. [Shift Report PM1-SHIFT-2026-02-19-D] [Shift Report PM1-SHIFT-2026-02-21-D] [Shift Report PM1-SHIFT-2026-02-28-D] [Action SM-0066]

## Shift reports Mar 2026 (seal strip water; see [[shift-handover-signals-2026-03]])
- "Couch roll: seal strip water low → strainer cleaned" 03-01 Day and Night; again "→ check seal water flow" 03-17 Day/Night and 03-18 Day/Night. No couch roll bearing or vibration item in March handovers. [Shift Report PM1-SHIFT-2026-03-01-D] [Shift Report PM1-SHIFT-2026-03-17-D] [Shift Report PM1-SHIFT-2026-03-18-N]

## Asset and Pi tags (from equipment/Pi tag listing)
- Couch roll is asset 00072210 (kind roll, section sec-forming). [equipment 00072210]
- Pi tags: PM1:COUCH_VAC (inHg) and PM1:COUCH_SOLIDS (%) mapped to position [[form-bottom]]; PM1:COUCH_DS_VIB couch roll DS bearing vibration (in/s). [Pi tag PM1:COUCH_VAC] [Pi tag PM1:COUCH_SOLIDS] [Pi tag PM1:COUCH_DS_VIB]
- See [[pi-tag-map]].

## Bonvoy (tags PM1:COUCH_DS_VIB, PM1:COUCH_VAC, PM1:COUCH_SOLIDS; tool: bonvoy_exceptions / bonvoy_report; see [[bonvoy]])
- First ramp 2025-11-07 -> 2025-11-19: High every day, daily max 0.139 -> 0.405 in/s; the last day is the RCFA-SM-25-001 failure date. [Bonvoy PM1:COUCH_DS_VIB 2025-11-07] [Bonvoy PM1:COUCH_DS_VIB 2025-11-19]
- 2026 blips: 2026-03-29 (3 h, max 0.081), 2026-09-17 (3 h, max 0.082). [Bonvoy PM1:COUCH_DS_VIB 2026-03-29] [Bonvoy PM1:COUCH_DS_VIB 2026-09-17]
- SECOND RAMP, OPEN (as of 2026-10-31): flagged every day from 2026-10-17 (10 h, max 0.086) to 2026-10-31 (24 h, max 0.243); streak 15 days; 13.5 sigma; trend +19.9 %/day. Alert limit 0.15 passed on 2026-10-26 (0.162); 0.236 on 10-31; Danger is 0.4. First ramp took 13 days from 0.139 to 0.405. [Bonvoy PM1:COUCH_DS_VIB 2026-10-17] [Bonvoy Report 2026-10-26] [Bonvoy Report 2026-10-31]
- Linked WO on the report: 26108274 "Rebuild couch roll seal strips", status 30; rcfas list empty (no RCFA open on this ramp). The WO is about seal strips, not the DS bearing. Report advice: off-route reading with a spectrum (BPFO / BPFI, 1x), check lubrication and bearing temperature. [Bonvoy Report 2026-10-25]
- This is a repeat of the Nov 2025 bearing mode after the route/sensor/grease actions were complete: [[bearing-failed-between-vibration-routes]]. Next outage [[out-2026-11-11]].
- Couch vacuum low: COUCH_VAC Low 2025-12-11 -> 2025-12-29 (19 d, daily min 17.04 -> 15.99 inHg) and 2026-07-09 -> 2026-07-16 (7 d, min ~18.0), both together with FLATBOX_VAC Low: [[bonvoy-multi-tag-dips]]. [Bonvoy PM1:COUCH_VAC 2025-12-29] [Bonvoy PM1:COUCH_VAC 2026-07-16]
- Couch solids (%): 15 tag-days, mean ~18.9-19.05 (Low 2025-12-06/08/09 and 2026-06-27, 06-28, 07-04, 09-17; High 2026-02-18, 07-10, 07-13, 10-02..07), each 3-11 h. [Bonvoy PM1:COUCH_SOLIDS 2026-10-07] [Bonvoy PM1:COUCH_SOLIDS 2025-12-06]

## BUS issues Jun-Aug 2026 (Tobias Renner; list in [[bus-issue-sheet]])
- 4 issues "Couch roll seal strip water low" (asset 00072210), "Check seal water flow" then "Strainer cleaned": 06-01 (two cycles, 6 days), 06-20 -> 06-29 (10 days), 07-09, 08-26. [BUS 2026-06-01 .. BUS 2026-06-06 | issue 98345c965dfe8fad] [BUS 2026-06-20 .. BUS 2026-06-29 | issue 184d28fc133a433e] [BUS 2026-08-26 .. BUS 2026-08-28 | issue 92843e84e31dc39b]

## BUS issues Oct 2026
- Seal strip water low, two more issues: 4aaae7885bf25d79 (10-18 to 10-19) and de56402d947a6bfa (10-24 to 10-26), Tobias Renner, both closed "Strainer cleaned". Same weeks as the Bonvoy DS bearing ramp. See [[bus-issues-2026-10-late]]. [BUS 2026-10-19] [BUS 2026-10-26]

## Work orders Feb-Jun 2026 (work-orders-2)
- Weekly PM "Lube route: wet end and press" (asset 00072210, MILL Beatrix Hale, 3 h est / 3.3 h act): 16 WOs, 26102940 (done 02-22) to 26105551 (06-06). No couch roll corrective or emergency WO in the extract. See [[work-orders-feb-jun-2026]]. [WO 26102940] [WO 26105551]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26100833 "Bearing failure: Couch roll" (type 3, prio 1, requested and completed 2025-11-19, MECH Beatrix Hale, est 12.1 h act 13.3 h): "Couch roll bearing failed (not caught on the route)." [WO 26100833]
- Weekly preventive "Lube route: wet end and press" is filed on this asset (MILL Beatrix Hale, 3 h est 3.3 h act): 17 WOs, 26100000 (done 2025-10-25) ... 26102779 (done 2026-02-14); the route ran every week before and after the failure. [WO 26100000] [WO 26102779] See [[routine-pm-work-orders]].
- Failure listed with the other emergencies in [[repeat-corrective-work-orders]].
