---
name: 4th-section-rotary-joint-ds
description: 4th section rotary joint (DS), asset 00072728 - syphon came loose and flooded the can 2026-04-10 (RCFA-SM-26-012 closed); syphon differential alarm action; also see 3rd section rotary joint leaks
type: equipment
aliases: ["asset 00072728", "4th section rotary joint", "syphon failure", "can flooded", "PM1:DRY4_DP"]
---
- 2026-04-10 syphon failure (can flooded), 3 h, 94 t; root cause "Syphon came loose in the can and flooded it"; contributing "Syphon differential fell for days before the stop"; Pi PM1:DRY4_DP, PM1:REEL_MOIST about 11 days before; RCFA-SM-26-012 closed 2026-05-21; lead Mei Fairbanks. [RCFA-SM-26-012]
- Actions done (Gloria Nakamura): check syphon clearances on the DS cans at the next outage SM-0112 (2026-04-27); alarm on syphon differential below 60% of normal SM-0111 (2026-05-21). [Action SM-0112] [Action SM-0111]
- 2026-10-16 14:00 planned "Rotary joint / syphon repair (planned)", 133 min, WO 26108974, grade 24#, crew B: "found Oct 13 (syphon differential falling)". Planned catch (the 2nd after 2026-06-26, WO 26106279), 3 days after the trend was seen and 2 days after Brightwater's 10/14 survey logged the differential 10% below March. No RCFA, no flood stop since 2026-04-10 in the log. [downtime DT-261016-0592] [WO 26108974] [downtime DT-260626-0408]
- Concept page: [[syphon-differential]].
- Separate open item on the 3rd section: SM-0230 "Root cause review: 3rd section rotary joint leaks (Jan, Jun, Oct)", Eamon Takahashi, bucket Reliability, due 2026-11-20, Not started; "Three seal failures this year; none hit the RCFA threshold." [Action SM-0230] (see [[open-actions]])
- Related BUS: Dryer can 13 condensate flooding (cold can), 9 follow-ups, Eamon Takahashi ([[bus-follow-up-actions]]).

## Work orders (work-order extract, 2026-09-27 to 2026-10-31; see [[work-order-routes-and-corrective]])
- WO 26108974 "Rotary joint / syphon repair (planned): 4th section rotary joint (DS)", prio 1, planned and completed 2026-10-16, est 6.7 h act 7.4 h (asset 00072728). [WO 26108974]

## BUS issues (owner Eamon Takahashi; list in [[bus-issue-sheet]])
- 2026-05-09 -> 05-19 "4th section steam at its limit on 34 Super: speed held back ~80 fpm"; action "Running slower on 34 Super until the felt is changed" (the 2nd press top felt was changed 05-19, [[p2-felt-top]]). [BUS 2026-05-09 .. BUS 2026-05-19 | issue 49269d69211214f3]
- 2026-06-24 -> 06-26 "Syphon differential falling: a can is flooding (syphon or joint)": steam and condensate survey, joint seal kit and syphon check planned, WO 26106279, closed "Done; running normal". [BUS 2026-06-24 .. BUS 2026-06-26 | issue 51a8520b6a798d47]
- 2026-10-13 -> 10-16 same text, WO 26108974, closed 10-16 "Done; running normal"; the Brightwater survey of 10-14 (3.68 psi) is below. [BUS 2026-10-13 .. BUS 2026-10-16 | issue 4966ad93f1acce50]

## BUS issues (see [[bus-sheet-issues-2025-11-to-2026-05]])
- 2025-12-02 broken syphon 2.0 h ("the can is filling with condensate and running cold. The sheet comes off wetter and the dryer drive is working harder"), WO 26101127, Gloria Nakamura, closed 2025-12-04. [BUS 2025-12-02 issue ad7ec518d28203fc]
- 2026-04-10 syphon failure (can flooded) 3.0 h, WO 26104256, "syphon differential falling for 22 days before", closed 2026-04-12. [BUS 2026-04-10 issue 8b26ff42d76d6a24]

## Brightwater steam and condensate surveys (reports library)
- 03/18/2026: 4th section DS joint 99 psig, syphon differential 4.07 psi, OK; "All joints and syphons within spec"; the survey is 23 days before the 04/10/2026 syphon failure and found nothing (computed) [DOC BS-SS-260318 p.1] [RCFA-SM-26-012]
- 10/14/2026: 100 psig, 3.68 psi, OK; differential 10% lower than in March (computed), the largest fall of the four joints [DOC BS-SS-261014 p.1]
- Grade setpoint for the 4th section is 120-135 psig, limit 140 (SM-REF-01); the survey reading of 99-100 psig is on a different basis, see [[steam-pressure-by-grade]]
- 4th section: cans 16-20, felt rolls d4-froll-1 to d4-froll-5, felt [[d4-felt]] [DOC SM-DWG-301 p.1]
- Sibling: [[3rd-section-rotary-joint]] (replace joint, 10/14/2026 finding)

## Work order 2026-06-26 (planned catch)
- WO 26106279 "Rotary joint / syphon repair (planned): 4th section rotary joint (DS)": type 1 Corrective, prio 1, requested 2026-06-24, planned and completed 2026-06-26, no outage, 6 h est / 6.6 h act, MECH Beatrix Hale. Matches the planned 121 min stop (DT-260626-0408) found on the 06-24 syphon differential trend. [WO 26106279] [downtime DT-260626-0408]

## Asset and Pi tags (from equipment/Pi tag listing)
- 4th section rotary joint (DS) is asset 00072728 (kind joint, section sec-dryer-4). Pi tags: PM1:DRY4_STEAM_P steam pressure (psig) and PM1:DRY4_DP syphon differential (psi). [equipment 00072728] [Pi tag PM1:DRY4_STEAM_P] [Pi tag PM1:DRY4_DP]
- See [[pi-tag-map]].

## Work orders Feb-Jun 2026 (work-orders-2)
- Emergency WO 26104256 (2026-04-10, syphon failure, can flooded; est 9.1 h act 10 h; "syphon differential falling for 22 days before"; RCFA-SM-26-012). Detail: [[syphon-failure]], [[emergency-work-orders-feb-jun-2026]]. [WO 26104256]

## Work orders Oct 2025 - Feb 2026 (WO extract work-orders-1)
- Emergency WO 26101127 "Broken syphon: 4th section rotary joint (DS)" (asset 00072728, type 3, prio 1, requested and completed 2025-12-02, MECH Beatrix Hale, est 6 h act 6.6 h): "A dryer can's syphon broke: the can is filling with condensate and running cold. The sheet comes off wetter and the dryer drive is working harder." [WO 26101127]
- Three weeks later the dryer drive lineup bearing failed (2025-12-24, [[dryer-drive-lineup]]); the WO text for the syphon already mentions the drive working harder. [WO 26101694] [WO 26101127]
