---
name: syphon-failure
description: Dryer syphon failures (can flooded, broken syphon) and rotary joint leaks on the 2nd, 3rd and 4th section DS rotary joints, Dec 2025 - Jun 2026; 4 unplanned, 1 planned repair, 2 leak stops
type: failure-mode
aliases: ["Broken syphon", "Syphon failure (can flooded)", "rotary joint leak", "rotary joint / syphon repair", "4th section rotary joint (DS)", "2nd section rotary joint (DS)", "3rd section rotary joint (DS)", "syphon differential falling"]
---
## Syphon failures (can fills with condensate and runs cold)
- 2025-12-03 00:23 4th dryer section / 4th section rotary joint (DS), cause Broken syphon, 121 min unplanned, WO 26101127, no RCFA, grade 24#, crew A: "A dryer can's syphon broke: the can is filling with condensate and running cold. The sheet comes off wetter and the dryer drive is working harder." [downtime DT-251202-0044] [Shift Report PM1-SHIFT-2025-12-02-N]
- 2026-01-01 04:03 2nd dryer section / 2nd section rotary joint (DS), cause Syphon failure (can flooded), 151 min, WO 26101890, grade 34 Super, crew A; "syphon differential falling for 22 days before". [downtime DT-251231-0091]
- 2026-04-10 10:00 4th section rotary joint (DS), Syphon failure (can flooded), 182 min, WO 26104256, RCFA-SM-26-012, grade 34 Super; "syphon differential falling for 22 days before". [downtime DT-260410-0245]
- Planned catch: 2026-06-26 17:00 4th section rotary joint (DS), "Rotary joint / syphon repair (planned)", 121 min, WO 26106279, "found Jun 24 (syphon differential falling)"; the trend was acted on within 2 days. [downtime DT-260626-0408]
- The 4th section DS rotary joint is involved in 3 of the 4 syphon events (Dec 3, Apr 10, Jun 26). [downtime DT-251202-0044] [downtime DT-260410-0245] [downtime DT-260626-0408]
- Signal to watch: syphon differential (Pi/Bonvoy trend) falling for about 3 weeks precedes the flood stop; see the concept topic [[syphon-differential]] and [[precursor-lead-times]].

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2025-12-02 4th section rotary joint (DS) broken syphon 2.0 h, WO 26101127. [BUS 2025-12-02 issue ad7ec518d28203fc] [[4th-section-rotary-joint-ds]]
- 2025-12-31 2nd section rotary joint (DS, asset 00072546) syphon failure (can flooded) 2.5 h, WO 26101890, "syphon differential falling for 22 days before"; closed 2026-01-02. [BUS 2025-12-31 issue 9add8b189bac5bc4]
- 2026-04-10 4th section rotary joint (DS) syphon failure (can flooded) 3.0 h, WO 26104256, "syphon differential falling for 22 days before". [BUS 2026-04-10 issue 8b26ff42d76d6a24]
- 2026-01-06 3rd section rotary joint (DS) steam leak 2.7 h, WO 26102009: [[3rd-section-rotary-joint]]. [BUS 2026-01-06 issue 9d17732befc50ebd]
- Cold can 13 on the 3rd section: 11 BUS issues, each closed "Syphon reset at the outage": [[dryer-can-13]]. [BUS 2025-11-18 issue baa9b85efad5f2d6]

## What crews saw before the 2025-12-03 broken syphon (shift reports Nov 2025)
- "Dryer can 13: condensate flooding (cold can) → check syphon clearance" first on the handover 2025-11-19 (Day, Night). [Shift Report PM1-SHIFT-2025-11-19-D] [Shift Report PM1-SHIFT-2025-11-19-N]
- 11-20 (Day, Night) and 11-23 (Day, Night): "→ syphon reset at the outage", i.e. deferred to the 2025-12-10 outage rather than fixed on the run; 11-22 (Day, Night) back to "check syphon clearance". [Shift Report PM1-SHIFT-2025-11-20-D] [Shift Report PM1-SHIFT-2025-11-22-D] [Shift Report PM1-SHIFT-2025-11-23-D]
- Not on the handover after 11-23 in this batch. About 10 days later the 4th section DS rotary joint syphon broke (DT-251202-0044, 121 min, WO 26101127). Whether "can 13" is on the 4th section is not stated in the reports (dryer-can numbering note in [[machine-layout]]). [Shift Report PM1-SHIFT-2025-11-30-N] [downtime DT-251202-0044]
- Related: the flooded-can sign is "cold can"; crew handover had it for 5 days before it dropped off. See [[shift-handover-signals-2025-11]], [[precursor-lead-times]].

