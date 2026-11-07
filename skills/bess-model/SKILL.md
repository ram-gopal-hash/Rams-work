---
name: bess-model
description: >
  Price a BESS (Battery Energy Storage System) deal for G2G Kaamyabi as an operating lease or a
  storage PPA, solving for the rental or tariff that hits a target post-tax equity IRR. Builds a
  9-sheet Excel workbook: Summary, Value Stack, Assumptions, Debt Schedule, Lease Model, PPA Model,
  Scenario Comparison, Sensitivity, Negotiation Points. Use whenever Ram mentions BESS, battery
  storage, energy storage, storage PPA, battery lease, peak shaving, DG offset, ToD arbitrage, or
  uploads a supplier battery quote and asks how to price it, lease it, or whether the deal works.
  Trigger on casual phrasing too: 'does this battery deal make sense?', 'what should we charge for
  storage?', 'run the numbers on this BESS quote'. Covers the customer value stack (DG offset, ToD
  arbitrage, solar-surplus charging, any export regime) and the pricing corridor between G2G's IRR
  floor and the customer's ceiling. For solar-only use solar-model.
---

# BESS Financial Model — G2G Kaamyabi Format

_v1.2 — adds: physical feasibility checks (one-charging-window rule, nameplate sizing, PCS power, grid-charging economics test), live on Value Stack section F._

_v1.1 — adds: Scenario Comparison as pricing source of truth; TV/warranty as negotiable-until-contracted; rebuild protocol; integrity-checks vs deal-verdict separation._

## What This Skill Does

Prices a behind-the-meter BESS deal from a supplier quote. Two structures, both solved to a target post-tax equity IRR:

- **Option A — Operating Lease:** flat monthly rental, full-service (G2G bears O&M + insurance). No volume risk.
- **Option B — Storage PPA:** ₹/kWh on energy discharged. Volume risk sits with G2G unless a take-or-pay floor is contracted.

Both are **tolling structures**. G2G owns and operates the battery; the customer supplies the charging energy. This single fact drives the whole architecture — see "The Tolling Insight" below.

Two deliverables, always:
1. The `.xlsx` workbook (live formulas; static Python-solved grids where a solver is unavoidable).
2. A chat summary: solved lease rental | solved PPA tariff | min DSCR | **the corridor** (ceiling − floor) | whether the deal exists.

---

## Step 0: Architecture First — Do Not Build Yet

Ram wants the design discussed before any code runs. This is a consistent, explicit preference across sessions. Present the plan — capex build-up, tenure scenarios, terminal-value treatment, value-stack structure — and get agreement. Then build.

Skipping this step produces a model that gets rebuilt anyway. It is not a shortcut.

---

## The Tolling Insight (the thing that makes BESS different from solar)

**Charging source does not affect G2G's IRR.** The customer buys the input energy. Whether the battery charges from grid off-peak, solar surplus, or a diesel-fired unicorn, G2G's cash flows are identical.

What charging source *does* affect:
- The **customer's** all-in cost, and therefore their willingness-to-pay ceiling.
- The **cycles per day** achievable — which is the single largest driver of the required PPA tariff.
- The **dispatch rights** that need writing into the contract.

Consequence: the model needs two halves that meet at one number.

```
G2G FLOOR                          CUSTOMER CEILING
(what we must charge               (what they can pay
 for 18% post-tax IRR)              and still save money)
        │                                   │
        └──────── THE CORRIDOR ─────────────┘
              If negative, there is no deal.
```

**Lead with the corridor in every summary.** A beautifully solved floor price is worthless if the customer's ceiling sits below it. On the Sangli 250 kW / 522 kWh deal at 1 cycle/day, the floor was ₹20.48/kWh and the ceiling ₹10.62 — the deal did not exist until cycles rose. Say so plainly and early.

---

## Step 1: Read the Supplier Quote — What to Extract and What to Distrust

| Extract | Watch for |
|---|---|
| Supply cost (ex-works, ex-GST) | Almost never the full capex. See below. |
| kW (PCS) / kWh (nameplate) | |
| Cycle life to 70% SOH (e.g. 8,000) | Sets the degradation curve and the cycle budget. |
| Round-trip efficiency | **Frequently absent.** If absent, flag it — see Negotiation Points. |
| Uptime / availability guarantee | 95% is common; 96–98% is the C&I benchmark. |
| O&M / extended warranty schedule | Frequently ambiguous on per-year vs lump-sum. **Ask.** |
| Extended warranty beyond Y5 | A liability, not a footnote. See Terminal Value. |
| FX / commodity peg | USD-INR and lithium pegs are standard and dangerous. |
| Payment terms, delivery, validity | Validity is often 7 days. |

