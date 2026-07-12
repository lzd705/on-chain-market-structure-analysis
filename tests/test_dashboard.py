import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dashboard import server


class DashboardServerTest(unittest.TestCase):
    def setUp(self):
        server.RUNTIME["public"] = False

    def tearDown(self):
        server.RUNTIME["public"] = False

    def test_payload_uses_real_factor_panel(self):
        payload = server.build_dashboard_payload()
        self.assertEqual(payload["metadata"]["grain"], "token-day")
        self.assertGreater(payload["metadata"]["row_count"], 0)
        self.assertGreaterEqual(payload["metadata"]["token_count"], 1)
        self.assertIn("dex_share", payload["metrics"])
        self.assertTrue(payload["factor_results"])

    def test_parse_value_preserves_missing_values(self):
        self.assertIsNone(server.parse_value(""))
        self.assertIsNone(server.parse_value("nan"))
        self.assertEqual(server.parse_value("12"), 12)
        self.assertEqual(server.parse_value("AAVE"), "AAVE")

    def test_sample_panel_uses_companion_factor_results(self):
        sample_path = server.PROJECT_ROOT / "data/mock/research/factor_panel.csv"
        with patch.dict(server.os.environ, {"DASHBOARD_DATA": str(sample_path)}):
            payload = server.build_dashboard_payload()
        self.assertEqual(payload["metadata"]["row_count"], 595)
        self.assertEqual(payload["metadata"]["token_count"], 5)
        self.assertEqual(len(payload["factor_results"]), 110)

    def test_public_mode_uses_curated_ten_token_snapshot(self):
        server.RUNTIME["public"] = True
        with patch.dict(server.os.environ, {}, clear=True):
            payload = server.build_dashboard_payload()
        self.assertEqual(payload["metadata"]["access_mode"], "public_read_only")
        self.assertFalse(payload["metadata"]["synthetic"])
        self.assertEqual(payload["metadata"]["row_count"], 1780)
        self.assertEqual(payload["metadata"]["token_count"], 10)
        self.assertEqual(len(payload["scope_sensitivity"]), 3)
        self.assertEqual(len(payload["factor_results"]), 147)
        self.assertGreaterEqual(len({row["factor_name"] for row in payload["factor_results"]}), 30)

    def test_public_mode_rejects_private_data_and_state_writes(self):
        server.RUNTIME["public"] = True
        private_path = server.PROJECT_ROOT / "data/a_review/research/factor_panel.csv"
        with patch.dict(server.os.environ, {"DASHBOARD_DATA": str(private_path)}):
            with self.assertRaises(PermissionError):
                server.resolve_panel_path()
        with self.assertRaises(PermissionError):
            server.save_state({})

    def test_state_is_sanitized_and_saved_atomically(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_path = Path(temporary_directory) / "state.json"
            history_path = Path(temporary_directory) / "history.jsonl"
            with patch.object(server, "STATE_PATH", state_path), patch.object(server, "HISTORY_PATH", history_path), patch.object(server, "STATE_DIR", state_path.parent):
                saved = server.save_state(
                    {
                        "selected_tokens": ["AAVE", "ARB"],
                        "metric": "dex_share",
                        "notes": "coverage check",
                        "checklist": [{"id": "one", "label": "First", "done": True}],
                    }
                )
                self.assertTrue(state_path.exists())
                self.assertEqual(saved["selected_tokens"], ["AAVE", "ARB"])
                self.assertEqual(json.loads(state_path.read_text())["checklist"][0]["done"], True)
                self.assertFalse(state_path.with_suffix(".tmp").exists())
                history = server.load_history()
                self.assertEqual(len(history), 1)
                self.assertEqual(history[0]["workspace"]["metric"], "dex_share")
                self.assertEqual(history[0]["data"]["row_count"], 1780)


if __name__ == "__main__":
    unittest.main()