## Rotary joint leaks (steam blowing)
- 2026-01-06 14:40 3rd dryer section / 3rd section rotary joint (DS), cause Rotary joint leak, 162 min, WO 26102009: "Steam blowing at the 3rd section DS rotary joint; seal kit changed." [downtime DT-260106-0104]
- 2026-06-23 19:10 same joint, 174 min, WO 26106237, same note, seal kit changed again 168 days after the first; no RCFA on either. [downtime DT-260623-0397]
- Totals: syphon 3 unplanned (454 min) + 1 planned (121); leaks 2 (336 min). [downtime DT-251202-0044 to DT-260623-0397]
- Update Oct 2026: 2026-10-02 07:25 3rd section DS rotary joint leak again, 144 min, WO 26108638, "seal kit changed" (third seal change of 2026; see [[3rd-section-rotary-joint]]). [downtime DT-261002-0576]
- Update Oct 2026: second planned catch, 2026-10-16 14:00 4th section rotary joint (DS) "Rotary joint / syphon repair (planned)", 133 min, WO 26108974, grade 24#, crew B: "found Oct 13 (syphon differential falling)"; acted on in 3 days (Jun catch: 2 days). Brightwater's 10/14 survey measured that joint's differential 10% lower than March, still "OK" (see [[4th-section-rotary-joint-ds]]). [downtime DT-261016-0592] [WO 26108974] [Shift Report PM1-SHIFT-2026-10-16-D]
- The 4th section DS rotary joint now has 4 of the 6 syphon/joint-repair events in the log (Dec 3, Apr 10, Jun 26, Oct 16), 2 of them planned catches. [downtime DT-251202-0044] [downtime DT-260410-0245] [downtime DT-260626-0408] [downtime DT-261016-0592]
- Neighbours: [[dryer-cans]], [[dryer-drive-lineup]].

## Shift reports Feb 2026 (cold can 13, no stop in the month)
- Handover "Dryer can 13: condensate flooding (cold can) -> check syphon clearance" in two bursts: 02-14 Day/Night and 02-15 Day/Night (4 shifts), then 02-26 Day/Night and 02-27 Day/Night (4 shifts). No closing status in either burst. [Shift Report PM1-SHIFT-2026-02-14-D] [Shift Report PM1-SHIFT-2026-02-15-N] [Shift Report PM1-SHIFT-2026-02-26-D] [Shift Report PM1-SHIFT-2026-02-27-N]
- No syphon, rotary joint or can-flooded stop in the February reports; the next logged syphon stop is 2026-04-10 on the 4th section DS joint (can 13 is the 3rd section per the Dec/Jan notes above, so a different joint). [Shift Report PM1-SHIFT-2026-02-28-D] [downtime DT-260410-0245]
- Same item seen 2025-11-19 to 11-23, 2025-12-19 to 12-31 and 2026-01-17/18: it recurs every two to four weeks and drops off the handover without a recorded fix. See [[dryer-cans]], [[precursor-lead-times]].

## What crews saw in Jan 2026 (shift reports; tool: shift_reports)
- 2026-01-01 stop (2nd section DS syphon, 151 min, WO 26101890): handover 01-02 Day/Night "syphon failure (can flooded): 2.5 h down ... syphon differential falling for 22 days before -> closed". [Shift Report PM1-SHIFT-2026-01-02-D] [Shift Report PM1-SHIFT-2026-01-02-N]
- 2026-01-06 3rd section DS rotary joint leak, 09:40, 162 min unplanned (2.7 h), WO 26102009: "Steam blowing at the 3rd section DS rotary joint; seal kit changed." Handover 01-06: "repaired; running"; 01-07 "watching after restart"; 01-08 "closed". No handover item on the joint in the 01-02 to 01-05 reports. See [[3rd-section-rotary-joint]]. [Shift Report PM1-SHIFT-2026-01-06-D] [Shift Report PM1-SHIFT-2026-01-07-D] [Shift Report PM1-SHIFT-2026-01-08-D]
- Possible early signs with no stop in the batch: 01-17 Day/Night and 01-18 Day/Night handover "Dryer can 13: condensate flooding (cold can) -> check syphon clearance" (can 13 is in the 3rd section, cans 11-15). The 01-19 reports no longer list it. [Shift Report PM1-SHIFT-2026-01-17-D] [Shift Report PM1-SHIFT-2026-01-18-N] [Shift Report PM1-SHIFT-2026-01-19-D]
- Handover "Steam header: pressure dips at grade changes -> review boiler master response" 01-01 Day/Night; related to [[steam-pressure-by-grade]]. [Shift Report PM1-SHIFT-2026-01-01-D]

## Shift reports Mar 2026: dryer can 13 cold can (no stop; see [[shift-handover-signals-2026-03]])
- "Dryer can 13: condensate flooding (cold can) → check syphon clearance" in handovers 03-19 Day and Night; 03-20 Day and Night "→ syphon reset at the outage"; then "check syphon clearance" again 03-27 Day to 03-29 Night (6 handovers). [Shift Report PM1-SHIFT-2026-03-19-D] [Shift Report PM1-SHIFT-2026-03-20-D] [Shift Report PM1-SHIFT-2026-03-27-D] [Shift Report PM1-SHIFT-2026-03-29-N]
- No syphon stop in March; the next syphon failure in the log is 2026-04-10 on the 4th section DS rotary joint (WO 26104256, RCFA-SM-26-012). Which section dryer can 13 is in is not stated in the shift reports; the "outage" meant is not named (next on record: [[out-2026-04-15]]). [downtime DT-260410-0245]
- Can 13 is the most repeated BUS item (9 follow-ups, no RCFA): [[bus-follow-up-actions]]. [Action SM-0090]

