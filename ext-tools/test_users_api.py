import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from app import app


class UsersBridgeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer test-operator"}
        self.env = patch.dict("os.environ", {"DGN_OPS_API_URL": "http://127.0.0.1:8000"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def upstream(self, status, data):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = status
        response.read.return_value = json.dumps(data).encode() if data is not None else b""
        return response

    @patch("users_api.build_opener")
    def test_crud_forwards_methods_credentials_and_payload(self, opener):
        for method, path, body, status, result in [
            ("GET", "/api/users", None, 200, [{"id": 7, "username": "demo"}]),
            ("GET", "/api/users/7", None, 200, {"id": 7}),
            ("POST", "/api/users", {"username": "demo", "display_name": "Demo"}, 201, {"id": 7}),
            ("PATCH", "/api/users/7", {"email": None, "active": False}, 200, {"id": 7}),
            ("DELETE", "/api/users/7", None, 204, None),
        ]:
            with self.subTest(method=method):
                opener.return_value.open.return_value = self.upstream(status, result)
                response = self.client.open(path, method=method, json=body, headers=self.headers)
                self.assertEqual(response.status_code, status)
                sent = opener.return_value.open.call_args.args[0]
                self.assertEqual(sent.method, method)
                self.assertEqual(sent.full_url, "http://127.0.0.1:8000/api/v1/" + path.removeprefix("/api/"))
                self.assertEqual(sent.get_header("Authorization"), "Bearer test-operator")
                self.assertEqual(opener.return_value.open.call_args.kwargs["timeout"], 15)
                if body is not None:
                    self.assertEqual(json.loads(sent.data), body)
                if status == 204:
                    self.assertEqual(response.data, b"")

    @patch("users_api.build_opener")
    def test_login_does_not_forward_authorization(self, opener):
        opener.return_value.open.return_value = self.upstream(200, {"access_token": "token", "role": "admin"})
        response = self.client.post("/api/users/login", json={"username": "admin", "password": "password"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        sent = opener.return_value.open.call_args.args[0]
        self.assertTrue(sent.full_url.endswith("/api/v1/auth/login"))
        self.assertIsNone(sent.get_header("Authorization"))
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    @patch("users_api.build_opener")
    def test_missing_auth_never_calls_upstream(self, opener):
        self.assertEqual(self.client.get("/api/users").status_code, 401)
        opener.assert_not_called()

    @patch("users_api.build_opener")
    def test_conflict_and_validation_are_preserved(self, opener):
        for status, detail in [(409, "User owns picks; deactivate instead"), (422, [{"loc": ["body", "password"], "msg": "Too short"}]), (401, "Token expired")]:
            opener.return_value.open.side_effect = HTTPError("http://api", status, "rejected", {}, io.BytesIO(json.dumps({"detail": detail}).encode()))
            response = self.client.patch("/api/users/7", json={"active": False}, headers=self.headers)
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.json["detail"], detail)

    @patch("users_api.build_opener")
    def test_invalid_input_never_calls_upstream(self, opener):
        response = self.client.post("/api/users", json=["wrong"], headers=self.headers)
        self.assertEqual(response.status_code, 400)
        opener.assert_not_called()

    @patch("users_api.build_opener")
    def test_connection_failure_is_readable(self, opener):
        opener.return_value.open.side_effect = URLError("connection refused")
        response = self.client.get("/api/users", headers=self.headers)
        self.assertEqual(response.status_code, 502)
        self.assertIn("DGN_OPS_API_URL", response.json["detail"])

    @patch("users_api.build_opener")
    def test_non_json_upstream_is_not_forwarded(self, opener):
        response = self.upstream(200, None)
        response.read.return_value = b"<html>gateway error</html>"
        opener.return_value.open.return_value = response
        self.assertEqual(self.client.get("/api/users", headers=self.headers).status_code, 502)

    def test_desktop_page_includes_users(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="users-pane"', response.data)
        self.assertIn(b"users.js", response.data)


if __name__ == "__main__":
    unittest.main()
