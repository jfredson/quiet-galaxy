// The typed view of the JSON the export script writes (scripts/export.py), plus the wording and
// the small helpers every page shares. Every page reads from here; nothing in the browser touches
// the TOML records. The file src/data/records.json is generated at build time and not committed:
// `npm run export` (or any build or dev run) writes it from ../data.
import data from '../data/records.json';

export interface Counts {
  factors: number;
  factors_expected: number;
  explanations: number;
  library: number;
  publications: number;
  retired: number;
  verify: number;
  estimates: number;
}

/** A publication as another record's page lists it. */
export interface PubBrief {
  id: string;
  title: string;
  date: string;      // when it appeared: year, year-month or full date, as text
  added_on: string;  // when it was logged, year-month-day
  authors: string[];
  moved_range: boolean;
  link?: string;
  path: string;      // /story/#id
}

export interface LibraryBrief {
  id: string;
  title: string;
  maker: string;
  year: number;
  kind: string;
  kind_name: string;
  path: string;      // /library/#id
}

export interface ExplanationBrief {
  id: string;
  name: string;
  family: string;
  family_name?: string;
  summary?: string;
  path: string;
}

export interface FactorBrief {
  id: string;
  order: number;
  symbol: string;
  unit: string;
  name: string;
  exists: boolean;
  path: string;
}

export interface Estimate {
  who: string;
  when: string;
  value?: number;
  low?: number;
  high?: number;
  source: string;
  method: string;
  link?: string;
  publication?: string;
  publication_brief?: PubBrief;
}

export interface Range {
  low: number;             // the pessimistic end; for a log-normal-rate range, the chance one spread below the centre
  high: number;            // the optimistic end; 1 for a log-normal-rate range
  shape: 'log-uniform' | 'uniform' | 'log-normal-rate';
  median?: number;         // log-normal-rate only: starts of life per planet at the centre of the bell curve
  spread_orders?: number;  // log-normal-rate only: the curve's spread, in powers of ten
  middle: number;          // where a slider starts: the middle of the range, or the chance at the centre rate
  words: string;           // the range in plain words (log-normal-rate only; else empty and rangeWords is used)
  short: string;           // the same, short enough for the equation strip
  status: 'first-pass' | 'reviewed';
  set_on: string;
  why: string;
  sources: PubBrief[];
}

export interface Revision {
  date: string;
  field: string;
  old: unknown;
  new: unknown;
  why: string;
  publication?: string;
  publication_brief: PubBrief | null;
}

export interface Factor extends FactorBrief {
  file: string | null;
  slider: { low: number; high: number };
  description: string;
  what_would_move_this: string;
  estimates: Estimate[];
  range: Range | null;
  revisions: Revision[];
  verify: string[];
  notes: string;
  explanations: { id: string; name: string; family: string; direction: Direction }[];
  publications: PubBrief[];
  library: LibraryBrief[];
}

export type Direction = 'lowers' | 'raises' | 'unchanged';

export interface Explanation {
  id: string;
  name: string;
  family: string;
  family_name: string;
  path: string;
  file: string;
  proposed_by: string;
  proposed_in: number;
  proposed_source: string;
  summary: string;
  body: string;
  standing: string;
  would_strengthen: string;
  would_weaken: string;
  bears_on: (FactorBrief & { factor: string; direction: Direction })[];
  related: ExplanationBrief[];
  related_in: ExplanationBrief[];
  library: LibraryBrief[];
  publications: PubBrief[];
  verify: string[];
  notes: string;
}

export interface Family {
  key: string;
  name: string;
  blurb: string;
  count: number;
  explanations: string[];
}

export interface LibraryEntry extends LibraryBrief {
  file: string;
  explanations: ExplanationBrief[];
  factors: FactorBrief[];
  how: string;
  worth_the_time: string;
  link: string;
  verify: string[];
  notes: string;
}

export interface Publication {
  id: string;
  date: string;
  added_on: string;
  authors: string[];
  title: string;
  venue: string;
  link: string;
  finding: string;
  path: string;
  file: string;
  factors: FactorBrief[];
  explanations: ExplanationBrief[];
  moved_range: boolean;
  revisions: { factor: string; factor_name: string; date: string; field: string; old: unknown; new: unknown; why: string }[];
  verify: string[];
  notes: string;
}

export type Headline =
  | { available: false; reason: string }
  | {
      available: true;
      median: number;
      alone_galaxy: number;
      alone_universe: number;
      optimist?: number;          // N with every piece at its most hopeful published estimate
      pessimist?: number;         // and at its most pessimistic
      optimist_from_ranges?: number;
      pessimist_from_ranges?: number;
      mean?: number;
      runs?: number;
      computed_on?: string;
      seed?: number | string;
      note?: string;
      file?: string;
      percentiles?: Record<string, number>;
      any_range_first_pass?: boolean;
      verify_open?: number;
      method?: { after?: string; runs?: number; seed?: number; independent_draws?: boolean; galaxies?: number; status?: string };
      life_sensitivity?: { label: string; in_use: boolean; median: number; alone_in_galaxy: number; alone_in_universe: number }[];
    };

