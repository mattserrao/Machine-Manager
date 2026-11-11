---
name: headbox-jet-contraction
description: Headbox slice jet thickness (contraction coefficient Cc) and angle; why slice opening is not jet thickness; TAPPI TIP 0410 references.
type: topic
aliases: ["slice opening", "vena contracta", "jet angle", "Cc", "TIP 0410-02", "jet impingement"]
---
Source: [[doc-forming-hydrodynamics-history]], [[doc-forming-hydrodynamics-history]]. Related: [[forming-hydrodynamics]].

- Only the jet velocity component perpendicular to the wire creates pressure, so jet angle and thickness must be controlled; the slice sets both. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.2]
- Jet thickness = Cc x slice opening b; Cc "can be as small as 0.62", so using slice opening as jet thickness gives significant error in headbox volumetric flow. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.2]
- Governing dimensionless numbers (Nelson 1960): bottom lip extension / slice opening L/b, and slice opening / upstream channel size b/B. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.3]
- Appel and Yu (1963) potential-flow model; Kerekes and Koller (1981) explicit equations (up to 10 constants) for angle and Cc are in TAPPI TIP 0410-02, 03, 04. [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.3]
- Boundary layers matter for MD streaks and jet stability (Soderberg and Alfredsson 2000). [DOC 8e89cddd-56fe-4ef8-9aca-84a8ffe2a0f6 p.3]
- Smook: jet speed v = √(2gh); the slice opening alone does not give jet thickness, so contraction must be included in flow. [DOC 66857f06-84b5-470f-ada6-025ffe226134 p.4] See [[headbox-types-and-pulsation]].
- Practical slice-lip check (warped lip, Teflon feeler gauge) is in [[cd-moisture-profile-troubleshooting]].

## Calculation sheets
- Hubbe 2020 review: "The contraction factor can be as low as 0.62" (slice opening vs thickness at the vena contracta); jet is about 99.5% water by mass [DOC 7d704e0a-0ca7-4284-8fb9-dc6721c03b8a p.6]
- Worked Cc and angle calculations and coefficients for vertical, 45 degree and inclined-lip slices: [[headbox-slice-flow-equations]]. Example: 20 mm opening, 10 mm lip, B 500 mm gives Cc 0.62 and 9.0 deg. [DOC dd1c4162-82cc-4158-b722-da1cfe25fa20 p.1]
