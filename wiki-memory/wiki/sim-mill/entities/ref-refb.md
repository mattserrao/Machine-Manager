---
name: ref-refb
description: REF 2 refiner plates (asset 00072175), 84 d target; 2026-07-08 to 09-30 run showed bars 85% worn at 12 weeks (normal ~60%), Ridgeway report RR-PL-260930-B; current run 30 d
type: position
aliases: ["REF 2 refiner", "refiner B", "asset 00072175", "PM1:REF_B_KW", "REF_B_SE", "refiner plate wear"]
---
## Current picture (as of 2026-10-31)
- Current plates 30 d into an 84 d target (installed 2026-09-30), but wearing fast. [position_life ref-refb] [Bonvoy Report 2026-10-31]
- Ridgeway field visit 10/26/2026 recommends changing at 11/11 together with REF 1; SE 74.5 kWh/t on 10/25 vs 61.8 on REF 1. [DOC RR-FV-261026 p.1]
- Scoped: WO 26108911 change REF 2 plates (8 h), "Planned - parts not reserved"; one Ridgeway set on hand, SM-0241 overdue. [WO 26108911] [Action SM-0241]
- Bonvoy REF_B_SE 12-day streak on 10-31, max 86.2 kWh/t. [Bonvoy Report 2026-10-31]
- Prior run 2026-07-08 to 09-30: bars 85% worn at 12 weeks (normal ~60%), report RR-PL-260930-B. [DOC RR-PL-260930-B]
- Eight earlier planned runs were 83 d. [position_life ref-refb]
- See [[refiner-plate-wear]], [[ref-refa]], [[out-2026-11-11]].

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108911 "Change REF 2 refiner plates" (asset 00072175, MILL Beatrix Hale, 8 h), status "Planned - parts not reserved", parts Not reserved; the plates are only 30 d into 84 d but wear is fast (see below). [WO 26108911] [Action SM-0241]
- Plate gap check WO 26109163 (completed 2026-10-29). [WO 26109163]

## Run history (tool: position_life ref-refb)
- Eight planned runs of 83 d vs target 84 d, 2025-02-19 to 2026-09-30, all worn. [position_life ref-refb]
- Changeover dates: 2025-02-19, 05-14, 08-06, 10-29, 2026-01-21, 04-15, 07-08, 09-30. [position_life ref-refb]
- Bars worn as expected, energy per ton steady to the end: RR-39815, RR-40098, RR-40102, RR-40108. [position_life ref-refb]
- Normal wear, Ridgeway plate report on file: RR-39892 (2025-05-14 to 08-06) and RR-39951 (2025-08-06 to 10-29). [position_life ref-refb]
- Installed 2026-07-08, removed 2026-09-30 ([[out-2026-07-08]] to [[out-2026-09-30]]): 83 d vs target 84 d, serial RR-40140; bars 85% worn at 12 weeks (normal ~60%); leading edges rounded. Ridgeway report RR-PL-260930-B. [position_life ref-refb]

## Current run
- Installed 2026-09-30, running: 30 d vs target 84 d, serial RR-40166 (as of 2026-10-30). [position_life ref-refb]
- Computed: 84 d reached about 2026-12-23; not due at [[out-2026-11-11]] by days, but watch wear given the RR-40140 result.

## Details
- Plates: Ridgeway Refining 34" LC plate, 3.0/4.0 bar/groove ([[ridgeway-refining]]). [position_life ref-refb]
- Pi tags: PM1:REF_B_KW (motor load), PM1:REF_B_SE (specific energy kWh/t) on asset 00072175; PM1:REF_B_VIB on motor 00072182. [Pi tag PM1:REF_B_SE] [Pi tag PM1:REF_B_VIB]
- Failure mode: [[refiner-plate-wear]]. Cause of the 85% wear is not stated in this batch.
- Compare [[ref-refa]].

