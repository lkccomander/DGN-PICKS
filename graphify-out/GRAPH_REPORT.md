# Graph Report - .  (2026-09-15)

## Corpus Check
- 153 files · ~309,442 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 428 nodes · 281 edges · 158 communities (155 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_MVP Product Spec|MVP Product Spec]]
- [[_COMMUNITY_Architecture Invariants|Architecture Invariants]]
- [[_COMMUNITY_Project Status|Project Status]]
- [[_COMMUNITY_M2 Domain Design|M2 Domain Design]]
- [[_COMMUNITY_UI Design System|UI Design System]]
- [[_COMMUNITY_Skill Documentation|Skill Documentation]]
- [[_COMMUNITY_M2 Implementation Plan|M2 Implementation Plan]]
- [[_COMMUNITY_Dashboard Plan|Dashboard Plan]]
- [[_COMMUNITY_Pick Management|Pick Management]]
- [[_COMMUNITY_API and Deployment|API and Deployment]]
- [[_COMMUNITY_Users CRUD|Users CRUD]]
- [[_COMMUNITY_API Implementation Plan|API Implementation Plan]]
- [[_COMMUNITY_Deployment Status|Deployment Status]]
- [[_COMMUNITY_Catalog CRUD|Catalog CRUD]]
- [[_COMMUNITY_M1 Bootstrap|M1 Bootstrap]]
- [[_COMMUNITY_Issue Tracking|Issue Tracking]]
- [[_COMMUNITY_Branding|Branding]]
- [[_COMMUNITY_Picks Dashboard|Picks Dashboard]]
- [[_COMMUNITY_API Design|API Design]]
- [[_COMMUNITY_Dashboard Design|Dashboard Design]]
- [[_COMMUNITY_Implementation Specs|Implementation Specs]]
- [[_COMMUNITY_Domain Glossary|Domain Glossary]]
- [[_COMMUNITY_Local Issue Tracking|Local Issue Tracking]]
- [[_COMMUNITY_Architecture Docs|Architecture Docs]]
- [[_COMMUNITY_Project Instructions|Project Instructions]]
- [[_COMMUNITY_Brand Assets|Brand Assets]]
- [[_COMMUNITY_Logo Assets|Logo Assets]]
- [[_COMMUNITY_Icon Assets|Icon Assets]]
- [[_COMMUNITY_Brand Mark|Brand Mark]]
- [[_COMMUNITY_Triage Labels|Triage Labels]]
- [[_COMMUNITY_API Client|API Client]]
- [[_COMMUNITY_Execution Plans|Execution Plans]]

## God Nodes (most connected - your core abstractions)
1. `DGN-PICKS Architecture` - 5 edges
2. `DGN-PICKS Session Status` - 4 edges
3. `M2 Domain and Seed Implementation Plan` - 4 edges
4. `Compact Sportsbook Dashboard Plan` - 4 edges
5. `GitHub to Railway Deployment Workflow` - 4 edges
6. `Documentation Pack Manifest` - 3 edges
7. `DGN-PICKS README` - 3 edges
8. `DGN-PICKS Branding` - 3 edges
9. `Modular Monolith` - 3 edges
10. `Deterministic Local Fixtures` - 3 edges

## Surprising Connections (you probably didn't know these)
- `API Python Requirements` --implements--> `Modular Monolith`  [INFERRED]
  apps/api/requirements.txt → ARCHITECTURE.md
- `Compact Sportsbook Dashboard Plan` --conceptually_related_to--> `GitHub to Railway Deployment Workflow`  [INFERRED]
  docs/exec-plans/active/2026-09-08-compact-dashboard.md → README.md
- `Documentation Pack Manifest` --references--> `GitHub to Railway Deployment Workflow`  [EXTRACTED]
  PACK-MANIFEST.txt → README.md
- `Documentation Pack Manifest` --references--> `Seed Users gato daran noch`  [EXTRACTED]
  PACK-MANIFEST.txt → AGENTS.md
- `Project Plans` --references--> `M2 Domain and Seed Implementation Plan`  [EXTRACTED]
  PLANS.md → docs/exec-plans/active/2026-09-07-m2-domain-seed.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **DGN-PICKS Source-of-Truth Documents** — agents_dgn_picks, architecture_dgn_picks, branding_dgn_picks, plans_dgn_picks [EXTRACTED 1.00]
