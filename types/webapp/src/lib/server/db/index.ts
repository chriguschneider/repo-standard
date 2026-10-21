import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { DATABASE_PATH } from '$app/env/private';
import * as schema from './schema.ts';

// One SQLite file, path from the environment (src/env.ts); the Docker
// image points it at the /data volume. Read at runtime, not at build time.
mkdirSync(dirname(DATABASE_PATH), { recursive: true });

const client = new Database(DATABASE_PATH);
// WAL: readers never block the writer, and a crash cannot corrupt the file.
client.pragma('journal_mode = WAL');
client.pragma('foreign_keys = ON');

export const db = drizzle(client, { schema });
export type Db = typeof db;
