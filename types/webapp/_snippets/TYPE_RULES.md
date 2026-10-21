### Web app rules

- **No state in the process.** Sessions live in the database or in a
  signed cookie, never in memory; no in-memory caches that would differ
  between two instances; background work is a row in a jobs table that
  any instance may pick up. Then any number of containers can run behind
  one proxy, and moving hosts is copying `/data`.
- **Every tenant table carries a tenant id column** (a household, an
  organisation, a family), even while there is only one tenant. Every
  query filters by it. Adding it later is the most expensive change there
  is.
- **Uploads go to object storage** (S3-compatible: R2, Hetzner, MinIO for
  self-hosters), never to the container's disk, except the SQLite file
  itself in `/data`.
- **Migrations are generated, not written**: change
  `src/lib/server/db/schema.ts`, run `npm run db:generate`, commit the
  file under `drizzle/` in the same PR. Never edit a committed migration;
  add a new one. No SQLite-specific SQL in queries, so Postgres stays a
  migration away.
- **Secrets only from the environment** (`.env`, never committed; the
  image has no defaults for them). A new variable is declared in
  `src/env.ts` (validated at startup, imported from `$app/env/private`)
  and documented in `.env.example` in the same change. Reading `.env*`
  is denied to agents.
- **Imports inside the app use `#lib/...` with the file extension**
  (`#lib/server/db/index.ts`): SvelteKit 3 subpath imports, resolved by
  Vite and TypeScript alike. `$lib` no longer exists.
- **Passwords with `@node-rs/argon2`**, never a home-made hash. Auth and
  session code (`src/hooks.server.ts`, `src/lib/server/auth*`) is held for
  a human review.
- **The production build is the test target**: `npm run test:e2e` builds
  and starts `node build`, the same artifact the image runs. A change that
  only works under `vite dev` is not done.
- **`/health` stays trivial**: no database access; Docker restarts the
  container when it fails.
- **`npm ci --ignore-scripts`**, in CI, in the Dockerfile and locally: npm
  10 runs `node-gyp rebuild` for `better-sqlite3` on `npm ci` although the
  package ships prebuilt binaries, and the slim image has no compiler.
  Nothing in the tree needs an install script (esbuild and
  `@node-rs/argon2` ship platform packages). A new native dependency must
  work the same way or go through an ADR.
