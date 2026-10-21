# syntax=docker/dockerfile:1
# One image, two stages: build with every dependency, run with only the
# production ones as a non-root user. State lives in /data (a volume).

FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
# --ignore-scripts: npm 10 runs node-gyp for better-sqlite3 on `npm ci` even
# though it ships prebuilt binaries (gypfile: false); nothing here needs
# install scripts (esbuild and argon2 ship platform packages).
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22-bookworm-slim
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000 \
    DATABASE_PATH=/data/@@DOMAIN@@.db
WORKDIR /app
COPY --from=build --chown=node:node /app/build ./build
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/package.json ./package.json
# Migrations run on startup (src/hooks.server.ts) and are read from here.
COPY --from=build --chown=node:node /app/drizzle ./drizzle
RUN mkdir -p /data && chown node:node /data
USER node
VOLUME /data
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:' + process.env.PORT + '/health').then((r) => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"
CMD ["node", "build"]
