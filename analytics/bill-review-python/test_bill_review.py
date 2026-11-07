"""Tests for bill_review.py. Run: python -m unittest test_bill_review.py"""
import json
import unittest
from pathlib import Path

import bill_review as br

SLABS = br.slabs_from([
    {"lower": 0, "upper": 400, "rate": 4.95},
    {"lower": 400, "upper": 500, "rate": 6.65},
    {"lower": 500, "upper": None, "rate": 8.80},
])


class TestCharge(unittest.TestCase):
    def test_first_slab_only(self):
        self.assertEqual(br.energy_charge(100, SLABS), 495.0)

    def test_telescopic(self):
        # 400*4.95 + 100*6.65 + 50*8.80 = 1980 + 665 + 440
        self.assertEqual(br.energy_charge(550, SLABS), 3085.0)

    def test_marginal_rate(self):
        self.assertEqual(br.marginal_rate(550, SLABS), 8.80)
        self.assertEqual(br.marginal_rate(450, SLABS), 6.65)

    def test_gap_in_slabs_rejected(self):
        with self.assertRaises(ValueError):
            br.slabs_from([{"lower": 0, "upper": 400, "rate": 1}, {"lower": 450, "upper": None, "rate": 2}])


class TestSample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = json.loads((Path(__file__).parent / "sample_bills.json").read_text())
        cls.r = br.run(spec)

    def test_published_order_does_not_match(self):
        self.assertFalse(self.r["tariff"]["order_rates_match"])

    def test_fit_recovers_escalation_and_verifies(self):
        self.assertAlmostEqual(self.r["tariff"]["escalation_factor"], 1.031, delta=0.01)
        self.assertTrue(self.r["tariff"]["rates_verified"])

    def test_scenarios_ordered(self):
        s = self.r["scenarios"]
        self.assertLess(s["low"]["year1_saving_inr"], s["base"]["year1_saving_inr"])
        self.assertLess(s["base"]["year1_saving_inr"], s["high"]["year1_saving_inr"])

    def test_subsidy_shortens_payback(self):
        b = self.r["scenarios"]["base"]
        self.assertLess(b["with_subsidy"]["escalated_payback_years"],
                        b["without_subsidy"]["escalated_payback_years"])

    def test_rate_saved_exceeds_average_tariff(self):
        # Solar displaces top-slab units, so the rate saved should beat the bill's average Rs/unit.
        for bill, row in zip(self.r["tariff"]["fitted_check"], self.r["scenarios"]["base"]["bills"]):
            if row["net_import"] > 500:
                self.assertGreater(row["avg_rate_saved"], bill["billed"] / bill["units"])


if __name__ == "__main__":
    unittest.main()
