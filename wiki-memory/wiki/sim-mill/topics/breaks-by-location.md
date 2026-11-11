---
name: breaks-by-location
description: where PM1 sheet breaks happen (2nd press top felt, reel, dryer cans 3/6/11/16) with counts and minutes Nov 2025 - Sep 2026; read before answering any breaks-by-location question
type: topic
aliases: ["breaks by location", "sheet breaks by area", "break downtime by equipment", "downtime by area"]
---
## Headline (downtime log 2025-11-01 to 2026-09-01, 522 events)
- 471 of 522 logged events are sheet breaks, about 21,945 min; the rest are 38 unplanned stops (9,510 min), 10 planned (8,848 min) and 3 slowdowns (514 min). [downtime DT-251101-0001 to DT-260901-0522]
- Tool: downtime_summary group=equipment kind=break (counts and minutes); downtime_events for individual rows. Counts below were tallied from the 522-row batch and should be re-fetched before citing. [downtime DT-251101-0001 to DT-260901-0522]

## By location (breaks, minutes)
- 2nd press top felt: 175 breaks, 12,764 min (about 58% of break minutes). See [[p2-felt-top]]. [downtime DT-251106-0005 to DT-260901-0522]
- Reel drum: 122 breaks, 2,267 min; typical break 10-22 min, but one reel break was 318 min (DT-260711-0440, same day as the headbox slime stop DT-260711-0439). See [[reel-drum]]. [downtime DT-260711-0440]
- 3rd dryer section, dryer can 11: 46 breaks, 1,841 min. [downtime DT-251118-0019] [downtime DT-260901-0522]
- 1st dryer section, dryer can 3: 45 breaks, 1,858 min. [downtime DT-251109-0011]
- 4th dryer section, dryer can 16: 42 breaks, 1,603 min. [downtime DT-251109-0010]
- 2nd dryer section, dryer can 6: 41 breaks, 1,612 min. [downtime DT-251104-0004]
- All four dryer sections together: 174 breaks, 6,914 min; see [[dryer-cans]]. [downtime DT-251104-0004 to DT-260830-0518]

## By month (all locations, breaks)
- 2025-11 35, 2025-12 48, 2026-01 54, 2026-02 34, 2026-03 38, 2026-04 43, 2026-05 73, 2026-06 52, 2026-07 54, 2026-08 37, 2026-09 3 (to 09-01). May 2026 is the peak. [downtime DT-260501-0281 to DT-260531-0359]

## Update: 2026-09-02 to 2026-10-31 (downtime log, 107 events; tool: downtime_summary group=equipment kind=break, re-fetch before citing)
- 98 breaks, about 4,448 min (counted from the rows): 2nd press top felt 38 / 2,734 min; reel drum 30 / 487; dryer can 6 9 / 298; can 11 8 / 354; can 16 7 / 319; can 3 6 / 256. [downtime DT-260901-0523 to DT-261030-0629]
- The 2nd press top felt is again about 61% of break minutes (2,734 of 4,448, computed); the four dryer cans together are 30 breaks, 1,227 min. [downtime DT-260901-0523 to DT-261030-0629]
- By month: Sep 47 breaks (2,092 min; press 19 / 1,352, reel 18 / 304); Oct 51 breaks (2,356 min; press 19 / 1,382, reel 12 / 183, can 6 7, can 16 5, can 3 4, can 11 4). [downtime DT-260901-0523 to DT-261030-0629]
- Non-break rows in the same window: 4 unplanned (1,044 min) and 5 planned (1,898 min, of which the 1,200 min outage); see [[downtime-by-category]]. [downtime DT-260907-0534 to DT-261029-0626]
- Longest breaks: 93 min (DT-261027-0622), 92 (DT-261029-0628), 91 (DT-260902-0524, DT-261008-0581), all at the 2nd press top felt. [downtime DT-261027-0622] [downtime DT-261029-0628]
- Full-log reading (Nov 2025 - Oct 2026): add this window to the 471 breaks / 21,945 min above for about 569 breaks / 26,393 min (computed). [downtime DT-251101-0001 to DT-261030-0629]

## Cautions
- Break minutes are dominated by press breaks (avg about 73 min) versus reel (about 19 min) and dryer (about 40 min); count and minutes rank locations differently. [downtime DT-251106-0005]
- Crew and grade splits are raw counts, not normalised for hours run: [[breaks-by-crew-and-grade]].
- Non-break downtime for the same period: [[downtime-by-category]].
