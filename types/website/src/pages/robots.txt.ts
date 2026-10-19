import type { APIRoute } from 'astro';
import { NOINDEX, PREVIEW } from '../config';

/**
 * Generated rather than a static file in public/, so PREVIEW and NOINDEX in
 * src/config.ts are the one switch: the meta tag in the layout and this file
 * read the same values and cannot disagree. A preview is always closed.
 */
export const GET: APIRoute = ({ site }) => {
  const lines = PREVIEW
    ? ['# Preview build, not approved: see PREVIEW in src/config.ts.', 'User-agent: *', 'Disallow: /']
    : NOINDEX
      ? ['# Not open for indexing yet: see NOINDEX in src/config.ts.', 'User-agent: *', 'Disallow: /']
      : ['User-agent: *', 'Allow: /', '', `Sitemap: ${new URL('sitemap-index.xml', site).href}`];

  return new Response(`${lines.join('\n')}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
