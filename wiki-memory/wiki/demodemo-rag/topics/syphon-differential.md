---
name: syphon-differential
description: Differential pressure (steam in minus condensate out) needed to drain dryers - by syphon type, speed and basis weight; flooding symptoms and causes; read for dryer drainage / flooded dryer questions
type: topic
aliases: ["differential pressure dryer", "flooded dryer", "drowning", "flow-through steam", "dp syphon", "dryer drainage"]
---
Sources: [[doc-steam-condensate-for-paper-machines]], Smook via [[dryer-condensate-siphons-and-blow-through]]. Context [[dryer-section-drying]].

## Berlin (rotating vs stationary)
- Rotating syphon: set dp by speed, "at 500 m/min a differential pressure of ca. 0,5 bar is necessary, at 1000 m/min even ca. 1 bar"; lower dp at lower speed or lower basis weight. [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.19]
- Stationary syphon: manufacturer asks at least 0,1 bar (0,1-0,2); adjusting to production is "basically not necessary"; at ca 1000 m/min drains even without dp. [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.15, p.19]
- Flow-through steam: rotating 15-25% of inlet steam (1000 kg/h drying needs ca 1250 kg/h); stationary about 10%. [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.15, p.18]
- Scoops need no dp; slow machines below waterring speed (ca 450-500 m/min). [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.23-24]
- Group dp example at 850 m/min: rotating syphons "ca. 0,6 bar - 0,7 bar", which holds the 2nd group (3,6 bar) below the 3rd (3,8 bar). [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.27]

## Flooded dryer: how to recognise
- Lower surface temperature at same steam pressure, heavier dryer, load on drives. [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.13]
- More paper breaks at the same spot, dryer vibration, rising moisture and steam pressure raised at same basis weight and speed. [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.19]
- Causes: operator dp setting, measuring/control (transmitter, positioner with oil/dirt in control air, blocked impulse lines), maintenance (steam joints, shoes, eroded horizontal tube). [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.19-21]
- Restart help: "fear-hole" above the syphon shoe plus moderate dp rise. [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.22]

## Smook comparison
- Smook: rotating siphon dp example about 1.4 bar at 1000 m/min; Berlin quotes ca 1 bar at 1000 m/min. CONFLICT-ish: different examples/designs, keep both. [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.11] [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.19]
- Smook blow-through 15-20% of condensate mass flow; Berlin 15-25% of steam into the dryer for rotating syphons. [DOC 212d6dd4-0711-4fdc-8e33-735d3a13d5de p.10] [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.18]

## Berlin pp.1-4 (cascade control)
- Stationary syphons in the cascade example: 0,1 to 0,2 bar; PdCV1/PdCV2 hold it during breaks and flooding: see [[steam-cascade-and-differential-pressure-control]] [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.2] [DOC f2d6b892-8f3a-49f6-bfb1-8f6beada12e7 p.4]
