import { defineEnvVars } from '@sveltejs/kit/env';

// Every environment variable the app reads is declared here (SvelteKit 3):
// server code imports it from `$app/env/private`, validated at startup.
// Document each new one in `.env.example` in the same change.
export const variables = defineEnvVars({
  DATABASE_PATH: {
    description: 'Path of the SQLite database file; the Docker image sets /data/@@DOMAIN@@.db',
    schema: (value) => value || './data/@@DOMAIN@@.db',
  },
});
