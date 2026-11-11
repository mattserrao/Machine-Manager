---
name: production-daily-reports
description: PM1 daily Production Reports 2025-11-01 to 2026-10-30 (364 days) - monthly tons, breaks, unplanned/planned minutes, kWh/t and OME, outage and short-stop days, the Sep-Oct 2026 energy rise; read for "how much did we make / how did month X go / which days were bad"
type: topic
aliases: ["Production Report", "PM1-PROD", "daily production", "production by month", "OME daily", "tons per day", "kWh/t", "steam t/t", "uptime"]
---
## What the reports are
- One Production Report per day, id PM1-PROD-YYYY-MM-DD, covers 2025-11-01 to 2026-10-30 with no missing day (364 reports). [Production Report PM1-PROD-2025-11-01] [Production Report PM1-PROD-2026-10-30]
- Fields per day: tons (and saleable), uptime %, sheet breaks (count and min), unplanned min, planned min, slowdown min, average speed fpm, grade mix in hours (e.g. "24# 24"), steam t/t, kWh/t, OME with time / rate / quality parts, the two crews on the day. Tool: shift_reports and production (daily); downtime_summary for the event detail behind the minutes. [Production Report PM1-PROD-2026-10-30]
- Totals over the 364 days (computed): 247,692 t made, 242,771 t saleable, 569 breaks / 26,393 min, 10,554 min unplanned, 10,746 min planned, 514 min slowdown. [Production Report PM1-PROD-2025-11-01 to PM1-PROD-2026-10-30]
- The report minutes match the downtime log through 2026-08-31 for unplanned (9,510 min), planned (8,848 min) and slowdown (514 min); breaks are 470 / 21,850 min in the reports vs 471 / 21,945 min in the log through 2026-09-01 (small difference, cause not in the reports). [Production Report PM1-PROD-2025-11-01 to PM1-PROD-2026-08-31] [downtime DT-251101-0001 to DT-260901-0522]; see [[downtime-by-category]]
- Three days show break minutes with 0 breaks (2026-01-19 58 min, 2026-02-17 80 min, 2026-10-12 58 min). [Production Report PM1-PROD-2026-01-19] [Production Report PM1-PROD-2026-02-17] [Production Report PM1-PROD-2026-10-12]

## By month (tons / breaks (min) / unplanned min / planned min; mean kWh/t; mean OME)
- 2025-11: 21,325 t, 37 (1,542), 408, 0; 62.5; 83.2 [Production Report PM1-PROD-2025-11-01 to PM1-PROD-2025-11-30]
- 2025-12: 21,253 t, 46 (1,954), 962, 1,200; 63.1; 80.4 [Production Report PM1-PROD-2025-12-10]
- 2026-01: 20,827 t, 54 (2,536), 827, 1,200; 63.7; 78.8 [Production Report PM1-PROD-2026-01-21]
- 2026-02: 19,579 t, 34 (1,671), 942, 327; 62.9; 81.7 (28-day month) [Production Report PM1-PROD-2026-02-09]
- 2026-03: 20,977 t, 38 (1,979), 1,156, 1,200; 63.4; 79.3 [Production Report PM1-PROD-2026-03-04]
- 2026-04: 20,522 t, 43 (2,011), 587, 1,200; 63.0; 80.1 [Production Report PM1-PROD-2026-04-15]
- 2026-05: 20,316 t, 73 (3,130), 1,430, 1,200; 64.5; 76.5 - the worst break month (73 breaks, 3,130 min) [Production Report PM1-PROD-2026-05-14]
- 2026-06: 20,367 t, 52 (2,527), 729, 121; 63.1; 78.9 [Production Report PM1-PROD-2026-06-24]
- 2026-07: 20,369 t, 56 (2,676), 1,685, 1,200; 63.8; 75.8 - lowest OME month and most unplanned minutes [Production Report PM1-PROD-2026-07-20]
- 2026-08: 21,163 t, 37 (1,824), 784, 1,200; 63.2; 79.9 [Production Report PM1-PROD-2026-08-19]
- 2026-09: 20,311 t, 49 (2,249), 613, 1,380; 65.2; 79.3 [Production Report PM1-PROD-2026-09-30]
- 2026-10 (to 10-30): 20,683 t, 50 (2,294), 431, 518; 67.6; 81.0 [Production Report PM1-PROD-2026-10-30]
- Mean OME 79.5 over all days (81.1 excluding the eight 20 h outage days); mean 694 t/day excluding outage days. Computed from the daily rows. Reported OME = time x rate x quality parts, see [[downtime-by-category]] for the stops behind the time part.

