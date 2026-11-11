---
name: vacuum-pump
description: Vacuum pump (asset 00072238, Forming) - vanes worn through / seal water starved Dec 2025 (RCFA-SM-25-003 closed); repeated BUS "seal water temperature high" follow-ups
type: equipment
aliases: ["asset 00072238", "couch vacuum pump", "seal water"]
---
- 2025-12-30 vacuum pump failure, 4.2 h, 129 t; root cause "Vacuum pump vanes worn through; seal water starved"; contributing "Seal water strainer plugged; no vibration on the pump"; RCFA-SM-25-003 closed 2026-02-01; lead Mei Fairbanks. [RCFA-SM-25-003]
- Pi trend about 17 days before the stop in PM1:COUCH_VAC, PM1:COUCH_SOLIDS, PM1:FLATBOX_VAC. [RCFA-SM-25-003]
- Actions done: seal water flow switch SM-0031 (2026-01-16); add pump to the vibration route SM-0030 (2026-02-01); Gloria Nakamura. [Action SM-0031] [Action SM-0030]
- BUS follow-ups "Vacuum pump seal water temperature high" (after the RCFA): SM-0106 (created 2026-04-06, completed 2026-04-17, 4 days late), SM-0117 (2026-04-22), SM-0170 (2026-07-07), all completed. [Action SM-0106] [Action SM-0117] [Action SM-0170]
- Seal-water issues recurring on BUS after the flow switch was installed; no second RCFA in this batch. See [[bus-follow-up-actions]], [[form-bottom]] (same Pi tags).

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO 26108554 "Vacuum pump seal water temperature high" corrective (completed 2026-10-01, 6.6 h). Weekly "Vacuum pump seal water check": 26108645, 26109051 done; 26109401 Entered (planned 11-06). [WO 26108554] [WO 26109401]

## What crews saw in Nov 2025 (shift reports; one month before the 12-30 failure)
- "Vacuum pump: seal water temperature high → check cooling water" on the handover every shift from 2025-11-28 Day to 2025-11-30 Night (6 shifts), never recorded as fixed. [Shift Report PM1-SHIFT-2025-11-28-D] [Shift Report PM1-SHIFT-2025-11-30-N]
- RCFA-SM-25-003 root cause is "seal water starved" with a plugged strainer; the crew sign two to four weeks earlier was high seal water temperature. The later BUS actions of the same wording (SM-0106, SM-0117, SM-0170) repeat it. [RCFA-SM-25-003] [Action SM-0106]
- See [[shift-handover-signals-2025-11]].

## What crews saw before the 2025-12-30 failure (shift reports; tool: shift_reports)
- First flag: night shift Dec 7 "Something to look at on the Vacuum pump: couch vacuum down a bit. Not sure yet; flagging it", 23 days before the stop. [Shift Report PM1-SHIFT-2025-12-07-N]
- Repeated on Dec 10 D, Dec 11 D, Dec 12 N, Dec 14 D, Dec 16 N, Dec 17 D, Dec 22 D, Dec 25 D and N, Dec 27 D and N, Dec 30 D; always "couch vacuum down a bit", never escalated to a WO before the stop. [Shift Report PM1-SHIFT-2025-12-10-D] [Shift Report PM1-SHIFT-2025-12-11-D] [Shift Report PM1-SHIFT-2025-12-14-D] [Shift Report PM1-SHIFT-2025-12-25-N] [Shift Report PM1-SHIFT-2025-12-30-D]
- Pi tags named in the notes: "COUCH_VAC, COUCH_SOLIDS, FLATBOX_VAC" on Dec 16 N, Dec 22 D and Dec 27 N (the same three tags as RCFA-SM-25-003). [Shift Report PM1-SHIFT-2025-12-16-N] [Shift Report PM1-SHIFT-2025-12-22-D] [Shift Report PM1-SHIFT-2025-12-27-N]
- Handover item "Vacuum pump: seal water temperature high → check cooling water" ran from Dec 17 D (13 days before the stop) to Dec 28 N; Dec 23 D status "strainer cleaned"; item dropped from handover Dec 29. The RCFA contributing cause was a plugged seal water strainer; the strainer was cleaned 7 days before the failure and the pump still failed. [Shift Report PM1-SHIFT-2025-12-17-D] [Shift Report PM1-SHIFT-2025-12-23-D] [Shift Report PM1-SHIFT-2025-12-28-N] [RCFA-SM-25-003]
- Related seal-water note: Dec 27 D handover "Couch roll: seal strip water low → strainer cleaned" ([[couch-roll]]). [Shift Report PM1-SHIFT-2025-12-27-D]
- Stop: night shift Dec 30, "Down 4.2 h at 20:49, Vacuum pump: vacuum pump failure. WO 26101876", 249 min unplanned, 241 t, sheet on 65.4%, grade 31# then 34 Super (shift-report clock; the downtime log shows 01:49 on Dec 31, 5 h later). Handover then "failure: 4.2 h down ... couch vacuum falling off with the pump at full speed for 33 days before. → repaired; running". [Shift Report PM1-SHIFT-2025-12-30-N]
- Pattern: rising seal-water temperature plus slowly falling couch vacuum were both in handovers for 2 to 3 weeks; see [[precursor-lead-times]]. Bonvoy view of the same days: [[bonvoy-multi-tag-dips]].

