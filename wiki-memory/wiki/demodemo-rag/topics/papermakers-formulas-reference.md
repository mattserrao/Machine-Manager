---
name: papermakers-formulas-reference
description: Where to find papermaker day-to-day formulas and guideline ranges (TIP 0502-17) - head and jet speed, retention, forming length, shake, dandy rpm, press impulse, rimming speed, drying rate, conversions
type: topic
aliases: ["papermaker's formulas", "paper machine calculations", "spouting velocity", "shake number", "press impulse", "rimming speed formula", "basis weight conversion", "forming length dwell time"]
---
Source: [[doc-tappi-tip-0502-17-papermakers-formulas]] (43 formulas, English and SI). Check units; do not mix English and SI constants.

## Stock and headbox
- Spouting velocity V = K sqrt(h): K 139.2 (in. H2O, ft/min), 481.5 (ft H2O), 732.3 (PSIG); SI 265.7 sqrt(h m H2O) m/min. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.5] Rigorous version with edge-flow caveat: [[headbox-slice-flow-equations]].
- Slice flow per width 0.052 x V x S.O. x Cc gal/min/in; Cc nozzle 0.95, A 0.75, B 0.70, C 0.60. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.6]
- Screen-to-headbox pipe velocity guideline 7-14 ft/s (2.1-4.3 m/s). [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.3]
- Retention = (headbox consistency - tray consistency) / headbox consistency x 100; example 92.1%. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.8] See [[wet-end-retention-and-zeta-potential]].

## Forming
- Dwell time guideline: 2.0 s under 1200 ft/min, 1.0 s above; liner 1.25 s; foodboard 2.0 s. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.8]
- Blade pulse frequency target above 60 cycles/s, up to 150; shake number target 50-60 (English) or 4200-5000 (SI); dandy roll 125-150 rev/min. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.9] Context [[forming-hydrodynamics]].

## Press and dryer
- Press impulse PI = 5 x PLL / speed (psi.s) or 0.060 x PLL / speed (MPa.s). [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.12] Context [[press-section-design]].
- Rimming speed = [5720 - 2160/D] L^(1/3) ft/min (D dryer ID ft, L film ft). [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.14] Compare Berlin's ca 450-500 m/min waterring speed in [[dryer-turbulator-bars]].
- Drying rate formulas #27 (uncoated) and #28 (coated); felt tension from hanging weight #30. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.13-14] Context [[dryer-section-drying]].

## Reel, conversions
- Production off reel kg/h = m/min x g/m2 x trim m x 0.06; t/d = x 0.024. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.15]
- Basis weight to g/m2: offset x1.48, bond x3.76, liner x4.89, news/tissue x1.63, market pulp x1.70. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.16]
- Crepe has two definitions (divide by reel or by Yankee speed). [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.15] See [[tissue-making-yankee-and-tad]].
- Critical speed, WR2, torque, power: #38-42. [DOC 2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701 p.17-18]
