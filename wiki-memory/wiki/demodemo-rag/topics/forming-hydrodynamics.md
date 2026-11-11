---
name: forming-hydrodynamics
description: Fourdrinier forming theory 1950-2000 - table-roll suction, foils, drainage equations, why foils replaced table rolls; read for wire/forming-section background questions.
type: topic
aliases: ["table roll suction", "drainage foils", "Fourdrinier drainage", "wire table drainage", "Taylor Wrist"]
---
Source: [[doc-forming-hydrodynamics-history]] and duplicate [[doc-forming-hydrodynamics-history]] (same article). Background, not operating guidance. See also [[twin-wire-formers]], [[headbox-jet-contraction]].

## Fourdrinier basics
- Jet consistency 0.15 to 1.0%; web leaves the table at the couch roll at about 20%; more than 95% of suspension water drained. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.1]
- Continuous forming invented by Robert 1798, commercialised as Fourdrinier 1807. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.1]

## Table rolls
- Wrist (1954): table roll induces suction of magnitude rho*U^2/2 in the diverging nip (U wire speed, rho water density). [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.3]
- Bennett (1954) verified it up to 600 ft/min; roll diameter affects the area of suction, not its magnitude. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.4]
- Speed limit: at about 900 m/min suction would equal atmospheric pressure so water would "boil" out of the sheet. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.4]
- Taylor (1956) Eq. 1: p_max = rho*U^2/2 (confirms Wrist for maximum suction only). [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.5]
- Taylor Eq. 2: Q = k^2 rho R^2 U^3 / mu^2, drainage rises as the cube of speed (laminar mat assumption); if mat resistance goes with velocity squared, Q is linear in U. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.5]
- Bergstrom (1957): from Wrist's data Q proportional to U^2, so flow through the mat depends on U^1.33. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.5]
- Taylor (1958) turbulent-mixing case gives peak suction 1.4 times Eq. 1; Wrist's measurements matched Eq. 1; left unresolved. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.5]
- As speeds rose, table rolls had to be removed, not added; some wire surface agitation improves formation, too much degrades sheet quality. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.3]

## Foils
- Burkard and Wrist (1956): a stationary foil also makes a suction pulse, lower peak and larger zone than a roll. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.5]
- Eq. 3: p_max = beta*mu*U/k (suction linear in flare angle beta). Eq. 4: Q = beta(1 - beta*mu/(k*rho*V)) L U. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.6]
- Optimum drainage at beta*mu/(k*rho*U) = 0.5; "Fourdriniers typically operate at about" 0.1. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.6]
- Foils only became practical when plastic fabrics (polyethylene, polyamide) replaced bronze wires, which needed changing almost weekly; widespread foil use from early 1970s. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.6]
- Many Fourdrinier machines run up to about 1200 m/min (Holik 2010). [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.6]

## Formation link
- Link between surface activity on the table and formation was only empirical correlation (Kiviranta and Paulapuro 1992); contoured foils were developed to give the right agitation. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.15]

## Dewatering review (Hubbe 2020) and vacuum practice
- Forming board: about a quarter of the fluid is drawn before the board so no air is drawn between fabric and web ("setting the sheet") [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.8]
- Hydrofoil: land parallel to the fabric then diverging surface "often about 3 degrees"; blades about 50 to 89 mm; table rolls became unstable well beyond 300 m/min; foils wash fines from the wire side up to about 6% solids [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.8-9]
- Fabric sealing and early-drainage limits: [[fabric-sealing-and-sealing-phenomena]]; vacuum box science: [[vacuum-box-dewatering-mechanisms]]; table vacuum control practice: [[forming-table-vacuum-control]]

## Practical strategies (Hubbe 2020)
- Early drainage, foils, vacuum boxes, rewetting: [[dewatering-enhancement-strategies]], [[vacuum-box-operation-and-dewatering]] [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.47]

## Practical guidelines (TIP 0502-17)
- Shake number, blade pulse frequency, forming length dwell time and dandy roll rpm targets are in [[papermakers-formulas-reference]]; e.g. shake number target 50-60 (English), dandy roll 125-150 rev/min. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.9]