## Keel vibration route (reports library; see [[vibration-routes]])
- "Vacuum pump (portable)" readings in/s: 0.071 (11/12/2025), 0.077 (12/10/2025), 0.084, 0.075, 0.074, 0.083, 0.081, 0.089 (06/10/2026), 0.076, 0.089 (08/12), 0.084, 0.075 (10/14/2026); no alert [DOC KV-VR-251112 p.1] [DOC KV-VR-261014 p.1]
- Highest portable on every route (0.071-0.089 vs 0.04-0.076 for the others); the pump was already a route point before the 12/30/2025 failure although RCFA-SM-25-003 says "no vibration on the pump" (CONFLICT; the failure was vanes/seal water, not bearing vibration) [RCFA-SM-25-003] [DOC KV-VR-251210 p.1]

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2025-12-30 BUS issue: vacuum pump failure 4.2 h, WO 26101876, Gloria Nakamura, "couch vacuum falling off with the pump at full speed for 33 days before"; closed 2026-01-02. [BUS 2025-12-30 issue 16a177312655c28c]
- "Vacuum pump seal water temperature high": 8 issues, always "Check cooling water" then "Strainer cleaned" (Gloria Nakamura): 2025-11-28 (WO 26101057; 10 days), 12-17 (WOs 26101547, 26101645), 12-26 (WO 26101764), 2026-01-18 (WO 26102247), 03-02 (WO 26103269), 03-12 (WO 26103619), 04-06 (WO 26104193; 10 days), 04-22 (WO 26104655; 10 days). [BUS 2025-11-28 issue cbcd63ef435f4147] [BUS 2026-04-22 issue feff58fa782344a5]
- Three of the eight (11-28, 12-17, 12-26) were raised in the 5 weeks before the 12-30 failure and were closed by cleaning the strainer; RCFA-SM-25-003 lists "Seal water strainer plugged" as contributing, so the BUS warnings preceded the failure. After the flow switch (SM-0031, 2026-01-16) five more were raised, all again closed by strainer cleaning. [BUS 2025-12-26 issue 5f6a0c1a449b1732] [RCFA-SM-25-003]

## BUS issues May-Sep 2026 (Gloria Nakamura; list in [[bus-issue-sheet]])
- 7 issues "Vacuum pump seal water temperature high", all "Check cooling water" then "Strainer cleaned": 05-13 (WOs 26105187, 26105236; 7 days), 05-21, 06-11 (WO 26105964), 06-27 -> 07-08 (WO 26106566; 15 days, three cleanings), 07-25 (WO 26107105), 09-06, 09-23 (WOs 26108484, 26108554). The strainer keeps plugging, the cause of the Dec 2025 failure. [BUS 2026-05-13 .. BUS 2026-05-17 | issue f2e7d8d71227eef4] [BUS 2026-06-27 .. BUS 2026-07-08 | issue 11cccf2746d211ff] [BUS 2026-09-23 .. BUS 2026-10-01 | issue 12d9aba0bd6d29da]

## Downtime log event
- 2025-12-31 01:49 Forming / Vacuum pump, cause "Vacuum pump failure", 249 min, WO 26101876, RCFA-SM-25-003, grade 31#, crew A: "couch vacuum falling off with the pump at full speed for 33 days before" (RCFA says about 17 days of Pi trend; both kept). [downtime DT-251230-0089] [Shift Report PM1-SHIFT-2025-12-30-N]

## Shift reports after the Dec 2025 failure (tool: shift_reports)
- 2026-01-01 Day and Night handover: "Vacuum pump: failure: 4.2 h down. Vacuum pump failure: couch vacuum falling off with the pump at full speed for 33 days before. -> watching after restart". The early sign crews are told to look for is couch vacuum falling with the pump already at full speed. [Shift Report PM1-SHIFT-2026-01-01-D] [Shift Report PM1-SHIFT-2026-01-01-N]
- 2026-01-19 Day and Night handover: "Vacuum pump: seal water temperature high -> strainer cleaned"; the plugged seal water strainer was a contributing cause in RCFA-SM-25-003, so this is the same early sign recurring 20 days after the failure. [Shift Report PM1-SHIFT-2026-01-19-D] [Shift Report PM1-SHIFT-2026-01-19-N]
- Couch roll "seal strip water low -> check seal water flow" handovers on 01-07, 01-08, 01-18, 01-19 are a separate item, see [[couch-roll]]. [Shift Report PM1-SHIFT-2026-01-07-D]

