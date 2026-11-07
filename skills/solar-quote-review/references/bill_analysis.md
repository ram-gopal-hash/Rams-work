# Reading the client's electricity bill

The bill is the second load point. It sets the savings (through the slab rates) and the sizing (through max demand and consumption). Never estimate savings from an "average ₹/unit"; Indian domestic tariffs are telescopic, and solar removes the most expensive top-slab units first.

## 1. Extract from every bill

| Field | Why it matters |
|---|---|
| Bill period and days | Bi-monthly vs monthly; generation is per day |
| Units (final − initial reading × MF) | Recompute it; the reading arithmetic must reconcile |
| Energy charge line (before subsidy) | Used to back-solve and verify slab rates |
| Govt subsidy line, fixed charges, duties | Separate lines; they don't follow slab displacement |
| Max demand recorded (kW) | Real peak load; sizes the inverter |
| Sanctioned load (kW) and phase | Net-metering capacity cap; 3-phase enables a 3-phase hybrid |
| Tariff category (e.g. LA1A) | Selects the tariff schedule to search |
| "Solar RTS: YES/NO" | Tells you whether an existing system is net-metered or off-grid |

Ask for **six bills (one year)**. With one bill you have one season. Summer bills overstate annual consumption.

## 2. Back-solve the slab rates (do this before any savings figure)

1. Search the current tariff order for the category: `<DISCOM> domestic tariff slabs <year> <category>`. Regulator orders (SERC) are tier-1 sources.
2. Put the slabs in the spec and run `python scripts/tariff_solver.py verify spec.json`.
3. If it doesn't match, the order is probably stale (annual escalations). Run `fit`: it searches for a uniform escalation factor and rounds rates to ₹0.05. In the first review, the 2024 order × 1.031 reproduced two bills to the paisa.
4. Only call the rates verified when **every** bill matches within ₹1. Otherwise tag them "Likely" and show the residual.

## 3. Derive the sizing facts

- kWh/day = units ÷ days; average load kW = kWh/day ÷ 24.
- Peak = maximum of max demand across bills. Compare with the inverter rating. Above about 1.5x, ask for a smaller-inverter price, **unless** the per-phase check says otherwise: single-phase loads (ACs) must fit within the inverter's per-phase limit (often 50% of rating for 3-phase hybrids; read the datasheet).
- Max demand on the bill is an interval average. It hides motor and compressor start-up surge. Fixed-speed ACs surge several times their running load; inverter ACs much less.
- PV kWp vs sanctioned load. Arrays sized just under sanctioned load are deliberate; going larger usually needs a load enhancement before net metering.

## 4. Savings method

For each bill and each scenario:
- New generation = kWp × yield × days.
- Lost generation from any **existing** system being replaced (off-grid systems don't show on the bill, but their output vanishes when they're removed).
- Net import = max(0, units + lost − new).
- Saving = charge(units) − charge(net import), at the verified slabs.

Annualise with scenarios (winter, average, summer), never by multiplying one summer bill by six. Show savings as a range.

**Two splits the memo must show:**
- **Solar part vs backup part.** Under net metering a battery adds backup, not bill savings. Price the solar-only equivalent from the benchmark and show its payback separately. The backup premium is outage insurance; call it that.
- **With and without uncertain subsidies.**

## 5. Cliffs and quirks to check

- **Threshold cliffs.** Tamil Nadu (from May 2026): ≤500 units bi-monthly gets 200 free units; above 500 gets 100. If net import after solar lands near a cliff, flag it as an upside or downside lever and confirm with the DISCOM whether net-metered homes are billed on net import.
- **Cycles per year** = bills per year from the bill's 'Billing Cycle' field: bi-monthly = 6, monthly = 12. It is an input on the Payback sheet.
- **Free-unit value is not modelled.** The workbook only flags net import at or below the threshold. The 'Govt subsidy' line on the bill does not equal free units × first-slab rate (₹1,371 and ₹1,160 vs ₹495 for 100 units at ₹4.95), so don't put a number on it until the DISCOM explains the computation.
- **Subsidy line moves with consumption.** It is not constant (₹1,371 at 1,860 units vs ₹1,160 at 1,509 in the first review). Holding it constant is an Assumed simplification of a few hundred rupees per cycle; say so.
- **Network or grid-support charges** for rooftop solar exist in some states and categories. Check whether the bill has the line and whether it applies to domestic net metering.
- **Tariff revisions mid-period.** A bill straddling a revision date will not reconcile to a single rate set.
