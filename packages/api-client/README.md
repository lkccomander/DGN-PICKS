# DGN-PICKS API client

This package is generated from the FastAPI OpenAPI contract. Do not edit
`src/index.ts` or `openapi.json` directly. Regenerate both after an API
contract change:

```powershell
$env:PYTHONPATH = "apps/api/src"
.\.venv\Scripts\python.exe scripts\generate_api_client.py
```

If the local Python environment is not installed, pass a downloaded OpenAPI
document instead:

```powershell
Invoke-WebRequest https://dgn-picks-production.up.railway.app/openapi.json -OutFile .\openapi.json
python scripts\generate_api_client.py --input .\openapi.json
Remove-Item .\openapi.json
```
