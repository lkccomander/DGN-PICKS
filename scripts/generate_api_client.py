#!/usr/bin/env python3
"""Generate the small TypeScript API client consumed by the web application.

The FastAPI OpenAPI document is the contract source of truth.  This generator
keeps a checked-in document and client so a frontend build does not depend on a
running API, while making contract refreshes explicit and repeatable.
"""

from __future__ import annotations

import json
import re
import argparse
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "api-client"
SCHEMA_PATH = PACKAGE / "openapi.json"
CLIENT_PATH = PACKAGE / "src" / "index.ts"


def schema_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return f'Components["schemas"]["{schema["$ref"].rsplit("/", 1)[-1]}"]'
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])
    if "anyOf" in schema:
        return " | ".join(schema_type(item) for item in schema["anyOf"])
    if "oneOf" in schema:
        return " | ".join(schema_type(item) for item in schema["oneOf"])

    kind = schema.get("type")
    if kind == "array":
        return f"Array<{schema_type(schema.get('items', {}))}>"
    if kind == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        if not properties and schema.get("additionalProperties"):
            return "Record<string, unknown>"
        required = set(schema.get("required", []))
        fields = [
            f"{json.dumps(name)}{' ' if name in required else '?'}: {schema_type(value)}"
            for name, value in properties.items()
        ]
        return "{ " + "; ".join(fields) + " }"
    if kind in {"integer", "number"}:
        return "number"
    if kind == "boolean":
        return "boolean"
    if kind == "null":
        return "null"
    return "string" if kind == "string" else "unknown"


def api_path(path: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        parameter = match.group(1)
        return "${number}" if parameter.endswith("_id") or parameter == "id" else "${string}"

    return "`" + re.sub(r"\{([^}]+)\}", replacement, path) + "`"


def render_client(document: dict[str, Any]) -> str:
    components = document.get("components", {}).get("schemas", {})
    rendered_components = "\n".join(
        f'      "{name}": {schema_type(schema)};'
        for name, schema in sorted(components.items())
    )
    rendered_paths = "\n".join(f"  | {api_path(path)}" for path in sorted(document["paths"]))
    return f'''/*
 * GENERATED FILE — do not edit by hand.
 * Source: packages/api-client/openapi.json
 * Regenerate: PYTHONPATH=apps/api/src .venv/bin/python scripts/generate_api_client.py
 */

export type Components = {{
  schemas: {{
{rendered_components}
  }};
}};

export type ApiPath =
{rendered_paths};

export type ApiPathWithQuery = ApiPath | `${{ApiPath}}?${{string}}`;

export class ApiError extends Error {{
  constructor(public readonly status: number, message: string) {{
    super(message);
    this.name = "ApiError";
  }}
}}

export class DgnPicksApiClient {{
  constructor(
    private readonly baseUrl: string,
    private readonly fetchImpl: typeof fetch = fetch,
  ) {{}}

  async request<T>(path: ApiPathWithQuery, options: RequestInit = {{}}): Promise<T> {{
    const response = await this.fetchImpl(`${{this.baseUrl}}${{path}}`, {{
      ...options,
      headers: {{ Accept: "application/json", ...options.headers }},
    }});
    if (!response.ok) {{
      const detail = await response.text();
      throw new ApiError(response.status, detail || response.statusText);
    }}
    if (response.status === 204) return undefined as T;
    return response.json() as Promise<T>;
  }}

  get<T>(path: ApiPathWithQuery, signal?: AbortSignal): Promise<T> {{
    return this.request<T>(path, {{ signal }});
  }}

  post<T>(path: ApiPathWithQuery, body: unknown, options: RequestInit = {{}}): Promise<T> {{
    return this.request<T>(path, {{
      ...options,
      method: "POST",
      body: JSON.stringify(body),
      headers: {{ "Content-Type": "application/json", ...options.headers }},
    }});
  }}
}}
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the TypeScript client from DGN-PICKS OpenAPI.")
    parser.add_argument("--input", type=Path, help="Existing OpenAPI JSON file (avoids importing the local API).")
    arguments = parser.parse_args()
    if arguments.input:
        document = json.loads(arguments.input.read_text(encoding="utf-8"))
    else:
        from dgn_picks_api.main import app

        document = app.openapi()
    CLIENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CLIENT_PATH.write_text(render_client(document), encoding="utf-8")
    print(f"Generated {SCHEMA_PATH.relative_to(ROOT)} and {CLIENT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
