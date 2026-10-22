// Typed access to the weekly readings the export script writes into records.json
// (scripts/export.py, export_readings; docs/weekly-reading.md), plus the wording the pages
// share. Copied from The Belt Equation's site/src/lib/scans.ts and adapted on 2026-10-16: a
// reading here is one week's reading of every factor and explanation against the news, with four
// verdicts rather than the Belt's five (nothing here "resolves"; a factor's range moves).
import { records, type PubBrief } from './records';

export type Verdict = 'quiet' | 'noted' | 'moved' | 'flagged';

export interface ReadingItem {
  record: string;
  kind: 'factor' | 'explanation';
  name: string;
  path: string;
  order: number | null;      // a factor's place in the equation
  symbol: string | null;
  family: string | null;     // an explanation's family key
  family_name: string;       // the family's plain name, or "The seven pieces" for a factor
  verdict: Verdict;
  queries: string[];
  reused: string[];
  found: string;
  sources: string[];
  publications: PubBrief[];
  for_john: string | null;
  /** On a flagged item: what took it off my list and when; null while it is still waiting. */
  picked_up: { on: string; how: string } | null;
}

export interface Reading {
  id: string;
  date: string;
  ran_at: string;
  run_by: 'scheduled' | 'hand';
  window: string;
  records_read: number;
  searches: number;
  commit_before: string;
  /** Added 2026-10-18: how many pages the run opened beyond its search tool ("none" and why), and
      what it could not see; both empty on the two readings that came before the rule. */
  pages_opened: string;
  limits: string;
  notes: string;
  file: string;
  path: string;
  counts: Record<Verdict, number>;
  moved: { record: string; name: string; path: string }[];
  open_flags: number;
  items: ReadingItem[];
}

/** One record's own reading, as its page shows it: the reading it came from, flattened in. */
export interface RecordReading {
  date: string;
  run_by: Reading['run_by'];
  file: string;
  path: string;
  verdict: Verdict;
  found: string;
  sources: string[];
  publications: PubBrief[];
  for_john: string | null;
  picked_up: { on: string; how: string } | null;
}

export type WaitingItem = ReadingItem & { reading_date: string; reading_path: string; run_by: Reading['run_by'] };

export const readings: Reading[] = records.readings;
export const latestReading: Reading | null = readings[0] ?? null;
export const waitingOnMe: WaitingItem[] = records.readings_waiting;
export const readingCounts = records.readings_counts;

/** Every reading of one record, newest first. */
export const readingsFor = (id: string): RecordReading[] => records.readings_by_record[id] ?? [];

export const VERDICT_ORDER: Verdict[] = ['moved', 'flagged', 'noted', 'quiet'];

/** The badge on a card: what the reading decided, in two or three words. */
export const verdictLabel: Record<Verdict, string> = {
  quiet: 'Nothing new',
  noted: 'Logged, no change',
  moved: 'A range moved',
  flagged: 'Waiting on me',
};

/** The same four, in a sentence, for the key on the reading page and the record pages. */
export const verdictMeaning: Record<Verdict, string> = {
  quiet: 'Nothing published in the window bore on what this record says would move it.',
  noted: 'Something bore on the test and was logged in the story so far; no range moved.',
  moved: 'The evidence met the piece’s test and one end of its range moved, within the limit a reading may move it.',
  flagged: 'Something the reading is not allowed to do on its own, written up for me to rule on.',
};

export const runByLabel: Record<Reading['run_by'], string> = {
  scheduled: 'the scheduled weekly task',
  hand: 'a session started by hand',
};

/** Counts read better as words at the low end: "none", "one", then digits. */
export function plainCount(n: number): string {
  return n === 0 ? 'none' : n === 1 ? 'one' : String(n);
}

/** The moment the reading finished, in my own time zone (the record keeps universal time, and
    the reading's date is already a Pacific date). Formatted at build time. */
