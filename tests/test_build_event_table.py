import unittest
from datetime import date

from scripts.build_event_table import build_event_rows


class BuildEventTableTests(unittest.TestCase):
    def make_candidate(self):
        return {
            "token_id": "ARB",
            "event_type": "unlock",
            "event_time": "2026-02-16T13:00:00Z",
            "event_name": "Team and investor unlock",
            "event_size_token": "92645833.3",
            "event_size_usd": "",
            "event_size_supply_pct": "",
            "source": "https://example.com/official",
            "secondary_source": "https://example.com/check",
            "confidence": "high",
            "notes": "",
        }

    def test_build_event_rows_normalizes_time_and_builds_window(self):
        rows = build_event_rows(
            [self.make_candidate()],
            {"ARB", "OP"},
            date(2026, 1, 9),
            date(2026, 7, 5),
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["event_time"], "2026-02-16T13:00:00Z")
        self.assertEqual(rows[0]["event_window_start"], "2026-02-09")
        self.assertEqual(rows[0]["event_window_end"], "2026-03-02")
        self.assertEqual(rows[0]["is_analysis_eligible"], "1")

    def test_build_event_rows_marks_incomplete_window_ineligible(self):
        candidate = self.make_candidate()
        candidate["event_time"] = "2026-01-10"

        rows = build_event_rows(
            [candidate],
            {"ARB"},
            date(2026, 1, 9),
            date(2026, 7, 5),
        )

        self.assertEqual(rows[0]["event_time"], "2026-01-10T00:00:00Z")
        self.assertEqual(rows[0]["event_window_start"], "2026-01-03")
        self.assertEqual(rows[0]["is_analysis_eligible"], "0")

    def test_build_event_rows_removes_duplicate_records(self):
        first = self.make_candidate()
        duplicate = self.make_candidate()
        duplicate["event_name"] = "  TEAM AND INVESTOR UNLOCK  "

        rows = build_event_rows(
            [first, duplicate],
            {"ARB"},
            date(2026, 1, 9),
            date(2026, 7, 5),
        )

        self.assertEqual(len(rows), 1)

    def test_build_event_rows_sorts_by_time_then_token(self):
        later = self.make_candidate()
        later["event_time"] = "2026-03-16"
        earlier = self.make_candidate()
        earlier["token_id"] = "OP"
        earlier["event_time"] = "2026-02-01"

        rows = build_event_rows(
            [later, earlier],
            {"ARB", "OP"},
            date(2026, 1, 9),
            date(2026, 7, 5),
        )

        self.assertEqual([row["token_id"] for row in rows], ["OP", "ARB"])

    def test_build_event_rows_rejects_invalid_candidates(self):
        invalid_changes = [
            ("token_id", "UNKNOWN"),
            ("event_type", "news"),
            ("event_time", "not-a-date"),
            ("event_time", "2026-07-06"),
            ("event_name", ""),
            ("source", ""),
            ("source", "not-a-url"),
            ("secondary_source", "not-a-url"),
            ("confidence", "very-high"),
            ("event_size_token", "not-a-number"),
            ("event_size_supply_pct", "-1"),
        ]

        for field, value in invalid_changes:
            with self.subTest(field=field, value=value):
                candidate = self.make_candidate()
                candidate[field] = value

                with self.assertRaises(ValueError):
                    build_event_rows(
                        [candidate],
                        {"ARB"},
                        date(2026, 1, 9),
                        date(2026, 7, 5),
                    )


if __name__ == "__main__":
    unittest.main()