- **M2 Domain Delivery** — m2_domain_seed_plan, m2_fixture_provider, m2_seed_service, m2_api_v1 [EXTRACTED 1.00]
- **Dashboard Brand Expression** — compact_dashboard_plan, dashboard_original_ui, branding_stripe, branding_navy_interface [EXTRACTED 1.00]
- **Immutable Taken Price Pick Lifecycle** — architecture_odds_snapshot, architecture_pick_taken_price, pick_management_plan, pick_management_pending_rules [EXTRACTED 1.00]
- **Development Write Controls** — m3_users_crud_plan, m3_development_write_boundary, pick_management_plan [EXTRACTED 1.00]
- **DGN-PICKS Logo Identity** — chatgpt_image_sep_7_2026_10_49_38_am_1_dgn_picks_logo, chatgpt_image_sep_7_2026_10_49_38_am_1_dgn_picks_wordmark, chatgpt_image_sep_7_2026_10_49_38_am_1_brand_stripe [EXTRACTED 1.00]
- **DGN wordmark over stripe on navy field** — ChatGPT_Image_Sep_7_2026_10_49_38_AM_2_dgn_brand_mark, ChatGPT_Image_Sep_7_2026_10_49_38_AM_2_dgn_wordmark, ChatGPT_Image_Sep_7_2026_10_49_38_AM_2_national_color_brand_stripe, ChatGPT_Image_Sep_7_2026_10_49_38_AM_2_dark_navy_background [EXTRACTED 1.00]
- **DGN Brand Mark Composition** — ChatGPT_Image_Sep_7_2026_10_49_39_AM_3_brand_asset, ChatGPT_Image_Sep_7_2026_10_49_39_AM_3_dgn_wordmark, ChatGPT_Image_Sep_7_2026_10_49_39_AM_3_brand_stripe [EXTRACTED 1.00]
- **DGN-PICKS Icon Brand Composition** — dgn_picks_icon_square_transparent_dgn_picks_icon, dgn_picks_icon_square_transparent_dgn_wordmark, dgn_picks_icon_square_transparent_brand_stripe, dgn_picks_icon_square_transparent_transparent_background [EXTRACTED 1.00]

## Communities (158 total, 3 thin omitted)

### Community 0 - "MVP Product Spec"
Cohesion: 0.04
Nodes (46): 10. Fixture requirements, 11. API, 12. UI screens, 13. Calculations, 14. Provider boundary, 15. Data integrity, 16. Observability, 17. Security baseline (+38 more)

### Community 1 - "Architecture Invariants"
Cohesion: 0.09
Nodes (29): API Python Requirements, DGN-PICKS Architecture, Modular Monolith, Append-Only OddsSnapshot, Pick Taken Line and Price Preservation, Provider Boundary, Non-Monetary Virtual Tokens, DGN-PICKS Branding (+21 more)

### Community 2 - "Project Status"
Cohesion: 0.12
Nodes (15): Active task: compact sportsbook-style frontend, Current status, Dashboard frontend, DGN-PICKS — session handoff, Global checklist, Known follow-up work, M1 — Bootstrap foundation, M2 — Domain, deterministic seed, and API v1 (+7 more)

### Community 3 - "M2 Domain Design"
Cohesion: 0.13
Nodes (14): Acceptance criteria, API v1, Architecture, Calculations, Components, Domain decisions, Error handling, Goal (+6 more)

### Community 4 - "UI Design System"
Cohesion: 0.15
Nodes (12): 1. Paleta y estilo general, 2. Header (barra superior), 3. Barra de navegación principal (debajo del header), 4. Barra de herramientas (debajo de la navegación), 5.1 Sidebar izquierdo, 5.2 Contenido central, 5.3 Bet Slip (panel derecho, fijo/sticky), 5. Layout general (3 columnas) (+4 more)

### Community 5 - "Skill Documentation"
Cohesion: 0.17
Nodes (11): 1. Explore, 2. Present findings and ask, 3. Confirm and edit, 4. Write, 5. Done, Agent skills, Domain docs, Issue tracker (+3 more)

### Community 6 - "M2 Implementation Plan"
Cohesion: 0.17
Nodes (11): Current status — 2026-09-07, Global Constraints, M2 Domain and Seed Implementation Plan, Task 1: SQLAlchemy base and domain models, Task 2: Alembic migration and database wiring, Task 3: Odds and pick calculation rules, Task 4: Provider contract and deterministic fixtures, Task 5: Transactional idempotent seed service (+3 more)

### Community 7 - "Dashboard Plan"
Cohesion: 0.20
Nodes (9): Compact sportsbook dashboard, Decision Log, Implementation plan, Outcomes & Retrospective, Progress, Purpose, Scope / Non-scope, Surprises & Discoveries (+1 more)

### Community 8 - "Pick Management"
Cohesion: 0.20
Nodes (9): Decision Log, Implementation plan, Outcomes & Retrospective, Pick management GUI, Progress, Purpose, Scope / Non-scope, Surprises & Discoveries (+1 more)

### Community 9 - "API and Deployment"
Cohesion: 0.20
Nodes (9): API v1 usage, Authentication and admin catalog, Baseline stack, Codex reading order, Current milestone status, Deployment, DGN-PICKS, Local E2E validation (+1 more)

