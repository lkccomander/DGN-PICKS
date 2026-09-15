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
