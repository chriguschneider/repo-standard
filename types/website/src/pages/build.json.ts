import type { APIRoute } from 'astro';

/**
 * `/build.json`: which commit this deployment was built from. Cloudflare
 * Pages sets CF_PAGES_COMMIT_SHA and CF_PAGES_BRANCH while building; a local
 * build says `local`. scripts/deploy-status.mjs reads it to confirm that a
 * push (or a promotion to production) is actually live, because a failed
 * Pages build silently keeps serving the previous deployment.
 *
 * No timestamp on purpose: the same commit builds the same bytes.
 */
export const GET: APIRoute = () =>
  new Response(
    `${JSON.stringify({
      commit: process.env.CF_PAGES_COMMIT_SHA ?? 'local',
      branch: process.env.CF_PAGES_BRANCH ?? 'local',
    })}\n`,
    { headers: { 'Content-Type': 'application/json; charset=utf-8' } },
  );
