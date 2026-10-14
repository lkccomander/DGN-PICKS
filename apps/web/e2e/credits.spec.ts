import { expect, test } from "@playwright/test";

const api = process.env.E2E_API_URL?.replace(/\/$/, "");
const desktop = process.env.E2E_DESKTOP_URL;
const operatorUsername = process.env.E2E_OPERATOR_USERNAME;
const operatorPassword = process.env.E2E_OPERATOR_PASSWORD;

test.skip(!api || !desktop || !process.env.E2E_WEB_URL || !operatorUsername || !operatorPassword,
  "Requires an isolated API, web, desktop and operator credentials.");

test("virtual credits require operator approval and never appear as money", async ({ page, request, browser }) => {
  test.setTimeout(60000);
  for (const origin of [api!, desktop!, process.env.E2E_WEB_URL!]) {
    expect(["127.0.0.1", "localhost", "[::1]"]).toContain(new URL(origin).hostname);
  }
  await page.goto("/deposit");
  await expect(page.getByRole("button", { name: "REQUEST CREDITS" })).toHaveCount(0);

  const username = `credits-${Date.now()}`;
  const registered = await request.post(`${api}/api/v1/auth/register`, {
    data: { username, email: `${username}@example.invalid`, display_name: "Credits account", password: "isolated-credit-password" },
  });
  expect(registered.ok()).toBeTruthy();
  const account = await registered.json();
  const headers = { Authorization: `Bearer ${account.access_token}` };
  await page.evaluate(token => localStorage.setItem("dgn-admin-token", token), account.access_token);
  await page.reload();
  await expect(page.getByRole("heading", { name: "Request credits", exact: true })).toBeVisible();
  await page.getByLabel("Virtual credits", { exact: true }).fill("125.5");
  await page.getByRole("button", { name: "REQUEST CREDITS" }).click();
  await expect(page.locator(".deposit-page-message")).toContainText(/pending/i);
  const requests = await (await request.get(`${api}/api/v1/deposits`, { headers })).json();
  expect(requests).toHaveLength(1);
  const creditRequest = requests[0];
  expect(creditRequest.status).toBe("pending");
  expect(Number((await (await request.get(`${api}/api/v1/auth/account`, { headers })).json()).balance)).toBe(0);
  expect((await request.get(`${api}/api/v1/admin/deposits`, { headers })).status()).toBe(403);

  const operator = await request.post(`${api}/api/v1/auth/login`, { data: { username: operatorUsername, password: operatorPassword } });
  expect(operator.ok()).toBeTruthy();
  const operatorToken = (await operator.json()).access_token;
  const operatorPage = await browser.newPage();
  await operatorPage.addInitScript(token => localStorage.setItem("dgn-ops-token", token), operatorToken);
  await operatorPage.goto(desktop!);
  await operatorPage.locator("#deposits-tab").click();
  const row = operatorPage.locator("#deposits-rows tr").filter({ hasText: `@${username}` });
  await expect(row).toContainText("125.50 créditos");
  await row.getByText("Revisar", { exact: true }).click();
  await row.getByRole("button", { name: "Aprobar", exact: true }).click();
  await expect(row).toContainText("Aprobado");
  await operatorPage.close();

  await page.reload();
  await expect(page.locator(".deposit-row").filter({ hasText: `Request #${creditRequest.id}` })).toContainText("Approved");
  await page.goto("/account");
  await expect(page.getByLabel("Virtual credits", { exact: true })).toHaveValue("125.50 credits");
  await expect(page.locator("main")).not.toContainText(/USD|Bank transfer|Debit card|USDC/);
  const ledger = await (await request.get(`${api}/api/v1/admin/balances`, { headers: { Authorization: `Bearer ${operatorToken}` } })).json();
  expect(ledger.filter((entry: { user_id: number }) => entry.user_id === account.user.id)).toHaveLength(1);
});