export function ranAtLabel(reading: Reading): string {
  const d = new Date(reading.ran_at);
  if (Number.isNaN(d.getTime())) return reading.ran_at;
  const time = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', hour: 'numeric', minute: '2-digit' }).format(d);
  const day = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
  return `${time} Pacific, ${day}`;
}

/** "39 records read, nothing moved, one left for me": the line the home page strip and the
    reading page both use, so the site says the same thing about a reading in both places. */
export function readingSummary(reading: Reading): string {
  const read = `${reading.records_read} record${reading.records_read === 1 ? '' : 's'} read`;
  const parts: string[] = [];
  if (reading.counts.moved) parts.push(`${plainCount(reading.counts.moved)} range${reading.counts.moved === 1 ? '' : 's'} moved`);
  if (reading.counts.flagged) {
    parts.push(reading.open_flags
      ? `${plainCount(reading.open_flags)} left for me`
      : `${plainCount(reading.counts.flagged)} ruled on since`);
  }
  if (parts.length === 0) return `${read}, nothing moved`;
  const joined = parts.length === 1 ? parts[0] : parts.slice(0, -1).join(', ') + ' and ' + parts[parts.length - 1];
  return reading.counts.moved ? `${read}, ${joined}` : `${read}, nothing moved, ${joined}`;
}

/** The reading page's one-line form of a note (the one-column layout John approved 2026-10-21,
 *  copied from Outrunning Ageing's lib/records.ts): its first sentence, and the rest for when the
 *  entry is opened. Nothing is rewritten; the split is at the first full stop, question or
 *  exclamation mark followed by a space and a capital, a digit or an opening bracket, skipping
 *  initials ("U.S.") and the common abbreviations. A note with no such break is all line. */
const ABBREVIATIONS = /(?:^|\s)(?:e\.g|i\.e|etc|vs|cf|al|Dr|Mr|Mrs|Ms|Prof|St|No|Fig|approx|Inc|Ltd|Co|Jr|Sr)\.$/;
export function splitFirstSentence(note: string): { line: string; rest: string } {
  const text = note.replace(/\s+/g, ' ').trim();
  const breakAt = /[.!?]["'’”)]?\s+(?=[A-Z0-9(“"‘'])/g;
  let m: RegExpExecArray | null;
  while ((m = breakAt.exec(text)) !== null) {
    const upTo = text.slice(0, m.index + 1);
    if (ABBREVIATIONS.test(upTo) || /(?:^|[\s.])[A-Z]\.$/.test(upTo)) continue;
    const end = m.index + m[0].trimEnd().length;
    return { line: text.slice(0, end), rest: text.slice(end).trim() };
  }
  return { line: text, rest: '' };
}

/** Which entries open by default: every verdict but "Nothing new", so a range that moved,
 *  anything logged, and anything left for me, whether or not it has since been ruled on. */
export const opensByDefault = (item: ReadingItem) => item.verdict !== 'quiet';

/** The order the counts line reads in: the common verdict first, the rare ones after. */
const COUNT_ORDER: Verdict[] = ['quiet', 'noted', 'moved', 'flagged'];

/** "39 records read · 30 logged, no change · 1 waiting on me, since ruled on": the line under
 *  the reading page's heading, in the verdicts' own words. */
export function readingCountLine(reading: Reading): string {
  const parts = [`${reading.records_read} record${reading.records_read === 1 ? '' : 's'} read`];
  for (const v of COUNT_ORDER) {
    const n = reading.counts[v];
    if (n === 0) continue;
    let part = `${n} ${verdictLabel[v].charAt(0).toLowerCase()}${verdictLabel[v].slice(1)}`;
    if (v === 'flagged') {
      const ruled = n - reading.open_flags;
      if (ruled > 0) part += reading.open_flags === 0 ? (n === 1 ? ', since ruled on' : `, all ${n} since ruled on`) : `, ${ruled} since ruled on`;
    }
    parts.push(part);
  }
  return parts.join(' · ');
}
