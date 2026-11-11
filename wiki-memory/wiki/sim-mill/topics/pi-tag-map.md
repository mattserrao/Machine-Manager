---
name: pi-tag-map
description: which PM1 Pi tag belongs to which asset and position (reel, stock prep, refiners, forming, press, dryers, vibration tags); read to find the tag for a question
type: topic
aliases: ["Pi tags", "PM1 Pi tags", "tag to asset map", "PM1:SPEED", "PM1:BREAKS"]
---
## Reel (asset 00072763 [[reel-drum]])
- PM1:SPEED reel speed (fpm); PM1:PROD production rate (t/h); PM1:BREAKS sheet break counter since Nov 1 (count); PM1:REEL_MOIST reel moisture (%); PM1:REEL_BW reel basis weight (lb/1000 ft2). [Pi tag PM1:SPEED] [Pi tag PM1:PROD] [Pi tag PM1:BREAKS] [Pi tag PM1:REEL_MOIST] [Pi tag PM1:REEL_BW]
- PM1:REEL_DRUM_DS_VIB (in/s) and PM1:REEL_DRUM_DS_TEMP (degF) are on the DS bearing, asset 00072770. [Pi tag PM1:REEL_DRUM_DS_VIB] [Pi tag PM1:REEL_DRUM_DS_TEMP]

## Stock prep and refiners
- PM1:PULPER_AMPS rotor current (A), PM1:PULPER_VIB rotor bearing vibration (in/s): [[pulper-rotor]] 00072084. PM1:PULPER_CONS (%): pulper 00072077. [Pi tag PM1:PULPER_AMPS] [Pi tag PM1:PULPER_VIB] [Pi tag PM1:PULPER_CONS]
- PM1:STOCK_CHEST_LVL (%): stock chest 00072133. PM1:FREENESS machine chest freeness (mL CSF): 00072140. PM1:STEAM_FLOW dryer steam flow (t/h): steam header 00072154. [Pi tag PM1:STOCK_CHEST_LVL] [Pi tag PM1:FREENESS] [Pi tag PM1:STEAM_FLOW]
- PM1:REF_A_KW (kW) and PM1:REF_A_SE (kWh/t) on 00072161, PM1:REF_A_VIB on motor 00072168: position [[ref-refa]]. [Pi tag PM1:REF_A_KW] [Pi tag PM1:REF_A_SE] [Pi tag PM1:REF_A_VIB]
- PM1:REF_B_KW, PM1:REF_B_SE on 00072175, PM1:REF_B_VIB on motor 00072182: position [[ref-refb]]. [Pi tag PM1:REF_B_KW] [Pi tag PM1:REF_B_SE] [Pi tag PM1:REF_B_VIB]
- Interpretation of specific energy: [[refiner-plate-wear]].

## Forming
- PM1:HB_CONS (%), PM1:HB_P (psi): [[headbox]] 00072189. PM1:FAN_PUMP_FLOW (gpm), PM1:FAN_PUMP_VIB (in/s): [[fan-pump]] 00072196. [Pi tag PM1:HB_CONS] [Pi tag PM1:HB_P] [Pi tag PM1:FAN_PUMP_FLOW] [Pi tag PM1:FAN_PUMP_VIB]
- PM1:FLATBOX_VAC (flat boxes 00072217), PM1:COUCH_VAC and PM1:COUCH_SOLIDS (couch roll 00072210) are all attached to position [[form-bottom]]. PM1:COUCH_DS_VIB couch roll DS bearing vibration is on [[couch-roll]]. [Pi tag PM1:FLATBOX_VAC] [Pi tag PM1:COUCH_VAC] [Pi tag PM1:COUCH_SOLIDS] [Pi tag PM1:COUCH_DS_VIB]

## Press
- Uhle box vacuum (inHg): PM1:UHLE_P1T_VAC (box 00072259, [[p1-felt-top]]), PM1:UHLE_P1B_VAC (00072280, [[p1-felt-bottom]]), PM1:UHLE_P2T_VAC (00072322, [[p2-felt-top]]), PM1:UHLE_P2B_VAC (00072343, [[p2-felt-bottom]]). Interpretation: [[uhle-box-vacuum]]. [Pi tag PM1:UHLE_P1T_VAC] [Pi tag PM1:UHLE_P1B_VAC] [Pi tag PM1:UHLE_P2T_VAC] [Pi tag PM1:UHLE_P2B_VAC]
- PM1:PRESS1_LOAD, PM1:PRESS1_DS_VIB: [[1st-press-drive]] 00072308. PM1:PRESS2_LOAD, PM1:PRESS2_DS_VIB: [[2nd-press-drive]] 00072371. Nip load in pli, vibration in in/s. [Pi tag PM1:PRESS1_LOAD] [Pi tag PM1:PRESS2_LOAD]
- PM1:PRESS_SOLIDS press exit solids (%) is attached to asset 00072364, position [[p2-roll-bottom]] (not to a felt). [Pi tag PM1:PRESS_SOLIDS]

## Dryers
- Steam pressure (psig) PM1:DRY1_STEAM_P / DRY2 / DRY3 / DRY4 and syphon differential (psi) PM1:DRY1_DP / DRY2 / DRY3 / DRY4 are attached to each section's rotary joint (DS): 00072455, 00072546, 00072637, 00072728. [Pi tag PM1:DRY1_STEAM_P] [Pi tag PM1:DRY4_DP]
- PM1:DRYER_DRIVE_VIB: [[dryer-drive-lineup]] 00072742. PM1:HOOD_EXH_TEMP (degF): [[hood-exhaust-fan]] 00072756. [Pi tag PM1:DRYER_DRIVE_VIB] [Pi tag PM1:HOOD_EXH_TEMP]
- PM1:WINDER_DRUM_VIB: [[winder-drums]] 00072784. [Pi tag PM1:WINDER_DRUM_VIB]
- Dryer fabrics and felt rolls (d1 to d4) have no Pi tags in the listing. [Pi tag PM1:DRY1_STEAM_P]

## Tool
- Bonvoy tag behaviour: [[bonvoy-tag-catalog]]. Values: tools pi_values and pi_daily.
