import { LitElement, css, html, nothing } from 'lit';

import { CARD_TAG, CARD_VERSION } from './const';

interface CardConfig {
  type: string;
  title?: string;
}

// Minimal shape of the `hass` object this card touches. Widen it as the
// card starts reading states.
interface Hass {
  states: Record<string, unknown>;
}

class CardElement extends LitElement {
  static properties = {
    hass: { attribute: false },
    _config: { state: true },
  };

  hass?: Hass;
  private _config?: CardConfig;

  static getStubConfig(): Omit<CardConfig, 'type'> {
    return { title: '@@NAME@@' };
  }

  setConfig(config: CardConfig): void {
    if (!config) throw new Error('Invalid configuration');
    this._config = config;
  }

  getCardSize(): number {
    return 1;
  }

  static styles = css`
    .content {
      padding: 16px;
    }
  `;

  render() {
    if (!this._config) return nothing;
    return html`
      <ha-card .header=${this._config.title}>
        <div class="content">@@NAME@@</div>
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
w.customCards.push({
  type: CARD_TAG,
  name: '@@NAME@@',
  description: '@@DESCRIPTION@@',
  preview: true,
});

console.info(`%c @@NAME@@ %c v${CARD_VERSION} `, 'color:white;background:#2196f3', '');
