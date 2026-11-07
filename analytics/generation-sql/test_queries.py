"""Run seed.py, execute queries.sql, and check the planted faults are found.
Run: python -m unittest test_queries.py"""
import sqlite3, subprocess, sys, unittest
from pathlib import Path

HERE = Path(__file__).parent


def run_queries():
    subprocess.run([sys.executable, str(HERE / "seed.py")], check=True, capture_output=True)
    db = sqlite3.connect(HERE / "solar.db")
    lines = [l for l in (HERE / "queries.sql").read_text().splitlines()
             if not l.startswith(".") and not l.lstrip().startswith("--")]
    stmts = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]
    results = [db.execute(s).fetchall() for s in stmts if not s.startswith("SELECT '")]
    return results  # Q1..Q5 in order


class TestPlantedFaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q1, cls.q2, cls.q3, cls.q4, cls.q5 = run_queries()

    def test_meter_fault_flagged_only_where_planted(self):
        flagged = [(r[0], r[1]) for r in self.q1 if r[5] == "INVESTIGATE"]
        self.assertEqual(flagged, [("PLANT_B", "2026-08")])

    def test_inverter_trip_found_as_five_day_run(self):
        runs = {(r[0], r[1], r[3]) for r in self.q3}
        self.assertIn(("PLANT_A", "2026-03-10", 5), runs)

    def test_cleaning_restores_pr(self):
        pr = dict(self.q4)
        self.assertLess(pr["2026-04-30"], 0.72)
        self.assertGreater(pr["2026-05-08"], 0.79)

    def test_pr_in_plausible_band_outside_fault_months(self):
        for plant, month, pr, cuf in self.q2:
            if (plant, month) not in {("PLANT_A", "2026-03"), ("PLANT_B", "2026-04")}:
                self.assertTrue(0.75 <= pr <= 0.85, (plant, month, pr))


if __name__ == "__main__":
    unittest.main()
