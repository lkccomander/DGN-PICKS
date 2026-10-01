import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as console


class GitStatusTests(unittest.TestCase):
    def setUp(self):
        self.client = console.app.test_client()
        self.previous_git_state = dict(console.state["git"])
        console.set_state("git", running=False, output="", error="")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(console.set_state, "git", **self.previous_git_state)
        self.log_path = Path(self.temp_dir.name) / "logs" / "git-status.log"
        log_patch = patch.object(console, "GIT_STATUS_LOG_PATH", self.log_path)
        log_patch.start()
        self.addCleanup(log_patch.stop)

    @patch("app.print")
    @patch("app.now", side_effect=["2026-10-01T12:00:00+00:00", "2026-10-01T12:01:00+00:00"])
    @patch("app.run_command", side_effect=[(0, "## main\n M documentación.md"), (1, "fatal: not a git repository")])
    def test_checks_print_and_append_timestamped_success_and_failure(self, command, clock, printer):
        first = self.client.get("/api/git/status").get_json()
        second = self.client.get("/api/git/status").get_json()
        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(second["code"], 1)
        self.assertIn(first["checked_at"], first["output"])
        self.assertIn("exit 1", second["output"])
        self.assertEqual(self.log_path.read_text(encoding="utf-8"), first["output"] + "\n" + second["output"] + "\n")
        self.assertEqual(printer.call_count, 2)
        printer.assert_any_call(first["output"], flush=True)
        self.assertEqual(self.client.get("/api/state").get_json()["git"]["output"], second["output"])
        command.assert_called_with(["git", "status", "--short", "--branch"])

    @patch("app.print")
    @patch("app.run_command", return_value=(0, "## main"))
    def test_log_failure_keeps_result_and_reports_warning(self, command, printer):
        self.log_path.parent.write_text("directory blocked", encoding="utf-8")
        response = self.client.get("/api/git/status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertIn("## main", data["output"])
        self.assertTrue(data["log_error"])
        self.assertIn(data["log_error"], data["output"])

    @patch("app.print")
    @patch("app.run_command", return_value=(0, "## main"))
    def test_check_does_not_replace_running_push_output(self, command, printer):
        console.set_state("git", running=True, output="push in progress")
        data = self.client.get("/api/git/status").get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(console.state["git"]["output"], "push in progress")
        self.assertIn("## main", self.log_path.read_text(encoding="utf-8"))