**Supplier prices are ex-works.** Client scope typically excludes freight, transit insurance, civil foundation, HT breaker, transformer-to-termination cabling, crane, and local install labour. Add **12% of supply cost** as the default capex adder and label it an estimate until real quotes land. Peer models put this at ₹10–15 L on a ₹87 L system; 12% is the calibrated midpoint. Every +5% on capex moves the lease rental ~₹0.13 L/month.

---

## Step 2: Assumptions — G2G Defaults

Required from the user (ask, do not assume):

| Parameter | Notes |
|---|---|
| Supplier quote | The document itself |
| Target equity IRR | Default (illustrative): **18% post-tax** |
| Debt:equity and rate | Default (illustrative): **70:30 @ 10.5%** |
| Tenure(s) to price | Default: price 5 / 7 / 10 side by side |
| Cycles/day | **Ask, then sensitise anyway.** Never accept a single number quietly. |
| DG-offset share of discharge | Decides the customer's ceiling. Get outage hours / fuel logs. |
| Solar surplus available | kWh/day, monsoon-adjusted annual average |
| Export regime | Curtailed / net-metered / banking / RESCO PPA |

Defaults (state them, let the user override):

| Parameter | Default | Why |
|---|---|---|
| Capex adder | 12% of supply | Client-scope items excluded from ex-works quotes |
| DoD | 90% | LFP usable window |
| Availability | 95% | Typical supplier guarantee; negotiate up |
| RTE | 86% | AC-to-AC incl. chiller aux load |
| Depreciation | **15% WDV** | Standalone BESS = plant & machinery |
| Tax | 25.17% | Sec 115BAA (22% + surcharge + cess), no MAT |
| O&M escalation | Per supplier schedule | Do not invent one |
| Insurance | 0.35% of capex p.a. | All-risk, lessor's scope |
| Debtor days | 30 | Monthly billing |
| Max debt tenure | **7 years** | Lenders will not go 10 on BESS today |
| Customer min saving | 20% | Ceiling = net value × (1 − this). Make it an input. |

### Depreciation — the 15% vs 40% question

Default to **15% WDV** (plant & machinery). The 40% "renewable energy device" rate is only defensible if the BESS is capitalised within an integrated solar-plus-storage asset, and it needs CA sign-off. It is worth roughly ₹0.13 L/month of pricing headroom — real money, but do not price it in on hope. Model it as a scenario, never as the base case.

---

## Step 3: Tenure Scenarios and Terminal Value

Terminal value is the **biggest single judgement call** in a BESS model and the number most likely to be challenged. Make every parameter an editable input, never a hardcode.

| | 5-year | 7-year | 10-year |
|---|---|---|---|
| Gross TV (% capex) | 25% | 15% | 7.5% |
| Post-Y5 extended warranty | **Netted off TV** — the buyer inherits it | Expensed p.a. from Y6 | Expensed p.a. Y6–10 |
| Debt tenure | 5 | 7 | 7 (Y8–10 deleveraged) |
| End SOH @ 1 cyc/day | ~93% | ~90% | ~86% |

Two rules learned the hard way:

1. **Amortise the post-Y5 warranty block evenly, don't lump it in Year 6.** Same NPV, much smoother DSCR, and lenders read DSCR year by year.
2. **Check the cycle budget.** At 2 cycles/day over 10 years you consume ~7,300 of an 8,000-cycle warranty life — 91%. Either cap cycles contractually or price augmentation capex. Flag it; do not let it pass silently.

**Terminal value and warranty treatment stay negotiable until they are contractually fixed.** Both are assumptions carrying real money — a 25% vs 15% TV moves the 5-year lease by roughly ₹0.25 L/month — and neither is settled by asserting a number in a spreadsheet. They are settled by a clause: a fixed-price customer buyout, a renewal option, a transferable extended warranty, a redeployment plan. Until such a clause exists, present them as open items, not as inputs that happen to have values. The moment the model treats them as fixed, the negotiation stops happening.

