---
name: headbox
description: Headbox (Forming) stops Jun - Jul 2026 - side door blew off (79 min) and slime build-up (315 min, RCFA-SM-26-020); read with the slime-buildup failure mode
type: equipment
aliases: ["Forming / Headbox", "headbox side door", "headbox approach", "PM1:HB_P"]
---
## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- Scoped for [[out-2026-11-11]]: WO 26108778 "Headbox slice inspection and clean" (OPS, 6 h, Reserved). [WO 26108778]
- Weekly "Operator rounds: wet end" (1 h): 26108547, 26108694, 26108925, 26109100 done; 26109282 Approved (planned 11-01). [WO 26109282]

## Downtime log events
- 2026-06-24 19:16 cause "Headbox side door blew off", 79 min unplanned, WO 26106258, grade 24#, crew A; logged at the same minute as a 1 min 2nd press top felt break (DT-260624-0401). [downtime DT-260624-0402] [Shift Report PM1-SHIFT-2026-06-24-D]
- 2026-07-11 11:08 cause "Slime build-up", 315 min unplanned, WO 26106636, RCFA-SM-26-020, grade 24#, crew D: "Slime build-up in the sheet! Speed cut to 70% and the winder is hayout city." [downtime DT-260711-0439] [Shift Report PM1-SHIFT-2026-07-11-D]
- A wad from the headbox approach caused the 2026-02-09 forming fabric hole; see [[form-bottom]]. [downtime DT-260209-0163]
- Pi tag PM1:HB_P (headbox pressure) also appears as a precursor of the fan pump failure: [[fan-pump]]. [downtime DT-260102-0094]
- Failure mode: [[slime-buildup]].

## Shift reports Jan 2026 (edge flow streak)
- Handover "Headbox: edge flow streak at the FS -> adjust FS edge valve" 01-05 Day/Night and 01-06 Day/Night; 01-07 "streak gone on the scanner". [Shift Report PM1-SHIFT-2026-01-05-D] [Shift Report PM1-SHIFT-2026-01-07-D]
- Same item again 01-29 Day/Night through 01-31 Night, still "adjust FS edge valve" with no close-out in the batch. Matches BUS "Headbox edge flow streak at the FS" (SM-0233 in Oct). [Shift Report PM1-SHIFT-2026-01-29-D] [Shift Report PM1-SHIFT-2026-01-31-N]

## Work orders Jun-Sep 2026 (tool: search_records; asset 00072189)
- Side door: WO 26106258 "Headbox side door blew off: Headbox", type 3 Emergency prio 1, requested and completed 2026-06-24, 4 h est / 4.4 h act, MECH Beatrix Hale. [WO 26106258]
- Slime: WO 26106636 "Slime build-up: Headbox", Emergency prio 1, requested and completed 2026-07-11, 15.8 h est / 17.4 h act, MECH Beatrix Hale; "Speed cut to 70% and the winder is hayout city." The WO hours are labour hours, not the 315 min stop. [WO 26106636] See [[slime-buildup]].
- Outage job "Headbox slice inspection and clean" (OPS Operations, type 4): 2026-07-08 6 h est [WO 26105733]; 2026-08-19 6 h est [WO 26106755]; 2026-09-30 4 h est [WO 26107826]. A further one (WO 26108778) is on the Oct reports above.
- Routine "Operator rounds: wet end" (OPS, 1 h est, asset Headbox): 16 weekly WOs 2026-06-14 to 2026-09-28. See [[work-orders-jun-sep-2026]].

## BUS issues Nov 2025 - Apr 2026 (see [[bus-sheet-issues-2025-11-to-2026-05]])
- "Headbox edge flow streak at the FS": 4 issues, Tobias Renner, "Adjust FS edge valve" then "Streak gone on the scanner": 2025-12-08 (10 days), 2026-01-05, 01-29 (7 days), 02-20. No WO on any. [BUS 2025-12-08 issue faa026866aeebc3b] [BUS 2026-02-20 issue 4e7565cae59e5e6d]
- The 2026-02-09 forming fabric hole from a wad off the headbox approach happened between the 01-29 and 02-20 streak issues (a link between them is not stated in the source); the fix was "Clean headbox approach piping at the outage" (closed 2026-02-13). [BUS 2026-02-10 issue d151cdf7fb993975] See [[forming-fabric-damage]].

## Asset and Pi tags (from equipment/Pi tag listing)
- Headbox is asset 00072189 (kind headbox, section sec-forming). Pi tags: PM1:HB_CONS headbox consistency (%) and PM1:HB_P headbox pressure (psi). [equipment 00072189] [Pi tag PM1:HB_CONS] [Pi tag PM1:HB_P]
- See [[pi-tag-map]].

## Bonvoy (tags PM1:HB_P 13 tag-days, PM1:HB_CONS 5 tag-days; see [[bonvoy]])
- HB_P (psi) runs in more than one mode: day mean 11.6 (band ~11.4-11.8), 7.1 (band ~6.9-7.3) and 7.9 (2026-10-11); Low flags are against that day's band. [Bonvoy PM1:HB_P 2025-12-22] [Bonvoy PM1:HB_P 2026-10-11]
- Low 11.6-mode days: 2025-12-20, 12-25, 12-27, 12-29, 2026-10-24, 10-26, 10-28 (3-7 h, min ~11.15-11.36). 7.1-mode: Low 2025-12-22, 2026-04-01, 10-13, 10-23; High 2026-05-08. [Bonvoy PM1:HB_P 2026-10-28] [Bonvoy PM1:HB_P 2026-05-08]
- In the daily reports HB_P Low appears 2026-10-26 (4 h, 7.9 sigma) and 2026-10-28 (7 h) at rank 3, with WO 26108778 "Headbox slice inspection and clean" (status 40) and doc RCFA-SM-26-020 "Slime build-up: Headbox" (2026-07-11); cause text "Stock system running below its band", check consistency control, chest levels and the pulper. [Bonvoy Report 2026-10-26] [Bonvoy Report 2026-10-28]
- HB_CONS (headbox consistency %) High 2026-05-21, 05-23 -> 05-26 (mean 0.799, max 0.844 on 05-25). [Bonvoy PM1:HB_CONS 2026-05-25]

