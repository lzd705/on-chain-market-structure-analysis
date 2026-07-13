import unittest
import subprocess
import sys

from scripts.run_pipeline import run_pipeline


class RunPipelineTests(unittest.TestCase):
    def test_run_pipeline_defaults_to_build_analysis_tables(self):
        steps = []

        def fake_build_panel():
            steps.append("build_panel")

        def fake_build_research_panel():
            steps.append("build_research_panel")

        def fake_build_factors():
            steps.append("build_factors")

        def fake_build_factor_return_panel():
            steps.append("build_factor_return_panel")

        run_pipeline(
            build_panel=fake_build_panel,
            build_research_panel=fake_build_research_panel,
            build_factors=fake_build_factors,
            build_factor_return_panel=fake_build_factor_return_panel,
        )

        self.assertEqual(
            steps,
            [
                "build_panel",
                "build_research_panel",
                "build_factors",
                "build_factor_return_panel",
            ],
        )

    def test_run_pipeline_can_fetch_before_building_panel(self):
        steps = []

        def fake_fetch_cex():
            steps.append("fetch_cex")

        def fake_fetch_dex():
            steps.append("fetch_dex")

        def fake_build_panel():
            steps.append("build_panel")

        def fake_build_research_panel():
            steps.append("build_research_panel")

        def fake_build_factors():
            steps.append("build_factors")

        def fake_build_factor_return_panel():
            steps.append("build_factor_return_panel")

        run_pipeline(
            fetch=True,
            fetch_cex=fake_fetch_cex,
            fetch_dex=fake_fetch_dex,
            build_panel=fake_build_panel,
            build_research_panel=fake_build_research_panel,
            build_factors=fake_build_factors,
            build_factor_return_panel=fake_build_factor_return_panel,
        )

        self.assertEqual(
            steps,
            [
                "fetch_cex",
                "fetch_dex",
                "build_panel",
                "build_research_panel",
                "build_factors",
                "build_factor_return_panel",
            ],
        )

    def test_run_pipeline_script_runs_from_project_root(self):
        result = subprocess.run(
            [sys.executable, "scripts/run_pipeline.py"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("merged rows to data/processed/merged_volume_panel.csv", result.stdout)
        self.assertIn("research rows to data/processed/research_panel.csv", result.stdout)
        self.assertIn("factor rows to data/processed/factor_table.csv", result.stdout)
        self.assertIn("factor return rows to data/processed/factor_return_panel.csv", result.stdout)


if __name__ == "__main__":
    unittest.main()
