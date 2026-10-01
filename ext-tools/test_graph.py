import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as console


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.client = console.app.test_client()
        self.headers = {"X-DGN-CSRF": console.app.config["DESKTOP_CSRF_TOKEN"]}
        self.previous = dict(console.state["graph"])
        self.addCleanup(console.set_state, "graph", **self.previous)
        console.set_state("graph", running=False, message="")

    def test_graphify_view_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory) / "graph.json"
            html = Path(directory) / "graph.html"
            graph.write_text('{"nodes":[{"id":"a"}],"links":[]}', encoding="utf-8")
            html.write_text('<html>Graphify communities</html>', encoding="utf-8")
            with patch.object(console, "GRAPH_PATH", graph), patch.object(console, "GRAPH_HTML_PATH", html):
                data = self.client.get("/api/graph").get_json()
                self.assertEqual(data["meta"]["view_version"], str(html.stat().st_mtime_ns))
                response = self.client.get("/api/graph/view")
                self.assertIn(b"Graphify communities", response.data)
                self.assertEqual(response.headers["Content-Security-Policy"], "frame-ancestors 'self'")
                response.close()
                html.unlink()
                self.assertEqual(self.client.get("/api/graph/view").status_code, 404)

    @patch("app.threading.Thread")
    def test_refresh_reserves_running_state_before_worker_starts(self, worker):
        first = self.client.post("/api/graph/refresh", json={}, headers=self.headers)
        second = self.client.post("/api/graph/refresh", json={}, headers=self.headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        self.assertTrue(console.state["graph"]["running"])
        worker.return_value.start.assert_called_once()

    @patch.dict("os.environ", {"GRAPHIFY_COMMAND": '"/tmp/graphify tools/python" -m graphify'})
    @patch("app.run_command", return_value=(0, "Updated graph.html"))
    def test_refresh_uses_supported_update_command_and_finishes(self, command):
        console.refresh_graph()
        command.assert_called_once_with(["/tmp/graphify tools/python", "-m", "graphify", "update", "."], timeout=1200)
        self.assertFalse(console.state["graph"]["running"])
        self.assertEqual(console.state["graph"]["code"], 0)
        self.assertIn("graph.html", console.state["graph"]["message"])

    @patch.dict("os.environ", {"GRAPHIFY_COMMAND": '"unterminated'})
    def test_invalid_command_leaves_retry_available(self):
        console.refresh_graph()
        self.assertFalse(console.state["graph"]["running"])
        self.assertEqual(console.state["graph"]["code"], 1)