## Ridgeway plate reports, fast wear and early change (reports library)
- Target 12 weeks (84 d), Ridgeway 34" LC plate, 3.0/4.0 bar/groove [DOC SM-REF-02 p.1]
- Plate reports (all 83 d): 10/29/2025 to 01/21/2026 bar wear 62%, 61.3 kWh/t [DOC RR-PL-260121-B p.1]; 01/21 to 04/15/2026 60%, 62.9 kWh/t [DOC RR-PL-260415-B p.1]; 04/15 to 07/08/2026 57%, 63.0 kWh/t [DOC RR-PL-260708-B p.1]
- 07/08 to 09/30/2026: bar wear 85%, 65.4 kWh/t, pattern "Leading edges rounded"; "Wear well above normal for 12 weeks (typical 55-62%). Check stock cleanliness (sand from the cleaners) and the plate gap control." [DOC RR-PL-260930-B p.1]
- Ridgeway field visit 10/26/2026 (rep Corinne Batista; distribution Rosalind Achebe, Curtis Lindahl): REF 2 specific energy 74.5 kWh/t on 10/25, 4 weeks into the set installed 09/30/2026, against 61.8 on REF 1 at 10 weeks [DOC RR-FV-261026 p.1]
- REF 2 specific energy "has climbed about 1.4% a day since 10/07"; previous set came out at 85% bar wear; probable cause sand carry-over from the LC cleaners into the REF 2 line [DOC RR-FV-261026 p.1]
- Recommendation: change REF 2 plates at the 11/11/2026 outage (6 weeks early) together with REF 1; one set on hand, order a second now (lead time 10 days); check LC cleaner reject rates [DOC RR-FV-261026 p.1]
- This supersedes the "not due at 11/11" note above: by days the set is only about 6 weeks old, but Ridgeway asks for the change on 11/11 [DOC RR-FV-261026 p.1]; see [[out-2026-11-11]]
- Pi/tool: PM1:REF_B_SE for the specific-energy trend (tool pi_daily / pi_values); vibration PM1:REF_B_VIB stayed 0.062-0.072 in/s, no alert [DOC KV-VR-261014 p.1]
- Related failure mode [[refiner-plate-wear]]; motor event [[ref-2-refiner-motor]]

## Downtime log events (REF 2 refiner)
- 2026-03-06 14:30 Refiners / REF 2 refiner motor, cause "Motor failure", 274 min, WO 26103346, RCFA-SM-26-008, grade 34 Super, crew B. [downtime DT-260306-0196] [Shift Report PM1-SHIFT-2026-03-06-D]
- 2026-06-24 15:47 slowdown 208 min, WO 26106272, cause "Refiner plates clash": "Refiner plates clashed! The refiners tripped: no stock is going forward to the machine chest." Grade 24#, crew A. A slowdown, not a full stop. [downtime DT-260624-0400]
- The plates clash (2026-06-24) fell inside the 2026-05-27 to 2026-07-08 plate run, not the later run that wore to 85% (RR-40140, installed 2026-07-08); the log does not tie the two. [downtime DT-260624-0400]

## BUS issue (list in [[bus-issue-sheet]])
- 2026-06-24 plates clash, "machine slowed 3.5 h", WO 26106272, owner Ingrid Solberg, "Fixed; back to full rate", closed 06-25. [BUS 2026-06-24 .. BUS 2026-06-25 | issue 42aa519eea9eadaf]
- 2026-10-13 -> 10-31 (19 days, still Open): "REF 2 specific energy climbing fast on the new plates (Sep 30 set)", owner Tobias Renner: 10-13 "Check plate gap and pattern"; 10-20 "Gap OK: plates wearing; Ridgeway to look"; 10-26 "Both refiners due Nov 11: one plate set on hand, order another". [BUS 2026-10-13 .. BUS 2026-10-31 | issue 31e32f535f07b6a6] See [[out-2026-11-11]], [[ridgeway-refining]].

