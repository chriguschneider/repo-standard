import de from './de';
import en from './en';
import { DEFAULT_LOCALE, LOCALES, type Dictionary, type Locale } from './types';

export { DEFAULT_LOCALE, LOCALES, type Dictionary, type Locale } from './types';

// Record<Locale, ...>: adding a locale to LOCALES without a dictionary fails `astro check`.
const DICTIONARIES: Record<Locale, Dictionary> = { de, en };

export const isLocale = (value: unknown): value is Locale =>
  typeof value === 'string' && (LOCALES as readonly string[]).includes(value);

/** The locale of the current route (`Astro.currentLocale`); anything unexpected falls back to the default. */
export const localeOf = (value: string | undefined): Locale => (isLocale(value) ? value : DEFAULT_LOCALE);

export const dictionary = (value: string | undefined): Dictionary => DICTIONARIES[localeOf(value)];

/** Root path of a locale: `/` for the default, `/<locale>/` for the others. */
export const localeRoot = (locale: Locale): string => (locale === DEFAULT_LOCALE ? '/' : `/${locale}/`);
