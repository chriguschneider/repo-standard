#!/usr/bin/env node
/**
 * Is this commit live? Polls `<url>/build.json` (src/pages/build.json.ts)
 * until it reports the expected commit, or gives up.
 *
 *   npm run deploy:status                          # production, expects origin/@@PRODUCTION_BRANCH@@
 *   npm run deploy:status -- --preview             # preview, expects origin/@@BRANCH@@
 *   npm run deploy:status -- <url> --commit <sha> --wait 300
 *
 * Why: a push is the deploy here, and when a Cloudflare Pages build fails,
 * Pages silently keeps serving the previous deployment. From outside that
 * looks like "still building". Step "Verify live" of the promotion
 * (AGENTS.md, "Release procedure") runs this.
 *
 * Reads the network, so it is a manual step and never runs in CI.
 * Needs only node and git, no Cloudflare token.
 */

import { execFileSync } from 'node:child_process';

const PRODUCTION_URL = '@@SITE_URL@@';
const PREVIEW_URL = '@@PREVIEW_URL@@';

const args = process.argv.slice(2);
const option = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args.splice(i, 2)[1] : fallback;
};
const preview = args.includes('--preview');
if (preview) args.splice(args.indexOf('--preview'), 1);

const wait = Number(option('--wait', '300'));
const git = (...cmd) => execFileSync('git', cmd, { encoding: 'utf8' }).trim();
const commit = option('--commit', null) ?? git('rev-parse', `origin/${preview ? '@@BRANCH@@' : '@@PRODUCTION_BRANCH@@'}`);
const url = new URL('build.json', args[0] ?? (preview ? PREVIEW_URL : PRODUCTION_URL));

console.log(`Waiting up to ${wait}s for ${url.origin} to serve ${commit.slice(0, 7)} ...`);
const deadline = Date.now() + wait * 1000;
let seen = 'nothing';

while (true) {
  try {
    url.searchParams.set('t', String(Date.now())); // past any cache
    const response = await fetch(url, { cache: 'no-store' });
    if (response.ok) {
      const build = await response.json();
      seen = `${String(build.commit).slice(0, 7)} (branch ${build.branch})`;
      if (build.commit === commit) {
        console.log(`Live: ${url.origin} serves ${seen}.`);
        process.exit(0);
      }
    } else {
      seen = `HTTP ${response.status}`;
    }
  } catch (error) {
    seen = `error: ${error.message}`;
  }
  if (Date.now() > deadline) break;
  await new Promise((resolve) => setTimeout(resolve, 10_000));
}

console.error(`Not live after ${wait}s: ${url.origin} serves ${seen}, expected ${commit.slice(0, 7)}.`);
console.error('Check the build log in the Cloudflare Pages dashboard (Deployments); a failed build keeps the previous one online.');
process.exit(1);
