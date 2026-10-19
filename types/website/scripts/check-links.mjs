#!/usr/bin/env node
/**
 * Internal link check over the built site in dist/. No network, no
 * dependencies; runs as part of `npm run build`, so Cloudflare Pages never
 * deploys a build with a broken internal link.
 *
 * For every `href` and `src` in every HTML file:
 *   - external links (another origin, mailto:, tel:) are skipped;
 *   - links to the site itself, relative or absolute on SITE_URL from
 *     src/config.ts (canonical, hreflang), must resolve to a file in dist/
 *     the way Cloudflare Pages serves it (`/a/` -> a/index.html,
 *     `/a` -> a.html or a/index.html);
 *   - a `#fragment` on an HTML target must match an id or name there.
 *
 *   node scripts/check-links.mjs [dist]
 */

import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const dist = join(root, process.argv[2] ?? 'dist');

// One source for the site address: src/config.ts. Read as text, since this
// script runs under plain node without a TypeScript loader.
const config = readFileSync(join(root, 'src', 'config.ts'), 'utf8');
const siteMatch = config.match(/export const SITE_URL = '([^']+)'/);
if (!siteMatch) {
  console.error("check-links: SITE_URL not found in src/config.ts (expected `export const SITE_URL = '...'`).");
  process.exit(1);
}
const site = new URL(siteMatch[1]);

if (!existsSync(dist)) {
  console.error(`check-links: ${relative(root, dist) || dist} does not exist; run \`astro build\` first.`);
  process.exit(1);
}

const walk = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory() ? walk(join(dir, entry.name)) : [join(dir, entry.name)],
  );

const pages = walk(dist).filter((file) => file.endsWith('.html'));

/** The URL a file in dist/ is served at. */
const urlOf = (file) => {
  const path = relative(dist, file).split(sep).join('/');
  const served = path === 'index.html' ? '' : path.endsWith('/index.html') ? path.slice(0, -'index.html'.length) : path;
  return new URL(served, site);
};

/** The file in dist/ that serves a path, or null. */
const fileFor = (pathname) => {
  const path = join(dist, ...decodeURIComponent(pathname).split('/').filter(Boolean));
  const candidates = pathname.endsWith('/') ? [join(path, 'index.html')] : [path, `${path}.html`, join(path, 'index.html')];
  return candidates.find((candidate) => existsSync(candidate) && statSync(candidate).isFile()) ?? null;
};

const anchorCache = new Map();
const anchorsOf = (file) => {
  if (!anchorCache.has(file)) {
    const html = readFileSync(file, 'utf8');
    anchorCache.set(file, new Set([...html.matchAll(/\s(?:id|name)="([^"]+)"/g)].map((m) => m[1])));
  }
  return anchorCache.get(file);
};

const errors = [];
let checked = 0;

for (const page of pages) {
  const html = readFileSync(page, 'utf8');
  const base = urlOf(page);
  for (const match of html.matchAll(/\s(href|src)="([^"]*)"/g)) {
    const raw = match[2].replaceAll('&amp;', '&');
    if (raw === '' || /^(mailto|tel|data):/i.test(raw)) continue;
    if (/^javascript:/i.test(raw)) {
      errors.push(`${relative(root, page)}: javascript: link (blocked by the CSP) -> ${raw}`);
      continue;
    }
    let target;
    try {
      target = new URL(raw, base);
    } catch {
      errors.push(`${relative(root, page)}: unparsable ${match[1]} -> ${raw}`);
      continue;
    }
    if (target.origin !== site.origin) continue;

    checked += 1;
    const file = fileFor(target.pathname);
    if (!file) {
      errors.push(`${relative(root, page)}: ${match[1]} -> ${raw} (no file for ${target.pathname})`);
      continue;
    }
    const fragment = decodeURIComponent(target.hash.slice(1));
    if (fragment && file.endsWith('.html') && !anchorsOf(file).has(fragment)) {
      errors.push(`${relative(root, page)}: ${match[1]} -> ${raw} (no id "${fragment}" in ${relative(dist, file)})`);
    }
  }
}

if (errors.length > 0) {
  console.error(`check-links: ${errors.length} broken internal link(s):`);
  for (const error of errors) console.error(`  - ${error}`);
  process.exit(1);
}
console.log(`check-links: ${checked} internal links in ${pages.length} pages resolve.`);
