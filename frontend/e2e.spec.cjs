const { test, expect } = require('@playwright/test');

test('basic functionality', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('h1')).toHaveText('Educational Video Pipeline');
});

test('quiz functionality', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('h1')).toHaveText('Educational Video Pipeline');
});
