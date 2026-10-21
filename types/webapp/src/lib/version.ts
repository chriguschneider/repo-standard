import pkg from '../../package.json' with { type: 'json' };

// package.json is the only place the version is written (AGENTS.md).
export const VERSION: string = pkg.version;
