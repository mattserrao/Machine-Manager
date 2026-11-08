// Model adapter: one request/response shape for the orchestrator, translated per provider.
// Switching provider is configuration (MM_LLM_PROVIDER, MM_LLM_MODEL); prompts and tools stay the same.
export type Tool = { name: string; description: string; parameters: Record<string, unknown> };
export type ToolCall = { id: string; name: string; args: Record<string, unknown> };
export type Turn = { text: string; calls: ToolCall[]; inTokens: number; outTokens: number };

export interface Model {
  provider: string; model: string;
  start(system: string, question: string): void;
  next(): Promise<Turn>;                           // one model step
  results(r: { id: string; content: string }[]): void;  // tool results for the last step's calls
}

export function makeModel(): Model {
  const provider = (Deno.env.get('MM_LLM_PROVIDER') ?? 'anthropic').toLowerCase();
  if (provider === 'anthropic') return new Anthropic(Deno.env.get('MM_LLM_MODEL') ?? 'claude-sonnet-5-5');
  if (provider === 'openai') return new OpenAI(Deno.env.get('MM_LLM_MODEL') ?? '');
  throw new ModelError(`Unknown MM_LLM_PROVIDER "${provider}" (use anthropic or openai).`);
}
export class ModelError extends Error {}

// Secrets pasted from a browser or a doc can carry spaces, quotes or invisible characters, which headers can't hold.
function secret(name: string): string {
  const raw = Deno.env.get(name) ?? '';
  const clean = raw.replace(/[^\x21-\x7e]/g, '').replace(/^['"]+|['"]+$/g, '');
  if (raw && clean !== raw) console.warn(`${name}: removed ${raw.length - clean.length} stray character(s); re-save the secret to tidy it`);
  return clean;
}

let TOOLS: Tool[] = [];
export function setTools(t: Tool[]) { TOOLS = t; }

class Anthropic implements Model {
  provider = 'anthropic'; key = secret('ANTHROPIC_API_KEY');
  system = ''; messages: any[] = [];
  constructor(public model: string) {
    const raw = Deno.env.get('ANTHROPIC_API_KEY') ?? '';
    if (!raw) throw new ModelError('ANTHROPIC_API_KEY is not set (Supabase → Edge Functions → Secrets).');
    if (!this.key) throw new ModelError(`ANTHROPIC_API_KEY is saved but unusable: ${raw.length} characters, none of them key characters (first is U+${raw.codePointAt(0)!.toString(16).toUpperCase().padStart(4, '0')}). Paste the key again.`);
    if (!this.key.startsWith('sk-ant-')) throw new ModelError(`ANTHROPIC_API_KEY doesn't look like an Anthropic key (should start sk-ant-; saved value is ${this.key.length} characters).`); }
  start(system: string, question: string) { this.system = system; this.messages = [{ role: 'user', content: question }]; }
  async next(): Promise<Turn> {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'x-api-key': this.key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
      body: JSON.stringify({ model: this.model, max_tokens: 2000, system: this.system, messages: this.messages,
        tools: TOOLS.map((t) => ({ name: t.name, description: t.description, input_schema: t.parameters })) }),
    });
    const j = await r.json();
    if (!r.ok) throw new ModelError(`Anthropic ${r.status}: ${j?.error?.message ?? JSON.stringify(j).slice(0, 300)}`);
    this.messages.push({ role: 'assistant', content: j.content });
    const text = j.content.filter((b: any) => b.type === 'text').map((b: any) => b.text).join('\n');
    const calls = j.content.filter((b: any) => b.type === 'tool_use').map((b: any) => ({ id: b.id, name: b.name, args: b.input ?? {} }));
    return { text, calls, inTokens: j.usage?.input_tokens ?? 0, outTokens: j.usage?.output_tokens ?? 0 };
  }
  results(rs: { id: string; content: string }[]) {
    this.messages.push({ role: 'user', content: rs.map((r) => ({ type: 'tool_result', tool_use_id: r.id, content: r.content })) });
  }
}

class OpenAI implements Model {
  provider = 'openai'; key = secret('OPENAI_API_KEY');
  messages: any[] = [];
  constructor(public model: string) {
    if (!this.key) throw new ModelError('OPENAI_API_KEY is not set (Supabase → Edge Functions → Secrets).');
    if (!model) throw new ModelError('Set MM_LLM_MODEL to the OpenAI model to use.');
  }
  start(system: string, question: string) { this.messages = [{ role: 'system', content: system }, { role: 'user', content: question }]; }
  async next(): Promise<Turn> {
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST', headers: { authorization: `Bearer ${this.key}`, 'content-type': 'application/json' },
      body: JSON.stringify({ model: this.model, messages: this.messages,
        tools: TOOLS.map((t) => ({ type: 'function', function: { name: t.name, description: t.description, parameters: t.parameters } })) }),
    });
    const j = await r.json();
    if (!r.ok) throw new ModelError(`OpenAI ${r.status}: ${j?.error?.message ?? JSON.stringify(j).slice(0, 300)}`);
    const m = j.choices[0].message; this.messages.push(m);
    const calls = (m.tool_calls ?? []).map((c: any) => ({ id: c.id, name: c.function.name, args: safeJson(c.function.arguments) }));
    return { text: m.content ?? '', calls, inTokens: j.usage?.prompt_tokens ?? 0, outTokens: j.usage?.completion_tokens ?? 0 };
  }
  results(rs: { id: string; content: string }[]) {
    for (const r of rs) this.messages.push({ role: 'tool', tool_call_id: r.id, content: r.content });
  }
}
const safeJson = (s: string) => { try { return JSON.parse(s || '{}'); } catch { return {}; } };
