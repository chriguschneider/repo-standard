// Pure metadata guards: versions in sync, changelog section present, HACS
// filename matching the build output. Node only, no browser.
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
const pkg = JSON.parse(read('package.json'));

describe('metadata', () => {
  it('keeps package.json and src/const.ts versions in sync', () => {
    const match = read('src/const.ts').match(/CARD_VERSION = '([^']+)'/);
    expect(match, 'CARD_VERSION not found in src/const.ts').not.toBeNull();
    expect(match[1]).toBe(pkg.version);
  });

  it('has a changelog section for the current version and [Unreleased]', () => {
    const changelog = read('CHANGELOG.md');
    expect(changelog).toMatch(/^## \[Unreleased\]/m);
    expect(changelog).toContain(`## [v${pkg.version}]`);
    expect(changelog).toContain(`[v${pkg.version}]:`);
  });

  it('points HACS at the file rollup builds and release.yml attaches', () => {
    const hacs = JSON.parse(read('hacs.json'));
    expect(hacs.render_readme).toBe(true);
    expect(read('rollup.config.mjs')).toContain(`dist/${hacs.filename}`);
    expect(read('.github/workflows/release.yml')).toContain(`dist/${hacs.filename}`);
  });
});
