from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "graphify-out" / "graph.json"
app = Flask(__name__)
state: dict[str, Any] = {
    "git": {"running": False, "output": "", "error": ""},
    "deploy": {"running": False, "status": "idle", "message": "", "updated_at": None},
    "graph": {"running": False, "message": ""},
}
state_lock = threading.Lock()


def run_command(args: list[str], cwd: Path = ROOT, timeout: int = 120) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            args, cwd=cwd, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=timeout, check=False,
        )
        return completed.returncode, completed.stdout.strip()
    except FileNotFoundError:
        return 127, f"Command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"Timed out after {timeout}s: {' '.join(args)}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_state(section: str, **values: Any) -> None:
    with state_lock:
        state[section].update(values)


def railway_status() -> dict[str, Any]:
    railway = shutil.which("railway")
    if not railway:
        return {"status": "unavailable", "message": "Railway CLI no está en PATH."}
    code, output = run_command(
        [railway, "deployment", "list", "--json", "--limit", "1"], timeout=30
    )
    if code:
        return {"status": "error", "message": output or "Railway no pudo consultar deployments."}
    try:
        payload = json.loads(output)
        latest = payload[0] if isinstance(payload, list) and payload else payload
        raw_status = str(latest.get("status", "UNKNOWN")).upper()
        mapping = {"SUCCESS": "ready", "ACTIVE": "ready", "FAILED": "failed", "CRASHED": "failed"}
        return {
            "status": mapping.get(raw_status, "deploying"),
            "raw_status": raw_status,
            "deployment_id": latest.get("id"),
            "message": f"Último deployment: {raw_status}",
        }
    except json.JSONDecodeError:
        return {"status": "error", "message": f"Respuesta Railway inválida: {output[-500:]}"}


def monitor_deploy() -> None:
    started = time.time()
    set_state("deploy", running=True, status="deploying",
              message="Esperando estado de Railway…", updated_at=now())
    while time.time() - started < 20 * 60:
        result = railway_status()
        set_state("deploy", running=result["status"] == "deploying", **result, updated_at=now())
        if result["status"] in {"ready", "failed", "error", "unavailable"}:
            return
        time.sleep(5)
    set_state("deploy", running=False, status="timeout",
              message="Railway no terminó en 20 minutos.", updated_at=now())


def git_push(message: str, branch: str) -> None:
    set_state("git", running=True, output="", error="")
    commands = [
        ["git", "status", "--short", "--branch"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", message],
        ["git", "push", "origin", branch],
    ]
    chunks: list[str] = []
    for command in commands:
        code, output = run_command(command)
        chunks.append(f"> {' '.join(command)}\n{output}")
        if code and command[1] == "commit" and "nothing to commit" in output.lower():
            continue
        if code:
            set_state("git", running=False, error=output, output="\n\n".join(chunks))
            return
    set_state("git", running=False, output="\n\n".join(chunks))
    threading.Thread(target=monitor_deploy, daemon=True).start()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def api_state():
    with state_lock:
        return jsonify(state)


@app.get("/api/git/status")
def git_status():
    code, output = run_command(["git", "status", "--short", "--branch"])
    return jsonify({"ok": code == 0, "output": output, "code": code})


@app.post("/api/git/push")
def git_push_route():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "chore: update DGN-PICKS")).strip()
    branch = str(payload.get("branch", "main")).strip()
    if not message or not branch or any(char in branch for char in ";&|\n\r"):
        return jsonify({"ok": False, "message": "Commit message y branch son requeridos."}), 400
    with state_lock:
        if state["git"]["running"] or state["deploy"]["running"]:
            return jsonify({"ok": False, "message": "Ya hay una operación en progreso."}), 409
    threading.Thread(target=git_push, args=(message, branch), daemon=True).start()
    return jsonify({"ok": True})


@app.post("/api/deploy/refresh")
def deploy_refresh():
    result = railway_status()
    set_state("deploy", **result, updated_at=now())
    return jsonify(result)


@app.get("/api/graph")
def graph():
    if not GRAPH_PATH.exists():
        return jsonify({"nodes": [], "edges": [], "meta": {"error": "No existe graphify-out/graph.json"}})
    try:
        payload = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        payload["meta"] = {
            "updated_at": datetime.fromtimestamp(GRAPH_PATH.stat().st_mtime, timezone.utc).isoformat()
        }
        return jsonify(payload)
    except (OSError, json.JSONDecodeError) as exc:
        return jsonify({"nodes": [], "edges": [], "meta": {"error": str(exc)}}), 500


def refresh_graph() -> None:
    set_state("graph", running=True, message="Actualizando grafo…")
    command = os.environ.get("GRAPHIFY_COMMAND", "graphify").split()
    code, output = run_command(command + [".", "--update"], timeout=20 * 60)
    set_state("graph", running=False, message=output[-1000:] if output else
              ("Grafo actualizado." if code == 0 else "Falló la actualización."), code=code)


@app.post("/api/graph/refresh")
def graph_refresh():
    with state_lock:
        if state["graph"]["running"]:
            return jsonify({"ok": False, "message": "El grafo ya se está actualizando."}), 409
    threading.Thread(target=refresh_graph, daemon=True).start()
    return jsonify({"ok": True})


def start_desktop() -> None:
    import webview

    port = int(os.environ.get("DGN_OPS_PORT", "5178"))
    threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False),
        daemon=True,
    ).start()
    time.sleep(0.35)
    webview.create_window(
        "DGN-PICKS Ops Console",
        f"http://127.0.0.1:{port}",
        width=1440,
        height=900,
        min_size=(1100, 700),
    )
    webview.start(debug=os.environ.get("DGN_OPS_DEBUG") == "1")


if __name__ == "__main__":
    if os.environ.get("DGN_OPS_BROWSER") == "1":
        app.run(host="127.0.0.1", port=int(os.environ.get("DGN_OPS_PORT", "5178")), debug=False)
    else:
        start_desktop()
