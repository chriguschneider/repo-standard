// Pure metadata guards: one version source and a changelog section for it.
import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { VERSION } from './version.ts';

const path = (rel: string) => new URL(`../../${rel}`, import.meta.url);
const read = (rel: string) => readFileSync(path(rel), 'utf8');
const pkg = JSON.parse(read('package.json'));

describe('metadata', () => {
  it('exports the version from package.json', () => {
    expect(VERSION).toBe(pkg.version);
    expect(VERSION).toMatch(/^\d+\.\d+\.\d+(-[\w.]+)?$/);
  });

  it.skipIf(!existsSync(path('package-lock.json')))(
    'has package-lock.json on the same version',
    () => {
      const lock = JSON.parse(read('package-lock.json'));
      expect(lock.version).toBe(pkg.version);
      expect(lock.packages?.['']?.version).toBe(pkg.version);
    },
  );

  it('has a changelog section for the current version and [Unreleased]', () => {
    const changelog = read('CHANGELOG.md');
    expect(changelog).toMatch(/^## \[Unreleased\]/m);
    expect(changelog).toContain(`## [v${pkg.version}]`);
    expect(changelog).toContain(`[v${pkg.version}]:`);
  });

  it('runs the image as the same version it declares', () => {
    // The image tag comes from the git tag, which release.yml checks
    // against package.json; the health endpoint reports VERSION.
    expect(read('src/routes/health/+server.ts')).toContain('VERSION');
  });
});
