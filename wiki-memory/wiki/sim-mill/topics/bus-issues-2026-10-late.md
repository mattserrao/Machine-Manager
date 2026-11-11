---
name: bus-issues-2026-10-late
description: BUS sheet issues carried 2026-10-16 to 2026-10-31 (27 issues) with issue ids, asset numbers, owners, daily status trail, WOs and what is still Open at 10-31; read for "what was on the BUS sheet / what is still open" in late October
type: topic
aliases: ["BUS issues Oct 16-31", "BUS sheet late October 2026", "BUS issue log", "bus-issues-3"]
---
## How to read (tool: search_records / BUS sheet records; follow-up actions are in [[bus-follow-up-actions]])
- Each issue has an id (16 hex chars), asset, optional position, owner, a daily status trail (New / Open / Closed) and sometimes a WO. "On the sheet N days" is first to last date; "days open" can be shorter than that. [BUS 2026-10-16]
- Status words in the trail are the action text of the day ("Grease and monitor", "Holding"); the closing text says what was done. [BUS 2026-10-17]
- Several issues repeat a subject already seen earlier in the year (same text, new issue id); the same subject reopened within days is common (hood supply fan, couch roll, reel drive, ragger). [BUS 2026-10-23]

## Still Open or New at the last BUS date in this batch (as of 2026-10-31)
- Coarse screen rejects high (issue 4a4d548f5c3ab6ac, asset 00072098, Ingrid Solberg, WO 26109261): last status Open; 10-29 "Basket OK; reject rate back down". [BUS 2026-10-29]
- 2nd press bottom felt guide hunting (issue 8cab8b47affc5f32, asset 00072336, position [[p2-felt-bottom]], Sunniva Brooks): Open since 10-26; 10-29 "Paddle cleaned" still Open; matching follow-up action SM-0243 is open ([[open-actions]]). [BUS 2026-10-29] [Action SM-0243]
- Ragger rope breaking (issue c17ca7d4811a8054, asset 00072147, Ingrid Solberg): Open; 10-30 "Rethreaded; new rope ordered". [BUS 2026-10-30]
- Forming HP shower oscillator stalling (issue ee77f6d2028c047a, asset 00072224, Gloria Nakamura): WO 26109345 closed 10-30 ("Oscillator motor coupling replaced") but a second WO 26109380 opened 10-30 and is Open 10-31 with the same text. Open follow-ups SM-0244 and SM-0246 are for this subject. [BUS 2026-10-31] [Action SM-0244] [Action SM-0246]
- HD cleaner reject valve sticking (issue baf6ce7697bdafa1, asset 00072091, Fenna Gallagher, WO 26109387): Open; 10-31 "Valve rebuilt". [BUS 2026-10-31]
- Hood exhaust humidity high (issue 3f1bc97ee9c0ad9c, asset 00072756, Fenna Gallagher): New 10-31 "Check exhaust fan damper"; follow-up SM-0248 is open ([[hood-exhaust-fan]]). [BUS 2026-10-31] [Action SM-0248]

## Press section
- 1st press top felt conditioning low (issue 82ff70c222af914a, asset 00072252, [[p1-felt-top]], Sunniva Brooks): 10-16 New "Raise Uhle vacuum setpoint 0.5 inHg", 10-17 Open, 10-22 "Holding" Closed (7 days). See [[uhle-box-vacuum]]. [BUS 2026-10-16] [BUS 2026-10-22]
- 2nd press bottom felt guide hunting (issue f346a34c00c8f631, [[p2-felt-bottom]], Sunniva Brooks): 10-16 "Check guide paddle", 10-17 "Paddle cleaned" Closed. It came back 10-26 (issue 8cab8b47affc5f32, above): two issues in 15 days for the same subject. [BUS 2026-10-17] [BUS 2026-10-26]

## Stock prep
- Ragger rope breaking: issue 019793aae51e82ca 10-17 to 10-21 (Ingrid Solberg) closed "Rethreaded; new rope ordered"; issue c17ca7d4811a8054 10-28 to 10-31 same text, still Open (above); rope ordered twice. Prior follow-ups SM-0007, 0024, 0176. [BUS 2026-10-21] [BUS 2026-10-30]
- Coarse screen rejects high: see Open list; basket checked OK, rejects back down 10-29, issue not closed. [BUS 2026-10-29]
- Machine chest level control hunting (issue 174261405ff84137, asset 00072140, Fenna Gallagher, WO 26109275): 10-25 "Tune LIC loop", 10-26 "Retuned; steady" Closed. Earlier follow-ups in [[bus-follow-up-actions]]. [BUS 2026-10-26]
- Steam header pressure dips at grade changes (issue 60b08b4b168cf47f, asset 00072154, Eamon Takahashi, WO 26109289): 10-25 to 10-29, closed "Ramp rate changed" (boiler master response reviewed). See [[steam-pressure-by-grade]]. [BUS 2026-10-29]
- HD cleaner reject valve sticking: see Open list. [BUS 2026-10-31]

