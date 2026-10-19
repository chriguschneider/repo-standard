import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { SITE_URL } from './src/config';
import { DEFAULT_LOCALE, LOCALES } from './src/i18n/types';

export default defineConfig({
  // Every absolute URL (canonical, hreflang, sitemap) is built from this,
  // also on the preview: the preview links to production on purpose, so a
  // shared preview link never becomes the canonical one.
  site: SITE_URL,
  output: 'static',

  // public/_headers sends a CSP without 'unsafe-inline'. Astro would inline
  // small stylesheets and scripts into the HTML, which that CSP blocks, so
  // both always ship as files. scripts/check-csp.mjs fails the build if
  // anything inline slips through.
  build: { inlineStylesheets: 'never' },
  vite: { build: { assetsInlineLimit: 0 } },

  // The locale list lives in src/i18n/types.ts, next to the Dictionary type
  // that forces every language to carry every key.
  i18n: {
    defaultLocale: DEFAULT_LOCALE,
    locales: [...LOCALES],
    routing: { prefixDefaultLocale: false },
  },

  integrations: [sitemap()],
});
