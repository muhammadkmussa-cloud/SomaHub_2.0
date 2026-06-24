import { test, expect } from '@playwright/test';

const E2E_EMAIL = process.env.E2E_LIBRARIAN_EMAIL ?? 'e2e-librarian@test.com';
const E2E_PASSWORD = process.env.E2E_PASSWORD ?? 'password123';

test.describe('Librarian circulation flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.getByLabel('Email address').fill(E2E_EMAIL);
    await page.locator('#password').fill(E2E_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('login → create book → register borrower → issue loan', async ({ page }) => {
    const bookTitle = `E2E Book ${Date.now()}`;
    const barcode = `E2E-${Date.now()}`;

    await page.goto('/dashboard/books');
    await page.getByLabel('Title').fill(bookTitle);
    await page.getByLabel('Author').fill('E2E Author');
    await page.getByLabel('Total Copies').fill('1');
    await page.getByRole('button', { name: 'Add book' }).click();
    await expect(page.getByRole('cell', { name: bookTitle })).toBeVisible({ timeout: 15_000 });

    await page.locator('select').first().selectOption({ label: bookTitle });
    await page.getByLabel('Barcode').fill(barcode);
    await page.getByRole('button', { name: 'Add copy' }).click();

    await page.goto('/dashboard/borrowers');

    const uniqueId = Date.now();
    const borrowerName = `E2E${uniqueId} Borrower`;

    await page.getByLabel('First Name').fill(`E2E${uniqueId}`);
    await page.getByLabel('Last Name').fill('Borrower');
    await page.getByLabel('Student ID').fill(`STU-${uniqueId}`);
    await page.getByRole('button', { name: 'Register' }).click();

    await expect(
      page.getByRole('cell', { name: borrowerName })
    ).toBeVisible({ timeout: 15_000 });

    await page.goto('/dashboard/loans');
    await page.getByLabel('Borrower').selectOption({ label: borrowerName });
    await page.getByLabel('Available Copy').selectOption({ label: barcode });
    await page.getByRole('button', { name: 'Issue' }).click();

    await expect(page.getByRole('cell', { name: borrowerName })).toBeVisible();
    await expect(page.getByText('issued').first()).toBeVisible();
  });
});
