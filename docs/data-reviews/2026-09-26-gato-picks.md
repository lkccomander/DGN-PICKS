# Gato picks — source and evaluation review, 2026-09-26

Source: `picks09262026.md`. Owner: `gato`. Each item is recorded as a single pick. The shared-game note is preserved; no parlay or combined odds were supplied.

All lines and Over sides come from the user. Names are source-backed normalizations of the user wording; the original text is preserved in import metadata. No odds were provided. Stake uses the existing application default of 1u, explicitly recorded as defaulted.

## New picks

| Pick | Game (away at home) | Kickoff UTC | Supplied line | Sources |
|---|---|---|---|---|
| Trinidad Chambliss | Ole Miss at Florida | 2026-09-26T19:30:00Z | Over 25.5 rushing yards | [Player](https://olemisssports.com/sports/football/roster/chambliss-trinidad/6554), [event](https://floridagators.com/game-center/27906) |
| Dallas Wilson | Ole Miss at Florida | 2026-09-26T19:30:00Z | Over 48.5 receiving yards | [Player](https://floridagators.com/sports/football/roster/dallas-wilson/18309), [event](https://floridagators.com/game-center/27906) |
| Aaron Philo | Ole Miss at Florida | 2026-09-26T19:30:00Z | Over 229.5 passing yards | [Player](https://floridagators.com/sports/football/roster/aaron-philo/18345), [event](https://floridagators.com/game-center/27906) |
| Cam Coleman | Texas at Tennessee | 2026-09-26T16:00:00Z | Over 61.5 receiving yards | [Player](https://texaslonghorns.com/sports/football/roster/cam-coleman/16950), [event](https://texaslonghorns.com/sports/football/schedule/text) |
| DJ Vonnahme | Iowa at Michigan | 2026-09-26T19:38:00Z | Over 28.5 receiving yards | [Player](https://hawkeyesports.com/sports/football/roster/player/dj-vonnahme), [event](https://hawkeyesports.com/sports/football/schedule/season/2026-27) |
| Anthony Evans III | Missouri at Mississippi State | 2026-09-26T23:45:00Z | Over 79.5 receiving yards | [Player](https://hailstate.com/sports/football/roster/anthony-evans%20iii/12875), [event](https://hailstate.com/sports/football/schedule/text) |
| Winston Watkins Jr. | Texas A&M at LSU | 2026-09-26T23:30:00Z | Over 54.5 receiving yards | [Player](https://lsusports.net/sports/fb/roster/player/winston-watkins-jr), [event](https://lsusports.net/sports/fb/schedule) |
| Ed Small | TCU at UCF | 2026-09-26T19:30:00Z | Over 69.5 receiving yards | [Player](https://gofrogs.com/sports/football/roster/ed-small/18258), [event](https://gofrogs.com/sports/football/schedule/text) |
| Devon Dampier | Utah at Iowa State | 2026-09-26T19:30:00Z | Over 219.5 passing yards | [Player](https://utahutes.com/sports/football/roster/devon-dampier/17509), [event](https://utahutes.com/news/2026/9/14/football-no-17-utah-at-iowa-state-kickoff-time-announced) |
| Sedrick Alexander | Vanderbilt at Auburn | 2026-09-26T20:15:00Z | Over 41.5 rushing yards | [Player](https://vucommodores.com/sports/football/roster/player/sedrick-alexander), [event](https://vucommodores.com/sports/football/schedule) |

At the initial evidence review (2026-09-26 17:45 UTC), no final statistics for these events were verified. Import results remain pending. Official roster and schedule links establish identity/event only; they do not establish taken prices or final performance.

## Original 13 definitions

All 13 original definitions were reviewed. They lack authoritative event date/opponent and taken odds. Malakai Toney 72.5 receiving yards also lacks an Over/Under side. The user was asked for those facts. No win/loss/push/void can be honestly assigned from the names and lines alone.

Every entry below was checked against the preserved public definition. Result for each: **unresolved; not graded**. Missing odds prevent priced P/L, but event identity (and side where absent) is the immediate blocker to verifying win/loss.

| # | Original pick | Missing grading facts |
|---|---|---|
| 1 | Stanford +24.5 | Event date/jornada or opponent |
| 2 | Malakai Toney 72.5 receiving yards | Event date/jornada or opponent; Over/Under |
| 3 | Josh Hoover Over 246.5 passing yards | Event date/jornada or opponent |
| 4 | Indiana Over 56.5 game total | Event date/jornada or opponent |
| 5 | Duke Over 51.5 game total | Event date/jornada or opponent |
| 6 | Auburn Over 58.5 game total | Event date/jornada or opponent |
| 7 | LSU Over 50.5 game total | Event date/jornada or opponent |
| 8 | UCLA Over 54.5 game total | Event date/jornada or opponent |
| 9 | Washington Over 50.5 game total | Event date/jornada or opponent |
| 10 | Notre Dame -20.5 | Event date/jornada or opponent |
| 11 | Ole Miss -6.5 | Event date/jornada or opponent |
| 12 | Houston Over 52.5 game total | Event date/jornada or opponent |
| 13 | SMU Over 53.5 game total | Event date/jornada or opponent |

Six older materialized records came from synthetic fixtures. Their synthetic event dates, scores and prices are not evidence of real outcomes. After a strict legacy-manifest preview, production records 1, 3, 4, 5, 6 and 7 were archived reversibly; no ambiguous matches were reported. The original 13 definitions remain publicly visible.

## Completion evidence

- [x] API and web deployed from `53c75c5` on 2026-09-27 UTC (September 26 in Guatemala).
- [x] Imported IDs 8–17 assigned to Gato, production user ID 7; ten active picks across eight games.
- [x] All imported odds remain null, each stake is defaulted to 1u, and all results are pending.
- [x] Repeat production preview found all ten existing records and zero new records to create.
- [x] Public API summary: ten pending picks and 10u pending exposure; settled profit/ROI unavailable.
- [x] Anonymous Playwright acceptance passed on desktop and mobile, including each pick/date/unknown-odds label and absence of editing controls.
- [ ] Obtain the missing original-card facts and verify official final results before assigning outcomes.

Full deployment IDs, test evidence, and GitHub synchronization limitation: [publication checkpoint](../checkpoints/2026-09-26-gato-publication.md).