Solved prices **fall** as tenure lengthens (longer amortisation beats the lower terminal value). That is a sales lever for locking customers in longer — say so.

### Scenario Comparison is the source of truth for tenure-specific pricing

The live sheets follow the tenure toggle, but the *prices* are solver outputs — one solved pair per tenure, sitting static on Scenario Comparison. Toggling tenure without pasting the matching price into Assumptions leaves the model computing an IRR that is no longer 18%.

Treat this as governance, not a footnote: **any price quoted to anyone comes from Scenario Comparison, never from a live sheet whose price cell may be stale.** Recon check #1 and #2 exist to catch the mismatch — if they read CHECK after a tenure toggle, that is the model working correctly, not a bug.

---

## Step 4: The Customer Value Stack (regime-agnostic by construction)

Do not model export regimes. Model the **opportunity cost of a solar-surplus kWh** — the only number a regime actually changes. One dropdown, four values:

| Regime | Opportunity cost | Logic |
|---|---|---|
| Curtailed / export-blocked | ₹0 | Surplus is stranded; the battery rescues it free |
| Net metering | ~₹3.3 | Export credit forgone |
| Banking | ~₹3.5 | Banked value forgone |
| RESCO PPA (Kaamyabi-owned solar) | = the solar tariff | The customer pays for those units anyway |

**Charging waterfall:** solar surplus fills first (cheaper lane), off-peak grid tops up to reach the target cycles. Charging energy = discharge ÷ RTE — which is precisely why the RTE guarantee is a commercial issue, not a technical footnote.

**Take solar surplus as a direct input (kWh/day, monsoon-adjusted).** Do not derive it from nameplate differences: a 530 kWp DC array against 400 kW demand does not yield 130 kW of surplus, because AC output peaks at ~75–85% of DC rating and the surplus is a bell-shaped sliver over a few midday hours. Nameplate arithmetic overstates it badly.

**Discharge value:** DG-offset share × DG cost (~₹25/kWh) + peak-shave share × ToD peak rate. Blend them.

```
Ceiling = (blended avoided cost − blended charging cost) × (1 − customer min saving)
Corridor = Ceiling − Floor
```

If G2G also owns the solar, add an **internal memo** section: every charging electron is solar-PPA revenue *and* the discharged electron is storage revenue. Two streams on the same electron gives room to concede on storage price and recover on solar volume. Mark it internal — do not show it to the customer.

### Physical Feasibility — check before pricing anything

Annual-energy arithmetic will happily produce a cycle count that no real site can deliver. A model that offsets 386,565 kWh/year looks fine on a spreadsheet and is impossible if the battery can only move 446 kWh in a day. **Run these checks before the pricing solve, not after.**

**1. The one-charging-window rule.** With solar-only charging, there is one sun per day, therefore one charging window, therefore:

```
cycles/day ≤ 1.0
```

The only exception is genuine discharge demand *inside* the charging window (e.g. a daytime DG-offset load), which permits an intra-window cycle. If every discharge window sits after the solar window — evening peak, overnight — the cap is hard. Sites with economic off-peak grid charging escape this: a second, separate charging window exists. Sites where off-peak *is* solar hours do not.

**2. Test whether grid top-up is economic before assuming >1 cycle.**

```
grid charging cost to deliver 1 kWh = off-peak rate ÷ RTE
```

Viable only if that sits well below the blended avoided rate. At Sangli: ₹5.48 ÷ 0.86 = ₹6.37 against ₹18.65 — viable, so 1.5–2 cycles is reachable. At Sevasadan: ₹13.93 ÷ 0.86 = ₹16.20 against ₹17.85 — a ₹1.65 spread, dead. **This single test decides whether the cycles lever exists at a site.** Do not carry the Sangli sensitivity conclusion ("corridor opens at 1.5–2 cycles") to a site that cannot physically reach 1.5 cycles.

**3. Nameplate sizing check.**

```
required nameplate  ≥  daily discharge kWh ÷ (DoD × availability)
```

At G2G defaults (90% × 95% = 0.855), a battery delivers 85.5% of nameplate per fill. A site needing 1,059 kWh/day therefore needs ~1,240 kWh nameplate, not 522. Run this the moment a load profile arrives, and state the required size — sizing is usually the real question, and pricing a wrongly-sized unit wastes the analysis.

