// The typed view of the JSON the export script writes (scripts/export.py). Every page reads
// from here; nothing in the browser touches the TOML records.
import data from '../data/records.json';

export interface Counts {
  factors: number;
  factors_expected: number;
  explanations: number;
  library: number;
  publications: number;
  verify: number;
}

export interface FactorSummary {
  id: string;
  order: number;
  symbol: string;
  name: string;
  unit: string;
  description: string;
  range: { low: number; high: number; shape: string; status: string; set_on: string } | null;
  estimates: number;
}

export interface Records {
  exported_on: string;   // year-month-day
  commit: string;        // short code of the source version, or ""
  counts: Counts;
  headline: { available: false; reason: string };
  factors: FactorSummary[];
  families: { key: string; name: string; count: number }[];
}

export const records = data as unknown as Records;

// "16 October 2026" for the footer; the design standard writes dates out there.
export function longDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  });
}
