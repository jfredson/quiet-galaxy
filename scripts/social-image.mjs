// Makes the social preview image, site/public/social-preview.png (1200 by 630): what link previews
// on iMessage, Slack, X, Reddit and the rest show when The Quiet Galaxy is shared. Drawn in the "Hush" skin's own
// tokens (site/src/styles/skin.css), carrying the site's name, the question from its home page and its
// address; no stock picture. The proposed rule is design/tracker-pattern.md in sentient-horizons.
//
// Run from the repository root after changing the skin or the home-page question:
//   node scripts/social-image.mjs
// It needs `sharp`, which Astro already installs in site/node_modules (run `npm ci` in site/ first).
// The picture is the same every time it is made; the only inputs are the values written below.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(new URL('../site/', import.meta.url));
const sharp = require('sharp');

const W = 1200;
const H = 630;
const SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif";
const MONO = "Menlo, 'SF Mono', Consolas, monospace";

// A small deterministic generator, so the picture is the same every time it is made.
function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function textBlock({ lines, x, y, size, lead, fill, weight = 600, spacing = -1 }) {
  return lines
    .map(
      (t, i) =>
        `<text x="${x}" y="${y + i * lead}" font-family="${SANS}" font-size="${size}" font-weight="${weight}" letter-spacing="${spacing}" fill="${fill}">${t}</text>`,
    )
    .join('\n');
}

function nameLine({ name, x, y, fill }) {
  return `<text x="${x}" y="${y}" font-family="${SANS}" font-size="28" font-weight="600" letter-spacing="5" fill="${fill}">${name.toUpperCase()}</text>`;
}

function domainLine({ domain, x, y, fill }) {
  return `<text x="${x}" y="${y}" font-family="${MONO}" font-size="26" fill="${fill}">${domain}</text>`;
}

function wrap(body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">\n${body}\n</svg>\n`;
}

function buildQuiet() {
  const bg = '#05070a', text = '#e8ecf1', muted = '#7d8794', accent = '#a6d4ea';
  // The ripples: hairline rings from a point just off the top right corner, each fainter than the last.
  const cx = W * 0.92, cy = -H * 0.06;
  const far = Math.max(Math.hypot(cx, H - cy), Math.hypot(W - cx, H - cy));
  let rings = '';
  const s = 1.25;
  for (let k = 0; ; k++) {
    const rad = (46 + 94 * k) * s;
    const f = rad / far;
    if (f >= 0.78) break;
    const mask = f <= 0.4 ? 1 - 0.3 * (f / 0.4) : 0.7 * (1 - (f - 0.4) / 0.38);
    rings += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${rad.toFixed(1)}" fill="none" stroke="${accent}" stroke-opacity="${(0.34 * mask).toFixed(3)}" stroke-width="1.8"/>`;
  }
  // A dozen still stars, no glow.
  const r = rng(20261016);
  let stars = '';
  for (let i = 0; i < 12; i++) {
    stars += `<circle cx="${(r() * W).toFixed(1)}" cy="${(r() * H * 0.9).toFixed(1)}" r="${(1 + r() * 1.1).toFixed(2)}" fill="${text}" fill-opacity="${(0.4 + r() * 0.5).toFixed(2)}"/>`;
  }
  return wrap(`<rect width="${W}" height="${H}" fill="${bg}"/>
${rings}
${stars}
${nameLine({ name: 'The Quiet Galaxy', x: 72, y: 96, fill: accent })}
${textBlock({ lines: ['Where is everybody?'], x: 72, y: 330, size: 112, lead: 120, fill: text, spacing: -2 })}
<text x="72" y="408" font-family="${SANS}" font-size="30" fill="${muted}">A public explainer and tracker of the Fermi Paradox</text>
${domainLine({ domain: 'thequietgalaxy.com', x: 72, y: 560, fill: muted })}`);
}


