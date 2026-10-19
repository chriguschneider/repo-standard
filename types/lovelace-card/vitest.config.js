// Pin the time zone so date formatting is the same on every machine and on
// CI. Set here rather than in the npm script so it works on Windows too;
// the test workers inherit it.
process.env.TZ = 'UTC';

export default {
  test: {
    // Node by default; a file that needs a DOM opts in with a
    // `// @vitest-environment jsdom` comment on its first line.
    environment: 'node',
    include: ['tests/**/*.test.js'],
  },
};
