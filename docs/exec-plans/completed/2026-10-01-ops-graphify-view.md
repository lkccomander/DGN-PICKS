# Graphify visualization in Ops Console

## Purpose
Use Graphify's actual interactive visualization and make the refresh button reliable.

## Scope / Non-scope
Desktop graph display, file metadata, update lifecycle and focused tests.
No changes to application domain semantics or deployment.

## Progress
- [x] Inspect Graphify output and installed CLI source.
- [x] Embed graph.html and reload only on file changes.
- [x] Correct update command and concurrent refresh handling.
- [x] Validate and document.

## Implementation plan
Serve the generated HTML in a script-enabled sandboxed iframe. Poll file metadata
without redrawing unchanged graphs. Show operation messages separately and disable
both refresh buttons until the worker completes. Use graphify update . to rebuild
code and regenerate Graphify outputs.

## Validation
Desktop tests for HTML serving, metadata, missing HTML, duplicate refresh and CLI
completion/error. JavaScript behavior checks for versioned reload and refresh states.

## Surprises & Discoveries
The prior visualization ignored Graphify links and recreated Cytoscape every eight
seconds. The existing CLI invocation used skill syntax rather than a CLI subcommand.
Installed Graphify update regenerates graph.html and preserves semantic data.

## Decision Log
Reuse the actual generated Graphify view. Enable same-origin framing only for its
route; the iframe allows scripts but has no same-origin permission.

## Outcomes & Retrospective
All 29 desktop unittest tests passed. JavaScript syntax and Node VM behavior
checks passed for Graphify links, unchanged-view preservation, update completion,
button lifecycle and missing HTML. Git whitespace checks passed. The native
Windows desktop was not launched; the Graphify view still needs network access
to load its existing vis-network CDN dependency.
