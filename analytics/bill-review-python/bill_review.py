#!/usr/bin/env python3
"""Electricity bill review for a rooftop solar decision.

Indian domestic tariffs are telescopic: each slab of consumption is billed at its
own rate, and solar removes the most expensive top-slab units first. Savings
estimated from an "average rupees per unit" are therefore wrong, usually by a lot.

This tool works only from what the bills show:

  1. verify   Do the published slab rates reproduce every bill's energy charge?
  2. fit      If not, search for the uniform escalation factor (rates rounded to
              Rs 0.05) that does. Rates are called verified only when every bill
              matches within Rs 1.
  3. sizing   Consumption per day, average load, peak demand, and the PV size
              the sanctioned load allows.
  4. savings  Bill-by-bill saving for low / base / high yield, annualised from
              the bills themselves (never one summer bill times six).
  5. payback  Simple payback and a 25-year cash view with degradation and
              tariff escalation, with and without the subsidy.

Usage:
    python bill_review.py sample_bills.json            # full report to stdout
    python bill_review.py sample_bills.json --json     # machine-readable output

Inputs are the energy-charge line only. Fixed charges, duties and government
subsidy lines do not follow slab displacement and are kept out on purpose.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass

TOLERANCE_INR = 1.0  # a bill "matches" if computed and billed charge differ by <= Rs 1


@dataclass(frozen=True)
class Slab:
    lower: float
    upper: float | None  # None = no upper bound
    rate: float


def slabs_from(raw: list[dict]) -> list[Slab]:
    out = [Slab(s["lower"], s.get("upper"), s["rate"]) for s in raw]
    for a, b in zip(out, out[1:]):
        if a.upper != b.lower:
            raise ValueError(f"slab boundaries do not join: {a} -> {b}")
    return out


def energy_charge(units: float, slabs: list[Slab]) -> float:
    """Telescopic charge: each slab's units at that slab's rate."""
    total = 0.0
    for s in slabs:
        hi = math.inf if s.upper is None else s.upper
        if units > s.lower:
            total += (min(units, hi) - s.lower) * s.rate
    return round(total, 2)


def marginal_rate(units: float, slabs: list[Slab]) -> float:
    """Rate on the last unit consumed: the rate the first solar unit saves."""
    for s in slabs:
        hi = math.inf if s.upper is None else s.upper
        if s.lower < units <= hi:
            return s.rate
    return slabs[0].rate


# ---------------------------------------------------------------- verification
def verify(bills: list[dict], slabs: list[Slab]) -> tuple[bool, list[dict]]:
    rows, ok = [], True
    for b in bills:
        c = energy_charge(b["units"], slabs)
        diff = round(c - b["energy_charge"], 2)
        ok &= abs(diff) <= TOLERANCE_INR
        rows.append({"period_end": b["period_end"], "units": b["units"],
                     "billed": b["energy_charge"], "computed": c, "diff": diff})
    return ok, rows


def fit_escalation(bills: list[dict], base: list[Slab], step: float = 0.05,
                   k_min: float = 0.80, k_max: float = 1.30) -> tuple[float, list[Slab], float]:
    """Grid-search a uniform factor k; rates = round(base * k / step) * step."""
    best = None
    for i in range(int(k_min * 1000), int(k_max * 1000) + 1):
        k = i / 1000
        trial = [Slab(s.lower, s.upper, round(round(s.rate * k / step) * step, 2)) for s in base]
        err = sum(abs(energy_charge(b["units"], trial) - b["energy_charge"]) for b in bills)
        if best is None or err < best[2] - 1e-9:
            best = (k, trial, round(err, 2))
    return best


# ---------------------------------------------------------------- sizing
def sizing(bills: list[dict], site: dict) -> dict:
    total_units = sum(b["units"] for b in bills)
    total_days = sum(b["days"] for b in bills)
    kwh_day = total_units / total_days
    return {
        "bills": len(bills),
        "days_covered": total_days,
        "annualised_units": round(kwh_day * 365),
        "kwh_per_day": round(kwh_day, 2),
        "average_load_kw": round(kwh_day / 24, 2),
        "peak_demand_kw": max(b["max_demand_kw"] for b in bills),
        "max_pv_kwp_under_sanctioned_load": site["sanctioned_kw"],
        "covers_full_year": total_days >= 360,
    }


# ---------------------------------------------------------------- savings
def bill_savings(bills: list[dict], slabs: list[Slab], kwp: float, yield_kwh: float) -> list[dict]:
    rows = []
    for b in bills:
        gen = kwp * yield_kwh * b["days"]
        net = max(0.0, b["units"] - gen)
        before, after = energy_charge(b["units"], slabs), energy_charge(net, slabs)
        rows.append({"period_end": b["period_end"], "units": b["units"], "generation": round(gen),
                     "net_import": round(net), "surplus_unvalued": round(max(0.0, gen - b["units"])),
                     "before": before, "after": after,
                     "saving": round(before - after, 2),
                     "avg_rate_saved": round((before - after) / min(gen, b["units"]), 2) if gen else 0.0})
    return rows


def annual_saving(rows: list[dict], bills: list[dict]) -> float:
    days = sum(b["days"] for b in bills)
    return round(sum(r["saving"] for r in rows) * 365 / days, 0)


# ---------------------------------------------------------------- payback
def payback(year1_saving: float, cost: float, degradation: float,
            escalation: float, life: int) -> dict:
    cum, payback_year, flows = -cost, None, []
    for y in range(1, life + 1):
        s = year1_saving * (1 - degradation) ** (y - 1) * (1 + escalation) ** (y - 1)
        cum += s
        flows.append(round(s))
        if payback_year is None and cum >= 0:
            prev = cum - s
            payback_year = round(y - 1 + (-prev / s), 1)
    return {"simple_payback_years": round(cost / year1_saving, 1) if year1_saving else None,
            "escalated_payback_years": payback_year,
            "lifetime_net_inr": round(cum)}


# ---------------------------------------------------------------- report
def run(spec: dict) -> dict:
    bills = spec["bills"]
    order = slabs_from(spec["tariff"]["order_slabs"])
    order_ok, order_rows = verify(bills, order)
    if order_ok:
        k, slabs, err = 1.0, order, 0.0
    else:
        k, slabs, err = fit_escalation(bills, order)
    fitted_ok, fitted_rows = verify(bills, slabs)

    p = spec["proposal"]
    scen = {}
    for name, y in p["yield_kwh_per_kwp_day"].items():
        rows = bill_savings(bills, slabs, p["pv_kwp"], y)
        yr1 = annual_saving(rows, bills)
        scen[name] = {
            "yield_kwh_per_kwp_day": y, "year1_saving_inr": yr1, "bills": rows,
            "without_subsidy": payback(yr1, p["system_cost_inr"], p["degradation_per_year"],
                                       p["tariff_escalation_per_year"], p["life_years"]),
            "with_subsidy": payback(yr1, p["system_cost_inr"] - p["subsidy_inr"], p["degradation_per_year"],
                                    p["tariff_escalation_per_year"], p["life_years"]),
        }
    return {
        "tariff": {"order_rates_match": order_ok, "order_check": order_rows,
                   "escalation_factor": k, "fit_total_abs_error_inr": err,
                   "rates_verified": fitted_ok, "fitted_slabs": [s.__dict__ for s in slabs],
                   "fitted_check": fitted_rows},
        "sizing": sizing(bills, spec["site"]),
        "scenarios": scen,
    }


def print_report(r: dict) -> None:
    t, s = r["tariff"], r["sizing"]
    print("TARIFF")
    print(f"  Published order reproduces bills: {'yes' if t['order_rates_match'] else 'no'}")
    if not t["order_rates_match"]:
        print(f"  Escalation factor found: {t['escalation_factor']:.3f} "
              f"(total abs error Rs {t['fit_total_abs_error_inr']:,.2f})")
    print(f"  Rates verified against every bill (<= Rs {TOLERANCE_INR:.0f}): "
          f"{'VERIFIED' if t['rates_verified'] else 'NOT VERIFIED - treat savings as Likely'}")
    for row in t["fitted_check"]:
        print(f"    {row['period_end']}  units {row['units']:>5}  billed {row['billed']:>10,.2f}  "
              f"computed {row['computed']:>10,.2f}  diff {row['diff']:+.2f}")
    print("\nSIZING")
    for key, val in s.items():
        print(f"  {key.replace('_', ' ')}: {val}")
    print("\nSAVINGS AND PAYBACK")
    print(f"  {'scenario':<8}{'yield':>7}{'yr-1 saving':>14}{'payback (no subsidy)':>23}{'payback (subsidy)':>20}")
    for name, sc in r["scenarios"].items():
        print(f"  {name:<8}{sc['yield_kwh_per_kwp_day']:>7.1f}{sc['year1_saving_inr']:>14,.0f}"
              f"{sc['without_subsidy']['escalated_payback_years']:>21} y"
              f"{sc['with_subsidy']['escalated_payback_years']:>18} y")
    base = r["scenarios"]["base"]["bills"]
    surplus = sum(row["surplus_unvalued"] for row in r["scenarios"]["base"]["bills"])
    print(f"\n  Surplus generation valued at zero (conservative; export credit varies by DISCOM): "
          f"{surplus:,} kWh in the base case")
    print("\n  Base case, bill by bill (rate saved shows why average Rs/unit misleads):")
    for row in base:
        print(f"    {row['period_end']}  saving Rs {row['saving']:>9,.2f}  "
              f"avg rate saved Rs {row['avg_rate_saved']:.2f}/kWh")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.spec) as f:
        result = run(json.load(f))
    print(json.dumps(result, indent=2)) if a.json else print_report(result)
