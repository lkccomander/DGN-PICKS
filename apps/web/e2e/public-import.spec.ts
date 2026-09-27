import { expect, test } from "@playwright/test";

const batch = process.env.E2E_PUBLIC_BATCH;
test.skip(!process.env.E2E_WEB_URL || !batch, "Set E2E_WEB_URL and E2E_PUBLIC_BATCH to verify a published import without signing in.");

test("published Gato card is visible without authentication on desktop and mobile", async ({ page, request }) => {
  const response = await request.get("/api/dashboard?user=gato");
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  const imported = data.picks.filter((pick: { import_metadata?: { batch_key?: string } }) => pick.import_metadata?.batch_key === batch);
  expect(imported).toHaveLength(10);
  expect(new Set(imported.map((pick: { user_id: number }) => pick.user_id)).size).toBe(1);
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Tracked picks", exact: true })).toBeVisible();
    for (const pick of imported) {
      const row = page.locator(".pick-row").filter({ hasText: pick.notes });
      await expect(row).toBeVisible();
      await expect(row).toContainText("2026-09-26");
      await expect(row).toContainText("Odds not supplied");
      await expect(row.locator(".pick-actions")).toHaveCount(0);
    }
    await expect(page.locator(".market-strip")).toContainText("GATO");
    await page.screenshot({ path: `test-results/gato-import-${viewport.width}.png`, fullPage: true });
  }
});
