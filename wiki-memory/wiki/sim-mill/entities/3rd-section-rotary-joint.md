---
name: 3rd-section-rotary-joint
description: 3rd section DS steam rotary joint (cans 11-15): three seal failures in 2026 (01/06, 06/23, 10/02), Brightwater 10/14/2026 finding "Seal worn: replace joint" and misaligned bracket, replacement wanted at the next outage; no RCFA, review action SM-0230 not started
type: equipment
aliases: ["3rd section rotary joint (DS)", "3rd section DS rotary joint", "rotary joint leak", "steam joint seal", "carbon ring", "joint bracket misaligned"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO 26108638 emergency 2026-10-02 (prio 1, 7.9 h): "Steam blowing at the 3rd section DS rotary joint; seal kit changed." [WO 26108638]
- Scoped for [[out-2026-11-11]]: WO 26108841 "Rotary joint seal inspection, all sections" (asset 00072637, MECH Beatrix Hale, 8 h, Reserved). It is an inspection; no WO to replace the joint and re-align the bracket (Brightwater 10/14) is in the extract. [WO 26108841] [DOC BS-SS-261014 p.1]
- Weekly "Rotary joint inspection, all sections": WO 26108701 (10-11), WO 26109114 (10-26). Dryer can 13 (3rd section) cold-can condensate flooding WOs 26108617 and 26108757. [WO 26108701] [WO 26109114] [WO 26108757]

## Seal failures in 2026
- Brightwater: "three seal failures this year (01/06, 06/23, 10/02), each a 2-3 h stop" [DOC BS-SS-261014 p.1]
- 2026-01-06: rotary joint leak, steam blowing at the 3rd section DS rotary joint, seal kit changed; 162 min, WO 26102009 [downtime DT-260106-0104] [WO 26102009]
- 2026-06-23: 3rd section rotary joint stop 174 min, WO 26106237 [downtime DT-260623-0397] [WO 26106237]
- 2026-10-02 07:25: third failure named by Brightwater; rotary joint leak, 144 min, WO 26108638, no RCFA, grade 31#, crew B: "Steam blowing at the 3rd section DS rotary joint; seal kit changed." Seals changed 3 times in 2026 (162, 174, 144 min = 480 min; computed); 101 days after the Jun 23 leak (computed). [downtime DT-261002-0576] [WO 26108638] [Shift Report PM1-SHIFT-2026-10-01-N]
- The Oct 2 leak came 2 days after the 2026-09-30 outage ([[out-2026-09-30]]): no joint replacement is recorded for that outage in the downtime log, and Brightwater's 10/14 survey still found "Seal worn: replace joint". [downtime DT-261002-0576] [DOC BS-SS-261014 p.1]
- Tool: downtime_events equipment="3rd section rotary joint"
- No RCFA for any of the three: "none hit the RCFA threshold"; review action SM-0230 "Root cause review: 3rd section rotary joint leaks (Jan, Jun, Oct)", Eamon Takahashi, due 11/20/2026, Not started [Action SM-0230]

## BUS issues 2026-01-06 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- Two BUS issues for the same leak: Gloria Nakamura, "Steam blowing at the 3rd section DS rotary joint; seal kit changed", 2.7 h, WO 26102009, closed 01-08; and Eamon Takahashi, "Steam leak ... 2.7 h down to change the seal", no WO, closed 01-07. [BUS 2026-01-06 issue 9d17732befc50ebd] [BUS 2026-01-06 issue db8d3bdffb9b0885]
- The cold can on this section is [[dryer-can-13]] (11 BUS issues Nov 2025 - Apr 2026).

## 2026-01-06 failure in the shift reports
- 09:40 on 01-06 Day (crew A): unplanned 162 min, "Down 2.7 h ... rotary joint leak. WO 26102009. 3rd section rotary joint (DS): repaired; running ... seal kit changed". [Shift Report PM1-SHIFT-2026-01-06-D]
- Close-out path: 01-06 N "repaired; running", 01-07 D/N "watching after restart", 01-08 D/N "closed"; night crew D "crew briefed". [Shift Report PM1-SHIFT-2026-01-07-N] [Shift Report PM1-SHIFT-2026-01-08-N]
- No crew-noted warning before the leak in the 01-02 to 01-05 reports (their handovers list wire guide, LC cleaners, fine screens, dryer can 6, headbox). [Shift Report PM1-SHIFT-2026-01-05-D]

## BUS issues (list in [[bus-issue-sheet]])
- 2026-06-23 leak 2.9 h, WO 26106237 (Gloria Nakamura, closed 06-25) plus a second issue "Steam leak ... 2.9 h down to change the seal" (Eamon Takahashi, "Seal kit changed; running", closed 06-24): one event on the sheet twice. [BUS 2026-06-23 .. BUS 2026-06-25 | issue f52bb370faa41b40] [BUS 2026-06-23 .. BUS 2026-06-24 | issue 9a965f0ae55b3510]
- 2026-10-02 leak 2.4 h, WO 26108638 (closed 10-04), again with a second Eamon Takahashi issue "Seal kit changed; running" (closed 10-03). This is the stop record the Brightwater report counts as the third failure. [BUS 2026-10-02 .. BUS 2026-10-04 | issue ab19a06e96c87d39] [BUS 2026-10-02 .. BUS 2026-10-03 | issue 706741b8dcbc9d06]
- Both times the fix was "seal kit changed"; Brightwater says seal kits alone will keep failing (below).

## Brightwater steam and condensate surveys (engineer Delphine Ortega)
- 03/18/2026: 77 psig, syphon differential 3.56 psi, OK; "re-sealed after the 01/06 leak and is running normally; watch its syphon differential" [DOC BS-SS-260318 p.1]
- 10/14/2026: 80 psig, 3.37 psi, condition "Seal worn: replace joint" (the only joint not OK) [DOC BS-SS-261014 p.1]
- Diagnosis: "The carbon ring wears unevenly: the joint body is misaligned on its support bracket." [DOC BS-SS-261014 p.1]
- Recommendation: "Replace the joint and re-align the bracket at the next outage. Seal kits alone will keep failing." [DOC BS-SS-261014 p.1]
- Next outage is [[out-2026-11-11]] (10/14 survey says "the next outage"); whether a replacement joint and bracket work are in the WO scope or parts are on hand: tool outage_scope, not in this batch.
- Syphon differential fell 3.56 to 3.37 psi (-5%) between the two surveys (computed); 4th section fell 10% over the same period, see [[steam-pressure-by-grade]]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072637 3rd section rotary joint (DS))
- Leak 2026-06-23: WO 26106237 "Rotary joint leak: 3rd section rotary joint (DS)", Emergency prio 1, requested and completed 2026-06-23, 8.7 h est / 9.6 h act, MECH Beatrix Hale; "Steam blowing at the 3rd section DS rotary joint; seal kit changed." (labour hours; the stop was 174 min). [WO 26106237]
- Outage inspection "Rotary joint seal inspection, all sections" (type 4, MECH): 2026-07-08 6 h est [WO 26105803]; 2026-08-19 4 h est [WO 26106818]; 2026-09-30 4 h est [WO 26107889]. All three were inspections; none replaced the joint, and the third failure (10/02) followed the 09/30 inspection by two days (10/02 stop per Brightwater). [DOC BS-SS-261014 p.1]
- Preventive "Rotary joint inspection, all sections" (2 h est, MECH): 8 WOs completed 2026-06-21, 07-05, 07-19, 08-02, 08-18, 08-31, 09-14, 09-28 (about every two weeks). [WO 26106020] [WO 26106398] [WO 26106657] [WO 26107126] [WO 26107378] [WO 26107686] [WO 26108120] [WO 26108421]
- See [[work-orders-jun-sep-2026]], [[dryer-can-13]] (same section 3 asset family: can 13 flooding WOs).

