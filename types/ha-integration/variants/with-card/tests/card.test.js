// The bundled card in Node: pure helpers and version sync. No browser.
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import {
  CARD_TAG,
  CARD_VERSION,
  IntegrationCard,
  stateText,
  validateConfig,
} from '../custom_components/@@DOMAIN@@/frontend/@@CARD_TAG@@.js';

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');

describe('metadata', () => {
  it('keeps CARD_VERSION, package.json and manifest.json in sync', () => {
    const pkg = JSON.parse(read('package.json'));
    const manifest = JSON.parse(read('custom_components/@@DOMAIN@@/manifest.json'));
    expect(CARD_VERSION).toBe(pkg.version);
    expect(CARD_VERSION).toBe(manifest.version);
  });

  it('uses a valid custom element name', () => {
    expect(CARD_TAG).toMatch(/^[a-z][a-z0-9._]*-[a-z0-9._-]*$/);
  });

  it('loads in Node without defining an element', () => {
    expect(globalThis.customCards).toBeUndefined();
  });
});

describe('stateText', () => {
  const hass = {
    states: {
      'sensor.a': { state: '21.5', attributes: { unit_of_measurement: '°C' } },
      'sensor.b': { state: 'idle', attributes: {} },
    },
  };

  it('shows the state with its unit', () => {
    expect(stateText(hass, 'sensor.a')).toBe('21.5 °C');
    expect(stateText(hass, 'sensor.b')).toBe('idle');
  });

  it('names a missing entity', () => {
    expect(stateText(hass, 'sensor.gone')).toBe('Entity not found: sensor.gone');
    expect(stateText(undefined, 'sensor.gone')).toBe('Entity not found: sensor.gone');
  });
});

describe('config', () => {
  it('requires an entity', () => {
    expect(() => validateConfig({})).toThrow(/entity/);
    expect(() => validateConfig({ entity: '' })).toThrow(/entity/);
    expect(validateConfig({ entity: 'sensor.a' })).toEqual({ entity: 'sensor.a' });
  });

  it('offers a stub config for the card picker', () => {
    expect(IntegrationCard.getStubConfig()).toHaveProperty('entity');
  });
});
