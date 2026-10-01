# MLB Stats API source note

## Current use

DGN-PICKS uses the public MLB Stats API schedule endpoint only for a read-only
development preview of today's MLB matchups:

`https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=YYYY-MM-DD`

No odds, lines, logos or other MLB content are copied into the product by this
adapter.

## Distribution restriction

MLB's published digital-property terms describe personal, non-commercial use
and restrict reproduction, distribution and derivative use without permission.
Before DGN-PICKS uses this feed in a monetized or publicly distributed product,
obtain written permission or replace it with a licensed commercial provider.

## Operational rule

Keep the adapter read-only and rate-limited. Do not use it as proof of commercial
data rights. Any future persistence or scheduled production ingestion requires a
rights review and an explicit decision-log entry.
