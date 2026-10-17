import { defineConfig } from 'astro/config';

// Same generator and settings as the sister sites (The Belt Equation, Sentient Horizons):
// a fully static build in dist/, served from Cloudflare Workers static assets.
export default defineConfig({
  site: 'https://thequietgalaxy.com',
  trailingSlash: 'always',
});