## RCFA and action records (from the RCFA/action register)
- Asset 00072189 Headbox, area Forming: 2026-07-11 slime build-up, 5.2 h, 163 t, category Process; root cause "Slime break-off at the headbox"; contributing "Biocide program gap"; RCFA-SM-26-020 closed 2026-08-02; lead Tobias Renner. [RCFA-SM-26-020] See [[slime-buildup]].
- Action SM-0174 review biocide dosing with the chemical vendor (Ingrid Solberg), done 2026-08-02. [Action SM-0174]
- BUS follow-up "Headbox edge flow streak at the FS": SM-0233 (Tobias Renner), created 2026-10-09, completed 2026-10-17. [Action SM-0233]
- Shift reports Dec 2025: "Headbox: edge flow streak at the FS → adjust FS edge valve" Dec 9 D to Dec 10 N; no stop. Earliest instance of the subject that SM-0233 repeats in Oct 2026. [Shift Report PM1-SHIFT-2025-12-09-D] [Action SM-0233]
- Headbox approach piping stock build-up caused the 2026-02-09 forming fabric hole: [[forming-fabric-damage]], [[form-bottom]].

## Shift reports Feb 2026
- Edge flow streak at the FS: handover "adjust FS edge valve" 02-21 Day to 02-22 Night (4 shifts); gone from the 02-23 handovers with no close-out wording. Third burst after 01-05/06 and 01-29/31. [Shift Report PM1-SHIFT-2026-02-21-D] [Shift Report PM1-SHIFT-2026-02-22-N]
- Headbox approach piping: handover 02-13 "clean headbox approach piping at the outage" after the wad hole; see [[forming-fabric-damage]]. [Shift Report PM1-SHIFT-2026-02-13-D]

## BUS issues May-Oct 2026 (list in [[bus-issue-sheet]])
- 2026-05-23 -> 05-26 consistency reading drifting, basis weight off target (transmitter drift suspected): grab samples, transmitter recalibrated 05-25, WO 26105369, Fenna Gallagher. [BUS 2026-05-23 .. BUS 2026-05-26 | issue f0e31db7959d4706]
- 2026-06-24 side door blew off 1.3 h, WO 26106258 (Gloria Nakamura). [BUS 2026-06-24 .. BUS 2026-06-26 | issue abddfa02b117144a]
- 2026-07-11 slime build-up 5.2 h, "Speed cut to 70% and the winder is hayout city", WO 26106636 ([[slime-buildup]]). [BUS 2026-07-11 .. BUS 2026-07-13 | issue 5fa72e0fecdb1c77]
- "Headbox edge flow streak at the FS" (Tobias Renner, "Adjust FS edge valve" then "Streak gone on the scanner"): 5 issues, 05-07, 07-01, 09-12, 10-05, 10-09 (7 days). [BUS 2026-05-07 .. BUS 2026-05-10 | issue e12e70d031593129] [BUS 2026-10-09 .. BUS 2026-10-15 | issue 37e0fb0beda283e5]

## BUS issue Oct 2026
- Issue fcb7614b4894429b (10-23 to 10-24, Tobias Renner): edge flow streak at the FS; "Adjust FS edge valve"; closed "Streak gone on the scanner". See [[bus-issues-2026-10-late]]. [BUS 2026-10-24]

## Work orders Feb-Jun 2026 (work-orders-2; see [[work-orders-feb-jun-2026]])
- Weekly PM "Operator rounds: wet end" (asset 00072189, OPS, 1 h est): 16 WOs, 26102968 (done 02-23) to 26105593 (06-09). [WO 26102968] [WO 26105593]
- Outage "Headbox slice inspection and clean" (OPS): WO 26103521 ([[out-2026-04-15]], 6/6.6 h) and WO 26104578 ([[out-2026-05-27]], 4/4.4 h). [WO 26103521] [WO 26104578]
- "Calibrate: consistency transmitter drift on Headbox" WO 26105369, type 1 prio 3, INST Fenna Gallagher, requested 2026-05-23, done 05-26, est 2 h act 2.2 h (tag PM1:HB_CONS, see [[pi-tag-map]]). [WO 26105369]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Outage "Headbox slice inspection and clean" (OPS Operations, type 4): 26100469 ([[out-2025-12-10]], 6.6 h), 26101477 ([[out-2026-01-21]], 6.6 h), 26102541 ([[out-2026-03-04]], 8.8 h). [WO 26100469] [WO 26101477] [WO 26102541]
- The 2026-02-09 forming fabric hole (wad off the headbox approach, WO 26102842) came between the 01-21 and 03-04 slice cleans; see [[forming-fabric-damage]]. [WO 26102842]
- Weekly "Operator rounds: wet end" is filed on the headbox (OPS, 1.1 h act): 17 WOs. [WO 26100028] See [[routine-pm-work-orders]].
