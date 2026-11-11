---
name: data-tools
description: which tool gives what, and the checks a superintendent expects
---
- Owners: BUS issue owners and action owners come back in search_records (owner/assigned_to fields) and overdue_actions. Look them up before saying "no owner".
- Parts readiness for any planned change: outage_scope (parts status) AND open actions / BUS lines about ordering or spares (search_records "order", "set on hand", "spare"). A change can be scoped with parts reserved and still be short of a second set.
- Position life: position_life gives installed date, days vs target; compute when it reaches target and compare with the outage dates in the rules (outages every 42 days). If a due position has no WO in outage_scope, say so.
- Trends: read the whole series before describing it — say when it started rising (flat until X, then rising), not "since <start of window>". Give the fitted rate and the projection, and say it is an extrapolation. Show alarm/Danger limits on charts as reference lines.
- Vendor findings (vibration routes, steam surveys, felt analysis, plate reports) live in search_documents (Sim Mill documents). Check them for every equipment item in a brief; they often hold the recommendation (replace, re-align, change early).
- Repeat failures: repeat_stops shows rcfas="none"; then check search_documents for vendor findings and overdue_actions/search_records for a root-cause review.
- Crews: shift_reports and downtime_summary group=crew give counts; normalise before ranking and say whether the gap is beyond normal variation.
