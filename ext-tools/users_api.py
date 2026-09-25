"""Narrow HTTP bridge to the existing authenticated user API."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from flask import Blueprint, Response, jsonify, request

users_api = Blueprint("users_api", __name__)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward credentials to a redirected origin.


def forward(path: str, *, login: bool = False):
    base = os.environ.get("DGN_OPS_API_URL", "http://127.0.0.1:8000").rstrip("/")
    parsed = urlsplit(base)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        return jsonify(detail="DGN_OPS_API_URL debe ser una URL HTTP(S) sin credenciales."), 503
    authorization = request.headers.get("Authorization", "")
    if not login and not authorization.startswith("Bearer "):
        return jsonify(detail="Inicia sesión para administrar usuarios."), 401
    headers = {"Accept": "application/json"}
    if authorization and not login:
        headers["Authorization"] = authorization
    data = None
    if request.method in {"POST", "PATCH"}:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(detail="Se requiere un objeto JSON válido."), 400
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if request.method == "GET" and path.startswith("users"):
        path = "admin/" + path
    upstream = Request(f"{base}/api/v1/{path}", data=data, headers=headers, method=request.method)
    try:
        with build_opener(NoRedirect()).open(upstream, timeout=15) as response:
            status, raw = response.status, response.read()
    except HTTPError as exc:
        status, raw = exc.code, exc.read()
    except (URLError, OSError, ValueError):
        return jsonify(detail="No se pudo conectar con la API. Revisa DGN_OPS_API_URL y vuelve a intentar."), 502
    if status == 204:
        return Response(status=204)
    try:
        body = json.loads(raw)
    except (ValueError, UnicodeError):
        return jsonify(detail="La API devolvió una respuesta inválida."), 502
    response = jsonify(body)
    response.status_code = status if 200 <= status < 300 or 400 <= status < 600 else 502
    response.headers["Cache-Control"] = "no-store"
    return response


@users_api.post("/api/users/login")
def login():
    return forward("auth/login", login=True)


@users_api.route("/api/users", methods=["GET", "POST"])
def collection():
    return forward("users")


@users_api.route("/api/users/<int:user_id>", methods=["GET", "PATCH", "DELETE"])
def member(user_id: int):
    return forward(f"users/{user_id}")
