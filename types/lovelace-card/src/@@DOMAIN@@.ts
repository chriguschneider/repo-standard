import { LitElement, css, html, nothing } from 'lit';

import { CARD_TAG, CARD_VERSION, DEFAULTS, DOCUMENTATION_URL, REQUIRED_KEYS } from './const';

interface CardConfig {
  type: string;
  entity: string;
  title?: string;
  show_state?: boolean;
}

// Minimal shape of the `hass` object this card touches. Widen it as the
// card starts reading more.
interface HassEntity {
  state: string;
  attributes: Record<string, unknown>;
}

interface Hass {
  states: Record<string, HassEntity>;
}

class CardElement extends LitElement {
  static properties = {
    hass: { attribute: false },
    _config: { state: true },
  };

  hass?: Hass;
  private _config?: CardConfig & typeof DEFAULTS;

  // Called when the card is added from the "Add card" picker.
  static getStubConfig(hass?: Hass): Omit<CardConfig, 'type'> {
    const entity = Object.keys(hass?.states ?? {})[0] ?? 'sun.sun';
    return { entity, title: '@@NAME@@', ...DEFAULTS };
  }

  // Schema for HA's built-in form editor (ha-form). Every key the card
  // reads belongs here, or the visual editor silently cannot set it.
  static getConfigForm() {
    return {
      schema: [
        { name: 'entity', required: true, selector: { entity: {} } },
        { name: 'title', selector: { text: {} } },
        { name: 'show_state', default: DEFAULTS.show_state, selector: { boolean: {} } },
      ],
    };
  }

  setConfig(config: CardConfig): void {
    if (!config || typeof config !== 'object') {
      throw new Error('Invalid configuration');
    }
    const missing = REQUIRED_KEYS.filter((key) => !config[key]);
    if (missing.length) {
      throw new Error(`Missing required option: ${missing.join(', ')}`);
    }
    this._config = { ...DEFAULTS, ...config };
  }

  // Masonry view: height in units of 50 px.
  getCardSize(): number {
    return 2;
  }

  // Sections view: a 12-column grid; keep columns a multiple of 3.
  getGridOptions() {
    return { columns: 6, rows: 2, min_columns: 3, min_rows: 1 };
  }

  static styles = css`
    .content {
      padding: 16px;
    }
  `;

  render() {
    if (!this._config) return nothing;
    const state = this.hass?.states[this._config.entity];
    return html`
      <ha-card .header=${this._config.title}>
        <div class="content">
          ${this._config.show_state ? (state?.state ?? 'unavailable') : this._config.entity}
        </div>
      </ha-card>
    `;
  }
}

if (!customElements.get(CARD_TAG)) {
  customElements.define(CARD_TAG, CardElement);
}

// Shows the card in the dashboard's "Add card" picker.
const w = window as unknown as { customCards?: Array<Record<string, unknown>> };
w.customCards = w.customCards ?? [];
if (!w.customCards.some((card) => card.type === CARD_TAG)) {
  w.customCards.push({
    type: CARD_TAG,
    name: '@@NAME@@',
    description: '@@DESCRIPTION@@',
    preview: true,
    documentationURL: DOCUMENTATION_URL,
  });
}

console.info(`%c @@NAME@@ %c v${CARD_VERSION} `, 'color:white;background:#2196f3', '');
