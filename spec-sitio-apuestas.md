que estamos usando para el contexto de # Especificación de UI — Sitio de Apuestas Deportivas (estilo Pinnacle)

> Documento de referencia para que un agente de desarrollo construya un sitio de apuestas deportivas basado en el layout de Pinnacle.com. Describe estructura, componentes, datos de ejemplo y estilo visual — no incluye lógica de negocio real de apuestas (odds engine, pagos, KYC), que debe implementarse aparte.

## 1. Paleta y estilo general

- **Fondo principal:** azul marino muy oscuro (`#0f1a2e` / `#0a1628` aprox.)
- **Acento primario:** naranja (`#e8600a` / `#f47b20`) — usado en logo, botones CTA, tabs activos, línea decorativa superior
- **Texto:** blanco / gris claro sobre fondo oscuro
- **Tarjetas/paneles:** azul un poco más claro que el fondo (`#16233d` aprox.), bordes sutiles
- **Positivo (cuotas favoritas / línea en vivo):** verde
- **Negativo/alerta:** rojo (badge de marcador en vivo)
- **Tipografía:** sans-serif condensada, títulos en mayúsculas y bold para encabezados de sección
- Franja delgada naranja/degradada en el borde superior de toda la página

## 2. Header (barra superior)

- Logo a la izquierda ("PINNACLE" o nombre del sitio, con línea naranja debajo)
- Formulario de login inline a la derecha: input "Email or ClientID", input "password", botón **LOG IN** (outline) y botón **JOIN** (naranja, sólido)
- Debajo del login: enlace "Forgot email or password?"

## 3. Barra de navegación principal (debajo del header)

Tabs horizontales con ícono + texto, tab activo con línea naranja debajo:
1. Sports Betting (activo por defecto)
2. Live Centre
3. Casino
4. Live Casino
5. Virtual Sports
6. Betting Resources

## 4. Barra de herramientas (debajo de la navegación)

De izquierda a derecha:
- Campo de búsqueda con ícono de lupa ("Search")
- "Quick Bet" con ícono info + input numérico (stake rápido)
- Toggle de tema claro/oscuro (ícono sol + checkbox)
- Selector de formato de cuota: "American Odds" (dropdown; también debería soportar Decimal/Fractional/Hong Kong)
- Selector de idioma: "EN" (dropdown)
- Reloj con zona horaria: `HH:MM:SS (GMT-06:00)`
- "Help" con ícono de interrogación

## 5. Layout general (3 columnas)

```
[ Sidebar izquierdo ] [ Contenido central ] [ Bet Slip derecho ]
```

### 5.1 Sidebar izquierdo

**Sección "FAVOURITES"**
- Mensaje: "Log in or Join to change your favourites." (estado sin sesión)

**Sección "TOP SPORTS"** — lista de deportes con ícono + nombre + contador de eventos disponibles, alineado a la derecha:
| Ícono | Deporte | # eventos |
|---|---|---|
| ⚽ | Soccer | 835 |
| 🎧 | Esports | 25 |
| 🏈 | Football | 218 |
| 🎾 | Tennis | 105 |
| ⚾ | Baseball | 40 |
| 🏀 | Basketball | 75 |
| 🥊 | MMA | 18 |
| 🏒 | Hockey | 158 |
| ⛳ | Golf | 2 |
| 🏐 | Volleyball | 4 |
| 🤾 | Handball | 16 |

**Sección "A-Z SPORTS"** — misma lista pero ordenada alfabéticamente, incluye deportes adicionales (Aussie Rules, Boxing, Chess, Cricket, Cycling, Entertainment, etc.)

Cada fila del sidebar es clickeable → filtra el contenido central por ese deporte.

### 5.2 Contenido central

**Banner promocional (hero)**
- Imagen full-width con jugador de fútbol, texto grande "EVERY MATCH. EVERY MARKET. BET THE BEST LA LIGA ODDS" y botón CTA naranja "BET NOW"
- Debe soportar carrusel de banners (flechas de navegación implícitas)

**Carrusel de eventos destacados (cards horizontales)**
- 3 tarjetas visibles + flecha "›" para ver más
- Cada tarjeta contiene:
  - Categoría/liga (ej. "BASEBALL - MLB")
  - Equipo local vs visitante
  - Fecha y hora del evento
  - Mercado "Money Line – Game" con 2 botones de cuota (local / visitante), formato americano (+/-)

**Banner de aviso**
- Ícono info + texto: "Odds are delayed for guest users. Log In or Join to see our up to date odds." + botón de cerrar (X)

