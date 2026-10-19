
### The bundled card

The card lives in `custom_components/@@DOMAIN@@/frontend/@@CARD_TAG@@.js`
and ships in the release zip with the integration. It is a plain ES module
with **no build step**: the committed file is what browsers run. The root
`package.json` exists only for the card's tests (vitest); nothing from npm
is shipped.

- **Registration.** `__init__.py` serves `frontend/` as a static path (once
  per HA run: it cannot be unregistered, and registering it twice raises)
  and adds the module URL with `add_extra_js_url` on every setup, removing
  it on every unload. A reload must neither lose nor double the card;
  `tests/test_card.py` checks it. With more than one config entry, count
  entries before removing the URL.
- **Versions.** `manifest.json`, `const.py` `VERSION`, the card's
  `CARD_VERSION` and `package.json` move together (`tests/test_metadata.py`,
  `tests/card.test.js`). The URL carries `?v=VERSION`, so browsers fetch the
  new card after an update.
- **Untrusted text.** The card writes states with `textContent`, never
  `innerHTML`.
- **Changelog: say what the user must do.** Every changelog entry ends with
  *frontend only (browser reload)* when only the card changed, or *requires
  restart* when Python changed (the integration, or how the card is
  registered). An entry that touches both says *requires restart*.
