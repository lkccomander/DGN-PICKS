"""Loopback request boundary for the desktop console's privileged operations."""
import hmac
import secrets
from urllib.parse import urlsplit
from flask import jsonify, request


def origin(value):
    if not value or any(c.isspace() for c in value) or "\\" in value:
        return None
    try:
        parsed = urlsplit(value)
        port = parsed.port
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username is not None or parsed.password is not None or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            return None
        return parsed.scheme, parsed.hostname.lower(), port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        return None


def install_desktop_boundary(app):
    token = secrets.token_urlsafe(32)
    app.config["DESKTOP_CSRF_TOKEN"] = token
    app.jinja_env.globals["desktop_csrf_token"] = token

    @app.before_request
    def enforce_boundary():
        expected = origin(request.host_url)
        if any(c in request.host for c in "/\\@?#") or expected is None or expected[1] not in {"localhost", "127.0.0.1", "::1"}:
            return jsonify(detail="Invalid desktop host"), 400
        supplied = request.headers.get("Origin")
        if supplied is not None and origin(supplied) != expected:
            return jsonify(detail="Cross-origin desktop request rejected"), 403
        if not request.path.startswith("/api/") or request.method in {"GET", "HEAD", "OPTIONS"}:
            return None
        supplied_token = request.headers.get("X-DGN-CSRF", "")
        if not hmac.compare_digest(supplied_token.encode(), token.encode()):
            return jsonify(detail="Invalid desktop request token"), 403
        if request.mimetype != "application/json":
            return jsonify(detail="application/json required"), 415
        if not isinstance(request.get_json(silent=True), dict):
            return jsonify(detail="A JSON object is required"), 400
        return None

    @app.after_request
    def protect_response(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'" if request.path == "/api/graph/view" else "frame-ancestors 'none'"
        return response
