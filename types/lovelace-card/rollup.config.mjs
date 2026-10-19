import resolve from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';
import typescript from '@rollup/plugin-typescript';

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
    typescript({ tsconfig: './tsconfig.json', compilerOptions: { noEmit: false } }),
    resolve(),
    // Class names kept so the custom element registration stays readable
    // in the browser console; the bundle is committed, so keep it stable.
    terser({ format: { comments: false }, mangle: { keep_classnames: true } }),
  ],
};
