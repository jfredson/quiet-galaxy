// The sitemap, built from the same export every page reads, so it lists exactly the pages that
// exist: the fixed pages, one page per piece of the equation whose record is written, one page
// per explanation at its permanent address, and one page per news post. The not-found page is
// left out (it carries a noindex), and so are /method/ and /story/, which have sent readers on to
// /about/ since 2026-10-21. Added 2026-10-17, when the family's lessons review found robots.txt
// promising a sitemap the site did not serve; the shape is the parent site's sitemap.xml.ts
// (sentient-horizons/site/src/pages/sitemap.xml.ts).
//
// A date in <lastmod> tells a search engine when the page itself last changed, so it is given only
// where the record knows that date: a news post's date. A record page has no single date of last
// change, so it carries none. The news index and the news posts were added on 2026-11-14,
// matching The Belt Equation's sitemap (belt-equation/site/src/pages/sitemap.xml.ts).
import type { APIRoute } from 'astro';
import { records } from '../lib/records';
import { allPosts, postPath } from '../lib/news';

const FIXED = ['/', '/equation/', '/explanations/', '/library/', '/news/', '/about/', '/reading/', '/disagree/'];

export const GET: APIRoute = async ({ site }) => {
  const posts = await allPosts();
  const urls: { loc: string; lastmod?: string }[] = [
    ...FIXED.map((p) => ({ loc: p })),
    ...records.factors.filter((f) => f.exists).map((f) => ({ loc: f.path })),
    ...records.explanations.map((e) => ({ loc: e.path })),
    ...posts.map((p) => ({ loc: postPath(p), lastmod: p.data.date })),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map((u) => `<url><loc>${new URL(u.loc, site).href}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}</url>`)
  .join('\n')}
</urlset>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
