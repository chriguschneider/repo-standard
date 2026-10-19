/**
 * The shape every dictionary must have.
 *
 * `de.ts` and `en.ts` are both typed as `Dictionary`, and `index.ts` maps
 * every entry of LOCALES to one. A key missing in one language, an extra
 * key, or a locale without a dictionary fails `astro check`, which runs
 * first in `npm run build`. Leftover text of another language on a page
 * cannot ship unnoticed.
 */

/** The first entry is the default locale; it is served at `/`, the others under `/<locale>/`. */
export const LOCALES = ['de', 'en'] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = LOCALES[0];

export interface Dictionary {
  /** Value of `<html lang>`. */
  htmlLang: string;
  /** The language's own name, shown in the language switch. */
  languageName: string;
  meta: {
    title: string;
    description: string;
  };
  /** Shown on top of every page of a preview build (PREVIEW in src/config.ts). */
  previewBanner: string;
  nav: {
    home: string;
    languages: string;
  };
  home: {
    heading: string;
    intro: string;
    postsHeading: string;
    noPosts: string;
  };
  post: {
    back: string;
    draft: string;
  };
  notFound: {
    title: string;
    text: string;
    back: string;
  };
  footer: {
    source: string;
  };
}
