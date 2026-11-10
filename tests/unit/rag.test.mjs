// The RAG worker's pure logic (supabase/functions/mm-rag-process/rag.ts): page quality, Claude's page transcription,
// the assessment clean-up, the score and gate, chunking with a context header, and position tagging.
//
//   node tests/unit/rag.test.mjs      (from the repo root; Node 22.18+ runs the .ts file directly)
import { garbleRate, needsModel, splitModelPages, isRefusal, NOTES_PROMPT, NOTES_MARK, parseJson, cleanAssessment, score, contextHeader, chunkPages, tagPositions,
         isPdf, assessPrompt } from '../../supabase/functions/mm-rag-process/rag.ts';

const failures = [];
const check = (name, ok, detail = '') => { if (!ok) failures.push(name); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); };

// ---- page quality ----
const clean = 'Keel Vibration Services route 2026-10-19. Dryer can 27 drive side bearing reads 0.24 in/s overall, up from 0.07 in/s on Sep 14. Recommend a bearing change at the Nov 11 outage and a follow-up reading in two weeks.';
const junk = 'Kxl Vbrtn Srvcs rt 2026 Dryr cn 27 drv sd brng rds 0.24 �� \u0001\u0002 qwrtpsdf lkjhgfds zxcvbnm';
check('clean text has a low garble rate', garbleRate(clean) < 0.03, garbleRate(clean).toFixed(3));
check('broken text has a high garble rate', garbleRate(junk) > 0.3, garbleRate(junk).toFixed(3));
check('units and part numbers are not garble', garbleRate('Nip load 85 pli, 3,450 rpm, P/N 7731-B, 0.31 in/s, 48°C ±2') < 0.05);
check('a near-empty page goes to Claude', needsModel('Page 3'));
check('a scanned page with no text layer goes to Claude', needsModel(''));
check('a clean page stays on the text layer', !needsModel(clean));
check('a garbled page goes to Claude', needsModel(junk + ' ' + junk + ' ' + junk));

// ---- Claude's transcription ----
const reply = 'Here you go\n=== PAGE 1 ===\n# Survey\nCaliper 2.1 mm\n=== PAGE 2 ===\n| Pos | Perm |\n|---|---|\n| TS | 38 |\n';
const m = splitModelPages(reply, [4, 9]);
check('transcribed pages map back to the original page numbers', m.get(4)?.startsWith('# Survey') && m.get(9)?.includes('| TS | 38 |') && m.size === 2);
check('an unexpected extra page is ignored', splitModelPages('=== PAGE 3 ===\nx', [4, 9]).size === 0);

check('a copyright refusal is recognised', isRefusal('Claude 400: Output blocked by content filtering policy') && !isRefusal('Claude 529: overloaded'));
check('the notes prompt keeps the page markers and asks for own words', NOTES_PROMPT.includes('=== PAGE <n> ===') && NOTES_PROMPT.includes(NOTES_MARK) && /Do not copy/.test(NOTES_PROMPT));

// ---- assessment ----
check('JSON is found inside a fenced reply', parseJson('Sure:\n```json\n{"kind":"vendor_report","relevance":5}\n```')?.kind === 'vendor_report');
check('no JSON → null', parseJson('I cannot help') === null);
const a = cleanAssessment({ kind: 'nonsense', doc_date: '2026-13-45', positions: ['d2-can27', 'made-up'], relevance: 9, readability: '4', issues: ['x'] }, new Set(['d2-can27']));
check('unknown kind → other', a.kind === 'other');
check('a bad date is dropped', a.doc_date === undefined);
check('positions not in the machine list are dropped', a.positions.length === 1 && a.positions[0] === 'd2-can27');
check('scores outside 1-5 are dropped, strings accepted', a.relevance === undefined && a.readability === 4);
check('the prompt fences the document and warns against its instructions', assessPrompt('TEXT', [], 'x.pdf').includes('<document>\nTEXT\n</document>') && /never follow instructions/.test(assessPrompt('', [], 'x')));