export interface Records {
  exported_on: string;   // year-month-day
  commit: string;        // short code of the source version, or ""
  counts: Counts;
  headline: Headline;
  reading: null;         // the latest weekly reading, once the weekly scan exists
  factors: Factor[];     // all seven, in equation order; `exists` says whether the record is written
  families: Family[];
  explanations: Explanation[];
  library: LibraryEntry[];
  library_kinds: { key: string; name: string; count: number }[];
  publications: Publication[];  // newest logged first
  story_totals: { entries: number; moved: number; held: number; days: number };
  retired: { id: string; kind: string; date: string; why: string; replaced_by?: string }[];
}

export const records = data as unknown as Records;
export const REPO = 'https://github.com/jfredson/quiet-galaxy';

export const factorById = (id: string) => records.factors.find((f) => f.id === id);
export const explanationById = (id: string) => records.explanations.find((e) => e.id === id);
export const familyByKey = (key: string) => records.families.find((f) => f.key === key);

// ---------------------------------------------------------------- wording

/** The direction an explanation pushes a factor, as a plain clause after the factor's name. */
export const directionWords: Record<Direction, string> = {
  lowers: 'says this is smaller than it looks',
  raises: 'says this is larger than it looks',
  unchanged: 'leaves this where it is; the silence is about us',
};
export const directionShort: Record<Direction, string> = {
  lowers: 'smaller',
  raises: 'larger',
  unchanged: 'left alone',
};

export const shapeWords: Record<Range['shape'], string> = {
  'log-uniform': 'every tenfold step between the two ends is equally likely',
  uniform: 'every value between the two ends is equally likely',
  'log-normal-rate': 'what is picked is not the share itself but the number of times life starts on such a planet over its life, from a bell curve in its powers of ten; the share is then one minus e to the minus that number, so about half the picks land near 1 and the rest spread evenly across the powers of ten below',
};

/** The range in plain words: "0.1 to 1 planets per star", or for the shape with no ends,
    the words the export wrote ("a rate centred on one start per planet, spread over fifty orders
    of magnitude"). `short` picks the form for the equation strip. */
export function rangeText(range: Range, unit: string, short = false): string {
  if (range.shape === 'log-normal-rate' && range.words) return short ? range.short || range.words : range.words;
  return rangeWords(range.low, range.high, unit);
}
export const statusWords: Record<Range['status'], string> = {
  'first-pass': 'first pass, not yet reviewed',
  reviewed: 'reviewed',
};

/** The unit, as it reads after a number: "0.1 to 1" for a fraction, "100 to 10 billion years". */
export function unitWords(unit: string): string {
  switch (unit) {
    case 'fraction': return '';
    case 'stars per year': return ' stars a year';
    case 'planets per star': return ' planets per star';
    case 'years': return ' years';
    default: return ` ${unit}`;
  }
}

/** The symbol as the equation writes it, with the small letter below the line: R* becomes
    R<sub>*</sub>, fp becomes f<sub>p</sub>; L stays L. For set:html. */
export function symbolHtml(symbol: string): string {
  if (symbol.length < 2) return symbol;
  return `${symbol[0]}<sub>${symbol.slice(1)}</sub>`;
}

// ---------------------------------------------------------------- numbers and dates

const WORDS: [number, string][] = [[1e12, 'trillion'], [1e9, 'billion'], [1e6, 'million'], [1e3, 'thousand']];

/** A number in plain words: 0.62, 1, 2.5, "10 billion", "1 in a million". Never scientific
    notation. Beyond a thousand trillion either way, the power of ten written out in words, as the
    project's own documents do ("one in ten to the 22"). */
export function plainNumber(x: number): string {
  if (!Number.isFinite(x)) return 'no number';
  if (x === 0) return '0';
  const neg = x < 0 ? '−' : '';
  const v = Math.abs(x);
  if (v >= 1e15 || v < 1e-15) {
    const inv = v < 1 ? 1 / v : v;
    const exp = Math.floor(Math.log10(inv) + 1e-9);
    const mant = inv / 10 ** exp;
    const about = mant > 1.05 ? 'about ' : '';
    return v < 1 ? `${about}1 in 10 to the ${exp}` : `${neg}${about}10 to the ${exp}`;
  }
  if (v >= 1e4) {
    if (v >= 1e15) return `${neg}a 1 followed by ${Math.round(Math.log10(v))} zeros`;
    for (const [unit, word] of WORDS) {
      if (v >= unit) {
        const q = v / unit;
        return `${neg}${trim(q, q >= 100 ? 0 : q >= 10 ? 1 : 2)} ${word}`;
      }
    }
  }
  if (v < 1e-4) {
    const inv = 1 / v;
    // Beyond the words we have (the pessimistic extreme is around 1 in 10 to the 65th):
    // say how many zeros, which a reader can hold, rather than print a float.
    if (inv >= 1e15) return `${neg}1 in a 1 followed by ${Math.round(Math.log10(inv))} zeros`;
    for (const [unit, word] of WORDS) {
      if (inv >= unit) {
        const q = inv / unit;
        return `${neg}1 in ${q >= 1.05 ? trim(q, q >= 10 ? 0 : 1) + ' ' : 'a '}${word}`;
      }
    }
    return `${neg}1 in ${trim(inv, 0)}`;
  }
  if (v >= 100) return neg + trim(v, 0);
  if (v >= 1) return neg + trim(v, 2);
  if (v >= 0.01) return neg + trim(v, 3);
  return neg + trim(v, 5);
}

