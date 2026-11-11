---
name: bonvoy-multi-tag-dips
description: days when many Bonvoy tags (fan pump flow, steam, syphon DP, refiner kW) went Low together for ~3 h (likely stops) and the Dec 2025 / Jul 2026 vacuum dips; read before treating these as separate process problems
type: topic
aliases: ["stop signature", "3 h low on many tags", "couch vacuum low", "syphon differential low", "dryer steam low"]
---
## 3-hour simultaneous Low days (consistent with a stop or break; confirm with downtime_events)
- 2026-03-02: FAN_PUMP_FLOW Low 3 h (min 551), REF_A_KW Low 3 h, REF_B_KW Low 3 h (min -2), DRY4_DP Low 3 h. [Bonvoy PM1:FAN_PUMP_FLOW 2026-03-02] [Bonvoy PM1:REF_B_KW 2026-03-02] [Bonvoy PM1:DRY4_DP 2026-03-02]
- 2026-04-02: REF_A_KW (5 h) and REF_B_KW (4 h) Low. [Bonvoy PM1:REF_A_KW 2026-04-02] [Bonvoy PM1:REF_B_KW 2026-04-02]
- 2026-08-25: FAN_PUMP_FLOW, DRY2_DP, DRY2_STEAM_P, DRY3_STEAM_P, DRY4_DP, DRY4_STEAM_P, STEAM_FLOW, REF_A_KW all Low 3 h; DRYER_DRIVE_VIB also High that day. [Bonvoy PM1:STEAM_FLOW 2026-08-25] [Bonvoy PM1:DRY4_STEAM_P 2026-08-25] [Bonvoy PM1:REF_A_KW 2026-08-25]
- 2026-09-21: FAN_PUMP_FLOW, DRY2_DP, DRY3_DP, DRY4_DP, STEAM_FLOW Low 3 h. [Bonvoy PM1:FAN_PUMP_FLOW 2026-09-21] [Bonvoy PM1:STEAM_FLOW 2026-09-21]
- 2026-10-06: FAN_PUMP_FLOW, DRY2_DP, DRY2_STEAM_P, DRY3_DP, DRY3_STEAM_P, DRY4_DP, DRY4_STEAM_P, STEAM_FLOW, REF_A_KW, REF_B_KW Low, FLATBOX_VAC Low 5 h. [Bonvoy PM1:STEAM_FLOW 2026-10-06] [Bonvoy PM1:REF_B_KW 2026-10-06] [Bonvoy PM1:FLATBOX_VAC 2026-10-06]
- 2026-07-19: DRY3_STEAM_P and DRY4_STEAM_P Low 3 h (also PRESS1_DS_VIB High 3 h). [Bonvoy PM1:DRY3_STEAM_P 2026-07-19] [Bonvoy PM1:DRY4_STEAM_P 2026-07-19]
- Single-tag 3 h dips are not necessarily stops; the multi-tag days are the stop-like ones. Tool: downtime_events / downtime_summary for the matching dates.

## Vacuum dips (forming)
- Dec 2025: COUCH_VAC Low 2025-12-11 -> 2025-12-29 (19 tag-days; daily min falls 17.04 -> 15.99 inHg, band mean ~19.2) and FLATBOX_VAC Low 2025-12-11 -> 2025-12-24 (14 days, min ~7.93-8.0, band ~8.3-9.7). [Bonvoy PM1:COUCH_VAC 2025-12-11] [Bonvoy PM1:COUCH_VAC 2025-12-29] [Bonvoy PM1:FLATBOX_VAC 2025-12-24]
- Jul 2026: COUCH_VAC Low 2026-07-09 -> 2026-07-16 (7 listed, min ~18.0) and FLATBOX_VAC Low on 07-09, 07-12..15 and 07-17 (6 days, min ~8.2-8.3) at the same time, plus FLATBOX_VAC High 2026-07-01. [Bonvoy PM1:COUCH_VAC 2026-07-09] [Bonvoy PM1:FLATBOX_VAC 2026-07-17]
- Dec 2025 vacuum dip overlaps the dryer drive and fan pump vibration ramps ([[bearing-failed-between-vibration-routes]]), which may be coincidence; nothing in the batch links them.

## Dryer syphon differential (psi), Low
- DRY2_DP Low 2025-12-22 -> 2025-12-31 (10 days); its band mean steps 2.563 -> 2.786 (12-24) -> 3.607 (12-26) -> 2.765 (12-30) -> 2.516 (12-31), i.e. the setpoint/baseline changed during the event; later single 3 h days 2026-08-25, 09-21, 10-06 (mean ~3.62-3.63). [Bonvoy PM1:DRY2_DP 2025-12-22] [Bonvoy PM1:DRY2_DP 2025-12-26] [Bonvoy PM1:DRY2_DP 2026-10-06]
- DRY3_DP Low 2026-01-04..06 (min 1.21 on 01-06, mean 4.26) and 2026-06-20..23 (mean 3.43 -> 4.27, min 1.47-1.73); DRY3_DP means switch between ~4.26 and ~3.43-3.46 (2026-10-01/02). [Bonvoy PM1:DRY3_DP 2026-01-06] [Bonvoy PM1:DRY3_DP 2026-06-21] [Bonvoy PM1:DRY3_DP 2026-10-01]
- DRY4_DP Low 2026-04-06..10 (mean 4.84 -> 3.96 on 04-09/10) plus 3 h days (2026-03-02, 08-25, 09-21, 10-06). DRY1_DP: one tag-day, 2025-12-27 (mean 2.431, min 2.1). [Bonvoy PM1:DRY4_DP 2026-04-10] [Bonvoy PM1:DRY1_DP 2025-12-27]
- DRY1_STEAM_P High 2026-05-13 -> 05-18 (max 44.6 on 05-17, mean ~40, band ~37.6-42.4). [Bonvoy PM1:DRY1_STEAM_P 2026-05-17]
- Concept: [[syphon-differential]].
