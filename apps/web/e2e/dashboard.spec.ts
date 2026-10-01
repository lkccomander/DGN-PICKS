import { expect, test } from "@playwright/test";

const apiUrl = process.env.E2E_API_URL?.replace(/\/$/, "");
const operatorUsername = process.env.E2E_OPERATOR_USERNAME;
const operatorPassword = process.env.E2E_OPERATOR_PASSWORD;
const requiredEnvironment = Boolean(apiUrl && process.env.E2E_WEB_URL && operatorUsername && operatorPassword);

type Game = { id: number; status: string; home_team_id: number; away_team_id: number };
type Market = { id: number; game_id: number; status: string; selections: Array<{ id: number; side?: string | null }> };
type Snapshot = { selection_id: number; sportsbook_id: number; line_value?: string | null; american_odds?: number | null; decimal_odds: string };
type Pick = { id: number; line_value?: string | null; american_odds?: number | null; selection_id?: number | null; market_id: number; notes?: string | null; decimal_odds?: string | null; stake_units: string; user_id: number };

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

test.skip(!requiredEnvironment, "Set E2E_WEB_URL, E2E_API_URL, E2E_OPERATOR_USERNAME and E2E_OPERATOR_PASSWORD for the isolated test stack.");

test("owned picks can be edited/deleted and keep their stored price after market movement", async ({ page, request }) => {
  // This test writes data: enforce loopback origins and use only an isolated database.
  for (const origin of [apiUrl!, process.env.E2E_WEB_URL!]) {
    expect(["127.0.0.1", "localhost", "[::1]"]).toContain(new URL(origin).hostname);
  }
  const operator = await json<{ access_token: string }>(`${apiUrl}/api/v1/auth/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: operatorUsername, password: operatorPassword }),
  });
  const username = `e2e-${Date.now()}`;
  const account = await json<{ access_token: string }>(`${apiUrl}/api/v1/auth/register`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email: `${username}@example.invalid`, display_name: "E2E account", password: "e2e-isolated-password" }),
  });
  await page.goto("/");
  await page.evaluate(({ token, username }) => {
    localStorage.setItem("dgn-admin-token", token);
    localStorage.setItem("dgn-active-user", username);
    localStorage.setItem("dgn-account-label", username);
  }, { token: account.access_token, username });
  const games = (await json<Game[]>(`${apiUrl}/api/v1/games`)).filter(game => ["scheduled", "live"].includes(game.status));
  const markets = (await Promise.all(games.map((game) => json<Market[]>(`${apiUrl}/api/v1/games/${game.id}/markets`)))).flat();
  const target = markets.find((market) => market.status === "open" && market.selections.some((selection) => selection.side));
  expect(target).toBeDefined();

  const note = `e2e-price-${Date.now()}`;
  await page.goto("/");
  await expect(page.locator(".game-select").first()).toBeVisible();
  const teams = await json<Array<{ id: number; short_name: string }>>(`${apiUrl}/api/v1/teams`);
  const game = games.find(item => item.id === target!.game_id)!;
  const home = teams.find(team => team.id === game.home_team_id)!;
  await page.locator(".game-select").filter({ hasText: home.short_name }).click();
  await expect(page.locator(".game-detail")).toBeVisible();
  await page.locator(`.market-row[data-market-id="${target!.id}"]`).first().getByRole("button", { name: /^Track / }).first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByLabel("Stake (units)").fill("1");
  await page.getByLabel("Note (optional)").fill(note);
  await page.getByRole("button", { name: "Create pick" }).click();
  await expect(page.getByText(note)).toBeVisible();

  const picks = await json<Pick[]>(`${apiUrl}/api/v1/picks?user=${username}`);
  const created = picks.find((pick) => pick.notes === note);
  expect(created).toBeDefined();
  expect(created?.selection_id).toBeDefined();
  const originalLine = displayedLine(created as Pick);

  const history = await json<Snapshot[]>(`${apiUrl}/api/v1/markets/${created?.market_id}/history`);
  const current = history.filter((snapshot) => snapshot.selection_id === created?.selection_id).at(-1);
  expect(current).toBeDefined();
  await json<Snapshot>(`${apiUrl}/api/v1/markets/${created?.market_id}/history`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${operator.access_token}` },
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
  const updated = (await json<Pick[]>(`${apiUrl}/api/v1/picks?user=${username}`)).find(pick => pick.id === created!.id)!;
  expect(updated.line_value).toBe(created!.line_value);
  expect(updated.decimal_odds).toBe(created!.decimal_odds);
  expect(updated.american_odds).toBe(created!.american_odds);
  await expect(row.getByRole("button", { name: "win", exact: true })).toHaveCount(0);

  // Exercise the real same-origin proxy's ownership and grading boundaries.
  const otherName = `other-${Date.now()}`;
  const other = await json<{ access_token: string }>(`${apiUrl}/api/v1/auth/register`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: otherName, email: `${otherName}@example.invalid`, display_name: "Other account", password: "e2e-isolated-password" }),
  });
  expect((await request.patch(`/api/development/picks/${created!.id}`, {
    headers: { Authorization: `Bearer ${other.access_token}` }, data: { user: username, notes: "forbidden" },
  })).status()).toBe(403);
  expect((await request.patch(`/api/development/picks/${created!.id}`, {
    headers: { Authorization: `Bearer ${account.access_token}` }, data: { user: username, result: "win" },
  })).status()).toBe(403);

  await row.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByLabel("Stake (units)").fill("2");
  await page.getByLabel("Note (optional)").fill(`${note}-edited`);
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(row).toContainText("2.0u");
  await expect(row).toContainText(`${note}-edited`);
  await expect(row).toContainText(originalLine);
  const afterEdit = (await json<Pick[]>(`${apiUrl}/api/v1/picks?user=${username}`)).find(pick => pick.id === created!.id)!;
  expect(afterEdit.user_id).toBe(created!.user_id);
  expect(afterEdit.line_value).toBe(created!.line_value);
  expect(afterEdit.decimal_odds).toBe(created!.decimal_odds);
  page.once("dialog", dialog => dialog.dismiss());
  await row.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(row).toBeVisible();
  page.once("dialog", dialog => dialog.accept());
  await row.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(row).toHaveCount(0);
  expect(await json<Pick[]>(`${apiUrl}/api/v1/picks?user=${username}`)).toEqual([]);
});
