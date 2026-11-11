"""Render corpus/raw/* into provenance-stamped text batches (<= ~120k chars) under corpus/batches/<org>/bNN-<name>.txt.
Every block starts with a [SOURCE: ...] line naming the citable id the answer agents would get back from a tool."""
import json, re
from collections import defaultdict
from pathlib import Path

H = Path(__file__).resolve().parents[1]
RAW = H / 'corpus/raw'
OUT = H / 'corpus/batches'
MAX = 120_000
ws = lambda s: re.sub(r'[ \t]+', ' ', str(s or '')).strip()


def load(org, t):
    return json.loads((RAW / org / f'{t}.json').read_text())


def write_batches(org, name, blocks):
    d = OUT / org; d.mkdir(parents=True, exist_ok=True)
    cur, n, out = [], 0, []
    for b in blocks:
        if cur and n + len(b) > MAX:
            out.append(cur); cur, n = [], 0
        cur.append(b); n += len(b) + 2
    if cur: out.append(cur)
    files = []
    for i, part in enumerate(out, 1):
        p = d / f'{name}{"-" + str(i) if len(out) > 1 else ""}.txt'
        p.write_text('\n\n'.join(part) + '\n'); files.append(p)
    return files


def sim():
    org = 'sim-mill'; made = []
    # --- reports: shift reports as written (by month); production reports summarised by production_daily below
    reps = sorted(load(org, 'reports'), key=lambda r: (r['mill_day'] or '', r['shift'] or ''))
    by_month = defaultdict(list)
    for r in reps:
        if r['type'] != 'shift': continue
        by_month[r['mill_day'][:7]].append(f"[SOURCE: Shift Report {r['report_id']} | {r['mill_day']} {r['shift']} | crew {r['crew']} | {r['author']}]\n{(r['text'] or '').strip()}")
    for m, blocks in sorted(by_month.items()):
        made += write_batches(org, f'shift-reports-{m}', blocks)
    # --- work orders
    wos = sorted(load(org, 'work_orders'), key=lambda w: (w.get('requested') or '', w['wo_no']))
    blocks = [f"[SOURCE: WO {w['wo_no']}] {ws(w['description'])} | asset {w.get('asset_no') or ''} {ws(w.get('asset'))} | position {w.get('position_id') or '-'} | "
              f"{w.get('section') or ''} | type {w.get('wo_type')} | prio {w.get('priority')} | {ws(w.get('status_text'))} | requested {w.get('requested')} | "
              f"planned {w.get('planned_start') or '-'} | completed {w.get('completed') or '-'} | outage {w.get('outage') or '-'} | parts {w.get('parts_status') or '-'} | "
              f"craft {w.get('craft') or '-'} {w.get('assigned_to') or ''} | est {w.get('est_hours')} h act {w.get('act_hours')} h"
              + (f" | notes: {ws(w['notes'])}" if w.get('notes') else '') for w in wos]
    made += write_batches(org, 'work-orders', blocks)
    # --- BUS daily sheet: one block per issue (all its daily lines collapsed)
    bus = defaultdict(list)
    for b in load(org, 'bus_items'): bus[b.get('issue_key') or (b['equipment'] + b['issue'][:30])].append(b)
    blocks = []
    for k, rows in sorted(bus.items(), key=lambda kv: min(r['sheet_date'] for r in kv[1])):
        rows.sort(key=lambda r: r['sheet_date']); f, l = rows[0], rows[-1]
        acts = []
        for r in rows:
            a = (ws(r.get('action')), r.get('owner'), r.get('status'), r.get('wo_no'))
            if not acts or acts[-1][1:] != a: acts.append((r['sheet_date'],) + a)
        blocks.append(f"[SOURCE: BUS {f['sheet_date']} .. BUS {l['sheet_date']} | issue {k}] {ws(f.get('area'))} / {ws(f.get('equipment'))} "
                      f"(asset {f.get('asset_no') or '-'}, position {f.get('position_id') or '-'}): {ws(f['issue'])}; on the sheet {len(rows)} days, last status {l.get('status')}, "
                      f"days open {l.get('days_open')}\n" + '\n'.join(f"  {d}: {a} | owner {o} | {s}" + (f" | WO {w}" if w else '') for d, a, o, s, w in acts[:12]))
    made += write_batches(org, 'bus-issues', blocks)
    # --- RCFAs and actions
    acts = {a['task_id']: a for a in load(org, 'actions')}
    blocks = []
    for r in sorted(load(org, 'rcfa'), key=lambda r: r['event_date']):
        al = '\n'.join(f"  [Action {a}] {ws(acts[a]['title'])} | {acts[a].get('assigned_to')} | due {acts[a].get('due')} | completed {acts[a].get('completed') or '-'} | {acts[a].get('progress')}"
                       for a in (r.get('action_ids') or []) if a in acts)
        blocks.append(f"[SOURCE: {r['rcfa_id']}] {ws(r['title'])} | event {r['event_date']} | opened {r.get('opened')} | closed {r.get('closed') or '-'} | {r['status']} | "
                      f"area {r.get('area')} | asset {r.get('asset_no') or '-'} {ws(r.get('asset'))} | position {r.get('position_id') or '-'} | downtime {r.get('downtime_h')} h | "
                      f"loss {ws(r.get('production_loss'))} | category {r.get('category')} | lead {r.get('lead')}\n  root cause: {ws(r.get('root_cause'))}\n  contributing: {ws(r.get('contributing'))}\n{al}")
    linked = {a for r in load(org, 'rcfa') for a in (r.get('action_ids') or [])}
    for a in sorted(acts.values(), key=lambda a: a.get('created') or ''):
        if a['task_id'] in linked: continue
        blocks.append(f"[SOURCE: Action {a['task_id']}] {ws(a['title'])} | bucket {a.get('bucket')} | {a.get('assigned_to')} | created {a.get('created')} | due {a.get('due')} | "
                      f"completed {a.get('completed') or '-'} | {a.get('progress')} | position {a.get('position_id') or '-'}" + (f" | {ws(a['description'])}" if a.get('description') else ''))
    made += write_batches(org, 'rcfa-actions', blocks)
    # --- downtime events, position runs, outages, equipment, Pi tags
    blocks = [f"[SOURCE: downtime {d['event_id']} | {d['starts_at'][:16]}] {d['kind']} {d['minutes']} min | {d.get('area')} / {ws(d.get('equipment'))} | cause {ws(d.get('cause'))} | "
              f"grade {d.get('grade')} | crew {d.get('crew')} | WO {d.get('wo_no') or '-'} | RCFA {d.get('rcfa_id') or '-'} | report {d.get('report_id') or '-'}" + (f" | {ws(d['comment'])}" if d.get('comment') else '')
              for d in sorted(load(org, 'downtime'), key=lambda d: d['starts_at'])]
    made += write_batches(org, 'downtime-events', blocks)
    blocks = [f"[SOURCE: position_life {p['position_id']}] {p.get('position_name')} | installed {p['installed']} | removed {p.get('removed') or 'running'} | {p.get('days')} d vs target {p.get('target_days')} d | "
              f"reason {p.get('reason') or '-'} | condition {p.get('condition') or '-'} | {p.get('vendor')} {p.get('style') or ''} | serial {p.get('serial') or '-'}" + (f" | {ws(p['comment'])}" if p.get('comment') else '')
              for p in sorted(load(org, 'position_runs'), key=lambda p: (p['position_id'], p['installed']))]
    blocks += [f"[SOURCE: outage {o['outage_id']}] {o['kind']} {o['starts_at'][:16]} to {o['ends_at'][:16]}" + (f" | {ws(o['note'])}" if o.get('note') else '') for o in load(org, 'outages')]
    blocks += [f"[SOURCE: equipment {e['asset_no']}] {e['name']} | section {e.get('section')} | kind {e.get('kind')} | position {e.get('position_id') or '-'} | parent {e.get('parent_asset') or '-'}" for e in load(org, 'equipment')]
    blocks += [f"[SOURCE: Pi tag {t['tag']}] {t['description']} ({t['units']}) | asset {t.get('asset_no') or '-'} | position {t.get('position_id') or '-'} | section {t.get('section')}" for t in load(org, 'pi_tags')]
    made += write_batches(org, 'positions-outages-equipment', blocks)
    # --- Bonvoy: exceptions collapsed per tag (runs of days), plus the 7 daily reports
    bv = defaultdict(list)
    for b in load(org, 'bonvoy'): bv[b['tag']].append(b)
    blocks = []
    for tag, rows in sorted(bv.items()):
        rows.sort(key=lambda r: r['period']); f = rows[0]
        lines = '\n'.join(f"  [Bonvoy {tag} {r['period']}] {r['direction']} {r['hours_outside']} h outside; mean {r['mean']:.4g} band {r['low']:.4g}-{r['high']:.4g} min {r['min']:.4g} max {r['max']:.4g}" for r in rows)
        blocks.append(f"[SOURCE: Bonvoy exceptions {tag}] {f.get('description')} ({f.get('units')}) | {f.get('area')} / {f.get('asset')} | position {f.get('position_id') or '-'} | {len(rows)} tag-days\n{lines}")
    for r in sorted(load(org, 'bonvoy_reports'), key=lambda r: str(r.get('report_day') or r.get('day') or '')):
        day = r.get('report_day') or r.get('day') or r.get('period')
        body = r.get('text') or json.dumps({k: v for k, v in r.items() if k not in ('org_id',)})[:20000]
        blocks.append(f"[SOURCE: Bonvoy Report {day}]\n{body}")
    made += write_batches(org, 'bonvoy', blocks)
    # --- production daily
    blocks = [f"[SOURCE: Production Report {p.get('report_id') or p['day']}] {p['day']} | {p['tons']} t (saleable {p.get('saleable_tons')}) | uptime {p['uptime_pct']}% | breaks {p['breaks']} ({p['break_min']} min) | "
              f"unplanned {p['unplanned_min']} min | planned {p['planned_min']} | slowdown {p['slowdown_min']} | speed {p.get('avg_speed')} | grades {p.get('grade_hours')} | "
              f"steam {p.get('steam_per_t')} t/t | {p.get('kwh_per_t')} kWh/t | OME {p.get('ome_pct')} (time {p.get('time_eff')} rate {p.get('prod_eff')} quality {p.get('quality_eff')}) | crews {p.get('crew_day')}/{p.get('crew_night')}"
              for p in sorted(load(org, 'production_daily'), key=lambda p: p['day'])]
    made += write_batches(org, 'production-daily', blocks)
    # --- Sim Mill documents (vendor reports, RCFA write-ups, drawings, charts)
    ch = defaultdict(list)
    for c in load(org, 'doc_chunks'): ch[c['doc_id']].append(c)
    blocks = []
    for d in sorted(load(org, 'documents'), key=lambda d: str(d.get('doc_date') or '')):
        text = '\n'.join(f"[p.{c['page']}] {c['content'].strip()}" for c in sorted(ch.get(d['doc_id'], []), key=lambda c: (c['page'] or 0, c['chunk_no'])))
        blocks.append(f"[SOURCE: DOC {d['doc_id']} | {d.get('title')} | {d.get('kind')} | {d.get('vendor') or '-'} | {d.get('doc_date') or '-'} | positions {', '.join(d.get('positions') or []) or '-'}]\n"
                      + (f"summary: {ws(d['summary'])}\n" if d.get('summary') else '') + text)
    made += write_batches(org, 'documents', blocks)
    return made


