// Pure metadata guards: one version source, changelog section present, HACS
// filename matching the build output. Node only, no browser.
import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const path = (rel) => new URL(`../${rel}`, import.meta.url);
const read = (rel) => readFileSync(path(rel), 'utf8');
const pkg = JSON.parse(read('package.json'));
const hacs = JSON.parse(read('hacs.json'));
const bundle = `dist/${hacs.filename}`;

describe('metadata', () => {
  it('writes the version only in package.json', () => {
    expect(pkg.version).toMatch(/^\d+\.\d+\.\d+(-[\w.]+)?$/);
    // The build injects it (rollup.config.mjs); a literal here would drift.
    expect(read('src/const.ts')).toContain("CARD_VERSION = '__CARD_VERSION__'");
  });

  it.skipIf(!existsSync(path('package-lock.json')))('has package-lock.json on the same version', () => {
    const lock = JSON.parse(read('package-lock.json'));
    expect(lock.version).toBe(pkg.version);
    expect(lock.packages?.['']?.version).toBe(pkg.version);
  });

  // Skipped only before the first build; afterwards dist/ is committed.
  it.skipIf(!existsSync(path(bundle)))('ships a bundle built for this version', () => {
    const code = read(bundle);
    // The console banner (`v<version>`) is where the injected version lands.
    expect(code, 'run `npm run build` after bumping the version').toContain(`v${pkg.version}`);
    expect(code).not.toContain('__CARD_VERSION__');
  });

  it('has a changelog section for the current version and [Unreleased]', () => {
    const changelog = read('CHANGELOG.md');
    expect(changelog).toMatch(/^## \[Unreleased\]/m);
    expect(changelog).toContain(`## [v${pkg.version}]`);
    expect(changelog).toContain(`[v${pkg.version}]:`);
  });

  it('points HACS at the file rollup builds and release.yml attaches', () => {
    expect(hacs.render_readme).toBe(true);
    expect(read('rollup.config.mjs')).toContain(`dist/${hacs.filename}`);
    expect(read('.github/workflows/release.yml')).toContain(`dist/${hacs.filename}`);
  });

  it('runs in UTC (vitest.config.js), so dates format the same everywhere', () => {
    expect(new Date(0).getTimezoneOffset()).toBe(0);
  });
});
