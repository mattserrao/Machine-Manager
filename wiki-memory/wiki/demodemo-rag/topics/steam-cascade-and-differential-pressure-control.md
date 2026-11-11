---
name: steam-cascade-and-differential-pressure-control
description: Dryer steam/condensate cascade per Berlin: group pressure control, 0.1-0.2 bar differential for stationary syphons, PdCV1/PdCV2 split range to the auxiliary condenser, behaviour at paper break, flooding and heat-up, cooling water as indicator, steam cost
type: topic
aliases: ["cascade system", "dryer cascade", "differential pressure control", "PdCV", "auxiliary condenser", "break nominal value", "dryer group pressure", "steam cost per ton", "closed steam system", "thermocompressor vs cascade"]
---
Source: [[doc-steam-condensate-for-paper-machines]] (pp.1-4, 12). Related: [[syphon-differential]], [[dryer-condensate-siphons-and-blow-through]] (Smook cascade vs thermo-compressor), [[dryer-section-drying]], [[steam-temperature-and-vacuum-plant]], [[mill-boiler-steam-and-power]].

## Why it matters
- Steam about 20-25 EUR per ton; at 8200 h/year, 100 t/h costs ca. 16.4 to 20.5 million EUR; saving 1 t/h is worth 164,000 to 205,000 EUR per year; rebuild pays back in "one or two years" per Berlin [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.1]
- Aim: a closed system, steam fully used for the dryers and other heat consumers, none blown off or sent to the auxiliary condenser [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.1]
- Causes of waste named: missing training, changed operating conditions vs design, wrong layout, planner knowledge [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.1]

## Cascade
- Cascade = heat recovery: flow-through and flash steam from a dryer group is reused to heat a lower-pressure group; example group 1 = 4 individually controlled dryers, group 2 = 7 dryers [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.2]
- Differential pressure setpoint is fixed in the control system and kept constant; stationary syphons need 0,1 to 0,2 bar [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.2]
- If flow-through steam is not enough, pressure drops below PCA1 setpoint and live steam is fed automatically via PCVA1 [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.2]
- Figure values in the example: main steam 5 barg / 165 C; group 2 at about 1,5 barg / 128 C; PCVA2 side 1,8 barg; dp = 0,2 bar [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.2]

## Hard-to-hold situations
- Paper break: condensation drops at once; drop heating pressures to a break-nominal value, ideally automated [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.3]
- Flooded dryers (wrong DCS setting, instrument fault, damaged drainage or steam joints, undersized syphon pipe/shoe): dp falls and the condensate ring floods the shoe; rotating syphons are the main problem; scoops cannot flood [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.3]
- Heating up the machine: small steam amount, same conditions as a break [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.3]
- Remedy: an extra control valve per dryer group to hold dp in every state [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.3]

## PdCV1 / PdCV2 and the auxiliary condenser
- PdCV1 opens 0 to 100% for controller output 0 to 50%; PdCV2 takes over for output 50 to 100% [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.4]
- PdCV2 piping goes to the lowest-pressure point, the auxiliary condenser (a "steam eliminating heat exchanger") where cooling water condenses the steam and creates a low vacuum [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.4]
- In normal production (no break) both valves should be closed [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.4]
- Check of the whole design: look at cooling water use in the auxiliary condenser; "should always be as low as possible" [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.4]
- This is a quick screening for steam waste: tool for the mill would be the Pi tags of the condenser cooling water flow and dryer group dp, not in this wiki.

## Physics reminder
- Steam flows into a dryer because condensation collapses volume (2 t/h steam at 0,1 bar overpressure, 3000 m3 specific volume, becomes 3 m3 of condensate) [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.12]
- Cool, wet paper drives condensation; no paper means no steam demand [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.12]