## Outage days (planned 1,200 min, uptime 16.7%)
- Eight normal outages in the reports, each a day of 54-100 t and OME 4-12: 2025-12-10 88 t, 2026-01-21 86 t, 2026-03-04 65 t, 2026-04-15 100 t, 2026-05-27 66 t, 2026-07-08 54 t (OME 4.1), 2026-08-19 89 t, 2026-09-30 98 t. [Production Report PM1-PROD-2025-12-10] [Production Report PM1-PROD-2026-07-08] [Production Report PM1-PROD-2026-09-30]
- The outage day's kWh/t and steam t/t spike because few tons are made (e.g. 95.3 kWh/t and 2.63 t/t on 2026-07-08; 88.3 and 2.36 on 2026-03-04); do not use outage days in energy trends. [Production Report PM1-PROD-2026-07-08] [Production Report PM1-PROD-2026-03-04]
- Dates and 42-day spacing: [[planned-outage-history]]; Sep 30 changeover list: [[out-2026-09-30]]; next outage 2026-11-11: [[out-2026-11-11]] (not yet in the reports, which end 10-30).
- Day after the outage: 2026-03-05 was the best day of the year, 840 t, OME 97.1, 1 break [Production Report PM1-PROD-2026-03-05]; 2025-12-11, 2026-04-16 and 2026-07-09 each had 4 breaks of 213-242 min [Production Report PM1-PROD-2025-12-11] [Production Report PM1-PROD-2026-04-16] [Production Report PM1-PROD-2026-07-09]; 2026-01-22 and 2026-05-28 each lost 303 and 307 min unplanned [Production Report PM1-PROD-2026-01-22] [Production Report PM1-PROD-2026-05-28]; 2026-10-01 lost 144 min [Production Report PM1-PROD-2026-10-01]. See the restart press-break pattern in [[planned-outage-history]] and [[p2-felt-top]].

## Short planned stops (not outages)
- 2026-02-04 163 min [Production Report PM1-PROD-2026-02-04] and 2026-02-21 164 min [Production Report PM1-PROD-2026-02-21] and 2026-06-26 121 min [Production Report PM1-PROD-2026-06-26] match the jobs in [[planned-outage-history]].
- New in Sep-Oct 2026 (planned min in the report; the reason is not in the reports, check downtime_events with the date): 2026-09-11 180 min [Production Report PM1-PROD-2026-09-11]; 2026-10-09 169 min [Production Report PM1-PROD-2026-10-09]; 2026-10-16 133 min [Production Report PM1-PROD-2026-10-16]; 2026-10-29 216 min [Production Report PM1-PROD-2026-10-29].

## Slowdowns
- Only three days carry slowdown minutes: 2025-11-01 239 min (717 t) [Production Report PM1-PROD-2025-11-01]; 2026-03-12 67 min (dye trouble, WO 26103612) [Production Report PM1-PROD-2026-03-12]; 2026-06-24 208 min (refiner plates clash, WO 26106272, also 376 min unplanned that day, 467 t) [Production Report PM1-PROD-2026-06-24]. See [[ref-refb]].

