#!/usr/bin/env python3
"""Telescopic slab tariff tools for Indian DISCOM bills.

Usage:
  python tariff_solver.py verify  spec.json   # do the slab rates reproduce each bill's energy charge?
  python tariff_solver.py fit     spec.json   # find escalation factor k so rates*k (rounded to 0.05) match
  python tariff_solver.py savings spec.json   # bill impact of the new solar, net of any existing system

spec.json uses the same schema as build_workbook.py (keys: tariff, bills, system, economics).
Works on the ENERGY CHARGE line only. Fixed charges, govt subsidy lines and duties are separate.
"""
import json
import sys


def charge(units, slabs):
    total = 0.0
    for s in slabs:
        lo, hi, r = s["lower"], s.get("upper"), s["rate"]
        hi = float("inf") if hi is None else hi
        if units > lo:
            total += (min(units, hi) - lo) * r
    return round(total, 2)


def verify(spec):
    ok = True
    for b in spec["bills"]:
        c = charge(b["units"], spec["tariff"]["slabs"])
        diff = round(c - b["energy_charge"], 2)
        ok = ok and abs(diff) <= 1.0
        print(f'{b.get("period", "bill")}: units {b["units"]}  computed {c:,.2f}  '
              f'bill {b["energy_charge"]:,.2f}  diff {diff:+.2f}')
    print("MATCH" if ok else
          "MISMATCH: wrong rates, wrong slab boundaries, or bill straddles a tariff revision")
    return ok


def fit(spec, step=0.05):
    base = spec["tariff"]["slabs"]
    best = None
    for i in range(800, 1301):  # k from 0.800 to 1.300
        k = i / 1000
        slabs = [dict(s, rate=round(round(s["rate"] * k / step) * step, 2)) for s in base]
        err = sum(abs(charge(b["units"], slabs) - b["energy_charge"]) for b in spec["bills"])
        if best is None or err < best[0]:
            best = (err, k, slabs)
    err, k, slabs = best
    print(f"best k = {k:.3f}  total abs error = {err:,.2f}")
    for s in slabs:
        print(f'  {s["lower"]:>6} - {str(s.get("upper") or "above"):>6} : {s["rate"]:.2f}')
    exact = err <= 1.0 * len(spec["bills"])
    print("EXACT: rates verified against bills" if exact else
          "NOT EXACT: tag rates as Likely and say so in the memo")
    return slabs


def savings(spec):
    slabs, sysd, eco = spec["tariff"]["slabs"], spec["system"], spec["economics"]
    for b in spec["bills"]:
        d = b["days"]
        gen = sysd["pv_kwp"] * eco["gen_kwh_per_kwp_day"] * d
        old = eco.get("existing_system_kwh_day", 0) * d
        net = max(0, b["units"] + old - gen)
        before, after = charge(b["units"], slabs), charge(net, slabs)
        print(f'{b.get("period", "bill")}: gen {gen:,.0f}  old-system {old:,.0f}  '
              f'net import {net:,.0f}  charge {before:,.2f} -> {after:,.2f}  '
              f'saving {before - after:,.2f}')


if __name__ == "__main__":
    mode, path = sys.argv[1], sys.argv[2]
    with open(path) as f:
        spec = json.load(f)
    {"verify": verify, "fit": fit, "savings": savings}[mode](spec)
