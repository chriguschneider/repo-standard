import { defineConfig } from 'drizzle-kit';

// `npm run db:generate` writes a migration into drizzle/ from a schema
// change; commit it with the schema. The app applies migrations on startup.
export default defineConfig({
  schema: './src/lib/server/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: { url: process.env.DATABASE_PATH ?? './data/@@DOMAIN@@.db' },
});
