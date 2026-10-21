import { defineConfig } from '@playwright/test';

// End-to-end smoke test against the production build (`node build`), the
// same artifact the Docker image runs. One browser, tablet-sized viewport.
const port = 4173;

export default defineConfig({
  testDir: 'tests',
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    viewport: { width: 1280, height: 800 },
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  webServer: {
    command: 'npm run build && node build',
    url: `http://127.0.0.1:${port}/health`,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    env: {
      HOST: '127.0.0.1',
      PORT: String(port),
      ORIGIN: `http://127.0.0.1:${port}`,
      // A throwaway database per run; the folder is gitignored.
      DATABASE_PATH: 'test-results/e2e.db',
    },
  },
});