## Shift report view of the Dec 2025 syphon events (tool: shift_reports)
- 4th section DS broken syphon, night shift Dec 2: "Down 2.0 h at 19:23 ... WO 26101127", 121 min unplanned, 278 t, sheet on 80.4%; the shift-report clock says 19:23 on Dec 2 while the downtime log says 00:23 on Dec 3 (CONFLICT of 5 h, same offset as the other Dec events). No earlier warning in the Dec 1 reports. Handover status "repaired; running" (Dec 2), "watching after restart" (Dec 3), "closed" (Dec 4). [Shift Report PM1-SHIFT-2025-12-02-N] [Shift Report PM1-SHIFT-2025-12-03-D] [Shift Report PM1-SHIFT-2025-12-04-D]
- 2nd section DS syphon (can flooded), night shift Dec 31 at 23:03, WO 26101890, 151 min, 294 t, sheet on 79.0%. [Shift Report PM1-SHIFT-2025-12-31-N]
- Early signs for the Dec 31 stop: "2nd section rotary joint (DS): section differential lower than normal. Not sure yet; flagging it" on Dec 22 N, Dec 25 N, Dec 26 D (operators), Dec 27 N (tags DRY2_DP, REEL_MOIST), Dec 29 D, Dec 30 D, Dec 31 D and N, up to 9 days before the stop; the downtime log says the syphon differential had been falling 22 days. No WO until the stop. [Shift Report PM1-SHIFT-2025-12-22-N] [Shift Report PM1-SHIFT-2025-12-27-N] [Shift Report PM1-SHIFT-2025-12-30-D] [downtime DT-251231-0091] See [[2nd-section-rotary-joint-ds]].
- Open watch item on a cold can: "Dryer can 13: condensate flooding (cold can) → check syphon clearance" in every handover from Dec 19 D to Dec 31 N (13 days) with no closing status; can 13 is in the 3rd section per the drawing. The same check was later the action for the 4th section (SM-0112). [Shift Report PM1-SHIFT-2025-12-19-D] [Shift Report PM1-SHIFT-2025-12-31-D] [Action SM-0112] See [[3rd-section-rotary-joint]], [[bus-follow-up-actions]].

## Work orders Feb-Jun 2026 (work-orders-2; see [[emergency-work-orders-feb-jun-2026]])
- WO 26104256 "Syphon failure (can flooded): 4th section rotary joint (DS)", type 3 Emergency prio 1, 2026-04-10, MECH Beatrix Hale, est 9.1 h act 10 h: "syphon differential falling for 22 days before." RCFA-SM-26-012. [WO 26104256]
- Inspection PM before it: fortnightly "Rotary joint inspection, all sections" (MECH, 2 h est) is booked on the 3rd section rotary joint (DS) asset 00072637: 26103129, 26103409, 26103843, 26104165, 26104445, 26104949, 26105257, 26105600 (done 03-03 to 06-07). The 4th section joint has no PM WO of its own in the extract. [WO 26103129] [WO 26105600]
- Outage jobs: "Inspect dryer can heads and syphons, all sections" (booked on dryer can 10) WO 26103542 ([[out-2026-04-15]], 6/6.6 h) and WO 26104599 ([[out-2026-05-27]], 4/4.4 h); "Rotary joint seal inspection, all sections" WO 26103577 (4/4.4 h) and WO 26104641 (8/8.8 h). The 04-10 flood came 5 days before the 04-15 head and syphon inspection. [WO 26103542] [WO 26104599] [WO 26103577] [WO 26104641]
- Cold-can repeats on the 3rd section: [[dryer-can-13]] (12 WOs Feb-May).

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency (type 3, prio 1, MECH Beatrix Hale): WO 26101127 broken syphon, 4th section rotary joint (2025-12-02, est 6 h act 6.6 h) [WO 26101127]; WO 26101890 "Syphon failure (can flooded): 2nd section rotary joint (DS)" (asset 00072546, requested 2025-12-31, completed 2026-01-01, est 7.5 h act 8.2 h): "syphon differential falling for 22 days before" [WO 26101890]; WO 26102009 3rd section rotary joint leak (2026-01-06, 8.9 h act) [WO 26102009].
- Dryer can 13 cold-can WOs in the same weeks (26100791, 26100889, 26101582): [[dryer-can-13]]. [WO 26101582]
- Outage "Inspect dryer can heads and syphons, all sections" (asset Dryer can 10, MECH): 26100490 ([[out-2025-12-10]], 4.4 h), 26101498 ([[out-2026-01-21]], 6.6 h), 26102562 ([[out-2026-03-04]], 6.6 h); the 2nd section joint syphon failed 21 days after the 2025-12-10 inspection (failure WO requested 2025-12-31). [WO 26100490] [WO 26101890]
- Listed with the other emergencies in [[repeat-corrective-work-orders]].
