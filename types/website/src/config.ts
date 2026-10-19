/**
 * Site-wide switches. These are decisions, flipped by hand by the owner,
 * not configuration an agent tunes (AGENTS.md, "Site rules").
 */

/** The production address. scripts/check-links.mjs reads it from here too. */
export const SITE_URL = '@@SITE_URL@@';

/** The branch Cloudflare Pages serves at SITE_URL. Everything else is a preview. */
export const PRODUCTION_BRANCH = '@@PRODUCTION_BRANCH@@';

/**
 * Whether this build is a preview. Cloudflare Pages sets CF_PAGES_BRANCH
 * while building; every branch except the production branch (above all
 * `@@BRANCH@@`, where PRs land) is a preview: a banner on every page, a
 * noindex meta tag and a robots.txt that disallows everything. A preview
 * must never end up in a search index next to the real site.
 *
 * Locally the variable is unset and the site builds as production;
 * `CF_PAGES_BRANCH=@@BRANCH@@ npm run build` shows the preview.
 */
export const PREVIEW = (process.env.CF_PAGES_BRANCH ?? PRODUCTION_BRANCH) !== PRODUCTION_BRANCH;

/**
 * Keeps search engines off the production site as well, e.g. before the
 * first real content. Read by the layout (meta tag) and robots.txt, so the
 * two cannot disagree.
 */
export const NOINDEX = false;
