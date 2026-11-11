---
name: darcy-kozeny-carman-permeability
description: Flow-resistance equations for wet webs: Darcy's law, specific filtration resistance, Kozeny-Carman permeability, Jackson-James dilute form, linear resistivity model, Lucas-Washburn, Forchheimer term; with Table 4 model history (Hubbe 2020)
type: topic
aliases: ["Darcy's law paper", "Kozeny-Carman equation", "specific filtration resistance", "Lucas-Washburn", "Forchheimer", "Ergun", "decreasing permeability model", "Terzaghi principle paper", "permeability of fiber mats"]
---
Source document: [[doc-hubbe-rate-limiting-water-removal]] (pp.19-27). Related: [[wet-web-dewatering-hypotheses]], [[wet-press-nip-mechanisms]], [[fines-plugging-and-drainage]], [[freeness-csf]].

## Equations (quoted from the review)
- Darcy Eq. 1: V = (k/mu)(P/L); V superficial velocity, k permeability, P pressure difference, mu viscosity, L bed height; Eq. 2: Q = (kA/(mu L)) delta P [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.22]
- Eq. 3 practical form V = P/(K b) with b basis weight, K specific filtration resistance; Eq. 4 relates K and k via density [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.22]
- Kozeny-Carman Eq. 5: k = epsilon^3 / (kc S^2 (1 - epsilon)^2); epsilon porosity, S specific surface area of solids [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.22]
- Dilute fiber networks: Jackson and James Eq. 6, k = (3 d^2 / (80 (1 - epsilon))) [-ln(1 - epsilon) - 0.931] [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.23]
- Linear resistivity Eq. 7: K = beta delta P + alpha I + gamma, valid 5 to 70 kPa; high pressure effect "mostly lost due to simultaneously increasing flow resistance" [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.23]
- Lucas-Washburn: P capillary = 2 gamma cos theta / r (Eq. 8); P viscous = 8 mu v L / r^2 (Eq. 9); integrated L = [(2 r gamma cos theta t)/(4 mu)]^(1/2) (Eq. 11) [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.25]
- Forchheimer/Ergun Eq. 12: delta P / L = (mu/k) Q + C rho Q^2; C = alpha (1 - epsilon)/(d epsilon^3), alpha 1.8 smooth, 4.0 rough particles [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.26]
- Capillary breakthrough Eq. 14: delta P = 2 gamma / R [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.39]

## Key points
- Permeability is not constant; it falls as water leaves and the web compresses, so Darcy with fixed k fails [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.22]
- Kozeny-Carman is the starting point for most paper dewatering analyses, but irregular and compressible fibers prevent a-priori prediction without experiments [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.23]
- Bimodal mixtures (fibers plus fines) give greater flow resistance [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.24]
- Terzaghi structural/hydraulic split (Wahlstrom) is questioned; Decreasing Permeability (DP) model of McDonald and Kerekes: removal is set by applied pressure and permeability; difficulty arises from decreasing permeability, "not diminishing hydraulic pressure" [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.13, p.27]
- Table 4 (selected): Darcy 1856; Kozeny 1927; Carman 1937/1939; Ergun 1952 inertial term; Wahlstrom 1960 hydraulic vs structural; Ingmanson 1964 compressible mat; Roux and Rueff 2012 "Filtrate per unit area is proportional to the square-root of suction time" (flatbox) [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.19-21]
- Table 5-6: lab devices (drainage jars, PDA, wet-press simulators); Ingmanson 1957 "Filtration resistance increases by a factor of about 3 from the breast roll to the end of the forming section" [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.28]
