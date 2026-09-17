"""Secure desktop configuration and local API lifecycle controls."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from flask import Blueprint, jsonify, request

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None

ROOT = Path(__file__).resolve().parents[1]
DESKTOP_FIELDS = ("DGN_OPS_API_URL", "DGN_OPS_PORT", "DGN_OPS_DEBUG", "GRAPHIFY_COMMAND")
API_FIELDS = ("DGN_AUTH_USERNAME", "DGN_AUTH_ROLE", "DGN_CORS_ORIGINS", "DGN_API_WRITE_MODE")
SECRET_FIELDS = ("DATABASE_URL", "DGN_AUTH_SECRET", "DGN_AUTH_PASSWORD", "DGN_API_WRITE_KEY")
DEFAULTS = {"DGN_OPS_API_URL": "http://127.0.0.1:8000", "DGN_OPS_PORT": "5178", "DGN_OPS_DEBUG": False, "GRAPHIFY_COMMAND": "graphify", "DGN_AUTH_ROLE": "admin", "DGN_API_WRITE_MODE": "disabled"}
configuration_api = Blueprint("configuration_api", __name__)
_process_lock = threading.Lock()
_local_api_process: subprocess.Popen[str] | None = None
_local_api_output = ""


def read_user_environment() -> dict[str, str | None]:
    names = (*DESKTOP_FIELDS, *API_FIELDS, *SECRET_FIELDS)
    if winreg is None:
        return {name: os.environ.get(name) for name in names}
    values: dict[str, str | None] = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            for name in names:
                try:
                    values[name] = str(winreg.QueryValueEx(key, name)[0])
                except FileNotFoundError:
                    values[name] = None
    except FileNotFoundError:
        values = {name: None for name in names}
    return values


def _effective_values() -> dict[str, str | None]:
    values = read_user_environment()
    for name in (*DESKTOP_FIELDS, *API_FIELDS, *SECRET_FIELDS):
        values[name] = values.get(name) or os.environ.get(name)
    return values


def hydrate_runtime_environment() -> None:
    """Make user-scoped settings available to this already-running desktop process."""
    for name, value in read_user_environment().items():
        if value:
            os.environ[name] = value


def _public_url(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip().rstrip("/")
    parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        return None
    return candidate


def read_configuration() -> dict[str, object]:
    values = _effective_values()
    desktop = {
        "DGN_OPS_API_URL": values["DGN_OPS_API_URL"] or DEFAULTS["DGN_OPS_API_URL"],
        "DGN_OPS_PORT": values["DGN_OPS_PORT"] or DEFAULTS["DGN_OPS_PORT"],
        "DGN_OPS_DEBUG": str(values["DGN_OPS_DEBUG"] or DEFAULTS["DGN_OPS_DEBUG"]).lower() in {"1", "true", "yes"},
        "GRAPHIFY_COMMAND": values["GRAPHIFY_COMMAND"] or DEFAULTS["GRAPHIFY_COMMAND"],
    }
    api = {name: values[name] or DEFAULTS.get(name, "") for name in API_FIELDS}
    api.update({name: {"configured": bool(values[name])} for name in SECRET_FIELDS})
    with _process_lock:
        process = _local_api_process
        running = process is not None and process.poll() is None
        local_api = {"running": running, "pid": process.pid if running else None, "output": _local_api_output}
    return {"desktop": desktop, "api": api, "local_api": local_api}


def write_user_environment(values: dict[str, str | None]) -> None:
    if winreg is None:
        raise RuntimeError("La configuración persistente solo está disponible en Windows.")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
        for name, value in values.items():
            if value is None:
                try:
                    winreg.DeleteValue(key, name)
                except FileNotFoundError:
                    pass
                os.environ.pop(name, None)
            else:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
                os.environ[name] = value


def _validate_patch(payload: object) -> tuple[dict[str, str | None], str | None]:
    if not isinstance(payload, dict):
        return {}, "Se requiere un objeto JSON válido."
    changes: dict[str, str | None] = {}
    current = _effective_values()
    for section, allowed in (("desktop", DESKTOP_FIELDS), ("api", (*API_FIELDS, *SECRET_FIELDS))):
        values = payload.get(section, {})
        if not isinstance(values, dict):
            return {}, f"{section} debe ser un objeto."
        unknown = set(values) - set(allowed)
        if unknown:
            return {}, f"Variable no permitida: {sorted(unknown)[0]}"
        for name, value in values.items():
            if name in SECRET_FIELDS:
                if value is not None and not isinstance(value, str):
                    return {}, f"{name} debe ser texto."
                if isinstance(value, str) and value:
                    changes[name] = value
            elif value is None:
                changes[name] = None
            elif name == "DGN_OPS_DEBUG":
                if not isinstance(value, bool):
                    return {}, "DGN_OPS_DEBUG debe ser verdadero o falso."
                changes[name] = "true" if value else "false"
            elif isinstance(value, str):
                changes[name] = value.strip()
            else:
                return {}, f"{name} debe ser texto."
    url = changes.get("DGN_OPS_API_URL", current.get("DGN_OPS_API_URL") or DEFAULTS["DGN_OPS_API_URL"])
    if _public_url(url) is None:
        return {}, "DGN_OPS_API_URL debe ser una URL HTTP(S) sin credenciales, ruta ni parámetros."
    port = changes.get("DGN_OPS_PORT", current.get("DGN_OPS_PORT") or DEFAULTS["DGN_OPS_PORT"])
    try:
        if port is None or not 1024 <= int(port) <= 65535:
            raise ValueError
    except ValueError:
        return {}, "DGN_OPS_PORT debe estar entre 1024 y 65535."
    role = changes.get("DGN_AUTH_ROLE", current.get("DGN_AUTH_ROLE") or DEFAULTS["DGN_AUTH_ROLE"])
    if role not in {"admin", "editor"}:
        return {}, "DGN_AUTH_ROLE debe ser admin o editor."
    mode = changes.get("DGN_API_WRITE_MODE", current.get("DGN_API_WRITE_MODE") or DEFAULTS["DGN_API_WRITE_MODE"])
    if mode not in {"disabled", "development"}:
        return {}, "DGN_API_WRITE_MODE debe ser disabled o development."
    if mode == "development" and not (changes.get("DGN_API_WRITE_KEY") or current.get("DGN_API_WRITE_KEY")):
        return {}, "DGN_API_WRITE_KEY es obligatorio con modo development."
    return changes, None


def _redact(text: str) -> str:
    for value in _effective_values().values():
        if value and len(value) >= 4:
            text = text.replace(value, "[redacted]")
    return text


def _drain_process_output(process: subprocess.Popen[str]) -> None:
    global _local_api_output
    if process.stdout is None:
        return
    for line in process.stdout:
        with _process_lock:
            _local_api_output = (_local_api_output + _redact(line))[-4000:]


def api_python() -> str:
    """Prefer Windows Python Launcher because the desktop venv need not include Uvicorn."""
    return shutil.which("py") or sys.executable

def _local_api_environment() -> tuple[dict[str, str] | None, str | None]:
    values = _effective_values()
    missing = [name for name in ("DATABASE_URL", "DGN_AUTH_SECRET", "DGN_AUTH_USERNAME", "DGN_AUTH_PASSWORD") if not values.get(name)]
    if missing:
        return None, f"Configura estas variables para iniciar la API local: {', '.join(missing)}."
    if (values.get("DGN_AUTH_ROLE") or DEFAULTS["DGN_AUTH_ROLE"]) not in {"admin", "editor"}:
        return None, "DGN_AUTH_ROLE debe ser admin o editor."
    child = os.environ.copy()
    for name in (*API_FIELDS, *SECRET_FIELDS):
        if values.get(name):
            child[name] = str(values[name])
    return child, None


@configuration_api.get("/api/configuration")
def get_configuration():
    return jsonify(read_configuration())


@configuration_api.patch("/api/configuration")
def save_configuration():
    changes, error = _validate_patch(request.get_json(silent=True))
    if error:
        return jsonify(detail=error), 422
    try:
        write_user_environment(changes)
    except RuntimeError as exc:
        return jsonify(detail=str(exc)), 503
    return jsonify({"ok": True, "message": "Configuración guardada. Reinicia la app para aplicar un nuevo puerto.", "configuration": read_configuration()})


@configuration_api.post("/api/configuration/test-connection")
def test_connection():
    payload = request.get_json(silent=True) or {}
    base = _public_url(payload.get("url"))
    if base is None:
        return jsonify(detail="DGN_OPS_API_URL debe ser una URL HTTP(S) sin credenciales, ruta ni parámetros."), 422
    target = f"{base}/api/health"
    try:
        with urlopen(Request(target, headers={"Accept": "application/json"}), timeout=8) as response:
            json.loads(response.read())
            return jsonify(ok=True, target=target, status=response.status)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return jsonify(ok=False, target=target, detail="No se pudo verificar la API. Revisa la URL y su disponibilidad."), 502


@configuration_api.post("/api/configuration/local-api/start")
def start_local_api():
    global _local_api_process, _local_api_output
    child_env, error = _local_api_environment()
    target_url = urlsplit(str(_effective_values().get("DGN_OPS_API_URL") or DEFAULTS["DGN_OPS_API_URL"]))
    if target_url.hostname not in {"127.0.0.1", "localhost"}:
        return jsonify(detail="Para iniciar la API local, configura DGN_OPS_API_URL con http://127.0.0.1:8000 o localhost."), 422
    if error:
        return jsonify(detail=error), 422
    with _process_lock:
        if _local_api_process is not None and _local_api_process.poll() is None:
            return jsonify(detail="La API local ya fue iniciada por esta consola.", pid=_local_api_process.pid), 409
        target = urlsplit(str(_effective_values().get("DGN_OPS_API_URL") or DEFAULTS["DGN_OPS_API_URL"]))
        api_port = str(target.port or 8000) if target.hostname in {"127.0.0.1", "localhost"} else "8000"
        command = [api_python(), "-m", "uvicorn", "dgn_picks_api.main:app", "--app-dir", "apps/api/src", "--port", api_port]
        _local_api_output = ""
        _local_api_process = subprocess.Popen(command, cwd=ROOT, env=child_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False, creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        threading.Thread(target=_drain_process_output, args=(_local_api_process,), daemon=True).start()
        return jsonify(ok=True, pid=_local_api_process.pid, command=command), 202


@configuration_api.post("/api/configuration/local-api/stop")
def stop_local_api():
    global _local_api_process
    with _process_lock:
        if _local_api_process is None or _local_api_process.poll() is not None:
            _local_api_process = None
            return jsonify(detail="No hay una API local iniciada por esta consola."), 409
        _local_api_process.terminate()
        return jsonify(ok=True, pid=_local_api_process.pid, message="Se solicitó detener la API local.")
