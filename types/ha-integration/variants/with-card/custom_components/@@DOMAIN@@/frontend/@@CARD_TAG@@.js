// @@NAME@@ card. Shipped inside the integration and loaded on every
// dashboard by __init__.py (frontend.add_extra_js_url), so there is nothing
// to add under Settings -> Dashboards -> Resources.
//
// Plain ES module, no build step: what is committed is what the browser
// runs. Pure helpers are exported so vitest can test them in Node, where
// HTMLElement and customElements do not exist.

export const CARD_VERSION = '0.0.1';
export const CARD_TAG = '@@CARD_TAG@@';

/** The text the card shows for an entity, or a hint when it is missing. */
export function stateText(hass, entityId) {
  const stateObj = hass?.states?.[entityId];
  if (!stateObj) return `Entity not found: ${entityId}`;
  const unit = stateObj.attributes?.unit_of_measurement;
  return unit ? `${stateObj.state} ${unit}` : String(stateObj.state);
}

export function validateConfig(config) {
  if (!config || typeof config.entity !== 'string' || !config.entity) {
    throw new Error('@@CARD_TAG@@: set "entity" in the card config');
  }
  return { ...config };
}

const Base = globalThis.HTMLElement ?? class {};

export class IntegrationCard extends Base {
  static getStubConfig() {
    return { entity: '' };
  }

  setConfig(config) {
    this._config = validateConfig(config);
    this._render();
  }

  // HA sets `hass` on every state change anywhere; render only when the
  // watched entity changed.
  set hass(hass) {
    const entity = this._config?.entity;
    const changed = !this._hass || this._hass.states?.[entity] !== hass.states?.[entity];
    this._hass = hass;
    if (changed) this._render();
  }

  getCardSize() {
    return 1;
  }

  _render() {
    if (!this._config || !this._hass) return;
    if (!this._content) {
      const card = document.createElement('ha-card');
      if (this._config.title) card.setAttribute('header', this._config.title);
      this._content = document.createElement('div');
      this._content.className = 'card-content';
      card.appendChild(this._content);
      this.replaceChildren(card);
    }
    // textContent, never innerHTML: states are not trusted markup.
    this._content.textContent = stateText(this._hass, this._config.entity);
  }
}

// Guarded: the module can be loaded twice (an old Lovelace resource next to
// the bundled URL), and defining a custom element twice throws.
if (globalThis.customElements && !globalThis.customElements.get(CARD_TAG)) {
  globalThis.customElements.define(CARD_TAG, IntegrationCard);
  globalThis.customCards = globalThis.customCards || [];
  globalThis.customCards.push({
    type: CARD_TAG,
    name: '@@NAME@@',
    description: '@@DESCRIPTION@@',
  });
  console.info(`%c${CARD_TAG} ${CARD_VERSION}`, 'font-weight: bold');
}
