"""The report lifecycle, shared by every producer and by the loader.

A report is one JSON envelope:

    {
      "report_id": "PM1-SHIFT-2026-10-30-D", "type": "shift", "schema": 1, "machine": "PM1",
      "period_start": "2026-10-30T06:00:00-04:00", "period_end": "2026-10-30T18:00:00-04:00",
      "mill_day": "2026-10-30", "shift": "Day", "crew": "B",
      "author": {"id": "P09", "name": "Lucille Brandt", "role": "Shift lead (crew B)"},
      "source": "sim-mill", "status": "submitted",
      "history": [{"at": "...", "to": "generated"}, {"at": "...", "to": "submitted"}],
      "body": {...the type's fields (registry.yaml: required)...},
      "text": "the report as a person reads it (markdown)"
    }

States, in order. A producer takes a report to `submitted`; the database takes it the rest of the way.

    generated   written and validated by its producer
    submitted   handed over (written to the outbox, emailed, posted)
    ingested    stored in llm.reports (public.mm_llm_ingest)
    extracted   its body is in the tables it feeds (public.mm_llm_process_reports)
    indexed     its text is searchable by MM LLM (documents + chunks; the embedder follows)
    failed      a step failed: `error` says why. Retrying goes back to the step that failed.
"""
import datetime as dt, json, os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = yaml.safe_load(open(os.path.join(HERE, 'registry.yaml')))
SCHEMA = 1

STATES = ('generated', 'submitted', 'ingested', 'extracted', 'indexed', 'failed')
NEXT = {'generated': {'submitted', 'failed'}, 'submitted': {'ingested', 'failed'}, 'ingested': {'extracted', 'failed'},
        'extracted': {'indexed', 'failed'}, 'indexed': set(), 'failed': {'generated', 'submitted', 'ingested'}}
SHIFT_CODE = {'Day': 'D', 'Night': 'N'}


class InvalidReport(ValueError):
    pass


def report_id(rtype, machine, mill_day, shift=None):
    spec = REGISTRY['types'][rtype]
    return spec['id'].format(machine=machine, type_code=rtype.upper(), mill_day=mill_day, shift_code=SHIFT_CODE.get(shift, ''))


def advance(rep, to, at=None, detail=None):
    """Move a report to the next state, recording it in its history. Raises on a move the lifecycle doesn't allow."""
    cur = rep.get('status')
    if cur is not None and to not in NEXT[cur]:
        raise InvalidReport(f"{rep.get('report_id')}: can't go from {cur} to {to}")
    at = at or dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    rep['status'] = to
    h = {'at': at, 'to': to}
    if detail: h['detail'] = detail
    rep.setdefault('history', []).append(h)
    if to == 'failed': rep['error'] = detail
    return rep


def validate(rep):
    """The envelope and the type's required body fields. Returns the report; raises InvalidReport."""
    for k in ('report_id', 'type', 'machine', 'period_start', 'period_end', 'mill_day', 'body', 'text'):
        if not rep.get(k) and rep.get(k) != 0: raise InvalidReport(f"{rep.get('report_id', '?')}: missing {k}")
    spec = REGISTRY['types'].get(rep['type'])
    if not spec: raise InvalidReport(f"{rep['report_id']}: unknown type {rep['type']}")
    miss = [k for k in spec['required'] if k not in rep['body']]
    if miss: raise InvalidReport(f"{rep['report_id']}: body is missing {', '.join(miss)}")
    if spec['cadence'] == 'shift' and rep.get('shift') not in SHIFT_CODE: raise InvalidReport(f"{rep['report_id']}: shift must be Day or Night")
    if rep['period_end'] <= rep['period_start']: raise InvalidReport(f"{rep['report_id']}: period ends before it starts")
    return rep


def path_for(outbox, rep):
    """Where a report lives in an outbox: <outbox>/<type>/<yyyy-mm>/<report_id>.json"""
    return os.path.join(outbox, rep['type'], rep['mill_day'][:7], rep['report_id'] + '.json')


def write(outbox, rep):
    p = path_for(outbox, rep); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f: json.dump(rep, f, indent=1, ensure_ascii=False); f.write('\n')
    return p


def periods(rtype, first_day, last_day, through=None):
    """(mill_day, shift) for every period of a type from first_day to last_day (mill days) that has ended by `through`
    (a naive mill-local datetime; None: all of them)."""
    spec = REGISTRY['types'][rtype]
    d = first_day
    while d <= last_day:
        start = dt.datetime.combine(d, dt.time(6))
        if spec['cadence'] == 'shift':
            for s, a in (('Day', start), ('Night', start + dt.timedelta(hours=12))):
                if through is None or a + dt.timedelta(hours=12) <= through: yield d, s
        elif through is None or start + dt.timedelta(days=1) <= through:
            yield d, None
        d += dt.timedelta(days=1)
