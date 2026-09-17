import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import configuration
from app import app


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.values = {
            "DGN_OPS_API_URL": "https://api.example.test",
            "DGN_OPS_PORT": "5178",
            "DGN_OPS_DEBUG": None,
            "GRAPHIFY_COMMAND": None,
            "DATABASE_URL": "postgresql://operator:secret@db.example/test",
            "DGN_AUTH_SECRET": "signing-secret",
            "DGN_AUTH_USERNAME": "operator",
            "DGN_AUTH_PASSWORD": "operator-password",
            "DGN_AUTH_ROLE": "admin",
            "DGN_CORS_ORIGINS": None,
            "DGN_API_WRITE_MODE": "disabled",
            "DGN_API_WRITE_KEY": "write-key",
        }
        self.reader = patch("configuration.read_user_environment", return_value=self.values)
        self.reader.start()
        self.addCleanup(self.reader.stop)

    def test_configuration_redacts_all_secrets(self):
        response = self.client.get("/api/configuration")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["desktop"]["DGN_OPS_API_URL"], "https://api.example.test")
        self.assertEqual(response.json["api"]["DATABASE_URL"], {"configured": True})
        self.assertNotIn("secret", str(response.json))
        self.assertNotIn("operator-password", str(response.json))

    @patch("configuration.write_user_environment")
    def test_save_rejects_unsafe_url_and_replaces_only_nonblank_secrets(self, writer):
        rejected = self.client.patch("/api/configuration", json={"desktop": {"DGN_OPS_API_URL": "https://operator:password@api.example.test"}})
        self.assertEqual(rejected.status_code, 422)
        response = self.client.patch("/api/configuration", json={"api": {"DGN_AUTH_SECRET": "", "DGN_AUTH_PASSWORD": "new-password"}})
        self.assertEqual(response.status_code, 200)
        writer.assert_called_once_with({"DGN_AUTH_PASSWORD": "new-password"})

    @patch("configuration.urlopen")
    def test_connection_check_reports_healthy_target(self, urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"status":"ok"}'
        urlopen.return_value.__enter__.return_value = response
        result = self.client.post("/api/configuration/test-connection", json={"url": "https://api.example.test"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["target"], "https://api.example.test/api/health")

    @patch("configuration.urlopen", side_effect=URLError("connection refused"))
    def test_connection_check_redacts_network_failure(self, _):
        result = self.client.post("/api/configuration/test-connection", json={"url": "http://127.0.0.1:8000"})
        self.assertEqual(result.status_code, 502)
        self.assertNotIn("connection refused", result.json["detail"])

    @patch("configuration.subprocess.Popen")
    def test_start_uses_argument_list_and_stop_only_owns_process(self, popen):
        self.values["DGN_OPS_API_URL"] = "http://127.0.0.1:8000"
        process = MagicMock()
        process.pid = 4242
        process.poll.return_value = None
        process.stdout = io.StringIO("")
        popen.return_value = process
        started = self.client.post("/api/configuration/local-api/start")
        self.assertEqual(started.status_code, 202)
        self.assertEqual(popen.call_args.args[0][:4], [configuration.api_python(), "-m", "uvicorn", "dgn_picks_api.main:app"])
        self.assertFalse(popen.call_args.kwargs["shell"])
        stopped = self.client.post("/api/configuration/local-api/stop")
        self.assertEqual(stopped.status_code, 200)
        process.terminate.assert_called_once()

    def test_stop_rejects_unowned_process(self):
        configuration._local_api_process = None
        response = self.client.post("/api/configuration/local-api/stop")
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
