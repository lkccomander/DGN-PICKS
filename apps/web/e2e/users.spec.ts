import { expect, test } from "@playwright/test";

for (const surface of ["web", "desktop"] as const) {
  test.describe(surface + " user management", () => {
    test.setTimeout(60000);
    const origin = surface === "web" ? process.env.E2E_WEB_URL : process.env.E2E_DESKTOP_URL;
    test.skip(!origin, "Set E2E_WEB_URL and/or E2E_DESKTOP_URL to a local test server.");
    test("creates, searches, edits, deactivates and deletes; preserves failures", async ({ page }) => {
      let users = [{ id: 1, username: "gato", display_name: "Gato", email: "gato@example.com" as string | null, country: "GT" as string | null, active: true, created_at: "2026-09-17T12:30:00Z" }];
      const writes: Array<{ method: string; body: Record<string, unknown> }> = [];
      let failNext = false;
      const api = surface === "web" ? "/api/admin/users" : "/api/users";
      await page.route((url) => url.pathname === api || url.pathname.startsWith(api + "/"), async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        if (url.pathname.endsWith("/login")) return route.fulfill({ json: { access_token: "fixture-token", role: "admin" } });
        if (request.method() === "GET") return route.fulfill({ json: users });
        const body = request.postDataJSON() ?? {};
        writes.push({ method: request.method(), body });
        if (failNext) { failNext = false; return route.abort("failed"); }
        const id = Number(url.pathname.split("/").at(-1));
        if (request.method() === "POST") {
          const user = { ...body, id: 2 }; users.push(user);
          return route.fulfill({ status: 201, json: user });
        }
        if (request.method() === "PATCH") {
          const user = users.find((user) => user.id === id)!;
          Object.assign(user, body); return route.fulfill({ json: user });
        }
        if (id === 1) return route.fulfill({ status: 409, json: { detail: "User owns picks; deactivate instead" } });
        users = users.filter((user) => user.id !== id);
        return route.fulfill({ status: 204 });
      });
      if (surface === "web") {
        await page.addInitScript(() => localStorage.setItem("dgn-admin-token", "fixture-token"));
        await page.goto(origin + "/admin");
      } else {
        await page.route("**/api/graph", (route) => route.fulfill({ json: { nodes: [], edges: [], meta: {} } }));
        await page.goto(origin!);
        await page.locator("#users-tab").click();
        await expect(page.locator("#users-workspace")).toBeVisible();
        await expect(page.locator("#users-rows")).toContainText("Inicia sesión como administrador o editor");
        await expect(page.getByRole("button", { name: "Nuevo usuario", exact: true })).toBeDisabled();
        await page.locator("#users-login").getByLabel("Usuario administrador").fill("admin");
        await page.locator("#users-login").getByLabel("Contraseña", { exact: true }).fill("test-password");
        await page.getByRole("button", { name: "Entrar", exact: true }).click();
      }
      const row = (name: string) => page.locator(surface === "web" ? ".admin-table article" : "#users-rows tr").filter({ hasText: "@" + name });
      await expect(row("gato")).toBeVisible();
      if (surface === "desktop") {
        await expect(row("gato")).toContainText("2026-09-17 12:30:00 UTC");
        await expect(row("gato").locator("td")).toHaveCount(8);
        await page.getByLabel("Buscar usuarios").fill("GT");
        await expect(row("gato")).toBeVisible();
        await page.getByLabel("Buscar usuarios").fill("");
        await page.locator("#users-filter").selectOption("inactive");
        await expect(row("gato")).toHaveCount(0);
        await page.locator("#users-filter").selectOption("all");
        await page.getByRole("button", { name: "Nuevo usuario", exact: true }).click();
      }
      await page.getByLabel("Usuario", { exact: true }).fill("demo");
      await page.getByLabel("Nombre visible", { exact: true }).fill("Demo User");
      await page.getByLabel("Email", { exact: true }).fill("demo@example.com");
      await page.getByLabel("País", { exact: true }).fill("GT");
      await page.getByLabel("Contraseña nueva (opcional)", { exact: true }).fill("demo-password");
      await page.getByRole("button", { name: "Crear usuario", exact: true }).click();
      await expect(row("demo")).toBeVisible();
      await page.getByLabel("Buscar usuarios").fill("demo");
      await expect(row("gato")).toHaveCount(0);
      await row("demo").getByRole("button", { name: "Editar", exact: true }).click();
      await expect(page.getByLabel("Usuario", { exact: true })).toBeDisabled();
      await expect(page.getByLabel("Contraseña nueva (opcional)", { exact: true })).toHaveValue("");
      await page.getByLabel("Email", { exact: true }).fill("");
      await page.getByLabel("País", { exact: true }).fill("");
      await page.getByRole("button", { name: "Guardar cambios", exact: true }).click();
      await expect(row("demo")).toContainText("Sin email");
      const patch = writes.find((entry) => entry.method === "PATCH")!;
      expect(patch.body).toMatchObject({ email: null, country: null });
      expect(patch.body).not.toHaveProperty("username");
      expect(patch.body).not.toHaveProperty("password");
      await row("demo").getByRole("button", { name: "Desactivar", exact: true }).click();
      await expect(row("demo")).toContainText("Inactivo");
      page.once("dialog", (dialog) => dialog.dismiss());
      await row("demo").getByRole("button", { name: "Eliminar", exact: true }).click();
      await expect(row("demo")).toBeVisible();
      page.once("dialog", (dialog) => dialog.accept());
      await row("demo").getByRole("button", { name: "Eliminar", exact: true }).click();
      await expect(row("demo")).toHaveCount(0);
      await page.getByLabel("Buscar usuarios").fill("");
      page.once("dialog", (dialog) => dialog.accept());
      await row("gato").getByRole("button", { name: "Eliminar", exact: true }).click();
      await expect(surface === "web" ? page.locator(".admin-error[role=alert]") : page.locator("#users-message")).toContainText(/picks/);
      await expect(row("gato")).toBeVisible();
      failNext = true;
      await row("gato").getByRole("button", { name: "Desactivar", exact: true }).click();
      await expect(surface === "web" ? page.locator(".admin-error[role=alert]") : page.locator("#users-message")).not.toBeEmpty();
      await expect(row("gato").getByRole("button", { name: "Desactivar", exact: true })).toBeEnabled();
      await page.screenshot({ path: "test-results/users-" + surface + ".png", fullPage: true });
      if (surface === "desktop") {
        await page.getByRole("button", { name: "Cerrar sesión", exact: true }).click();
        await expect(page.locator("#users-workspace")).toBeVisible();
        await expect(page.locator("#users-rows")).toContainText("Inicia sesión como administrador o editor");
        await expect(row("gato")).toHaveCount(0);
        await expect(page.getByRole("button", { name: "Nuevo usuario", exact: true })).toBeDisabled();
      }
    });
  });
}