## Context
- 3rd dryer section: cans 11-15, felt rolls d3-froll-1 to d3-froll-5, felt [[d3-felt]] [DOC SM-DWG-301 p.1]; section steam setpoints 101-115 psig by grade in [[steam-pressure-by-grade]]
- Sibling events: 2nd and 4th section syphon failures in [[syphon-failure]] and [[4th-section-rotary-joint-ds]]; concept [[syphon-differential]]
- Open actions list: [[open-actions]]
- Shift reports Dec 2025: "Dryer can 13: condensate flooding (cold can) → check syphon clearance" appears in every handover from Dec 19 D to Dec 31 N (13 days) with no closing status; can 13 is in this section (cans 11-15). Months before the first BUS follow-up on can 13 (SM-0038, Jan 2026). [Shift Report PM1-SHIFT-2025-12-19-D] [Shift Report PM1-SHIFT-2025-12-31-N] [Action SM-0038] See [[syphon-failure]].

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- Fortnightly PM "Rotary joint inspection, all sections" (asset 00072637, MECH Beatrix Hale, 2 h est) 8 WOs: 26103129 (done 03-03), 26103409 (03-15), 26103843 (03-29), 26104165 (04-14), 26104445 (04-26), 26104949 (05-10), 26105257 (05-24), 26105600 (06-07). The 06-23 seal-kit leak ([[syphon-failure]]) came 16 days after the last of them (computed). [WO 26105600]
- Outage "Rotary joint seal inspection, all sections": WO 26103577 ([[out-2026-04-15]], est 4 h act 4.4 h) and WO 26104641 ([[out-2026-05-27]], est 8 h act 8.8 h). [WO 26103577] [WO 26104641]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26102009 "Rotary joint leak: 3rd section rotary joint (DS)" (asset 00072637, type 3, prio 1, requested and completed 2026-01-06, MECH Beatrix Hale, est 8.1 h act 8.9 h): "Steam blowing at the 3rd section DS rotary joint; seal kit changed." [WO 26102009]
- Preventive "Rotary joint inspection, all sections" is filed on this asset (MECH, 2.2 h act): 9 WOs about every 2 weeks, 26100035 (done 2025-10-26) ... 26102828 (done 2026-02-15); one was done 2026-01-05, the day before the leak. [WO 26100035] [WO 26101820] [WO 26102828] [WO 26102009]
- Outage "Rotary joint seal inspection, all sections": 26100532 ([[out-2025-12-10]], 6.6 h), 26101533 ([[out-2026-01-21]], 6.6 h), 26102597 ([[out-2026-03-04]], 8.8 h). [WO 26100532] [WO 26101533] [WO 26102597]
