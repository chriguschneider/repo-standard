## Self-hosting

One container, one SQLite file. You need Docker with Compose.

```bash
mkdir @@REPO@@ && cd @@REPO@@
curl -fsSLO https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/@@BRANCH@@/docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/@@BRANCH@@/.env.example -o .env
# edit .env: ORIGIN is the address users will type in
docker compose up -d
```

Open <http://localhost:3000>. The app listens on `127.0.0.1` only; put a
reverse proxy with TLS in front (Caddy, nginx, Traefik) and set `ORIGIN`
to its public address.

- **Data**: everything is in `./data/` (the SQLite database and uploads).
- **Backup**: copy `./data/` while the container is stopped, or let your
  backup tool take the folder every night after the app's own dump.
- **Update**: `docker compose pull && docker compose up -d`. Migrations
  run on startup; read the release notes first.
- **Versions**: images are tagged `vX.Y.Z` and `latest`
  ([releases](https://github.com/@@OWNER@@/@@REPO@@/releases)). Pin a
  version in `docker-compose.yml` if you want updates to be deliberate.

## Development

```bash
npm ci --ignore-scripts
cp .env.example .env
npm run dev            # http://localhost:5173, database in ./data/
npm run lint && npm run typecheck && npm test && npm run build
npx playwright install chromium && npm run test:e2e
docker build -t @@REPO@@ .
```

A schema change (`src/lib/server/db/schema.ts`) needs `npm run db:generate`;
commit the new migration under `drizzle/` with it. CI fails otherwise.

TODO(repo-standard): configuration table (environment variables beyond
`ORIGIN`), screenshots.
