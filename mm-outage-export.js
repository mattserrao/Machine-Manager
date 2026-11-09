// Machine Manager: Operations Outage Planning → Word (.docx) outage plan.
//
//   MMOutageExport.outline(model)  plain sections (no Word); unit tested in Node
//   MMOutageExport.docx(model)     Promise<Blob>, loads vendor/docx-*.js the first time it's needed
//
// The page hands over a plain model of one outage (see exportModel in OperationsOutagePlanning.html):
//   { machine, outage: { date, type, shutdown, onReel, hours }, due: [...], tasks: [...], packages: [...],
//     positions: [...], shifts: [{ k, grp, name }], manning: { shift: { pos: { v, inherited } } }, crews: { A: { names } } }
//
// Sections: Outage prep · Resources · Shutdown · Short Off · Days · Start-up. Each work section is split by area:
// Stock prep (SP), Wet end (WE), Dry end (DE), then anything without an area.
(() => {
  'use strict';
  const DOCX_SRC = 'vendor/docx-9.15.3.js';
  const AREAS = [{ k: 'SP', l: 'Stock prep' }, { k: 'WE', l: 'Wet end' }, { k: 'DE', l: 'Dry end' }];
  const WORK = [
    { k: 'shutdown', l: 'Shutdown', shift: 'shutdown' },
    { k: 'shortoff', l: 'Short Off', shift: 'shortoff' },
    { k: 'day', l: 'Days', shift: 'day' },
    { k: 'startup', l: 'Start-up', shift: 'startup' },
  ];

  // Area from free text (a package's area, a machine section): stock prep, wet end or dry end.
  function areaOf(text){
    const t = String(text || '').toLowerCase();
    if (/stock|refin|pulp|cleaner|screen|chest|occ|approach/.test(t)) return 'SP';
    if (/dry|calender|reel|winder|hood|yankee|size press|steam/.test(t)) return 'DE';
    if (/wire|form|press|wet|headbox|couch|uhle|lump|vacuum|ply/.test(t)) return 'WE';
    return '';
  }
  // A package phase (frame title in the Ops Task Library) → outage phase.
  function phaseOfTitle(title){
    const t = String(title || '').toLowerCase();
    if (/before|prep|plan|order|stage|pre-/.test(t)) return 'prep';
    if (/shut|lock|isolat|wash.?up/.test(t)) return 'shutdown';
    if (/start|run.?up|run in|sheet on|thread/.test(t)) return 'startup';
    return 'day';
  }
  const pad = n => String(n).padStart(2, '0');
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const DOW = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const dParts = s => { const [y, m, d] = s.slice(0, 10).split('-').map(Number); return { y, m, d, dow: new Date(y, m - 1, d).getDay() }; };
  const dayShort = s => { const p = dParts(s); return `${MON[p.m - 1]} ${p.d}`; };
  const dayLong = s => { const p = dParts(s); return `${DOW[p.dow]}, ${MON[p.m - 1]} ${p.d}, ${p.y}`; };
  const when = s => s ? `${DOW[dParts(s).dow].slice(0, 3)} ${dayShort(s)} ${s.slice(11, 16)}` : '';
  const hrs = h => h == null ? '' : `${String(Math.round(h * 10) / 10).replace(/\.0$/, '')} h`;

  // Lines of a library step worth printing: checklist items and bullets as plain text.
  const cleanLines = ls => (ls || []).map(l => l.replace(/^\s*[-*] \[( |x|X)\] ?/, '').replace(/^\s*[-*] /, '').trim()).filter(Boolean);

  function outline(m){
    const o = m.outage;
    // Everything that is work: tasks and package steps, each with a phase and an area.
    const work = [];
    for (const t of m.tasks || []){
      work.push({ kind: 'task', phase: t.phase || '', area: t.area || '', text: t.text, crew: t.crew || '', who: t.who || '', done: !!t.done, hrs: null, lines: [] });
    }
    for (const k of m.packages || []){
      const area = k.areaCode || areaOf(k.area || k.name);
      for (const ph of k.phases || []){
        const phase = phaseOfTitle(ph.title);
        for (const st of ph.steps || []){
          work.push({ kind: 'step', phase, area, pkg: k.name, text: `${k.name}: ${st.title}`, crew: '', who: st.who || '', done: !!st.done, hrs: st.hrs || null,
            lines: [...cleanLines(st.lines), ...(st.subs || [])] });
        }
      }
    }
    const byArea = items => {
      const groups = AREAS.map(a => ({ k: a.k, title: `${a.l} (${a.k})`, items: items.filter(w => w.area === a.k) }));
      groups.push({ k: '', title: 'No area set', items: items.filter(w => !AREAS.some(a => a.k === w.area)) });
      return groups.filter(g => g.items.length);
    };

    const sections = [];
    // ---- Outage prep ----
    const due = (m.due || []).filter(x => !x.changed);
    const accepted = due.filter(x => x.accepted && !x.declined), open = due.filter(x => !x.accepted && !x.declined), declined = due.filter(x => x.declined);
    const dueRow = (x, decision) => ({
      name: x.name, section: x.section, area: areaOf(x.section) || '', due: x.due ? dayShort(x.due) : '',
      decision, note: [x.flag && `Flagged: ${x.flag}`, x.missed && `Missed ${dayShort(x.missed)}`, x.deferred && `Deferred from ${dayShort(x.deferred)}`, x.note].filter(Boolean).join(' · '),
    });
    sections.push({ k: 'prep', title: 'Outage prep',
      fabrics: [...accepted.map(x => dueRow(x, 'Accepted')), ...open.map(x => dueRow(x, 'To decide'))],
      declined: declined.map(x => ({ name: x.name, to: x.to ? dayShort(x.to) : '' })),
      groups: byArea(work.filter(w => w.phase === 'prep')) });

    // ---- Resources: the manning sheet, then who has tasks ----
    const shifts = m.shifts || [];
    const manning = (m.positions || []).map(pos => ({ pos, names: shifts.map(sh => ((m.manning[sh.k] || {})[pos] || {}).v || '') }));
    const people = {};
    for (const w of work) if (w.kind === 'task' && (w.who || w.crew)){
      const key = (w.crew || '') + '|' + (w.who || '');
      (people[key] = people[key] || { crew: w.crew, who: w.who, tasks: [] }).tasks.push(w);
    }
    const assignments = Object.values(people).sort((a, b) => (a.crew || 'Z').localeCompare(b.crew || 'Z') || (a.who || '').localeCompare(b.who || ''));
    const crewList = ['A', 'B', 'C', 'D'].map(c => ({ crew: c, names: ((m.crews || {})[c] || {}).names || [] })).filter(c => c.names.length);
    sections.push({ k: 'resources', title: 'Resources', shiftNames: shifts.map(sh => `${sh.grp} · ${sh.name}`), manning, assignments, crews: crewList });

    // ---- Shutdown · Short Off · Days · Start-up ----
    for (const ph of WORK){
      const sh = shifts.find(s => s.k === ph.shift);
      const crew = (m.positions || []).map(pos => ({ pos, v: ((m.manning[ph.shift] || {})[pos] || {}).v || '' })).filter(x => x.v);
      const time = ph.k === 'shutdown' && o.shutdown ? `Sheet off ${when(o.shutdown)}` : ph.k === 'startup' && o.onReel ? `On reel ${when(o.onReel)}` : '';
      sections.push({ k: ph.k, title: ph.l, shift: sh ? `${sh.grp} · ${sh.name}` : '', time, crew, groups: byArea(work.filter(w => w.phase === ph.k)) });
    }
    const unphased = work.filter(w => !w.phase);
    if (unphased.length) sections.push({ k: 'other', title: 'Not yet given a phase', groups: byArea(unphased) });

    const counts = { tasks: (m.tasks || []).length, done: (m.tasks || []).filter(t => t.done).length, steps: work.filter(w => w.kind === 'step').length };
    return {
      title: `${m.machine || 'PM1'} outage plan`,
      date: dayLong(o.date), dateIso: o.date, type: o.type === 'annual' ? 'Annual outage' : 'Outage',
      times: o.shutdown || o.onReel ? `Shutdown ${o.shutdown ? when(o.shutdown) : 'not set'}  →  On reel ${o.onReel ? when(o.onReel) : 'not set'}${o.hours != null ? `  ·  ${hrs(o.hours)} planned` : ''}` : 'Shutdown and on-reel times not set',
      counts, sections,
    };
  }

  /* ---------- Word ---------- */
  let loading = null;
  function loadDocx(){
    if (window.docx) return Promise.resolve(window.docx);
    if (loading) return loading;
    // same version stamp as this file, so the two are fetched together
    const me = [...document.scripts].find(s => /mm-outage-export\.js/.test(s.src));
    const v = me && /\?v=([^&]+)/.exec(me.src);
    loading = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = DOCX_SRC + (v ? '?v=' + v[1] : '');
      s.onload = () => window.docx ? res(window.docx) : rej(new Error('Word library didn’t load'));
      s.onerror = () => { loading = null; rej(new Error('Couldn’t load the Word library')); };
      document.head.appendChild(s);
    });
    return loading;
  }

  function render(D, ol){
    const { Document, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, AlignmentType, Header, Footer, PageNumber, TableLayoutType } = D;
    const FONT = 'Calibri', INK = '1F1F1E', MUTED = '6B6B66', LINE = 'C9C7BF', HEAD = 'EFEDE6', ACC = 'B7791F';
    const t = (text, o = {}) => new TextRun({ text: String(text == null ? '' : text), font: FONT, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color || INK, strike: o.strike });
    const p = (runs, o = {}) => new Paragraph({ children: Array.isArray(runs) ? runs : [typeof runs === 'string' ? t(runs, o) : runs], spacing: { after: o.after == null ? 80 : o.after, before: o.before || 0 }, alignment: o.align, pageBreakBefore: o.pageBreak, keepNext: o.keepNext, heading: o.heading });
    const h1 = (text, pageBreak) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: pageBreak, keepNext: true, spacing: { before: 0, after: 120 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACC, space: 4 } }, children: [t(text, { size: 30, bold: true })] });
    const h2 = text => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 200, after: 80 }, children: [t(text, { size: 23, bold: true })] });
    const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
    const borders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };
    const cell = (content, o = {}) => new TableCell({
      width: o.w ? { size: o.w, type: WidthType.PERCENTAGE } : undefined,
      shading: o.head ? { type: ShadingType.CLEAR, color: 'auto', fill: HEAD } : undefined,
      margins: { top: 50, bottom: 50, left: 90, right: 90 },
      children: (Array.isArray(content) ? content : [content]).map(c => c instanceof Paragraph ? c : p([t(c, { bold: o.head, size: o.size || 19, color: o.color })], { after: 0 })),
    });
    const table = (head, rows, widths) => new Table({
      width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED, borders,
      rows: [new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, { head: true, w: widths[i] })) }),
        ...rows.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, { w: widths[i] })) }))],
    });
    const box = done => done ? '☒' : '☐';

    const workTable = items => table(['', 'Task', 'Crew', 'Assigned to', 'Hrs'], items.map(w => [
      p([t(box(w.done), { size: 22 })], { after: 0, align: AlignmentType.CENTER }),
      [p([t(w.text, { size: 19, bold: w.kind === 'task', strike: w.done, color: w.done ? MUTED : INK })], { after: w.lines.length ? 30 : 0 }),
        ...w.lines.map((l, i) => p([t('– ' + l, { size: 17, color: MUTED })], { after: i === w.lines.length - 1 ? 0 : 10 }))],
      w.crew ? `Crew ${w.crew}` : '', w.who, w.hrs ? String(w.hrs) : '',
    ]), [5, 55, 10, 22, 8]);
    const groups = (gs, none) => {
      if (!gs.length) return [p(none, { color: MUTED, italics: true })];
      return gs.flatMap(g => [h2(g.title), workTable(g.items)]);
    };

    const kids = [];
    // Title block
    kids.push(p([t(ol.title, { size: 40, bold: true })], { after: 40 }));
    kids.push(p([t(`${ol.type} · ${ol.date}`, { size: 24, color: MUTED })], { after: 40 }));
    kids.push(p([t(ol.times, { size: 21, bold: true })], { after: 60 }));
    kids.push(p([t(`${ol.counts.tasks} tasks (${ol.counts.done} done) · ${ol.counts.steps} package steps`, { size: 18, color: MUTED })], { after: 240 }));

    ol.sections.forEach((s, i) => {
      kids.push(h1(s.title, i > 0));
      if (s.k === 'prep'){
        kids.push(h2('Fabrics & rolls'));
        if (s.fabrics.length) kids.push(table(['Position', 'Section', 'Area', 'Due', 'Decision', 'Note'],
          s.fabrics.map(f => [f.name, f.section, f.area, f.due, f.decision, f.note]), [24, 18, 7, 10, 12, 29]));
        else kids.push(p('No fabrics or rolls due at this outage.', { color: MUTED, italics: true }));
        if (s.declined.length) kids.push(p([t('Declined: ', { size: 18, bold: true, color: MUTED }), t(s.declined.map(d => `${d.name} → ${d.to || 'no later outage scheduled'}`).join('; '), { size: 18, color: MUTED })], { before: 80 }));
        kids.push(...groups(s.groups, 'No prep tasks yet.'));
      } else if (s.k === 'resources'){
        kids.push(h2('Manning'));
        kids.push(table(['Position', ...s.shiftNames], s.manning.map(r => [r.pos, ...r.names]), [16, 21, 21, 21, 21]));
        kids.push(p([t('Start-up runs with the Shutdown crew unless a position is changed.', { size: 17, color: MUTED, italics: true })], { before: 60 }));
        if (s.assignments.length){
          kids.push(h2('Assigned tasks'));
          kids.push(table(['Crew', 'Person', 'Tasks'], s.assignments.map(a => [a.crew ? `Crew ${a.crew}` : '', a.who || '(crew)',
            a.tasks.map(w => (w.phase ? ({ prep: 'Prep', shutdown: 'Shutdown', shortoff: 'Short Off', day: 'Days', startup: 'Start-up' })[w.phase] + ': ' : '') + w.text)]), [12, 22, 66]));
        }
        if (s.crews.length){
          kids.push(h2('Crews'));
          kids.push(table(s.crews.map(c => `Crew ${c.crew}`), [s.crews.map(c => c.names)], s.crews.map(() => Math.floor(100 / s.crews.length))));
        }
      } else {
        const meta = [s.shift, s.time].filter(Boolean).join(' · ');
        if (meta) kids.push(p([t(meta, { size: 21, bold: true })], { after: 60 }));
        if (s.crew && s.crew.length) kids.push(p([t('On shift: ', { size: 18, bold: true }), t(s.crew.map(c => `${c.pos} ${c.v}`).join(' · '), { size: 18, color: MUTED })], { after: 100 }));
        kids.push(...groups(s.groups, 'Nothing planned for this part of the outage yet.'));
      }
    });

    return new Document({
      creator: 'Machine Manager', title: `${ol.title} ${ol.dateIso}`,
      styles: { default: { document: { run: { font: FONT, size: 20 } } } },
      sections: [{
        properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } },
        headers: { default: new Header({ children: [p([t(`${ol.title} · ${ol.date}`, { size: 16, color: MUTED })], { align: AlignmentType.RIGHT, after: 0 })] }) },
        footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
          new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: MUTED })] })] }) },
        children: kids,
      }],
    });
  }

  async function docx(model){
    const D = await loadDocx();
    return D.Packer.toBlob(render(D, outline(model)));
  }

  const api = { outline, docx, areaOf, phaseOfTitle, render };
  if (typeof window !== 'undefined') window.MMOutageExport = api;
  if (typeof module !== 'undefined') module.exports = api;
})();
