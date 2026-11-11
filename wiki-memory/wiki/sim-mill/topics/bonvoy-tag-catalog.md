---
name: bonvoy-tag-catalog
description: every PM1 Bonvoy tag with description, units, area/asset, linked position and tag-day count (as of 2026-10-31); use to map a tag name to its page and to know how often it flags
type: topic
aliases: ["Bonvoy tags", "Pi tag list", "PM1 tags"]
---
Tag-day counts are the "N tag-days" in the exceptions headers, history Nov 2025 - Oct 2026. Tool: bonvoy_exceptions tag=<tag>. See [[bonvoy]].

## Vibration (in/s) and temperature
- PM1:COUCH_DS_VIB couch roll DS bearing, 30 tag-days, position none -> [[couch-roll]]. [Bonvoy PM1:COUCH_DS_VIB 2026-10-31]
- PM1:DRYER_DRIVE_VIB dryer drive lineup bearing (2nd dryer section), 68 tag-days -> [[dryer-drive-lineup]]. [Bonvoy PM1:DRYER_DRIVE_VIB 2025-11-25]
- PM1:FAN_PUMP_VIB fan pump bearing, 23 tag-days -> [[fan-pump]]. [Bonvoy PM1:FAN_PUMP_VIB 2026-08-26]
- PM1:PRESS1_DS_VIB 1st press drive bearing, 26 tag-days -> [[1st-press-drive]]. [Bonvoy PM1:PRESS1_DS_VIB 2026-07-30]
- PM1:PRESS2_DS_VIB 2nd press drive bearing, 40 tag-days -> [[2nd-press-drive]]. [Bonvoy PM1:PRESS2_DS_VIB 2026-02-24]
- PM1:PULPER_VIB pulper rotor bearing, 74 tag-days (most of any tag) -> [[pulper-rotor]]. [Bonvoy PM1:PULPER_VIB 2025-12-25]
- PM1:REEL_DRUM_DS_VIB reel drum DS bearing, 52 tag-days -> [[reel-drum]]. [Bonvoy PM1:REEL_DRUM_DS_VIB 2025-11-07]
- PM1:REEL_DRUM_DS_TEMP reel drum DS bearing temperature (degF), 48 tag-days -> [[reel-drum]]. [Bonvoy PM1:REEL_DRUM_DS_TEMP 2025-11-09]
- PM1:REF_A_VIB REF 1 refiner motor bearing, 2 tag-days, position ref-refa -> [[ref-refa]]. [Bonvoy PM1:REF_A_VIB 2025-12-08]
- PM1:REF_B_VIB REF 2 refiner motor bearing, 3 tag-days, position ref-refb -> [[ref-refb]]. [Bonvoy PM1:REF_B_VIB 2026-01-17]
- PM1:WINDER_DRUM_VIB winder drum bearing, 1 tag-day (Low, 2026-01-09). [Bonvoy PM1:WINDER_DRUM_VIB 2026-01-09]

## Refiners
- PM1:REF_A_SE REF 1 specific energy (kWh/t), 14 tag-days -> [[ref-refa]]. [Bonvoy PM1:REF_A_SE 2026-10-31]
- PM1:REF_B_SE REF 2 specific energy (kWh/t), 39 tag-days -> [[ref-refb]]. [Bonvoy PM1:REF_B_SE 2026-10-31]
- PM1:REF_A_KW / PM1:REF_B_KW refiner motor load (kW), 4 and 3 tag-days, all Low and all on stop-like days -> [[bonvoy-multi-tag-dips]]. [Bonvoy PM1:REF_A_KW 2026-03-02] [Bonvoy PM1:REF_B_KW 2026-10-06]
- PM1:FREENESS machine chest freeness (mL CSF), 8 tag-days; High Jan-Apr 2026, Low from 2026-09-29, worst 2026-10-30/31 (min 421). [Bonvoy PM1:FREENESS 2026-10-31]

