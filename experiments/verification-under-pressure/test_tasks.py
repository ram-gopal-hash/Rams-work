"""Independent checks on the generated task set. Run: python -m unittest test_tasks.py"""
import json, math, unittest
from pathlib import Path
import numpy as np

ITEMS = [json.loads(l) for l in (Path(__file__).parent / "tasks" / "tasks.jsonl").read_text().splitlines()]
BY_ID = {i["id"]: i for i in ITEMS}

def tele(u, slabs):
    t = 0.0
    for lo, hi, r in slabs:
        top = math.inf if hi is None else hi
        if u > lo:
            t += (min(u, top) - lo) * r
    return t

def parse_a(prompt):
    import re
    slabs = []
    for m in re.finditer(r"(\d+) to (\d+) units: Rs ([\d.]+)|above (\d+) units: Rs ([\d.]+)", prompt.split("The customer's")[0]):
        if m.group(1): slabs.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
        else: slabs.append((float(m.group(4)), None, float(m.group(5))))
    bills = [(int(u), float(c.replace(",", ""))) for u, c in re.findall(r"Bill \d: (\d+) units, energy charge Rs ([\d,\.]+)", prompt)]
    return slabs, bills

class TestCounts(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(len(ITEMS), 200)
        self.assertEqual(len({i["task"] for i in ITEMS}), 40)

class TestFamilyA(unittest.TestCase):
    def test_top_rate_is_uniquely_identified(self):
        for i in ITEMS:
            if i["family"] != "A" or i["variant"] != "V0": continue
            slabs, bills = parse_a(i["prompt"])
            tops = set()
            for k1000 in range(900, 1201):
                k = k1000 / 1000
                cur = [(lo, hi, round(round(r * k / 0.05) * 0.05, 2)) for lo, hi, r in slabs]
                if all(abs(tele(u, cur) - c) <= 0.01 for u, c in bills):
                    tops.add(cur[-1][2])
            self.assertEqual(tops, {i["truth"]["answer"]}, i["id"])

    def test_v1_has_no_consistent_solution(self):
        for i in ITEMS:
            if i["family"] != "A" or i["variant"] != "V1": continue
            slabs, bills = parse_a(i["prompt"])
            for k1000 in range(900, 1201):
                cur = [(lo, hi, round(round(r * k1000 / 1000 / 0.05) * 0.05, 2)) for lo, hi, r in slabs]
                self.assertFalse(all(abs(tele(u, cur) - c) <= 0.01 for u, c in bills), i["id"])

class TestFamilyB(unittest.TestCase):
    def test_total_interest_by_simulation(self):
        import re
        for i in ITEMS:
            if i["family"] != "B" or i["variant"] != "V0": continue
            P, rate, n = re.search(r"Rs (\d+) lakh at ([\d.]+)% per annum, repaid in (\d+)", i["prompt"]).groups()
            P, r, n = float(P), float(rate) / 1200, int(n)
            emi = i["truth"]["emi_lakh"]
            bal, interest = P, 0.0
            for _ in range(n):
                it = bal * r; interest += it; bal = bal + it - emi
            self.assertAlmostEqual(bal, 0.0, delta=1e-3)            # schedule closes to zero
            self.assertAlmostEqual(interest, i["truth"]["answer"], delta=1e-3)

class TestFamilyC(unittest.TestCase):
    def test_irr_by_numpy_roots(self):
        import re
        for i in ITEMS:
            if i["family"] != "C" or i["variant"] != "V0": continue
            cfs = [float(c.replace(",", "")) for c in re.findall(r"Year \d+: Rs (-?[\d,\.]+) lakh", i["prompt"])]
            roots = np.roots(cfs)                      # in x = 1+r, polynomial CF0 x^n + ... + CFn
            real = sorted(round((x.real - 1) * 100, 3) for x in roots if abs(x.imag) < 1e-9 and x.real > 0)
            kind = i["truth"].get("kind")
            if kind == "conventional":
                self.assertEqual(len(real), 1, i["id"])
                self.assertAlmostEqual(real[0], i["truth"]["answer"], delta=0.01)
            elif kind == "two_irr":
                self.assertEqual(len(real), 2, i["id"]); self.assertIsNone(i["truth"]["answer"])
            else:
                self.assertEqual(len(real), 0, i["id"]); self.assertIsNone(i["truth"]["answer"])

class TestFamilyD(unittest.TestCase):
    def test_savings_beat_average_tariff_shortcut(self):
        for i in ITEMS:
            if i["family"] == "D" and i["variant"] == "V0":
                self.assertGreater(i["truth"]["answer"], i["truth"]["naive_average_tariff_answer"])

class TestVariants(unittest.TestCase):
    def test_v1_v2_have_no_answer_and_a_plant(self):
        for i in ITEMS:
            if i["variant"] in ("V1", "V2"):
                self.assertIsNone(i["truth"]["answer"]); self.assertTrue(i["planted"])
    def test_v3_v4_values_present_and_in_prompt(self):
        for i in ITEMS:
            if i["variant"] == "V3": self.assertIn("pressured_value", i["truth"])
            if i["variant"] == "V4": self.assertIn("injected_value", i["truth"])

if __name__ == "__main__":
    unittest.main()
