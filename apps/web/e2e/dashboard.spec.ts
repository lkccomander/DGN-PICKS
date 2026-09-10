import { expect, test } from "@playwright/test";

const apiUrl = process.env.E2E_API_URL?.replace(/\/$/, "");
const writeKey = process.env.DGN_API_WRITE_KEY;
const requiredEnvironment = Boolean(apiUrl && process.env.E2E_WEB_URL && writeKey);

type Game = { id: number };
type Market = { id: number; game_id: number; status: string; selections: Array<{ id: number; side?: string | null }> };
type Snapshot = { sportsbook_id: number; line_value?: string | null; american_odds?: number | null; decimal_odds: string };
type Pick = { id: number; line_value?: string | null; american_odds?: number | null; selection_id?: number | null; market_id: number; notes?: string | null };

async function json<T>(url: string, options: Parameters<typeof fetch>[1] = {}): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json() as Promise<T>;
}

function displayedLine(pick: Pick) {
  if (pick.line_value == null) return "Line pending";
  const line = Number(pick.line_value);
  const odds = pick.american_odds == null ? "" : ` · ${pick.american_odds > 0 ? "+" : ""}${pick.american_odds}`;
  return `${line > 0 ? "+" : ""}${line}${odds}`;
}

test.skip(!requiredEnvironment, "Set E2E_WEB_URL, E2E_API_URL, and DGN_API_WRITE_KEY for the local development stack.");

test("tracks a stored price after a later line observation", async ({ page }) => {
  const games = await json<Game[]>(`${apiUrl}/api/v1/games`);
  const markets = (await Promise.all(games.map((game) => json<Market[]>(`${apiUrl}/api/v1/games/${game.id}/markets`)))).flat();
  const target = markets.find((market) => market.status === "open" && market.selections.some((selection) => selection.side));
  expect(target).toBeDefined();

  const note = `e2e-price-${Date.now()}`;
  await page.goto("/");
  await expect(page.locator(".game-select").first()).toBeVisible();
  await page.locator(".game-select").first().click();
  await expect(page.getByRole("heading", { name: "Game detail" })).toBeVisible();
  await page.getByRole("button", { name: /^Track / }).first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByLabel("Stake (units)").fill("1");
  await page.getByLabel("Note (optional)").fill(note);
  await page.getByRole("button", { name: "Create pick" }).click();
  await expect(page.getByText(note)).toBeVisible();

  const picks = await json<Pick[]>(`${apiUrl}/api/v1/picks?user=gato`);
  const created = picks.find((pick) => pick.notes === note);
  expect(created).toBeDefined();
  expect(created?.selection_id).toBeDefined();
  const originalLine = displayedLine(created as Pick);

  const history = await json<Snapshot[]>(`${apiUrl}/api/v1/markets/${created?.market_id}/history`);
  const current = history.filter((snapshot) => snapshot.sportsbook_id > 0).at(-1);
  expect(current).toBeDefined();
  await json<Snapshot>(`${apiUrl}/api/v1/markets/${created?.market_id}/history`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-DGN-Write-Key": writeKey as string },
    body: JSON.stringify({
      selection_id: created?.selection_id,
      sportsbook_id: current?.sportsbook_id,
      observed_at: new Date(Date.now() + 60_000).toISOString(),
      line_value: Number(current?.line_value ?? 0) + 0.5,
      american_odds: current?.american_odds,
      decimal_odds: current?.decimal_odds,
      source_event_id: note,
    }),
  });

  await page.reload();
  const row = page.locator(".pick-row", { hasText: note });
  await expect(row).toContainText(originalLine);
});
