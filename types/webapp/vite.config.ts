import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [
    sveltekit({
      compilerOptions: {
        // Runes everywhere in our own code; libraries decide for themselves.
        runes: ({ filename }) =>
          filename.split(/[/\\]/).includes('node_modules') ? undefined : true,
      },
      // One Node server in `build/`, started with `node build` (Dockerfile CMD).
      adapter: adapter({ out: 'build' }),
    }),
  ],
  test: {
    // Unit tests live next to the code; `tests/` holds the Playwright specs.
    include: ['src/**/*.test.ts'],
    environment: 'node',
  },
});