const out = fileURLToPath(new URL('../site/public/social-preview.png', import.meta.url));
// ---- the news posts' cards (tracker pattern, rule 4.15; John 2026-10-18), copied from Outrunning Ageing's ----
import { readdirSync, readFileSync, mkdirSync } from 'node:fs';
import { basename, join } from 'node:path';
const KIND_LABEL = { 'start-here': 'start here', 'rung-reached': 'a rung reached', 'estimate-revised': 'a range revised', 'flagged-item-ruled': 'a flagged item ruled', 'claim': 'a claim settled', 'headline-moved': 'the headline moved', 'method-changed': 'the method changed' };
function fm(text) { const m = text.match(/^---\n([\s\S]*?)\n---/); const d = {}; if (!m) return d; for (const line of m[1].split('\n')) { const k = line.match(/^([a-z_]+):\s*(.*)$/); if (k) d[k[1]] = k[2].trim().replace(/^"|"$/g, ''); } return d; }
function longDate(iso) { const d = new Date(iso + 'T12:00:00Z'); return `${d.getUTCDate()} ${d.toLocaleString('en-GB', { month: 'long', timeZone: 'UTC' })} ${d.getUTCFullYear()}`; }
function wrapWords(text, max) { const lines = []; let cur = ''; for (const w of text.split(/\s+/)) { const t = (cur + ' ' + w).trim(); if (t.length <= max) cur = t; else { lines.push(cur); cur = w; } } if (cur) lines.push(cur); return lines; }
function buildPostCard(post) {
  const bg = '#05070a', text = '#e8ecf1', soft = '#b9c2cc', muted = '#7d8794', accent = '#a6d4ea';
  let lines = wrapWords(post.title, 30); let size = 56, lead = 68;
  if (lines.length > 3) { lines = wrapWords(post.title, 38); size = 46; lead = 56; }
  lines = lines.slice(0, 4);
  const kicker = `NEWS · ${longDate(post.date).toUpperCase()} · ${(KIND_LABEL[post.kind] || post.kind).toUpperCase()}`;
  const numbers = wrapWords(post.before && post.after ? `${post.before} to ${post.after}` : (post.after || ''), 74).slice(0, 2);
  const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return wrap(`<rect width="${W}" height="${H}" fill="${bg}"/>
${nameLine({ name: 'The Quiet Galaxy', x: 72, y: 116, fill: accent })}
<text x="${W - 72}" y="116" text-anchor="end" font-family="${MONO}" font-size="26" fill="${muted}">thequietgalaxy.com</text>
${textBlock({ lines: lines.map(esc), x: 72, y: 232, size, lead, fill: text, spacing: -1 })}
<text x="72" y="${H - 132}" font-family="${SANS}" font-size="20" font-weight="600" letter-spacing="2" fill="${muted}">${esc(kicker)}</text>
${numbers.map((ln, i) => `<text x="72" y="${H - 96 + i * 32}" font-family="${SANS}" font-size="24" fill="${soft}">${esc(ln)}</text>`).join('')}`);
}
const argv = process.argv.slice(2);
if (argv[0] === '--posts') {
  const dir = fileURLToPath(new URL('../site/src/content/news/', import.meta.url));
  const outDir = fileURLToPath(new URL('../site/public/news/', import.meta.url)); mkdirSync(outDir, { recursive: true });
  const files = argv.length > 1 ? argv.slice(1).map((f) => basename(f)) : readdirSync(dir).filter((f) => f.endsWith('.md'));
  for (const f of files) {
    const post = fm(readFileSync(join(dir, f), 'utf8')); const slug = f.replace(/\.md$/, '');
    await sharp(Buffer.from(buildPostCard(post))).png({ compressionLevel: 9 }).toFile(join(outDir, `${slug}-card.png`));
    console.log('wrote', join(outDir, `${slug}-card.png`));
  }
} else {
  await sharp(Buffer.from(buildQuiet())).png({ compressionLevel: 9 }).toFile(out);
  console.log('wrote', out);
}
