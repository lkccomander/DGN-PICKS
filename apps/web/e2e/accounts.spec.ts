import { createHmac } from "node:crypto";
import { expect, test } from "@playwright/test";

const api = process.env.E2E_API_URL?.replace(/\/$/, "");
const operatorUsername = process.env.E2E_OPERATOR_USERNAME;
const operatorPassword = process.env.E2E_OPERATOR_PASSWORD;
const password = "isolated-account-password";

test.skip(!api || !process.env.E2E_WEB_URL || !operatorUsername || !operatorPassword,
  "Requires the isolated API/web stack and operator credentials.");
test.beforeEach(() => {
  for (const origin of [api!, process.env.E2E_WEB_URL!]) {
    expect(["127.0.0.1", "localhost", "[::1]"]).toContain(new URL(origin).hostname);
  }
});

for (const width of [1440, 390]) {
  test(`registration, private account, login/logout and revoked session at ${width}px`, async ({ page, request }) => {
    await page.setViewportSize({ width, height: 1000 });
    const username = `account-${width}-${Date.now()}`;
    const email = `${username}@example.invalid`;
    await page.goto("/account");
    await expect(page.getByText("Sign in from the")).toBeVisible();
    expect((await request.get("/api/auth/account")).status()).toBe(401);

    await page.goto("/join");
    await page.getByLabel("First name", { exact: true }).fill("Acceptance");
    await page.getByLabel("Last name", { exact: true }).fill("User");
    await page.getByLabel("Email address", { exact: true }).fill(email);
    await page.getByLabel("Client ID", { exact: true }).fill(username);
    await page.getByLabel("Password", { exact: true }).fill(password);
    await page.getByLabel("Confirm password", { exact: true }).fill("different-password");
    await page.getByRole("checkbox").check();
    await page.getByRole("button", { name: "CREATE ACCOUNT" }).click();
    await expect(page.getByRole("alert")).toHaveText("Passwords do not match.");
    await page.getByLabel("Confirm password", { exact: true }).fill(password);
    await page.getByRole("button", { name: "CREATE ACCOUNT" }).click();
    await expect(page.getByRole("status")).toContainText("Account created.");
    await page.getByRole("link", { name: /Go to the board/ }).click();
    await expect(page.locator(".account-trigger")).toContainText("Acceptance User");
    await expect(page.locator(".market-strip")).toContainText(username.toUpperCase());
    await expect(page.getByText("No picks have been recorded for this user yet.")).toBeVisible();
    await page.locator(".account-trigger").click();
    await page.getByRole("link", { name: "My Account", exact: true }).click();
    await expect(page.locator(".profile-fields")).toContainText(email);
    await expect(page.locator(".profile-fields")).toContainText("Costa Rica");
    const token = await page.evaluate(() => localStorage.getItem("dgn-admin-token"));
    const publicUsers = await (await request.get(`${api}/api/v1/users`)).json();
    const user = publicUsers.find((item: { username: string }) => item.username === username);
    expect(user).toBeDefined();
    for (const item of publicUsers) {
      expect(item).not.toHaveProperty("email");
      expect(item).not.toHaveProperty("country");
      expect(item).not.toHaveProperty("password_hash");
    }
    expect((await request.get("/api/admin/users", { headers: { Authorization: `Bearer ${token}` } })).status()).toBe(403);

    await page.goto("/");
    await page.locator(".account-trigger").click();
    await page.getByRole("button", { name: /Log out/ }).click();
    await expect(page.getByRole("button", { name: "LOG IN", exact: true })).toBeVisible();
    expect(await page.evaluate(() => localStorage.getItem("dgn-admin-token"))).toBeNull();
    await page.goto("/account");
    await expect(page.locator(".profile-fields")).toHaveCount(0);
    await page.goto("/");
    await page.getByLabel("Email or Client ID").fill(email);
    await page.getByLabel("Password", { exact: true }).fill("wrong-password");
    await page.getByRole("button", { name: "LOG IN", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText("Invalid credentials");
    await page.getByLabel("Password", { exact: true }).fill(password);
    await page.getByRole("button", { name: "LOG IN", exact: true }).click();
    await expect(page.locator(".account-trigger")).toContainText(username.toUpperCase());

    // A real account mutation invalidates a previously valid browser session.
    const login = await request.post(`${api}/api/v1/auth/login`, { data: { username: operatorUsername, password: operatorPassword } });
    expect(login.ok()).toBeTruthy();
    const operator = await login.json();
    const deactivated = await request.patch(`${api}/api/v1/users/${user.id}`, {
      headers: { Authorization: `Bearer ${operator.access_token}` }, data: { active: false },
    });
    expect(deactivated.ok()).toBeTruthy();
    await page.goto("/account");
    await expect(page.getByText("Sign in from the")).toBeVisible();
    await expect(page.locator(".profile-fields")).toHaveCount(0);
    expect(await page.evaluate(() => localStorage.getItem("dgn-admin-token"))).toBeNull();
    await page.screenshot({ path: `test-results/account-${width}.png`, fullPage: true });
  });
}

test("an expired signed session clears private account data and disables board writes", async ({ page, request }) => {
  const secret = process.env.E2E_AUTH_SECRET;
  test.skip(!secret, "Set the isolated signing secret to exercise actual token expiry.");
  const username = `expiry-${Date.now()}`;
  const registered = await request.post(`${api}/api/v1/auth/register`, {
    data: { username, email: `${username}@example.invalid`, display_name: "Expiry User", password },
  });
  expect(registered.ok()).toBeTruthy();
  const { access_token: token } = await registered.json();
  const payload = JSON.parse(Buffer.from(token.split(".")[0], "base64url").toString());
  payload.exp = Math.floor(Date.now() / 1000) - 60;
  const raw = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const expired = `${raw}.${createHmac("sha256", secret!).update(raw).digest("base64url")}`;
  await page.goto("/account");
  await page.evaluate(({ token, username }) => {
    localStorage.setItem("dgn-admin-token", token);
    localStorage.setItem("dgn-active-user", username);
  }, { token: expired, username });
  await page.reload();
  await expect(page.getByText("Sign in from the")).toBeVisible();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("dgn-admin-token"))).toBeNull();
  await page.goto("/");
  await expect(page.getByRole("button", { name: "LOG IN", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: /^Track / })).toHaveCount(0);
  expect((await request.get("/api/auth/account", { headers: { Authorization: `Bearer ${expired}` } })).status()).toBe(401);
});