## Work orders Jun-Sep 2026 (WO extract work-orders-3; asset 00072175 REF 2 refiner)
- Change at [[out-2026-07-08]]: WO 26105698 (type 4, MILL Beatrix Hale, 6 h est / 6.6 h act): "Removed after 83 days. Bars worn as expected; energy per ton steady to the end." [WO 26105698] This agrees with Ridgeway's 57% wear, 63.0 kWh/t for that set.
- Change at [[out-2026-09-30]]: WO 26107791 (6 h est / 6.6 h act): "Removed after 83 days. Bars 85% worn at 12 weeks (normal ~60%); leading edges rounded. Ridgeway report RR-PL-260930-B." [WO 26107791]
- Plates clash 2026-06-24: WO 26106272 "Refiner plates clash: REF 2 refiner", type 1 Corrective, prio 2 (not Emergency type 3), requested 2026-06-24, completed 2026-06-25, 4 h est / 4.4 h act, MECH Beatrix Hale: "Refiner plates clashed! The refiners tripped: no stock is going forward to the machine chest." [WO 26106272] See [[machine-chest]].
- Preventive: "Refiner plate gap check, REF 2" (MECH, 1 h est): 4 WOs completed 2026-06-29 [WO 26106202], 07-29 [WO 26106993], 08-30 [WO 26107616], 09-27 [WO 26108414]. The gap checks ran monthly through the 07-08 to 09-30 run that wore to 85% (Ridgeway asks to check plate gap control, RR-PL-260930-B), so the WOs record the checks but not the gap readings. See [[work-orders-jun-sep-2026]].
- Next change: WO 26108911 for [[out-2026-11-11]], parts not reserved.

## Bonvoy (tags PM1:REF_B_SE 39 tag-days, REF_B_KW 3, REF_B_VIB 3; see [[refiner-plate-wear]])
- Story F3, OPEN: current plates (on since 2026-09-30) "wearing fast: energy per ton climbing since Oct 7. Only one Ridgeway set on hand for two refiners." REF_B_SE flagged every day 2026-10-20 -> 2026-10-31 (streak 12 by 10-31); daily mean 62.08 -> 64.54 kWh/t (normal ~59-60), daily max up to 86.2; 24 days into the 84-day target on 10-25, 30 on 10-31. [Bonvoy Report 2026-10-25] [Bonvoy Report 2026-10-31]
- Docs on the report: Ridgeway plate report RR-PL-260930-B (2026-09-30, the previous plate set's 85% wear) on 10-25; field visit RR-FV-261026 (2026-10-26) "REF 2 plates wearing fast" from 10-26. WO 26108911 "Change REF 2 refiner plates" status 30. [Bonvoy Report 2026-10-26]
- CONFLICT with the position run history above: it shows the next 84 d target about 2026-12-23, but the WO to change REF 2 plates is already open and the plates are wearing fast, with the order for a second Ridgeway set overdue (SM-0241, see [[ref-2-refiner-motor]]). [Bonvoy Report 2026-10-31]
- Previous plate set (2026-07-08 -> 09-30): REF_B_SE High on 09-06, 09-10..14, 09-16..19 (max 70.6), 09-24 (max 71.8), 09-26; these precede the 09-30 change. [Bonvoy PM1:REF_B_SE 2026-09-24]
- Freeness (machine chest) went Low from 2026-09-29, worst 2026-10-30/31 (min 421 mL CSF). [Bonvoy PM1:FREENESS 2026-10-31]

## Work orders Feb-Jun 2026 (work-orders-2)
- "Change REF 2 refiner" WO 26103486 at [[out-2026-04-15]] (asset 00072175, MILL Beatrix Hale, type 4 prio 2, est 6 h act 6.6 h): "Removed after 83 days. Bars worn as expected; energy per ton steady to the end." (The 07-08 REF 2 change has WO 26105698, see [[out-2026-07-08]].) [WO 26103486]
- Emergency WO 26103346 REF 2 refiner motor failure, 2026-03-06 (13.7 / 15.1 h; RCFA-SM-26-008): [[ref-2-refiner-motor]]. [WO 26103346]
- Monthly PM "Refiner plate gap check, REF 2" (MECH, 1 h est): 26103122 (done 03-01), 26103892 (03-31), 26104690 (04-30), 26105390 (05-31). [WO 26103122] [WO 26105390]
- See [[refiner-plate-wear]], [[work-orders-feb-jun-2026]].

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Plate change WO 26101449 "Change REF 2 refiner" (asset 00072175, type 4, MILL Beatrix Hale, est 6 h act 6.6 h) at [[out-2026-01-21]]: "Removed after 83 days. Bars worn as expected; energy per ton steady to the end." [WO 26101449]
- Preventive refiner plate gap check REF 2 (MECH, 1.1 h) monthly: 26100161 (done 2025-11-03), 26100966 (12-01), 26101708 (12-31), 26102352 (2026-01-30). [WO 26100161] [WO 26102352]
- See [[routine-pm-work-orders]].
