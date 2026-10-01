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

    @patch("app.threading.Thread")
    @patch("app.now", return_value="2026-10-01T12:00:00+00:00")
    @patch("app.run_command", return_value=(0, "done"))
    def test_commit_appends_timestamp_to_custom_message(self, command, clock, worker):
        console.git_push("fix: estado", "main")
        command.assert_any_call(["git", "commit", "-m", "fix: estado [2026-10-01T12:00:00+00:00]"])
        self.assertIn("fix: estado [2026-10-01T12:00:00+00:00]", console.state["git"]["output"])
        clock.assert_called_once()

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
        history = self.client.get("/api/git/log").get_json()
        self.assertEqual(history["output"], self.log_path.read_text(encoding="utf-8"))
        self.assertEqual(history["last_status"], {"checked_at": second["checked_at"], "code": 1})

    def test_loads_saved_history_without_running_git(self):
        saved = "[2026-09-30T12:00:00+00:00] git status --short --branch (exit 0)\n## main\n\n"
        self.log_path.parent.mkdir()
        self.log_path.write_text(saved, encoding="utf-8")
        with patch("app.run_command") as command:
            data = self.client.get("/api/git/log").get_json()
        command.assert_not_called()
        self.assertEqual(data["output"], saved)
        self.assertEqual(data["last_status"], {"checked_at": "2026-09-30T12:00:00+00:00", "code": 0})

    def test_missing_log_has_no_previous_status(self):
        data = self.client.get("/api/git/log").get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["output"], "")
        self.assertIsNone(data["last_status"])

    def test_unreadable_log_reports_error(self):
        self.log_path.parent.mkdir()
        self.log_path.mkdir()
        response = self.client.get("/api/git/log")
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.get_json()["ok"])

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
