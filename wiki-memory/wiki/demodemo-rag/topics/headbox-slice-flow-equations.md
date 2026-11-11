---
name: headbox-slice-flow-equations
description: Slice jet angle beta and contraction coefficient Cc by slice geometry (vertical, 45 degree, inclined lip) and head-to-jet-velocity relations - TAPPI TIP 0410-02/03/04/05; read to compute jet thickness
type: topic
aliases: ["Cc calculation", "jet angle calculation", "slice geometry", "L/b b/B", "Kerekes Koller equations", "head velocity jet", "TIP 0410"]
---
Extends [[headbox-jet-contraction]] (concept) with the calculation sheets. Documents: [[doc-tappi-tip-0410-02-flow-vertical-slice]], [[doc-tappi-tip-0410-03-flow-45-degree-slice]], [[doc-tappi-tip-0410-04-flow-inclined-upper-lip]], [[doc-tappi-tip-0410-05-head-behind-slice]].

- Inputs: X = L/b (bottom lip extension / slice opening) and Y = b/B (opening / stock depth); jet thickness d = Cc b. [DOC dd1c4162-82cc-4158-b722-da1cfe25fa20 p.1]
- Vertical slice worked case B=500, b=20, L=10 mm: beta 9.0 deg, Cc 0.62, d 12.4 mm; lengthening lip to 15 mm gives beta 5.0 deg. [DOC dd1c4162-82cc-4158-b722-da1cfe25fa20 p.1, p.4]
- Max errors of fitted equations: vertical 0.005 Cc / 0.20 deg; 45 degree 0.005 Cc / 0.10 deg. [DOC dd1c4162-82cc-4158-b722-da1cfe25fa20 p.5] [DOC 51304c5d-eed0-4604-ac12-2d6f15cb82dc p.5]
- 45 degree fit valid 0 <= L/b <= 5.0 and 0 <= b/B <= 0.95. [DOC 51304c5d-eed0-4604-ac12-2d6f15cb82dc p.5]
- Inclined upper lip (alpha under 10 deg): example B 0.8 in, b 0.5 in, L -0.4 in gives beta 7.75 deg, Cc 1.04. [DOC bfa80fb6-95c6-4275-bf94-2f8a3a97014c p.5]
- Head to velocity: Vj = K sqrt(H) with K = 138.9 for H in inches H2O and V in ft/min (265.7 for m H2O, m/min); H includes elevation (and ideally velocity) head, not just the transmitter reading. [DOC a58b3808-c123-425c-8a4d-636b917678f9 p.2]
- Q = Vj x Cc x b x w; 88 in. head gives 1303 ft/min; 200 in. wide, 0.75 in. slice, Cc 0.77 gives 7818 gpm. [DOC a58b3808-c123-425c-8a4d-636b917678f9 p.2-3]
- Edge flow adjustment at the tube bank can show an apparent head change at pond-side transmitters. [DOC a58b3808-c123-425c-8a4d-636b917678f9 p.3]
- Papermaker's Formulas gives the same idea with K = 139.2 (in. H2O) and slice flow gal/min/in = 0.052 x V x S.O. x Cc; Cc approx 0.95 nozzle, 0.75/0.70/0.60 types A/B/C. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.5-6] See [[papermakers-formulas-reference]].
- Use the exact coefficients in the document pages rather than from memory (tool: get_document_page).
