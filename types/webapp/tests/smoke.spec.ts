import { expect, test } from '@playwright/test';

test('the home page shows the app name', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('@@NAME@@');
});

test('the health endpoint reports ok and a version', async ({ request }) => {
  const response = await request.get('/health');
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.status).toBe('ok');
  expect(body.version).toMatch(/^\d+\.\d+\.\d+/);
});
