#!/usr/bin/env python3
"""Load synthetic data into solar.db. Deterministic (fixed seed).

Two plants, one year. Three faults are planted so the queries have something to find:
  - PLANT_A: inverter trip, 5 days in March 2026 (generation near zero on sunny days)
  - PLANT_B: soiling builds through April 2026, cleared by cleaning on 1 May
  - PLANT_B: billing meter under-records by c. 6% in August 2026
"""
import math, random, sqlite3, datetime as dt
from pathlib import Path

random.seed(42)
here = Path(__file__).parent
db = sqlite3.connect(here / "solar.db")
db.executescript((here / "schema.sql").read_text())

plants = [("PLANT_A", "Rooftop plant A", "rooftop", 400.0, 330.0, "2025-10-01", 4.60),
          ("PLANT_B", "Ground-mount plant B", "ground-mount", 2000.0, 1650.0, "2025-10-01", 3.40)]
db.executemany("INSERT INTO plants VALUES (?,?,?,?,?,?,?)", plants)

start, days = dt.date(2025, 10, 1), 365
for pid, _, ptype, dc, ac, _, _ in plants:
    base_pr = 0.79 if ptype == "rooftop" else 0.81
    monthly = {}
    for i in range(days):
        d = start + dt.timedelta(days=i)
        season = 5.2 + 1.0 * math.sin(2 * math.pi * (d.timetuple().tm_yday - 80) / 365)
        monsoon = 0.62 if d.month in (7, 8) else 1.0
        poa = max(0.6, random.gauss(season * monsoon, 0.55))
        pr = base_pr + random.gauss(0, 0.015)
        if pid == "PLANT_A" and d.month == 3 and d.year == 2026 and 10 <= d.day <= 14:
            pr = 0.02                                    # inverter trip
        if pid == "PLANT_B" and d.month == 4 and d.year == 2026:
            pr -= 0.004 * d.day                          # soiling build-up
        kwh = min(dc * poa * pr, ac * 24 * 0.33)       # clip at a plausible daily AC ceiling
        db.execute("INSERT INTO irradiance_daily VALUES (?,?,?)", (pid, d.isoformat(), round(poa, 3)))
        db.execute("INSERT INTO generation_daily VALUES (?,?,?)", (pid, d.isoformat(), round(kwh, 1)))
        monthly[d.strftime("%Y-%m")] = monthly.get(d.strftime("%Y-%m"), 0) + kwh
    for m, kwh in monthly.items():
        loss = random.uniform(0.010, 0.022)              # normal transformer / cable loss
        if pid == "PLANT_B" and m == "2026-08":
            loss += 0.06                                 # meter fault
        db.execute("INSERT INTO meter_monthly VALUES (?,?,?)", (pid, m, round(kwh * (1 - loss), 0)))
db.commit()
print("solar.db loaded:", db.execute("SELECT COUNT(*) FROM generation_daily").fetchone()[0], "plant-days")
