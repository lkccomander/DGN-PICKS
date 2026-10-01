import { expect, test } from "@playwright/test";

test.skip(!process.env.E2E_WEB_URL, "Set E2E_WEB_URL to a local test server.");

for (const width of [1440, 390]) {
  test(`board loading, failure, retry and empty states at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    let release!: () => void;
    const pending = new Promise<void>(resolve => { release = resolve; });
    await page.route("**/api/dashboard?**", async route => {
      await pending;
      await route.fulfill({ status: 502, json: { detail: "Isolated unavailable API" } });
    });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByLabel("Loading dashboard")).toBeVisible();
    release();
    await expect(page.getByRole("heading", { name: "Couldn't load the board." })).toBeVisible();
    await page.unroute("**/api/dashboard?**");
    await page.route("**/api/dashboard?**", route => route.fulfill({ json: {
      games: [], picks: [], teams: [], definitions: [], markets: [], history: [],
      summary: { wins: 0, losses: 0, pushes: 0, pending: 0, void: 0, total_units_risked: "0", profit_units: null, roi: null, pending_units: "0", unpriced_settled_count: 0 },
    } }));
    await page.getByRole("button", { name: "Retry sync" }).click();
    await expect(page.getByRole("heading", { name: "No fixtures in the feed yet." })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Couldn't load the board." })).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
    await page.screenshot({ path: `test-results/board-empty-${width}.png`, fullPage: true });
  });
}