## Worst unplanned days (unplanned min, tons)
- 2026-02-09 570 min, 432 t, OME 51.4 - forming fabric hole [Production Report PM1-PROD-2026-02-09]; see [[forming-fabric-damage]]
- 2026-07-20 510 min, 377 t (lowest non-outage day), OME 44.7 - pulper rotor bearing [Production Report PM1-PROD-2026-07-20]; see [[pulper-rotor]]
- 2026-05-19 450 min, 510 t - unplanned 2nd press top felt change [Production Report PM1-PROD-2026-05-19]; see [[p2-felt-top]]
- 2026-08-26 408 min, 554 t [Production Report PM1-PROD-2026-08-26]; 2026-09-20 412 min, 501 t [Production Report PM1-PROD-2026-09-20]; 2026-06-24 376 min [Production Report PM1-PROD-2026-06-24]; 2026-01-02 362 min, 464 t [Production Report PM1-PROD-2026-01-02]; 2026-07-21 347 min [Production Report PM1-PROD-2026-07-21]; 2026-05-12 321 min [Production Report PM1-PROD-2026-05-12]
- 2026-10-14 287 min, 582 t - latest unplanned day over 200 min [Production Report PM1-PROD-2026-10-14]
- 42 days carry unplanned minutes (10,554 min total); 26 of them are 200 min or more. Computed. Tool: downtime_events kind=unplanned for the cause of each day.
- Days with 5+ breaks: 2026-05-14 had 7 (239 min) and 2026-05-06 had 6; May 2026 holds five of the ten 5+ break days (05-01, 05-06, 05-07, 05-09, 05-14); also 2025-11-19, 2026-01-03, 2026-01-18, 2026-02-25, 2026-10-19. [Production Report PM1-PROD-2026-05-14] [Production Report PM1-PROD-2026-10-19]; see [[breaks-by-location]]
- Longest break minutes in one day: 368 min on 2026-07-11 with only 2 breaks [Production Report PM1-PROD-2026-07-11]; 300 min on 2026-03-18 [Production Report PM1-PROD-2026-03-18].
- 78 of 364 days had zero breaks. Computed.

## Energy: kWh/t rose through Sep-Oct 2026
- On steady 24# days (full 24 h of 24#, uptime 100%) mean kWh/t was 61.7-63.0 each month Nov 2025 - Aug 2026, then 64.3 in Sep 2026 and 66.9 in Oct 2026. Computed from daily rows. [Production Report PM1-PROD-2025-11-01 to PM1-PROD-2026-10-30]
- Within October on 24#: 60.5 (10-05), 63.1 (10-08), 64.8 (10-15), 69.9 (10-16), 70.0 (10-19), 71.2 (10-25), 73.4 (10-26), 72.3 (10-28). [Production Report PM1-PROD-2026-10-05] [Production Report PM1-PROD-2026-10-16] [Production Report PM1-PROD-2026-10-26]
- On 34 Super: 60.8 (10-02), 63.0 (10-12), 69.9 (10-22), 71.2 (10-23). [Production Report PM1-PROD-2026-10-02] [Production Report PM1-PROD-2026-10-22]
- Last days: 75.6 kWh/t on 2026-10-30 (31# 3 h, 34 Super 21 h) [Production Report PM1-PROD-2026-10-30]; 80.5 on 10-29 (216 min planned stop) [Production Report PM1-PROD-2026-10-29]. Highest non-outage values of the year.
- Steam t/t over the same October days stays about 1.45-1.55 on single grades, so the rise is in electrical energy, not steam. [Production Report PM1-PROD-2026-10-28]
- The report is mill-total kWh/t. Refiner REF 2 specific energy (tag PM1:REF_B_SE, new plates from 2026-09-30) is rising in Bonvoy from 10-07 but only 62-65 kWh/t at the refiner, so the refiner alone does not account for the plant rise; the cause is not stated in the reports. See [[refiner-plate-wear]], [[ref-refb]]. [Bonvoy Report 2026-10-31]
- Do not compare kWh/t across grades without the grade mix: 24# days average 63.0 and 34 Super days 63.0 on single-grade days over the year. Computed.

## Grade mix and speed seen in the reports (single-grade days, computed)
- 24#: 196 single-grade days, mean speed 2,564 fpm, 684 t/day, OME 80.6; 34 Super: 40 days, 2,000 fpm, 720 t/day, OME 83.2. Reference table speeds are 2632 (24#) and 2027 (34 Super) in [[grade-speeds-production]]; the daily "speed" is a mix average on mixed-grade days (low 1,960-2,300 fpm when 31# / 34 Super run).
- Grade change days (3-4 grades in the day) give the lowest rate and quality parts, e.g. 2025-11-18 quality 88.3 and 655 t (saleable 600) [Production Report PM1-PROD-2025-11-18]; 2026-07-08 quality 54.9 is the outage restart [Production Report PM1-PROD-2026-07-08].
- Saleable vs made: a gap of 25-50 t on grade-change days (e.g. 2026-01-29 663 t made, 612 saleable) [Production Report PM1-PROD-2026-01-29].

## Crews
- The report lists two crews per day (day / night pairs); each of A, B, C and D appears on exactly 182 of 364 days. Computed. Crew break comparison: [[breaks-by-crew-and-grade]].
