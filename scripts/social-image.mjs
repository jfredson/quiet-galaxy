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
await sharp(Buffer.from(buildQuiet())).png({ compressionLevel: 9 }).toFile(out);
console.log('wrote', out);
