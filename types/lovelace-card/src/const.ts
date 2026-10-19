// Replaced with package.json's version at build time by the inline rollup
// plugin in rollup.config.mjs. package.json is the only place the version
// is written; never put a version literal here.
export const CARD_VERSION = '__CARD_VERSION__';

export const CARD_TAG = '@@DOMAIN@@';

export const DOCUMENTATION_URL = 'https://github.com/@@OWNER@@/@@REPO@@#readme';

// Keys a config must have; setConfig rejects a config without them.
export const REQUIRED_KEYS = ['entity'] as const;

// The one source of truth for defaults: setConfig merges them under the
// user's config, getStubConfig starts from them and the visual editor's
// schema takes its `default` values from here (guarded by
// tests/card.test.js).
export const DEFAULTS: Readonly<{ show_state: boolean }> = Object.freeze({
  show_state: true,
});