**4. PCS power checks** — energy can fit while power does not:

```
charge power    = charging kWh/day ÷ charging window hours   ≤ PCS kW
discharge power = discharge kWh/day ÷ discharge window hours ≤ PCS kW
```

Averages understate the peak: solar surplus is a bell curve, so midday can clip the PCS while the tails contribute little. Flag it as needing the hourly profile — annual totals cannot answer it.

**Where these live:** on the Value Stack sheet with the deal verdict, **not** in the Summary reconciliation block. A physically infeasible configuration is not a broken model — it is a correct model reporting a real constraint. Same separation as the corridor.

### ToD inputs (Maharashtra / MSEDCL)

Verify against the current MERC MYT order and, better, the customer's actual bill. As of the FY26–30 control period: peak 17:00–24:00 at +25% for HT/LT industrial, off-peak in the **solar hours 09:00–17:00** with a 25% rebate. Note the consequence — grid top-up charging happens in the same window as the solar surplus. Base energy charge is category-specific; never guess it.

---

## Step 5: Build the Workbook

Run `references/bess_builder.py` — it carries the working engine (bisection IRR solver, tenure logic, value stack) and the 9-sheet writer. Adapt the `BASE` dict to the deal; the structure holds.

**Then always recalculate.** openpyxl writes formulas but never evaluates them: until something calculates the file, every formula cell is empty and any `#REF!` / `#NUM!` / `#NAME?` bug stays invisible. Never quote a number from an unrecalculated workbook.

```bash
python3 references/bess_builder.py
python3 references/recalc.py <output.xlsx> 120
```

`recalc.py` is bundled and self-contained — it works in the Claude.ai/Cowork sandbox, and in Claude Code on Windows, macOS and Linux, finding LibreOffice wherever it lives. Exit codes: `0` clean, `1` formula errors found (locations printed), `2` could not recalculate — **values not verified, do not trust them**.

Two traps it handles, both of which will otherwise waste an hour:
- A killed or timed-out LibreOffice leaves a `.~lock.<file>#` beside the workbook. Every later headless run then blocks on it silently until timeout — including runs of entirely different scripts. It looks exactly like LibreOffice is broken. `recalc.py` clears stale locks first.
- The sandbox blocks AF_UNIX sockets and needs an LD_PRELOAD shim; a normal laptop does not. `recalc.py` detects which environment it is in.

After recalculating, **read back the Summary reconciliation checks** — all six must read OK before the model goes anywhere.

**Sheet order:** Summary → Value Stack → Assumptions → Debt Schedule → Lease Model → PPA Model → Scenario Comparison → Sensitivity → Negotiation Points.

**Colour convention (consistent with solar-model):**
- Blue = input
- Black = live formula
- Green = cross-sheet link
- **Purple = static Python-solved** (sensitivity grids, scenario prices)
- Yellow fill = key lever or solved price

**Live where possible, static only where a solver is unavoidable.** Everything downstream of an input must recalculate. Tenure is a master toggle: set 5, 7 or 10 on Assumptions and every sheet follows, with years beyond tenure masked to zero by an explicit flag row.

**Sensitivity tables that earn their place:**
- T1: PPA tariff — cycles/day × terminal value %
- T2: Lease rental — capex adder × terminal value %
- T3: Depreciation (15/40%) and interest rate scenarios
- Corridor vs cycles (floor static, ceiling live) — the one that decides the deal

---

## Step 6: Reconciliation Checks — Non-Negotiable

Put these on the Summary sheet as live formulas reading OK / CHECK. They have caught real bugs:

1. Lease IRR = target (within 5bps)
2. PPA IRR = target
3. Debt fully amortised by end of debt tenure
4. **No cash flows beyond tenure** (lease and PPA separately)
5. Charging waterfall balances (solar + grid = required)
6. Σ principal = debt drawn

### Bug patterns to watch — every one of these has bitten

