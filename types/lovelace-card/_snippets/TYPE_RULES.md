### Lovelace card pitfalls

- **`dist/` conflicts on rebase: rebuild, never hand-merge.** Take either
  side of the minified bundle, run `npm run build`, `git add dist/`,
  continue. CI fails a hand-merged bundle anyway.
- **HACS shows the README as it was at the release tag**, not as it is on
  the default branch, and its sanitiser strips `<picture>`/`<source>` and
  breaks relative image paths. In `README.md` use plain `<img>` with
  absolute `https://raw.githubusercontent.com/...` URLs, and never rename
  or move an image or badge URL between releases: older installs still
  point at the old one.
- **Editor defaults equal runtime defaults.** `DEFAULTS` in `src/const.ts`
  is the one source; `setConfig`, `getStubConfig` and the schema in
  `getConfigForm` read it, and `tests/card.test.js` fails when they
  disagree or when a config key is missing from the editor schema. A new
  option goes into all of them in the same PR.
- **Locale files are discovered automatically**, not imported one by one:
  when the card gets translations, load `src/locales/*` through a glob or
  a test that lists the directory, so a new language cannot be forgotten
  in a hand-kept list.
- **The changelog is for dashboard owners.** HACS shows the release
  section in its update dialog: say what changes for them and whether
  they must do anything (YAML change, cache refresh), no file paths or
  tool names.
