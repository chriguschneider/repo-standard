import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';

// Example table; replace with the app's own. After every change here run
// `npm run db:generate` and commit the new file under drizzle/.
export const settings = sqliteTable('settings', {
  key: text('key').primaryKey(),
  value: text('value').notNull(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull(),
});
