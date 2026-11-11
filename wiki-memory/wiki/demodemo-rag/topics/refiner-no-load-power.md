---
name: refiner-no-load-power
description: Stock prep refiner no-load (circulating) power: what drives it, the AFT formula in hp, wear effect, reduced periphery plates, worked case; read when net power or net hpd/t is asked
type: topic
aliases: ["no-load power", "no load hp", "circulating power", "reduced periphery plates", "Finebar"]
---
Sources: [[doc-aft-intro-stock-prep-refining]]; other formula in [[specific-refining-energy]] (recycling lecture). Related: [[specific-edge-load]], [[refiner-plate-selection]], [[disc-and-conical-refiners]].

- No-load is hydraulic pumping plus viscous shear that "produces no measurable change in the properties of the pulp"; net power = motor load - no-load. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.32]
- Mostly depends on rotor diameter and speed, and on bar/groove pattern; flow, consistency and plate gap have minor influence. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.32]
- Contrary to supplier claims, no-load does not depend on weight of the rotating elements. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.32]
- It falls as plates wear, as much as 60-80% lower fully worn than new; measuring it is hard (rotor leans on a stator; fibre present gives wrong readings), so calculated values are often used. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.32]
- Proportional to speed cubed and to active diameter to the power 4.3. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.33]
- Formula (hp): "NL = 102 x (RPM/100)^3 x (Da/100)^4.3 x (2 x Gw /( Bw + Gw)) x (Gd /4)", Da inches, Gw Bw Gd in sixteenths. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.33]
- Published no-load data usually assume new cast plates, bar and groove 2.0 sixteenths, groove depth about 4.0 sixteenths (0.25 in). [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.33]
- CONFLICT of form, not necessarily value: the recycling lecture gives kW = 2.299x10^-13 x Diam^4.249 x RPM^3 [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.30] (exponent 4.249) vs 4.3 here; units differ (kW vs hp), so compare by calculation, not by quoting one for the other.
- Reduced periphery plates cut active diameter, so lower no-load: 46 to 40 in saves about 150 hp (about $49,000/yr at $0.05/kWh). [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.29]
- Case: 34 in DD, 600 rpm, 2.0/2.0/4.0 plates, no-load 213 hp; 31 in plates 1.0/1.5/3.5 give 150 hp (63 hp saved, about $18,400/yr at $0.045/kWh). [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.40] [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.42]
- Plate with 1/8 in grooves and 1/4 in bars has higher no-load than 1/4 in grooves and 1/8 in bars. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.29]
