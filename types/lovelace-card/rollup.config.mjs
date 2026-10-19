import { readFileSync } from 'node:fs';

import resolve from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';
import typescript from '@rollup/plugin-typescript';

const pkg = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf8'));

// package.json is the single source of the version: this replaces the
// literal '__CARD_VERSION__' in src/ at build time, so a release bumps one
// file and the console banner can never disagree with it. Inline instead
// of @rollup/plugin-replace: one substitution is not worth a dependency.
// tests/metadata.test.js checks the built bundle carries the version.
const injectCardVersion = {
  name: 'inject-card-version',
  transform(code, id) {
    if (!id.includes('/src/') && !id.includes('\\src\\')) return null;
    const replaced = code.replaceAll("'__CARD_VERSION__'", JSON.stringify(pkg.version));
    return replaced === code ? null : { code: replaced, map: null };
  },
};

// One self-contained ES module: HACS registers it as a Lovelace resource of
// `type: module`. The filename must match `filename` in hacs.json (guarded
// by tests/metadata.test.js).
export default {
  input: 'src/@@DOMAIN@@.ts',
  output: {
    file: 'dist/@@DOMAIN@@.js',
    format: 'es',
    sourcemap: false,
  },
  plugins: [
    // Before TypeScript, so no later pass sees the placeholder.
    injectCardVersion,
    typescript({ tsconfig: './tsconfig.json', compilerOptions: { noEmit: false } }),
    resolve(),
    // Class names kept so the custom element registration stays readable
    // in the browser console; the bundle is committed, so keep it stable.
    terser({ format: { comments: false }, mangle: { keep_classnames: true } }),
  ],
};
