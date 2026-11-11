---
name: citations
description: how to cite so every citation passes the automatic check
---
- A citation passes only if every id-like token in it (tag, date, WO no., report id, RCFA id) appears in a row a tool returned in THIS conversation. One unsupported citation caps the whole answer at 50.
- pi_daily and pi_values rows do NOT contain the tag name, only day/avg/min/max. So a citation like [Pi PM1:TAG 2026-10-31] fails unless the tag also came back in another tool result. For trend numbers, also call bonvoy_exceptions with term=<tag> (its rows carry tag + period) and cite [Bonvoy PM1:TAG <period>] only for days that came back there; otherwise cite the trend without the tag, e.g. "(pi_daily, Oct 1-31)" in words, not in brackets.
- Never cite a date range or a tool call ([downtime_summary ...], [grade_hours ...]); cite record ids or say the numbers come from the tool in plain words.
- [BUS <date>] needs that exact sheet date in a returned row (search_records / position_history rows carry the day). Don't cite a BUS date you inferred.
- downtime_summary and grade_hours rows have no record ids: give their numbers uncited in words ("from the downtime summary"), or cite individual events from downtime_events.
- Vendor report ids (e.g. KV-VR-..., RR-FV-..., MP-FA-...) are citable as [DOC <id> p.N] only after search_documents/search_library/get_document returned them.
