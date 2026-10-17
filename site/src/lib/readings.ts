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