def rag():
    org = 'demodemo-rag'
    docs = {d['doc_id']: d for d in load(org, 'documents')}
    pages = defaultdict(list)
    for p in load(org, 'doc_pages'): pages[p['doc_id']].append(p)
    blocks = []
    for doc_id, d in sorted(docs.items(), key=lambda kv: kv[1]['title']):
        if d['status'] != 'indexed': continue
        head = f"[SOURCE: DOC {doc_id} | {d['title']} | {d.get('kind')} | {d.get('vendor') or '-'} | {d.get('doc_date') or '-'} | {d.get('pages')} pages]"
        blocks.append(head + (f"\nsummary: {ws(d['summary'])}" if d.get('summary') else ''))
        blocks += [f"[DOC {doc_id} p.{p['page']}] ({d['title'][:60]})\n{(p['text'] or '').strip()}" for p in sorted(pages[doc_id], key=lambda p: p['page'])]
    return write_batches(org, 'library', blocks)


if __name__ == '__main__':
    import shutil; shutil.rmtree(OUT, ignore_errors=True)
    files = sim() + rag()
    tot = 0
    for f in files:
        n = f.stat().st_size; tot += n
    print(len(files), 'batch files,', tot // 1024, 'KB')
    for org in ('sim-mill', 'demodemo-rag'):
        fs = sorted((OUT / org).glob('*.txt'))
        print(org, len(fs), 'files', sum(f.stat().st_size for f in fs) // 1024, 'KB')