## Shift reports Mar 2026 (seal water; no stop; see [[shift-handover-signals-2026-03]])
- "Vacuum pump: seal water temperature high" in handovers 03-02 Day and Night ("check cooling water"), 03-03 Day and Night ("strainer cleaned"); again 03-12 and 03-13 Day/Night ("check cooling water") and 03-14 Day/Night ("strainer cleaned"). [Shift Report PM1-SHIFT-2026-03-02-D] [Shift Report PM1-SHIFT-2026-03-03-N] [Shift Report PM1-SHIFT-2026-03-13-D] [Shift Report PM1-SHIFT-2026-03-14-N]
- Two episodes in March, each cleared by cleaning the seal water strainer, the same cause as the Dec 2025 failure (strainer plugged). The BUS follow-up ids listed above (SM-0106, 0117, 0170) start 2026-04-06, so these March items have no follow-up id in [[bus-follow-up-actions]]. No pump stop in March. [Shift Report PM1-SHIFT-2026-03-14-D] [Action SM-0106]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072238, MECH Beatrix Hale)
- "Vacuum pump seal water temperature high" corrective prio 3: 4 WOs completed 2026-06-14 [WO 26105964], 07-08 [WO 26106566], 07-27 [WO 26107105], 09-26 [WO 26108484]. WO 26106566 was requested 2026-07-07, the day BUS follow-up SM-0170 was created. [Action SM-0170]
- "Vacuum pump seal water check" preventive (1 h est): 8 WOs completed 2026-06-20 to 2026-09-25 (about every two weeks). Recurrence after the seal water flow switch (SM-0031): 4 corrective WOs in 4 months, no RCFA. See [[work-orders-jun-sep-2026]].

## Asset and Pi tags (from equipment/Pi tag listing)
- Vacuum pump is asset 00072238 (kind pump, section sec-forming); no Pi tag is mapped to it in the Pi tag listing. [equipment 00072238]

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- 6 "Vacuum pump seal water temperature high" WOs, MECH Beatrix Hale, type 1 prio 3, all Closed (requested -> done, actual h): 26103269 (03-02 -> 03-03, 4.4), 26103619 (03-12 -> 03-14, 3.3), 26104193 (04-06 -> 04-15, 4.4), 26104655 (04-22 -> 05-01, 6.6), 26105187 (05-14 -> 05-15, 6.6), 26105236 (05-16 -> 05-17, 6.6); 31.9 h (computed). The job size grew from 3.3-4.4 h to 6.6 h. [WO 26103269] [WO 26103619] [WO 26104193] [WO 26104655] [WO 26105187] [WO 26105236]
- Dates match BUS follow-ups: WO 26104193 requested 04-06 (SM-0106 created 04-06, completed 04-17) and WO 26104655 requested 04-22 (SM-0117). [Action SM-0106] [Action SM-0117]
- 8 fortnightly "Vacuum pump seal water check" PM WOs (MECH, 1 h est): 26103073, 26103353, 26103766, 26104109, 26104375, 26104893, 26105201, 26105537 (done 03-01 to 06-05). Corrective seal-water WOs kept coming despite the PM and the flow switch SM-0031. [WO 26103073] [WO 26105537] [Action SM-0031]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26101876 "Vacuum pump failure: Vacuum pump" (type 3, prio 1, requested 2025-12-30, completed 2025-12-31, MECH Beatrix Hale, est 12.5 h act 13.8 h): "couch vacuum falling off with the pump at full speed for 33 days before." [WO 26101876]
- Corrective "Vacuum pump seal water temperature high" (type 1, prio 3): 5 WOs, 26101057 (requested 2025-11-28, done 12-07), 26101547 (12-17, done 12-23), 26101645 (12-21, done 12-23), 26101764 (12-26, done 2026-01-01), 26102247 (2026-01-18, done 01-19). Four of the five were requested before the 12-30 failure WO, i.e. seal water temperature was being worked for a month before the pump failed with seal water starved. [WO 26101057] [WO 26101547] [WO 26101645] [WO 26101764] [WO 26102247] [WO 26101876]
- Weekly-ish preventive "Vacuum pump seal water check" (MECH, 1.1 h): 8 WOs, 26100301 (done 2025-11-07) ... 26102772 (done 2026-02-13). [WO 26100301] [WO 26102772]
- See [[repeat-corrective-work-orders]].