## Forming
- Couch roll seal strip water low: two issues, 4aaae7885bf25d79 (10-18 to 10-19, "Strainer cleaned") and de56402d947a6bfa (10-24 to 10-26, "Strainer cleaned"), asset 00072210, Tobias Renner; same fix twice in a week. See [[couch-roll]] (also on a Bonvoy DS bearing vibration ramp in the same weeks). [BUS 2026-10-19] [BUS 2026-10-26]
- Flat box cover wear at the TS edge (issue b60a193f532e19c3, asset 00072217, Curtis Lindahl, WO 26109128): 10-19 "Inspect at the next outage", closed 10-28 "Added to outage scope" (next outage [[out-2026-11-11]]; check outage_scope to confirm WO 26109128 is in it). [BUS 2026-10-28]
- Wire guide palm drifting to the TS (issue 4cf84368e7d22ac1, asset 00072231, Fenna Gallagher, WO 26109205): 10-22 to 10-24, closed "Regulator replaced" (guide air supply). [BUS 2026-10-24]
- Headbox edge flow streak at the FS (issue fcb7614b4894429b, asset 00072189, Tobias Renner): 10-23 "Adjust FS edge valve", 10-24 "Streak gone on the scanner" Closed; follow-up SM-0233 in [[headbox]]. [BUS 2026-10-24]
- Fan pump: "Fan pump flow and headbox pressure dipping in bursts: cavitation or impeller wear" (issue 8759513b5205e0d6, asset 00072196, Gloria Nakamura, WO 26109338): 10-28 "Check silo level and the pump suction", 10-29 "Done; running normal" Closed. Same wording as the Jan 2026 impeller RCFA precursor; see [[fan-pump]]. [BUS 2026-10-29]
- Forming HP shower oscillator stalling: see Open list. [BUS 2026-10-31]

## Dryer section
- 4th section Hood supply fan bearing noisy (issue 87b0c863b64ab1d7, asset 00072749, Gloria Nakamura): 10-16 to 10-26, "Grease and monitor" three times (WO 26109030 closed 10-17 "Quiet after greasing"; WO 26109219 opened 10-23, closed 10-24 "Quiet after greasing"; 10-25 Open again, 10-26 closed "Quiet after greasing"). Greased and recurring three times in 10 days; no vibration data on it beyond the portable route point. See [[hood-supply-fan]], [[hood-fan-failures]]. [BUS 2026-10-26]
- 2nd section PV fan amps low (asset 00072553, Gloria Nakamura): issue d024034ac50aa1c1 10-23 to 10-25 (WO 26109212) "Belts tensioned"; issue a235568853f9ec75 10-27 to 10-28 "Belts tensioned" again. Repeated within 3 days. [BUS 2026-10-25] [BUS 2026-10-28]
- Dryer can 6 (asset 00072476, 2nd dryer section): "5 sheet breaks in 24 h, mostly at the dryer" (issue d949965d5eed11b8, Tobias Renner) 10-18 "Shift leads to review break tapes", 10-19 "Watching" Closed. See [[dryer-cans]]. [BUS 2026-10-19]
- Hood exhaust humidity high: see Open list. [BUS 2026-10-31]

## Reel and winder
- Reel drive (asset 00072777) "Reel turn-up missed twice on nights", Desmond Pike: issue 78f53783d6845608 10-18 to 10-22 (WO 26109107, "Timing adjusted" 10-20; text returned 10-21, closed 10-22) and issue 58ccf65a1418a95c 10-26 to 10-30 (WO 26109317, "Timing adjusted" 10-30). Timing adjusted three times in two weeks. See [[reel-drum]]. [BUS 2026-10-22] [BUS 2026-10-30]
- Reel drum (asset 00072763): "Spool bar damage at the reel" (issue ce0af10c4b3f4801, Harlan Mbeki) 10-20 "Pull damaged spool", 10-21 "Spool sent for repair" Closed. [BUS 2026-10-21]
- Reel drum "5 sheet breaks in 24 h, mostly at the reel" (issue b4e74e9340a63f34, Tobias Renner) 10-20 to 10-21 "Watching"; and "4 sheet breaks in 24 h, mostly at the reel" (issue 84f05edde2c2487b) 10-28 to 10-29 "Watching". Two reel break flags in 9 days, while the Bonvoy reel drum Danger watch ran ([[bonvoy-report-2026-10]]). See [[reel-drum]], [[breaks-by-location]]. [BUS 2026-10-21] [BUS 2026-10-29]
- Winder slitter dust (issue 385623407f81df1e, asset 00072798, Dolores Vance): 10-29 "Change slitter blades", status flipped New again 10-31, then "Changed" Closed 10-31. CONFLICT: follow-up SM-0245 for this subject is still In progress (due 2026-11-05) in the action register. See [[winder-drums]]. [BUS 2026-10-31] [Action SM-0245]

## Counts and owners (computed from this batch)
- 27 issues; 21 Closed, 6 Open or New at last date (coarse screen, guide hunting, ragger, HP shower oscillator, HD cleaner valve, hood exhaust humidity).
- By owner: Tobias Renner 6 (dryer can 6 breaks, reel breaks x2, couch roll x2, headbox streak), Gloria Nakamura 5 (hood supply fan, PV fan x2, fan pump, HP shower oscillator), Fenna Gallagher 4 (wire guide, machine chest, HD cleaner, hood exhaust), Ingrid Solberg 3 (ragger x2, coarse screen), Sunniva Brooks 3, Desmond Pike 2, Eamon Takahashi 1, Curtis Lindahl 1, Harlan Mbeki 1, Dolores Vance 1.
