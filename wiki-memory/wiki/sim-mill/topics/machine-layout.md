---
name: machine-layout
description: PM1 drawings - press section layout (SM-DWG-201), dryer section cans/felt rolls/rotary joints (SM-DWG-301) and roll list (SM-DWG-101); read to map a position id to its nip, section, cans and steam joint
type: topic
aliases: ["SM-DWG-201", "SM-DWG-301", "SM-DWG-101", "press section layout", "dryer sections drawing", "can numbers", "drawings"]
---
## Conventions
- "Machine direction right to left. Tending side (TS) at the bottom of the drawing." (all three drawings) [DOC SM-DWG-201 p.1]
- Sim Mill PM1 is a recycled linerboard fourdrinier [DOC HF-SV-251210 p.1]

## Press section (SM-DWG-201)
- 1st press: top roll [[p1-roll-top]], bottom roll [[p1-roll-bottom]]; felts [[p1-felt-top]] and [[p1-felt-bottom]]; Uhle boxes on the top and bottom felts [DOC SM-DWG-201 p.1]
- 2nd press: top roll [[p2-roll-top]], bottom roll [[p2-roll-bottom]]; felts [[p2-felt-top]] and [[p2-felt-bottom]]; Uhle boxes on the top and bottom felts [DOC SM-DWG-201 p.1]
- Pi tags PM1:UHLE_P1T_VAC, UHLE_P1B_VAC, UHLE_P2T_VAC, UHLE_P2B_VAC read the four Uhle boxes; see [[uhle-box-vacuum]]

## Dryer sections (SM-DWG-301 "PM1 dryer sections: cans, felt rolls and rotary joints")
- All four sections are uno-run felt runs [DOC SM-DWG-301 p.1]
- 1st dryer section: cans 1-5; felt rolls d1-froll-1 to d1-froll-5; "1st section rotary joint (DS)"; felt [[d1-felt]] [DOC SM-DWG-301 p.1]
- 2nd dryer section: cans 6-10; felt rolls d2-froll-1 to d2-froll-5; 2nd section rotary joint (DS); felt [[d2-felt]]; the [[dryer-drive-lineup]] asset is filed under the 2nd dryer section in the equipment list [DOC SM-DWG-301 p.1]
- 3rd dryer section: cans 11-15; felt rolls d3-froll-1 to d3-froll-5; [[3rd-section-rotary-joint]]; felt [[d3-felt]] [DOC SM-DWG-301 p.1]
- 4th dryer section: cans 16-20; felt rolls d4-froll-1 to d4-froll-5; [[4th-section-rotary-joint-ds]]; felt [[d4-felt]] [DOC SM-DWG-301 p.1]
- So the drawing lists 20 dryer cans (5 per section) and one DS steam rotary joint per section [DOC SM-DWG-301 p.1]; the downtime log and BUS use other can numbers (for example "Dryer can 13"), see [[dryer-cans]]

## Roll list (SM-DWG-101)
- 24 rolls: 4 press rolls and 20 dryer felt rolls, all Pellham Roll Service; targets in [[clothing-life-targets]] [DOC SM-DWG-101 p.1]
- Fleet status by roll: [[dryer-felt-roll-fleet]]
