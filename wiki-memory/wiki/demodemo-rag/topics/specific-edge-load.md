---
name: specific-edge-load
description: Specific edge load (SEL), refining intensity - definition, effect on fiber cutting vs fibrillation, why recycled fiber needs lower SEL, effects outside the recommended range.
type: topic
aliases: ["SEL", "refining intensity", "Ws/m", "Ws/km", "bar edge load"]
---
Source: [[doc-recycling-part3-refining-fractionation]]. Related: [[specific-refining-energy]], [[refining-recovered-fibers]].

- Smook: specific edge load = net power divided by the total length of bar edges contacting the stock per unit time; intensity is harder to evaluate than net energy. See [[refining-mechanisms-and-variables]]. [DOC d9815fa5-40a2-474b-9932-eaf665991fc0 p.27]
- SEL = energy expended per unit length of bar crossings; describes intensity of refining impacts. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.34]
- Higher SEL = more shortened and cut fibers; lower SEL = more pronounced fibrillation; "Recycling requires lower SEL". [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.34]
- Fig. 163 (LC refining of writing/printing papers): at 500 Ws/km tear is higher and tensile higher than at 1,500 Ws/km at the same specific energy; "Lower SEL provides better properties." [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.35]
- Lower than recommended: potentially poor fiber development, length maintained, inefficient freeness drop. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.36]
- Higher than recommended: severe fiber cutting, plate clashing, short plate life, poor strength development. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.36]
- Units differ across slides: Ws/km on Fig. 163, Ws/m in Table 17.1 (3.6 Ws/m virgin, 1.6 Ws/m OCC); do not mix them. [DOC 856ff3f6-9be4-42e7-b4dc-fee63dfd3cfd p.37]
## AFT stock prep refining manual ([[doc-aft-intro-stock-prep-refining]])
- Formula: "I = (Applied Motor Power - No-Load) / [RPM x Bar Edge Length x (min/60s)]", unit Ws/m; SEL theory dates from the 1960s. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.23]
- Number of deformations N = (RPM x Bar Edge Length) / t/d; specific energy P = I x N = net power / (t/d). [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.23] [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.24]
- C-factor (Kerekes) adds fibre length and coarseness for I and N per fibre; SEL ignores fibre properties but has much history. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.24]
- Recommended intensity Ws/m (Table 6): SWD kraft 1.0-2.5; HWD kraft 0.1-0.5; recycle 0.2-0.8; TMP/GWD 0.2-0.5. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.28]
- Worked case: 363 net kW, 30 km/rev, 600 rpm gives 1.2 Ws/m; reduced periphery plates 59 km/rev give 0.6 Ws/m. [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.41] [DOC 573e2f9c-afca-42a5-b4a6-10980694ab2e p.42]
- Units: kW / (km/rev x rpm / 60) in Ws/m; this manual (Ws/m) matches Table 17.1 style, not the Ws/km of Fig 163. See [[refiner-plate-selection]] for the HWD range CONFLICT (0.1-0.5 vs 0.3-0.8).
