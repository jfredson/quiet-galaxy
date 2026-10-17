// The sitemap, built from the same export every page reads, so it lists exactly the pages that
// exist: the fixed pages, one page per piece of the equation whose record is written, and one
// page per explanation at its permanent address. The not-found page is left out (it carries a
// noindex). Added 2026-10-17, when the family's lessons review found robots.txt promising a
// sitemap the site did not serve; the shape is the parent site's sitemap.xml.ts
// (sentient-horizons/site/src/pages/sitemap.xml.ts), without the dates, since a record page has
// no single publication date to give.
import type { APIRoute } from 'astro';
import { records } from '../lib/records';

const FIXED = ['/', '/equation/', '/explanations/', '/library/', '/story/', '/reading/', '/method/', '/disagree/'];

export const GET: APIRoute = ({ site }) => {
  const paths = [
    ...FIXED,
    ...records.factors.filter((f) => f.exists).map((f) => f.path),
    ...records.explanations.map((e) => e.path),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${paths.map((p) => `<url><loc>${new URL(p, site).href}</loc></url>`).join('\n')}
</urlset>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