### Community 10 - "Users CRUD"
Cohesion: 0.22
Nodes (8): API contract, Decision Log, M3 users CRUD/API contract, Outcomes & Retrospective, Progress, Purpose, Scope / Non-scope, Validation

### Community 11 - "API Implementation Plan"
Cohesion: 0.22
Nodes (8): API v1 Implementation Plan, Global Constraints, Self-review checklist, Task 1: API schemas and database dependency, Task 2: Read-only users, games, markets, and odds routes, Task 3: Pick creation and pick listing, Task 4: Analytics and development seed route, Task 5: Migration and integration validation

### Community 12 - "Deployment Status"
Cohesion: 0.22
Nodes (8): 1. DGN-PICKS (Primary Service), 2. dgnweb (Frontend/Web Service), 3. Postgres (Database), DGN-PICKS Project Status Report, Overall Project Health: ✅ HEALTHY, Project Information, Service Status Breakdown, Summary

### Community 13 - "Catalog CRUD"
Cohesion: 0.25
Nodes (7): Decision Log, M3 data-management API, Outcomes & Retrospective, Progress, Purpose, Scope / Non-scope, Validation

### Community 14 - "M1 Bootstrap"
Cohesion: 0.25
Nodes (7): Global Constraints, Milestone 1 Bootstrap Implementation Plan, Task 1: Repository tooling and local services, Task 2: FastAPI shell, Task 3: Next.js shell, Task 4: Database migration foundation, Task 5: Documentation and verification

### Community 15 - "Issue Tracking"
Cohesion: 0.29
Nodes (6): Conventions, Issue tracker: GitHub, Pull requests as a triage surface, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 16 - "Branding"
Cohesion: 0.29
Nodes (6): Conventions, Issue tracker: GitLab, Merge requests as a triage surface, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 17 - "Picks Dashboard"
Cohesion: 0.29
Nodes (6): Approved brand treatment, Asset locations, DGN-PICKS Branding, Initial palette, Name, Visual direction

### Community 18 - "API Design"
Cohesion: 0.29
Nodes (6): Global Constraints, Picks Dashboard Implementation Plan, Task 1: Confirm Existing Data and Route Boundaries, Task 2: Add the Picks API Contract, Task 3: Add Frontend API Client and Dashboard State, Task 4: Verify Full Stack and Deploy

### Community 19 - "Dashboard Design"
Cohesion: 0.29
Nodes (6): Architecture, DGN-PICKS API v1 Design, Endpoints, Pick and Odds Semantics, Scope, Testing

### Community 20 - "Implementation Specs"
Cohesion: 0.29
Nodes (6): API Contract, Architecture, Frontend Behavior, Picks Dashboard Design, Scope, Testing

### Community 21 - "Domain Glossary"
Cohesion: 0.33
Nodes (5): Before exploring, read these, Domain Docs, File structure, Flag ADR conflicts, Use the glossary's vocabulary

### Community 22 - "Local Issue Tracking"
Cohesion: 0.33
Nodes (5): Conventions, Issue tracker: Local Markdown, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 23 - "Architecture Docs"
Cohesion: 0.40
Nodes (4): ARCHITECTURE.md — DGN-PICKS, Critical invariants, Overview, Repository boundaries

### Community 24 - "Project Instructions"
Cohesion: 0.67
Nodes (4): Dark Navy Background, DGN Brand Mark, White DGN Wordmark, Blue White Red White Blue Brand Stripe

### Community 25 - "Brand Assets"
Cohesion: 0.50
Nodes (3): AGENTS.md — DGN-PICKS, Rules, Source of truth

### Community 26 - "Logo Assets"
Cohesion: 0.50
Nodes (4): Blue White Red White Blue Brand Stripe, DGN-PICKS Logo, DGN-PICKS Wordmark, White Block Typography

### Community 27 - "Icon Assets"
Cohesion: 0.50
Nodes (4): Blue White Red White Blue Brand Stripe, DGN-PICKS Icon, DGN Wordmark, Transparent Background

### Community 28 - "Brand Mark"
Cohesion: 0.67
Nodes (3): DGN Brand Mark Asset, Blue White Red White Blue Brand Stripe, DGN Wordmark

## Knowledge Gaps
- **241 isolated node(s):** `Setup Matt Pocock's Skills`, `Process`, `1. Explore`, `2. Present findings and ask`, `3. Confirm and edit` (+236 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Setup Matt Pocock's Skills`, `Process`, `1. Explore` to the rest of the system?**
  _241 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MVP Product Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._
- **Should `Architecture Invariants` be split into smaller, more focused modules?**
  _Cohesion score 0.0896551724137931 - nodes in this community are weakly interconnected._
- **Should `Project Status` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `M2 Domain Design` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._