**Sección "SPORTS BETTING-LIVE"**
- Tabs: Soccer (activo, línea verde) / Esports / Tennis
- Tabla de eventos en vivo agrupados por liga (encabezado de liga clickeable con "›"):
  - Columnas: `1` `X` `2` (resultado) | `HANDICAP` (con controles ▲▼ de líneas alternativas) | `OVER` `UNDER`
  - Cada fila: nombre equipo local (marcador) / nombre equipo visitante (marcador), marcador en vivo con badge rojo si hay gol reciente, minuto/periodo del partido en verde (ej. "Second Half - 36'", "Half Time", "First Half - 29'")
  - Al final de cada liga: enlace "+N" (mercados adicionales)
  - Ligas de ejemplo: Portugal - Primeira Liga, Colombia - Primera B, Chile - Primera B, USA - MLS Next Pro League, Honduras - Reserve League

**Sección "HIGHLIGHTS"** (footer del contenido central, colapsable)

### 5.3 Bet Slip (panel derecho, fijo/sticky)

- Tabs: **BET SLIP** (activo) / **MY BETS**
- Subsección **SINGLES**
  - Estado vacío: ilustración de ticket + texto "There are no bets on your ticket." / "Click the odds to add a bet."
- Subsección **MULTIPLES**
  - Estado vacío: texto explicativo "To place a Multiple bet you need a minimum of two bets on your Bet Slip. Alternatively, you can place a Single bet."
- Subsección **TEASERS** (colapsada, con chevron ▼)

Al hacer click en cualquier cuota del sitio, se agrega como fila al Bet Slip (estado con selección, stake editable, cuota, ganancia potencial, botón eliminar).

## 6. Componentes reutilizables a implementar

1. `OddsButton` — botón de cuota (label + valor), estados: normal / seleccionado / suspendido (ícono ⊖ cuando no hay línea disponible, ver fila "Juticalpa - Lobos UPNFM")
2. `EventCard` — tarjeta de evento próximo (liga, equipos, fecha, mercado principal)
3. `LiveEventRow` — fila de tabla para evento en vivo (marcador, minuto, mercados 1X2/hándicap/O-U)
4. `LeagueHeader` — encabezado de agrupación de liga, clickeable/expandible
5. `SidebarSportItem` — ítem de deporte con ícono + contador
6. `BetSlip` — panel lateral con tabs Singles/Multiples/Teasers, estado vacío y estado con selecciones
7. `TopBar` — buscador, quick bet, theme toggle, formato de odds, idioma, reloj, help
8. `AuthHeader` — inputs de login + botones Log In/Join

## 7. Datos de ejemplo (mock) usados en el screenshot

```json
{
  "upcoming": [
    {"league": "MLB", "home": "Los Angeles Dodgers", "away": "Cincinnati Reds", "date": "2026-09-14T16:40", "homeOdds": -206, "awayOdds": 187},
    {"league": "MLB", "home": "Detroit Tigers", "away": "Toronto Blue Jays", "date": "2026-09-14T17:07", "homeOdds": 127, "awayOdds": -138},
    {"league": "MLB", "home": "New York Yankees", "away": "Minnesota Twins", "date": "2026-09-14T17:40", "homeOdds": -121, "awayOdds": 111}
  ],
  "live": [
    {"league": "Portugal - Primeira Liga", "home": "Braga", "away": "Estoril", "score": [1,0], "clock": "Second Half - 36'", "odds1": 159, "oddsX": -158, "odds2": 1515},
    {"league": "Colombia - Primera B", "home": "Tigres", "away": "Bogota", "score": [0,0], "clock": "Half Time", "odds1": 147, "oddsX": 112, "odds2": 429},
    {"league": "Chile - Primera B", "home": "Deportes Santa Cruz", "away": "Deportes Recoleta", "score": [0,0], "clock": "First Half - 29'", "odds1": 212, "oddsX": 177, "odds2": 151}
  ]
}
```

## 8. Requerimientos técnicos sugeridos

- **Stack:** React + TypeScript, Tailwind CSS (fácil de theming oscuro/naranja) o CSS Modules
- **Estado global:** contexto o store (Zustand/Redux) para el Bet Slip, ya que se comparte entre todas las vistas
- **Responsive:** en mobile, colapsar sidebar izquierdo a un drawer y el bet slip a un botón flotante/bottom sheet
- **Datos en vivo:** preparar la tabla de eventos live para actualizarse por WebSocket/polling (marcador y minuto cambian en tiempo real)
- **Accesibilidad:** contraste alto ya presente por el tema oscuro; asegurar foco visible en los `OddsButton`

## 9. Fuera de alcance de este documento

- Motor de cálculo de cuotas / trading de riesgo
- Procesamiento de pagos y KYC/verificación de identidad
- Cumplimiento legal y licencias de juego (varía por jurisdicción — validar requisitos locales antes de lanzar)