function trim(v: number, places: number): string {
  const t = v.toFixed(places);
  return t.includes('.') ? t.replace(/\.?0+$/, '') : t;
}

/** "0.1 to 1", "100 to 10 billion years"; "from 1 in 10 to the 22 up to 1" when an end is a power of ten in words. */
export function rangeWords(low: number, high: number, unit: string): string {
  const a = plainNumber(low), b = plainNumber(high);
  if (a.includes(' to the ') || b.includes(' to the ')) return `from ${a} up to ${b}${unitWords(unit)}`;
  return `${a} to ${b}${unitWords(unit)}`;
}

/** The middle estimate of detectable civilisations, said so that a number below one reads
    plainly: "about one detectable civilisation per 450 million galaxies like ours". */
export function medianWords(n: number): string {
  if (n >= 1.5) return `about ${plainNumber(n)} detectable civilisations in our galaxy`;
  if (n >= 0.5) return 'about one detectable civilisation in our galaxy';
  // A count of galaxies is a whole number to a reader: 64, not 63.57.
  const per = 1 / n;
  const perWords = per < 1000 ? String(Math.round(per)) : plainNumber(per).replace(/^about /, '');
  return `about one detectable civilisation per ${perWords} galaxies like ours`;
}

/** An estimate's number: a single value or a range, in the factor's unit. */
export function estimateWords(e: Estimate, unit: string): string {
  if (e.value !== undefined) return `${plainNumber(e.value)}${unitWords(unit)}`;
  if (e.low !== undefined && e.high !== undefined) return rangeWords(e.low, e.high, unit);
  return 'no number';
}

/** A chance between 0 and 1 as a percentage with sensible precision. */
export function percent(p: number): string {
  const v = p * 100;
  if (v >= 99.95) return '99.9%';
  if (v < 0.1) return 'under 0.1%';
  return (v < 10 ? v.toFixed(1) : Math.round(v).toString()) + '%';
}

/** "16 October 2026" for the footer and the strip; the design standard writes dates out there. */
export function longDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  });
}

/** A date the world supplied, as text: "1961", "2012-01" or "2012-01-12", written out as far as it goes. */
export function worldDate(text: string): string {
  const parts = text.split('-').map(Number);
  if (parts.length === 1) return text;
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  if (parts.length === 2) return `${months[parts[1] - 1]} ${parts[0]}`;
  return `${parts[2]} ${months[parts[1] - 1]} ${parts[0]}`;
}

/** The year alone, from a world date. */
export function yearOf(text: string): string {
  return text.slice(0, 4);
}

export function countWord(n: number): string {
  return ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'][n] ?? String(n);
}

export function plural(n: number, one: string, many: string): string {
  return `${n} ${n === 1 ? one : many}`;
}

/** A multi-line record field, split into paragraphs on blank lines. */
export function paragraphs(text: string): string[] {
  return text.split(/\n\s*\n/).map((p) => p.replace(/\s*\n\s*/g, ' ').trim()).filter(Boolean);
}

// ---------------------------------------------------------------- links

/** The record's file in the public repository. */
export function recordUrl(file: string): string {
  return `${REPO}/blob/main/${file}`;
}

/** A new issue in the repository, from one of the three templates, with a title already filled in.
    Copied from The Belt Equation's `issueUrl` in site/src/lib/tree.ts, with the template added. */
export function issueUrl(template: string, title: string, body = ''): string {
  const q = new URLSearchParams({ template, title });
  if (body) q.set('body', body);
  return `${REPO}/issues/new?${q.toString()}`;
}

/** Escape HTML, then turn `code` spans and [text](url) links into markup.
    Copied from The Belt Equation's `inline` in site/src/lib/tree.ts. */
export function inline(text: string): string {
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return escaped
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" rel="noopener">$1</a>');
}

/** The host of a link, for a short label: "arxiv.org". */
export function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

/** The footer's "from ..." clause: how much is behind the page, in the reader's terms. */
export function builtFrom(): string {
  const c = records.counts;
  return `${c.factors} of the equation's ${c.factors_expected} pieces, ${plural(c.explanations, 'explanation', 'explanations')}, ${plural(c.library, 'library entry', 'library entries')} and ${plural(c.publications, 'publication', 'publications')}`;
}
