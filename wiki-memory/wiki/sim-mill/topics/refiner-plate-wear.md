---
name: refiner-plate-wear
description: how refiner plate wear shows up in Bonvoy (specific energy kWh/t rising, freeness low) and the Oct 2026 REF 2 / REF 1 situation with plate WOs and the Ridgeway documents
type: topic
aliases: ["specific energy", "REF_A_SE", "REF_B_SE", "plate wear", "Ridgeway plates", "refiner plates"]
---
Positions: [[ref-refa]] (REF 1), [[ref-refb]] (REF 2). Tool: bonvoy_exceptions tag=REF_B_SE; bonvoy_report; position_life ref-refb. Concept pages (specific edge load etc.) live in the library wiki.

## Oct 2026 situation (as of 2026-10-31)
- REF 2 plates installed Sep 30 are wearing fast: specific energy climbing since Oct 7, 12-day streak by 10-31, trend +1.2 to +1.75 %/day. [Bonvoy Report 2026-10-31]
- REF_B_SE daily mean: 62.08 (10-20), 62.49 (10-23), 62.88 (10-27), 63.58 (10-30), 64.54 (10-31); daily max 86.2 on 10-31; normal mean is ~59-60 kWh/t. [Bonvoy PM1:REF_B_SE 2026-10-20] [Bonvoy PM1:REF_B_SE 2026-10-31]
- REF 2 life: 24 days into an 84-day target on 10-25, 30 days on 10-31. [Bonvoy Report 2026-10-25] [Bonvoy Report 2026-10-31]
- Report text: "Only one Ridgeway set on hand for two refiners." (parts constraint for WO 26108911 / 26108904). [Bonvoy Report 2026-10-25]
- REF 1: 72 days into the 84-day target on 10-31 (84 reached about 2026-11-11/12, matching [[out-2026-11-11]]), High specific energy 3 h on 10-31. [Bonvoy Report 2026-10-31] [Bonvoy PM1:REF_A_SE 2026-10-31]
- Open WOs: 26108911 "Change REF 2 refiner plates" (status 30), 26108904 "Change REF 1 refiner plates" (status 30). [Bonvoy Report 2026-10-31]
- Documents: Ridgeway Refining plate report RR-PL-260930-B (2026-09-30), Field visit RR-FV-261026 (2026-10-26) "REF 2 plates wearing fast". [Bonvoy Report 2026-10-26]
- Check advice: plate gap and bar wear; LC cleaner reject rates "(sand wears plates fast)". [Bonvoy Report 2026-10-25]
- Freeness: machine chest freeness went Low from 2026-09-29 and was Low on 10-22, 10-24, 10-30 (17 h, min 421), 10-31 (16 h); report cause "Refining load low against its normal band". [Bonvoy PM1:FREENESS 2026-10-30] [Bonvoy Report 2026-10-30]

## Earlier REF 2 specific-energy exceptions (older plate set, before Sep 30)
- 39 tag-days: Dec 2025 - Sep 2026, mostly 3-6 h High; Low days 2026-04-17, 07-09, 07-12, 07-13 (min ~56). Sep 2026 cluster: 09-06, 09-10..14, 09-16..19, 09-24, 09-26 (max 71.8 on 09-24). [Bonvoy PM1:REF_B_SE 2026-09-24] [Bonvoy PM1:REF_B_SE 2026-09-26]
- REF 1 specific energy: 14 tag-days, 2025-11-29 to 2026-10-31, Low on 2025-12-12 and 2026-06-02. [Bonvoy PM1:REF_A_SE 2025-11-29] [Bonvoy PM1:REF_A_SE 2026-06-02]

## Refiner motor load and vibration
- REF_A_KW Low 3 h on 2026-03-02, 04-02 (5 h), 08-25, 10-06; REF_B_KW Low 2026-03-02, 04-02, 10-06 (stop-like days, see [[bonvoy-multi-tag-dips]]). [Bonvoy PM1:REF_A_KW 2026-08-25] [Bonvoy PM1:REF_B_KW 2026-04-02]
- REF_A_VIB: Low 2025-11-20, High 2025-12-08 (3 h each, max 0.081); REF_B_VIB: Low 2025-12-17, High 2026-01-17, Low 2026-02-23. No vibration ramp on either refiner motor in the record. [Bonvoy PM1:REF_A_VIB 2025-12-08] [Bonvoy PM1:REF_B_VIB 2026-01-17]

