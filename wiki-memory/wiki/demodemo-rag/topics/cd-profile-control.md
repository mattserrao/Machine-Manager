---
name: cd-profile-control
description: Machine-direction vs cross-direction variability, scanning sensors, and caliper, moisture and grammage profile control per Smook (calender air jets, induction, steam showers, slice actuators, dilution headbox)
type: topic
aliases: ["profile control", "CD profile", "caliper profile", "moisture profile", "grammage profile", "basis weight profile", "slice lip actuators", "scanner", "dilution headbox"]
---
Source: [[doc-smook-fundamentals-part-10]]. Related: [[cd-moisture-profile-troubleshooting]] (checklist), [[calendering]], [[dryer-pocket-ventilation-and-hoods]].

## Variability and measurement
- MD varies with time; CD varies with position; most MD variation traces to headbox/approach pulsations [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.20]
- A scanner follows a diagonal path so its reading mixes MD and CD; pure CD profile needs MD removed by exponential multiple-scan trending; "About 10 scans are needed to register 90% of a step change in the profile." [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.20]
- Grammage by beta-particle attenuation; moisture by infrared (light, low-moisture) or microwave (heavier or wetter); caliper by contacting or semi-contacting magnetic reluctance sensors; first scanning gauges 1960s [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.20, p.21]

## Control methods
- Caliper: air-jet cooling of calender rolls (first automated system 1973), later hot/cold showers and induction heating; newer machines use localized induction [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.21]
- Moisture: steam showers (wet-end), zonal-crown press rolls, localized pocket ventilation, sectionalized dryer bars, moisturizing sprays; first automated system 1977 [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.21]
- Grammage: slice micro-adjuster screws; actuator moves slice lip in increments as small as .02 microns with LVDT position feedback [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.22]
- Fig 17-41 improvement stages: 6.9 g/m2 peak to peak before; new slice lip and apron 38% (4.3); remote manual 61% (2.7); closed loop 93% (0.5) per figure label, while the text says total 91% [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.22] CONFLICT: 93% (figure label) vs 91% (text) on the same page
- Slice bending is limited; dilution control headboxes keep uniform flow and adjust local consistency, removing interaction with fibre orientation [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.22]

## Measurement limits
- Scanner CD profiles contain MD and residual variation; true CD needs reel samples and about 10 plies; data box size changes COV. See [[paper-variation-md-cd-residual]]. [DOC 6a85a636-1e70-46d5-af7e-3dc0beae290f p.4, p.7]
