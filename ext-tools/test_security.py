import unittest
from unittest.mock import patch
from app import app

class DesktopBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.token = app.config["DESKTOP_CSRF_TOKEN"]

    @patch("app.threading.Thread")
    def test_rejected_mutations_never_start_work(self, worker):
        cases = [
            ({}, {}, 403),
            ({"X-DGN-CSRF": "wrong"}, {}, 403),
            ({"X-DGN-CSRF": "é"}, {}, 403),
            ({"X-DGN-CSRF": self.token, "Origin": "https://evil.example"}, {}, 403),
            ({"X-DGN-CSRF": self.token, "Origin": "null"}, {}, 403),
            ({"X-DGN-CSRF": self.token, "Origin": "http://localhost:9999"}, {}, 403),
            ({"X-DGN-CSRF": self.token, "Host": "evil.example"}, {}, 400),
        ]
        for headers, body, expected in cases:
            with self.subTest(headers=headers):
                self.assertEqual(self.client.post("/api/git/push", json=body, headers=headers).status_code, expected)
        self.assertEqual(self.client.post("/api/git/push", data="", content_type="application/x-www-form-urlencoded", headers={"X-DGN-CSRF": self.token}).status_code, 415)
        worker.assert_not_called()

    @patch("app.threading.Thread")
    def test_valid_json_reaches_worker(self, worker):
        response = self.client.post("/api/git/push", json={"message": "test", "branch": "main"}, headers={"X-DGN-CSRF": self.token, "Origin": "http://localhost"})
        self.assertEqual(response.status_code, 200)
        worker.return_value.start.assert_called_once()

    def test_boundary_covers_all_mutation_routes(self):
        for path in ("/api/users/login", "/api/users", "/api/configuration", "/api/configuration/local-api/start", "/api/graph/refresh"):
            method = "PATCH" if path == "/api/configuration" else "POST"
            self.assertEqual(self.client.open(path, method=method, json={}).status_code, 403)

    def test_html_token_and_read_only_access(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.token.encode(), response.data)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(self.client.get("/api/state").status_code, 200)
        self.assertEqual(self.client.get("/", headers={"Host": "attacker.example"}).status_code, 400)
