// @vitest-environment jsdom
// Behaviour smoke test: the card registers, accepts and rejects configs the
// way Home Assistant expects, and the visual editor's schema keeps up with
// the config (a key missing from the schema cannot be set in the UI).
import { describe, expect, it } from 'vitest';

import { CARD_TAG, DEFAULTS, REQUIRED_KEYS } from '../src/const.ts';
import '../src/@@DOMAIN@@.ts';

const hass = { states: { 'sensor.demo': { state: '21.5', attributes: {} } } };
const Card = () => customElements.get(CARD_TAG);
const schemaFields = () =>
  new Map(Card().getConfigForm().schema.map((field) => [field.name, field]));

describe('card', () => {
  it('is defined under its tag and listed in the card picker', () => {
    expect(Card()).toBeDefined();
    const entry = window.customCards.find((card) => card.type === CARD_TAG);
    expect(entry).toMatchObject({ preview: true });
    expect(entry.documentationURL).toMatch(/^https:\/\//);
  });

  it('accepts its own stub config', () => {
    const card = document.createElement(CARD_TAG);
    expect(() => card.setConfig({ type: `custom:${CARD_TAG}`, ...Card().getStubConfig(hass) })).not.toThrow();
  });

  it.each(REQUIRED_KEYS)('rejects a config without %s, naming the key', (key) => {
    const config = { type: `custom:${CARD_TAG}`, ...Card().getStubConfig(hass) };
    delete config[key];
    const card = document.createElement(CARD_TAG);
    expect(() => card.setConfig(config)).toThrow(key);
  });

  it('returns a sane stub config and grid size', () => {
    const stub = Card().getStubConfig(hass);
    expect(stub.entity).toBe('sensor.demo');
    expect(Card().getStubConfig().entity).toBeTruthy();

    const card = document.createElement(CARD_TAG);
    expect(card.getCardSize()).toBeGreaterThan(0);
    const grid = card.getGridOptions();
    expect(grid.rows).toBeGreaterThan(0);
    for (const key of ['columns', 'min_columns']) {
      expect(grid[key] % 3, `${key} on the 12-column sections grid`).toBe(0);
      expect(grid[key]).toBeLessThanOrEqual(12);
    }
  });

  it('renders the entity state', async () => {
    const card = document.createElement(CARD_TAG);
    card.setConfig({ type: `custom:${CARD_TAG}`, entity: 'sensor.demo' });
    card.hass = hass;
    document.body.append(card);
    await card.updateComplete;
    expect(card.shadowRoot.textContent).toContain('21.5');
    card.remove();
  });
});

describe('visual editor schema', () => {
  it('covers every key of the stub config', () => {
    const fields = schemaFields();
    const uncovered = Object.keys(Card().getStubConfig(hass)).filter((key) => !fields.has(key));
    expect(uncovered).toEqual([]);
  });

  it('marks the required keys as required', () => {
    const fields = schemaFields();
    for (const key of REQUIRED_KEYS) expect(fields.get(key)?.required, key).toBe(true);
  });

  // An editor default that differs from the runtime default shows one
  // value in the UI while the card uses another.
  it.each(Object.entries(DEFAULTS))('uses the runtime default for %s', (key, value) => {
    expect(schemaFields().get(key)?.default).toBe(value);
  });
});