## Plate run history (position_life; plate life in days, not kWh)
- All REF 1 and REF 2 plate runs 2025-01-08 to 2026-09-30 were 83 d vs target 84 d, planned, except as noted; typical remark "Bars worn as expected; energy per ton steady to the end". [position_life ref-refa] [position_life ref-refb]
- REF 2 run 2026-07-08 to 2026-09-30 (serial RR-40140) is the exception: "Bars 85% worn at 12 weeks (normal ~60%); leading edges rounded. Ridgeway report RR-PL-260930-B." [position_life ref-refb]
- REF 2 current plates RR-40166 installed 2026-09-30, 30 d of 84 d as of 2026-10-30. [position_life ref-refb]
- REF 1 current plates RR-40082 installed 2026-08-19, 72 d of 84 d as of 2026-10-30; reaches 84 d on 2026-11-11 (computed), see [[out-2026-11-11]]. [position_life ref-refa]
- Ridgeway Refining vendor page: [[ridgeway-refining]].

## Ridgeway reports in numbers (reports library; bar wear in % of height, specific energy at removal in kWh/t)
- REF 1 (all 83 d, Even wear): 53% / 62.3 (12/10/2025), 64% / 62.9 (03/04/2026), 62% / 62.6 (05/27), 62% / 62.7 (08/19) [DOC RR-PL-251210-A p.1] [DOC RR-PL-260304-A p.1] [DOC RR-PL-260527-A p.1] [DOC RR-PL-260819-A p.1]
- REF 2 (all 83 d): 62% / 61.3 (01/21/2026), 60% / 62.9 (04/15), 57% / 63.0 (07/08), then 85% / 65.4 with leading edges rounded (09/30) [DOC RR-PL-260121-B p.1] [DOC RR-PL-260415-B p.1] [DOC RR-PL-260708-B p.1] [DOC RR-PL-260930-B p.1]
- Ridgeway's normal range: "typical 55-62%" bar wear for 12 weeks [DOC RR-PL-260930-B p.1]; the normal specific energy at removal is 61.3-63.0 kWh/t, so the 74.5 kWh/t on 10/25 at 4 weeks is about 12 kWh/t above it [DOC RR-FV-261026 p.1]
- Field visit RR-FV-261026 (10/26/2026, rep Corinne Batista): REF 2 SE up about 1.4% a day since 10/07; probable cause sand carry-over from the LC cleaners; recommendation: change both refiners' plates at 11/11 with a second set ordered now (lead time 10 days), check LC cleaner reject rates [DOC RR-FV-261026 p.1]
- CONFLICT on level: Ridgeway quotes REF 2 specific energy 74.5 kWh/t on 10/25, while Bonvoy REF_B_SE daily mean is 62.49 (10/23), 62.88 (10/27) and 64.54 (10/31) with daily max 86.2 on 10/31; basis of the 74.5 figure (instant, shift or max) is not stated; both kept [DOC RR-FV-261026 p.1] [Bonvoy PM1:REF_B_SE 2026-10-31]
- Plate-life units: days (83 d vs 84 d) in position_life; weeks (12) in [[clothing-life-targets]]; bar wear % and kWh/t in the reports; do not mix
- Mill-level energy in the Production Reports also rises in Oct 2026 (steady 24# days 60.5 kWh/t on 10-05 to 72-73 on 10-26/28; Sep mean 64.3, Oct mean 66.9), a base different from the refiner tag REF_B_SE (62-65); details in [[production-daily-reports]]. [Production Report PM1-PROD-2026-10-05] [Production Report PM1-PROD-2026-10-26]
- Plate-gap and cleanliness: Ridgeway asks to check "stock cleanliness (sand from the cleaners) and the plate gap control" [DOC RR-PL-260930-B p.1]
