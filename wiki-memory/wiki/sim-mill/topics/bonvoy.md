---
name: bonvoy
description: what Bonvoy is (PM1 tag-exception monitor), how its exceptions and daily reports are built, alarm limits, and which tool returns what; read first for any "what is Bonvoy flagging" question
type: topic
aliases: ["Bonvoy", "Bonvoy exceptions", "Bonvoy Report", "tag exceptions", "normal band"]
---
## What it is
- Bonvoy flags PM1 Pi tags that run outside their normal band; each exception is one tag-day with hours outside, mean, band, min, max. [Bonvoy PM1:COUCH_DS_VIB 2026-10-31]
- Exception line format: direction (High/Low), "N h outside" (hours of that day), day mean, band (low-high), then min/max of the out-of-band readings. [Bonvoy PM1:COUCH_DS_VIB 2026-10-31]
- Tools: bonvoy_exceptions (per tag, per day; the history of tag-days) and bonvoy_report (one JSON per day, ranked items). [Bonvoy Report 2026-10-31]
- Catalogue of the ~40 tags with units, area, linked position and tag-day counts: [[bonvoy-tag-catalog]].
- Daily reports Oct 25-31 2026 (what was ranked, WOs, docs, alarm levels): [[bonvoy-report-2026-10]].

## How the band behaves (matters when reading the numbers)
- The band is computed from the recent mean and std, so during a ramp the band widens and its mean creeps up (couch DS vib band 0.0564-0.0802 on 2025-11-07 became -0.0071-0.1661 on 2025-11-19). [Bonvoy PM1:COUCH_DS_VIB 2025-11-07] [Bonvoy PM1:COUCH_DS_VIB 2025-11-19]
- Because the baseline moves with the defect, a tag can sit above its alarm limit and no longer be flagged: the Oct 2026 reports list REEL_DRUM_DS_VIB under "watch" with flagged false while at 0.41-0.43 in/s. [Bonvoy Report 2026-10-25]
- Some tags have more than one operating mode, so the band differs by day (HB_P means 11.6, 7.1 and 7.9 psi on different days). See [[headbox]]. [Bonvoy PM1:HB_P 2025-12-22] [Bonvoy PM1:HB_P 2026-10-11]
- Tool trap: a "Low" flag on a vibration tag with max ~0.057 is a quiet reading, not a problem. [Bonvoy PM1:PULPER_VIB 2026-10-23]

## Alarm limits seen in reports (vibration, in/s)
- Alert limit 0.15 in/s; Danger limit 0.4 in/s. [Bonvoy Report 2026-10-26] [Bonvoy Report 2026-10-25]
- Report "watch" entries carry value, level (Alert/Danger), limit and flagged true/false. [Bonvoy Report 2026-10-29]

## Patterns across the batch
- Vibration ramps that climb from ~0.08 to ~0.40 in/s over 2-5 weeks recur on six assets: [[bearing-failed-between-vibration-routes]].
- Several tags dip together for ~3 h on the same day, consistent with a stop or break (check downtime_events): [[bonvoy-multi-tag-dips]].
- Uhle box vacuum rises on press felts: [[uhle-box-vacuum]], [[press-felt-plugging]].
- Refiner specific energy / plate wear: [[refiner-plate-wear]], [[ref-refa]], [[ref-refb]].
- Report fields story F2 / F3 label the two curated stories: F2 = reel drum DS bearing defect ([[reel-drum]]), F3 = REF 2 plates wearing fast ([[ref-refb]]). [Bonvoy Report 2026-10-26]
- The reports are labelled "MM LLM (mocked for the demo)", generated_by mock. [Bonvoy Report 2026-10-25]
