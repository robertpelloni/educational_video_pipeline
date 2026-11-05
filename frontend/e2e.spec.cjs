const { test, expect } = require('@playwright/test');

test('unified dashboard operations hub', async ({ page }) => {
  await page.goto('/');

  // Header & Branding
  await expect(page.locator('h1')).toContainText('Educational Video Pipeline');
  await expect(page.locator('.brand-badge')).toContainText('v0.4.0');

  // Core Sections
  await expect(page.getByText('Autonomous Video Studio')).toBeVisible();
  await expect(page.getByText('Interactive Story Branching Web Player')).toBeVisible();
  await expect(page.getByText('Celery Task Execution Monitor')).toBeVisible();
  await expect(page.getByText('Cross-Platform Analytics')).toBeVisible();
  await expect(page.getByText('ERP Order Event Simulator')).toBeVisible();
  await expect(page.getByText('Desktop System Tray Manager')).toBeVisible();

  // Tooltips & Controls
  const tooltips = page.locator('.tooltip-icon');
  await expect(tooltips.first()).toBeVisible();

  // Auth Handshake Modal
  await page.getByRole('button', { name: /Auth Credentials/i }).click();
  await expect(page.getByText('API Authentication Handshake')).toBeVisible();
  await page.getByRole('button', { name: 'Close' }).click();
  await expect(page.getByText('API Authentication Handshake')).not.toBeVisible();
});
