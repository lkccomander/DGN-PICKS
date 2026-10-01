# Timestamped Ops Console Git status

## Purpose
Make each Ver estado check visible with a UTC timestamp and preserve it in a local log.

## Scope / Non-scope
Git status display, terminal output, append-only UTF-8 log, and focused verification.
No API/domain semantics or release changes.

## Progress
- [x] Inspect console and project guidance.
- [x] Implement timestamped reporting and append-only logging.
- [x] Validate console tests and document the log location.

## Implementation plan
Format the Git result once in the status route, print it, append it under a lock,
and retain it in console state so polling preserves the display. Surface file
write failures without losing the Git result or overwriting an active push.

## Validation
Check repeated success/error appends, terminal output, polling persistence,
unwritable log handling, and active push preservation. Run desktop unittest suite.

## Surprises & Discoveries
Polling previously replaced manually queried Git status after 2.5 seconds.
The repository already ignores *.log files.

## Decision Log
Use ext-tools/logs/git-status.log relative to app.py, independent of launch directory.
Store UTC timestamps and serialize log writes within the desktop process.

## Outcomes & Retrospective
Implemented and documented. All 21 desktop unittest tests passed, including three
new status logging tests. Git diff whitespace checks passed. Tests used a
temporary Linux virtual environment; the native Windows desktop was not launched.
