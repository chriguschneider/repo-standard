#!/usr/bin/env node
/**
 * Fails the build when dist/ contains something the CSP in public/_headers
 * would block in the browser: an inline <script> or <style>, a style
 * attribute or an inline event handler. Without this check the page looks
 * fine in `astro dev` (no CSP there) and breaks only in production.
 *
 * JSON data blocks (`type="application/ld+json"`, `application/json`) are
 * not executed and stay allowed.
 *
 *   node scripts/check-csp.mjs [dist]
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const dist = join(root, process.argv[2] ?? 'dist');

if (!existsSync(dist)) {
  console.error(`check-csp: ${relative(root, dist) || dist} does not exist; run \`astro build\` first.`);
  process.exit(1);
}

const walk = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory() ? walk(join(dir, entry.name)) : [join(dir, entry.name)],
  );

const RULES = [
  {
    what: 'inline <script>',
    find: /<script\b([^>]*)>([\s\S]*?)<\/script>/gi,
    bad: (m) => !/\ssrc=/i.test(m[1]) && !/type="application\/(ld\+)?json"/i.test(m[1]) && m[2].trim() !== '',
  },
  { what: 'inline <style>', find: /<style\b[^>]*>/gi, bad: () => true },
  { what: 'style attribute', find: /<[a-z][^>]*\sstyle="/gi, bad: () => true },
  { what: 'inline event handler', find: /<[a-z][^>]*\son[a-z]+="/gi, bad: () => true },
];

const errors = [];
const pages = walk(dist).filter((file) => file.endsWith('.html'));
for (const page of pages) {
  const html = readFileSync(page, 'utf8');
  for (const rule of RULES) {
    for (const m of html.matchAll(rule.find)) {
      if (rule.bad(m)) errors.push(`${relative(root, page)}: ${rule.what}: ${m[0].slice(0, 80)}`);
    }
  }
}

if (errors.length > 0) {
  console.error(`check-csp: ${errors.length} thing(s) the Content-Security-Policy would block:`);
  for (const error of errors) console.error(`  - ${error}`);
  console.error('Move it into a file (src/styles/, a <script> Astro bundles), or add a CSP exception with a comment in public/_headers.');
  process.exit(1);
}
console.log(`check-csp: ${pages.length} pages, nothing inline.`);
