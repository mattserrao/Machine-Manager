---
name: breaks-by-crew-and-grade
description: raw counts of PM1 sheet breaks by crew (A-D) and grade (24#, 28#, 31#, 34 Super) Nov 2025 - Sep 2026; counts are NOT normalised for hours run
type: topic
aliases: ["crew break rates", "breaks by crew", "breaks by grade", "crew comparison"]
---
## By crew (sheet breaks, 2025-11-01 to 2026-09-01)
- Crew A 98 breaks / 4,170 min; crew B 131 / 6,212; crew C 128 / 6,064; crew D 114 / 5,499. [downtime DT-251103-0002 to DT-260901-0522]
- 2nd press top felt breaks by crew: A 36 (2,471 min), B 49 (3,650), C 46 (3,428), D 44 (3,215). [downtime DT-251106-0005 to DT-260901-0522]
- Reel drum breaks by crew: A 31, B 29, C 30, D 32; the reel is evenly spread. [downtime DT-251103-0002 to DT-260901-0522]
- Counts are not normalised for hours on shift or for grade mix; crew A has fewer breaks possibly because of fewer hours. Normalise before ranking crews; tool: downtime_summary group=crew kind=break (and shift_reports for hours). [downtime DT-251103-0002 to DT-260901-0522]

## By grade
- All logged events by grade: 24# 362, 28# 12, 31# 56, 34 Super 92 (of 522). [downtime DT-251101-0001 to DT-260901-0522]
- 2nd press top felt breaks by grade: 24# 120, 28# 7, 31# 16, 34 Super 32. [downtime DT-251106-0005 to DT-260901-0522]
- Per-grade break rates need hours by grade; tool: grade_hours (not in the downtime log). Do not compare these counts across grades without it.
- See [[breaks-by-location]] for where breaks occur.

## Update: 2026-09-02 to 2026-10-31 (98 breaks; raw counts, counted from the rows)
- By crew: A 24 breaks / 1,061 min; B 30 / 1,397; C 18 / 799; D 26 / 1,191. [downtime DT-260901-0523 to DT-261030-0629]
- 2nd press top felt (38 breaks) by crew: A 8 (576 min), B 14 (972), C 7 (526), D 9 (660); crew B has the most again, as in Nov 2025 - Sep 2026. [downtime DT-260901-0523 to DT-261030-0629]
- By grade: 24# 66 (3,151 min), 28# 4 (137), 31# 9 (382), 34 Super 19 (778); 2nd press top felt by grade 24# 28, 28# 1, 31# 3, 34 Super 6. [downtime DT-260901-0523 to DT-261030-0629]
- Still not normalised for hours run or grade mix; use grade_hours and shift_reports. [downtime DT-260901-0523 to DT-261030-0629]
