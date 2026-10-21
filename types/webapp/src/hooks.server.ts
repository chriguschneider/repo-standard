import type { Handle } from '@sveltejs/kit/hooks';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import { db } from '#lib/server/db/index.ts';

// Apply pending migrations once, when the server starts. drizzle/ is
// committed and copied into the image, so a new version migrates itself.
migrate(db, { migrationsFolder: 'drizzle' });

export const handle: Handle = async ({ event, resolve }) => resolve(event);