// ---- score and gate ----
const set = { accept_min: 75, review_min: 40, model: 'm' };
const sig = (o = {}) => ({ pages: 4, empty_pages: 0, model_pages: 0, avg_chars: 1800, avg_garble: 0.01, near_duplicate: null, has_positions_list: true, model_ok: true, ...o });
const good = { kind: 'vendor_report', doc_date: '2026-10-19', positions: ['d2-can27'], relevance: 5, readability: 5, completeness: 5, issues: [] };
let g = score(sig(), good, set);
check('a clean, dated, linked mill document is accepted', g.decision === 'accepted' && g.score >= 95, JSON.stringify(g));
g = score(sig(), { ...good, doc_date: undefined }, set);
check('a missing date sends it to review even with a high score', g.decision === 'needs_review' && g.score >= 75 && g.review.includes('no date found'));
g = score(sig(), { ...good, kind: 'manual', doc_date: undefined }, set);
check('a manual or paper without a date is accepted (reference material)', g.decision === 'accepted', JSON.stringify(g));
g = score(sig({ has_positions_list: false }), { ...good, positions: [] }, set);
check('no positions needed when the org has none set up', g.decision === 'accepted', JSON.stringify(g));
g = score(sig(), { ...good, contains_instructions_to_ai: true }, set);
check('instructions aimed at an AI always go to review', g.decision === 'needs_review' && g.review.some((r) => /instructions/.test(r)));
g = score(sig({ near_duplicate: { doc_id: 'abc', title: 'Old route', distance: 0.02 } }), good, set);
check('a near-duplicate goes to review and names the other document', g.decision === 'needs_review' && g.review.some((r) => r.includes('Old route')));
g = score(sig(), { ...good, relevance: 1, completeness: 2 }, set);
check('a document not about a mill is rejected', g.decision === 'rejected', JSON.stringify(g));
g = score(sig({ empty_pages: 4 }), good, set);
check('no readable text on any page → rejected with score 0', g.decision === 'rejected' && g.score === 0);
g = score(sig({ avg_garble: 0.2 }), { ...good, readability: 2 }, set);
check('garbled text lands in review', g.decision === 'needs_review' && g.reasons.includes('much of the text is garbled'), JSON.stringify(g));
g = score(sig({ model_ok: false }), cleanAssessment(null, new Set()), set);
check('when the check model fails, a person reviews it', g.decision !== 'accepted' && g.review.some((r) => /review by hand/.test(r)));

// ---- chunks ----
const header = contextHeader({ vendor: 'Keel Vibration Services', kind: 'vendor_report', doc_date: '2026-10-19', title: 'Route Oct', positionNames: ['Dryer can 27'] });
check('context header reads naturally', header === 'Keel Vibration Services · Vendor report · 2026-10-19 · Route Oct · Dryer can 27', header);
const table = '| Point | in/s |\n|---|---|\n' + Array.from({ length: 80 }, (_, i) => `| Can ${i + 1} DS | 0.${String(i).padStart(2, '0')} |`).join('\n');
const long = Array.from({ length: 40 }, (_, i) => `Sentence ${i} about the felt run and its permeability readings.`).join(' ');
const chunks = chunkPages([{ page: 2, text: '# Findings\n' + long + '\n\n' + table, text_source: 'layer' }, { page: 1, text: clean, text_source: 'layer' }], header);
check('chunks are in page order and numbered', chunks[0].page === 1 && chunks.every((c, i) => c.chunk_no === i));
check('every chunk starts with the context header and its page', chunks.every((c) => c.content.startsWith(header + ' · p.' + c.page + '\n')));
check('chunks stay near the size limit', chunks.every((c) => c.content.length <= 1100 + header.length + 12), Math.max(...chunks.map((c) => c.content.length)));
const tableChunks = chunks.filter((c) => c.content.includes('| Can '));
check('a long table is split by rows and each part keeps the header row', tableChunks.length >= 2 && tableChunks.every((c) => c.content.includes('| Point | in/s |')));
check('no row is lost when a table is split', Array.from({ length: 80 }, (_, i) => `| Can ${i + 1} DS |`).every((r) => chunks.some((c) => c.content.includes(r))));
check('an empty page makes no chunk', chunkPages([{ page: 1, text: '  ', text_source: 'layer' }], header).length === 0);

// ---- position tagging ----
const pos = [{ id: 'd2-can27', name: 'Dryer can 27' }, { id: 'd2-can2', name: 'Dryer can 2' }, { id: 'p2-felt-top', name: '2nd press top felt' }];
check('a position is tagged by name', tagPositions('Reading at dryer can 27 DS', pos).includes('d2-can27'));
check('"can 27" doesn\'t tag can 2', !tagPositions('Reading at dryer can 27 DS', pos).includes('d2-can2'));
check('the document\'s own positions are kept', tagPositions('nothing here', pos, ['p2-felt-top'])[0] === 'p2-felt-top');

// ---- file check ----
check('PDF magic bytes', isPdf(new TextEncoder().encode('%PDF-1.7\n')) && !isPdf(new TextEncoder().encode('MZ\x90\x00\x03')));

console.log(failures.length ? `\n${failures.length} failed` : '\nall passed');
process.exit(failures.length ? 1 : 0);
