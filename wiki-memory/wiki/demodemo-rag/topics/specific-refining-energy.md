---
name: specific-refining-energy
description: Specific refining energy (SRE) formula, no-load power formula, net refining requirements by grade (HPD/UST, kWh/UST, kWh/MT) and freeness drop per net HPD/T by furnish.
type: topic
aliases: ["SRE", "net refining energy", "HPD/T", "kWh/t refining", "no load energy", "freeness drop per HPD/T", "net refining requirements"]
---
Source: [[doc-recycling-part3-refining-fractionation]]. Related: [[freeness-csf]], [[specific-edge-load]], [[refining-consistency]], [[refining-recovered-fibers]].

## Definitions
- SRE = energy transferred from motor to fiber: kWh/t = (Motor Load kW - No Load kW) / metric tonnes per hour; HPD/T = (Motor Load HP - No Load HP) / tons per day. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.29]
- No Load (kW) = (2.299x10^-13)(Diam^4.249)(RPM^3), Diam = plate diameter in inches, RPM = refiner motor speed; "The refiner is an inefficient pump!" [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.30]
- Freeness drop per energy: -dCSF / HPD/T = (CSF_in - CSF_out) / HPD/T; a measure of refiner efficiency and whether it operates correctly. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.32]

## Smook view (hp-day/ton, different source and basis)
- Net energy = brake (gross) energy minus no-load energy; no-load rises with the cube of rotor speed. [DOC d9815fa5-40a2-474b-9932-eaf665991fc0 p.29] [DOC 01a335fe-bfba-4f11-b32c-df2de03d8521 p.3]
- Fig 13-22 disc vs Jordan vs Claflin hp-day/ton by grade: see [[disc-and-conical-refiners]]; control by constant specific energy: see [[refiner-control-and-metering-blending]]. [DOC 01a335fe-bfba-4f11-b32c-df2de03d8521 p.5]

## Net refining requirements for major grades (J&L; HPD/UST | kWh/UST | kWh/MT)
- Linerboard base 5-7 | 89-125 | 99-138; linerboard top 10-12 | 179-215 | 197-237. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]
- Sack/bag 12-14 | 215-250 | 237-276. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]
- Medium: virgin HWD 6-10 | 107-179 | 118-197; waste 2-3 | 36-54 | 39-59; tickler 1.0-1.5 | 18-27 | 20-30. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]
- Fine papers: hardwood 4-6 | 72-107 | 79-118; softwood 6-8 | 107-143 | 118-158. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]
- Foodboard/milk carton: hardwood 2-3 | 36-54 | 39-59; softwood 3-4 | 54-72 | 59-79. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]
- News: SB kraft 2-5 | 36-89 | 39-99; groundwood 2-3 | 36-54 | 39-59. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]
- Grades with OCC: 2.5-5.0 | 81-117 | 50-100 (as printed; kWh/UST and kWh/MT ranges do not convert consistently, 81-117 vs 50-100 - possible source error). [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.31]

## Freeness drop per net HPD/T (CSF points)
- Unbleached softwood kraft: Northern U.S. 15-25, Southern U.S. 15-30. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.33]
- Bleached softwood kraft: Northern 25-50, Southern 25-60. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.33]
- Bleached hardwood kraft: most species 60-100, eucalyptus 45-50. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.33]
- Secondary fiber: OCC 40-70, mixed 50-70, news 20-35. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.33]
- Note on the slide: results combine fiber properties and refiner operating conditions. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.33]
## AFT stock prep refining manual ([[doc-aft-intro-stock-prep-refining]])
- Net specific energy = (total applied power - no load) / t/d, hpd/t or kWh/t; "short t/d = Flow (gpm) x 6 x % Consistency". [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.25]
- Worked: 575 hp motor, 115 hp no-load, 135 t/d gives 3.4 hpd/t; metric 342 kW / 3.8 t/h = 90 kWh/t; hp to kW factor 0.746. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.25]
- Table 4 hpd/t and Table 5 freeness drop per hpd/t (bleached HWD 60-100 ml, OCC 40-70, news 20-35) agree in range with the J&L table above; linerboard base 5-7 and top 10-12 match. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.26]
- Keep refining power about 25% above expected nominal. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.26]
- No-load formula in hp with exponent 4.3 on diameter: see [[refiner-no-load-power]]; case study 2.3 net hpd/t, 55 ml per hpd/t. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.41]