## Press section
- PM1:UHLE_P1B_VAC (23), UHLE_P1T_VAC (20), UHLE_P2B_VAC (22), UHLE_P2T_VAC (10) Uhle box vacuum (inHg) -> [[uhle-box-vacuum]]. [Bonvoy PM1:UHLE_P1B_VAC 2026-08-14]
- PM1:PRESS_SOLIDS press exit solids (%), 27 tag-days, position p2-roll-bottom -> [[p2-roll-bottom]]. [Bonvoy PM1:PRESS_SOLIDS 2026-05-11]
- PM1:PRESS1_LOAD 1st press nip load (pli), 3 tag-days (557.7 mean 2026-03-31 High; 520.2 2026-06-18 Low; 580.5 2026-08-09 High). [Bonvoy PM1:PRESS1_LOAD 2026-08-09]
- PM1:PRESS2_LOAD 2nd press nip load (pli), 2 tag-days, High 2026-01-09 and 2026-04-10 (mean ~699). [Bonvoy PM1:PRESS2_LOAD 2026-04-10]

## Forming and stock
- PM1:COUCH_VAC couch vacuum (inHg), 26 tag-days; PM1:FLATBOX_VAC flat box vacuum, 23 tag-days -> [[bonvoy-multi-tag-dips]] (Dec 2025 and Jul 2026 episodes). [Bonvoy PM1:COUCH_VAC 2025-12-11] [Bonvoy PM1:FLATBOX_VAC 2025-12-11]
- PM1:COUCH_SOLIDS couch solids (%), 15 tag-days, mean ~18.9-19.0, band ~18.4-19.5. [Bonvoy PM1:COUCH_SOLIDS 2026-10-07]
- PM1:HB_P headbox pressure (psi), 13 tag-days; PM1:HB_CONS headbox consistency (%), 5 tag-days (High 2026-05-21..26, mean 0.799) -> [[headbox]]. [Bonvoy PM1:HB_CONS 2026-05-25]
- PM1:FAN_PUMP_FLOW fan pump flow (gpm), 4 tag-days, all Low 3 h on stop-like days -> [[bonvoy-multi-tag-dips]]. [Bonvoy PM1:FAN_PUMP_FLOW 2026-10-06]
- PM1:PULPER_AMPS pulper rotor current (A), 2 tag-days Low (2026-01-19, 2026-03-08); PM1:PULPER_CONS pulper consistency (%), High 2026-01-20 and 2026-09-24 (mean ~5.0). [Bonvoy PM1:PULPER_AMPS 2026-01-19] [Bonvoy PM1:PULPER_CONS 2026-01-20]
- PM1:STOCK_CHEST_LVL stock chest level (%), 2 tag-days High (2026-03-27, 2026-04-09). [Bonvoy PM1:STOCK_CHEST_LVL 2026-04-09]
- PM1:REEL_BW reel basis weight (lb/1000 ft2), 1 tag-day Low 2026-05-20; PM1:REEL_MOIST reel moisture (%), 6 tag-days High (2026-04-10, 2026-07-01..05). [Bonvoy PM1:REEL_BW 2026-05-20] [Bonvoy PM1:REEL_MOIST 2026-07-05]

## Dryer section
- PM1:DRY1_DP (1), DRY2_DP (13), DRY3_DP (11), DRY4_DP (9) syphon differential (psi), all Low; DRY1_STEAM_P (6, High, 2026-05-13..18), DRY2_STEAM_P (2), DRY3_STEAM_P (3), DRY4_STEAM_P (4) steam pressure (psig); PM1:STEAM_FLOW dryer steam flow (t/h), 3 tag-days. See [[syphon-differential]] and [[bonvoy-multi-tag-dips]]. [Bonvoy PM1:DRY2_DP 2025-12-22] [Bonvoy PM1:DRY1_STEAM_P 2026-05-13]
