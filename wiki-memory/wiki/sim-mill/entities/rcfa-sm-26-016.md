---
name: rcfa-sm-26-016
description: RCFA-SM-26-016, unplanned 2nd press top felt change 05/19/2026 (7.5 h, 232 t, WO 26105306), open with SM-0138 overdue; the felt analysis MP-FA-260526, the 22% plugged HP shower and the age conflict between the RCFA and Marlow
type: rcfa
aliases: ["RCFA-SM-26-016", "unplanned felt change", "2nd press top felt filled early", "WO 26105306", "MP-FA-260526"]
---
## Record
- Event 05/19/2026 06:00, 2nd press top felt, Press section, running again 13:30 (7.5 h), production loss 232 t, lead Tobias Renner, status "Open - actions pending" [RCFA-SM-26-016]
- Emergency WO 26105306 [WO 26105306]
- Event text: "2nd press top felt filled at 3 weeks: changed early (Uhle vacuum up 4.6 inHg, 4th section steam at its limit)" [RCFA-SM-26-016]
- Root cause: "2nd press top felt filled early: HP shower nozzles plugged (22%) so the felt wasn't conditioned" [RCFA-SM-26-016]
- Contributing: "Shower nozzles not checked since the Feb audit; heavier 34 Super run in May; strainer on the shower supply not cleaned" [RCFA-SM-26-016]

## Evidence in the vendor documents
- Spraywell audit 05/13/2026: 2nd press top HP shower 22% nozzles plugged, supply strainer packed solid, "expect it to fill" [DOC SW-SA-260513 p.1]
- Marlow used-felt analysis (felt MPF-40661, 04/15 to 05/19/2026, 34 days, target 42): fill 71% vs 40-45%, water 1,180 vs 780 gsm, air perm 9 vs 19 cfm; Uhle vacuum 14.4 inHg on 05/18 vs about 10; press exit solids 42.1% [DOC MP-FA-260526 p.1]
- Marlow 05/27/2026 survey: replacement installed 05/19/2026 "running normally: 2nd press top Uhle vacuum 9.5 inHg the day before this outage" [DOC MP-SV-260527 p.1]
- CONFLICT: "filled at 3 weeks" in the RCFA vs 34 days (4.9 wk) in the Marlow analysis; both kept [RCFA-SM-26-016] [DOC MP-FA-260526 p.1]
- Steam context: SM-REF-01 lists the 4th section at 132 psig on 34 Super against the 140 limit [DOC SM-REF-01 p.2]; see [[steam-pressure-by-grade]]

## Actions (as of 10/31/2026)
- SM-0141 weekly press shower nozzle check by operations, Tobias Renner, 06/10/2026, Completed [Action SM-0141]
- SM-0139 clean the HP shower supply strainer every outage, Sunniva Brooks, 07/01/2026, Completed [Action SM-0139]
- SM-0138 add Uhle vacuum rate-of-rise to the Bonvoy watch list, Mei Fairbanks, due 07/15/2026, In progress (the only open one) [Action SM-0138]

## Links
- Position [[p2-felt-top]]; failure mode [[press-felt-plugging]]; showers [[press-hp-showers]]; Uhle trend [[uhle-box-vacuum]]; register [[rcfa-register]]
