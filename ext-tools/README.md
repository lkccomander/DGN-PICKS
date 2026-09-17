# DGN-PICKS Ops Console

Desktop utility using Flask, CoreUI Bootstrap 5, pywebview, and Cytoscape.js.

Run from Windows PowerShell:

    cd C:\Projects\DGN-PICKS\ext-tools
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python app.py

Prerequisites: Git, Railway CLI authenticated with railway login, and the
repository linked to the intended Railway project/environment.

The Git tab runs explicit Git argument lists, then watches Railway with
railway deployment list --json. The Graph tab reads
../graphify-out/graph.json, polls for changes, and can run graphify . --update.
Set GRAPHIFY_COMMAND if the local graphify installation needs another command.

## Usuarios (desktop y web)

La pestaña **Usuarios** de Ops Console y **Usuarios** en la web `/admin`
permiten buscar, crear, editar, activar/desactivar y eliminar cuentas.
Ambas usan la misma API y requieren iniciar sesión como administrador o editor.

El desktop usa `http://127.0.0.1:8000` por defecto. Para apuntarlo a otra API,
configura su origen antes de iniciar la app (sin el sufijo `/api/v1`):

```powershell
$env:DGN_OPS_API_URL = "https://tu-api.example.com"
.\.venv\Scripts\python.exe app.py
```

La API debe estar ejecutándose, con sus migraciones aplicadas y autenticación
configurada (`DGN_AUTH_SECRET`, `DGN_AUTH_USERNAME`, `DGN_AUTH_PASSWORD` y
`DGN_AUTH_ROLE=admin` para el operador configurado). El desktop no carga archivos
`.env` automáticamente. No guarda el token en disco; cerrar sesión o la ventana
lo descarta. Las contraseñas existentes nunca se muestran.

- El nombre de usuario no cambia después de crearlo.
- Una contraseña vacía al editar mantiene la anterior; una nueva requiere al menos 8 caracteres.
- Email y país pueden vaciarse.
- Si un usuario tiene picks, la API rechaza su eliminación: desactívalo para conservar el historial.
- Los errores de conexión, validación y duplicados se muestran sin perder el formulario.

### Verificación local

Desde `ext-tools`:

```powershell
.\.venv\Scripts\python.exe -m unittest test_users_api -v
```

Las pruebas de interfaz están en `apps/web/e2e/users.spec.ts`. Con web y desktop
ejecutándose localmente, desde `apps/web`:

```powershell
$env:E2E_WEB_URL = "http://127.0.0.1:3191"
$env:E2E_DESKTOP_URL = "http://127.0.0.1:5189"
npx playwright test e2e/users.spec.ts --workers=1
```

Estas pruebas interceptan las respuestas del CRUD y no modifican usuarios reales.
Se puede seleccionar un navegador instalado con `E2E_BROWSER_CHANNEL=chrome` o
`msedge`; sin esa variable se usa el Chromium de Playwright.

## Configuración

La pestaña **Configuración** guarda las variables de desktop y de la API local
para el usuario actual de Windows. No crea archivos .env ni guarda secretos en
el repositorio. DATABASE_URL, DGN_AUTH_SECRET, DGN_AUTH_PASSWORD y
DGN_API_WRITE_KEY no se muestran después de guardarse; deja esos campos vacíos
para conservar el valor existente.

La prueba de conexión comprueba <DGN_OPS_API_URL>/api/health. Cambiar la URL o
el puerto de la consola requiere reiniciar la app desktop. **Iniciar API local**
solo funciona cuando la URL apunta a http://127.0.0.1:8000 o localhost, y
solo puede detener el proceso iniciado por esa misma ventana. Railway no se
modifica desde este tab.