- **Working-capital delta beyond tenure double-counts the debtor release.** In Year 6 of a 5-year deal, `debtors(6) − debtors(5)` is negative, and a cash-flow row that subtracts it hands back the Year-5 debtors a second time. Symptom: IRR reads ~19.2% instead of 18.0%. Fix: multiply the WC delta by the tenure flag. Check #4 catches this.
- **Note text starting with `=` or `@` is parsed by Excel as a formula** and returns #N/A. Reword the note.
- **CUMIPMT / CUMPRINC throw #NUM! when debt = 0** or the period exceeds the loan term. Gate with `IF(year <= debt_tenure, ..., 0)`.
- **Cross-sheet references break on sheet names containing spaces** unless quoted: `'Debt Schedule'!C6`.
- **Hardcoded values that don't move when assumptions change** — the failure mode of every model built by pasting a chat answer into Excel.

---

## Integrity Checks vs the Deal Verdict — Keep Them Apart

The six checks above answer one question: **does the model compute correctly?** The corridor on Value Stack answers a different one: **does the deal exist?**

Never merge them into a single OK/CHECK list. If "customer ceiling above floor" sits among the integrity checks, a negative corridor reads as a bug — and the instinctive response to a bug is to adjust assumptions until it turns green. That is precisely how a model gets talked into a deal that does not work.

A model that correctly reports the deal is underwater is a **working model, not a failing one.** Recon checks live on Summary; the deal verdict lives on Value Stack. Report both, and never let the second one be confused for a defect in the first.

---

## Rebuild Protocol

For a model that has drifted, broken, or been edited by someone else — do not patch cell by cell. Recast in this order, because each step depends on the one before:

1. **Recast formulas from Assumptions forward** — through Debt Schedule, then depreciation and tax, then the operating sheets. Every value downstream of an input must be a formula, not a pasted number.
2. **Re-link lease and PPA prices to the tenure toggle** — and confirm the price cells hold the solved pair for the *selected* tenure.
3. **Recompute the scenario grids** for 5, 7 and 10 years by re-running the solver. Static grids go stale the moment any assumption moves; a stale grid is worse than no grid because it looks authoritative.
4. **Recalculate the workbook and validate** — all six recon checks OK, both IRRs at target, DSCR sane. If a check reads CHECK, stop and find out why. Do not proceed.
5. **Preserve the Negotiation Points tab**, with every ask still tied to the model input it protects. This tab is the first thing lost in a rebuild and the last thing anyone remembers to restore.

A rebuild that skips step 4 is not a rebuild — it is a new set of unverified numbers wearing the old model's name.

---

## Step 7: Negotiation Points Sheet

Every ask must name the model input it protects. Supplier quotes are systematically incomplete in the same places:

| Clause | Typical supplier position | Benchmark | Model input protected |
|---|---|---|---|
| RTE guarantee | Absent | 85–88% AC-to-AC at PCC, incl. aux load | RTE → customer charging cost |
| Uptime / restoration | 95%, 96h restoration | 96–98%, 48h for C&I | Availability → revenue |
| FX / lithium peg | Repriced at PO date, 7-day validity | Fixed INR or ±2.5% cap | Supply cost |
| O&M schedule | Ambiguous per-year vs lump-sum | 2.0–3.5% of capex p.a. | O&M rows (~₹0.14 L/month) |
| Post-Y5 warranty | Opt-in within 3 months | 6–12 month window | Terminal value / Y6+ opex |
| Payment terms | 30% on PO, small PBG | Retention or PBG to PR test | Construction risk |
| Client scope | Freight, civil, HT, cabling excluded | Turnkey or shared | Capex adder |

---

## Step 8: The Chat Summary

Lead with the corridor and whether the deal exists. Then the prices. Then what would change the answer.

```
At 1 cycle/day this deal does not exist: floor ₹20.48/kWh vs ceiling ₹10.62 — corridor −₹9.86.

Solved to 18% post-tax:
              5-year     7-year    10-year
Lease/month   ₹2,69,710  ₹2,16,700 ₹1,93,530
PPA (₹/kWh)   ₹20.48     ₹16.61    ₹15.00
Min DSCR      1.36x      1.39x     1.24x

Two levers close the gap: cycles/day (2.0 brings the floor to ₹10.34) and DG-offset
share (60% → 90% lifts the ceiling toward ₹17). Get the customer's outage hours and
DG fuel logs before quoting anything.
```

Close with the standard disclaimer: for discussion; tax treatment, Ind AS 116 lease classification, and lender terms need professional review.

---

## File Naming

`ProjectName_BESS_PricingModel_vX.Y.xlsx` — no spaces, increment versions, never overwrite.
