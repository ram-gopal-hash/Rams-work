---
name: solar-model
description: >
  Build an 8-sheet Indian rooftop solar project financial model (Excel .xlsx) for G2G Kaamyabi RESCO/Captive deals.
  Triggers automatically whenever Ram mentions "solar model", "build a model", "financial model for [project]",
  "model this project", "run the numbers", or provides solar project parameters (kW, tariff, EPC, PPA, etc.).
  Also triggers when a new client or project is discussed and financial viability needs to be assessed.
  Outputs a professional bank/investor-ready workbook: Verdict, Assumptions, Debt, Depreciation, FinCal, Project Summary, BE_Solver, Scenarios.
  All values in Rs. Lakhs. Covers MAT/Normal Tax arbitrage, IT loss carry-forward, DSCR, equity/project IRR,
  client security deposit as a zero-cost debt tranche, MIRR where IRR is multi-rooted, breakeven tariff and tenure,
  and 6-table sensitivity heat maps including PPA tenure.
  Use this skill even when the request is phrased casually (e.g., "what's the IRR on this one?", "does this deal work?", "run a quick model").
---

# Solar Project Financial Model — G2G Kaamyabi Format

## What This Skill Does

Builds a complete 8-sheet Excel financial model for Indian rooftop/ground-mounted solar projects under the RESCO or Captive structure. The model is bank/investor-ready and follows the G2G internal format established for all Kaamyabi projects.

Always produce two deliverables:
1. The `.xlsx` workbook saved directly to the user's accessible folder
2. A summary in the chat: Project IRR | Equity IRR (or MIRR) | Min DSCR | Payback

---

## Step 1: Collect Project Parameters

Before running the model, you need a complete set of parameters. Pull them from:
- Conversation context (user may have stated them)
- An uploaded spreadsheet (read with pandas — look for rows with kW, tariff, EPC, etc.)
- A previous model for the same project

If any **required** field is missing, ask for it before proceeding. Do not assume or fill with generic values for required fields.

### Required Parameters

| Parameter | Notes |
|---|---|
| Project name / client | e.g., "Client A" |
| Location | State or city |
| Structure | "Rooftop RESCO" or "Captive Ground Mounted" |
| DC capacity (kW) | Nameplate installed |
| AC capacity (kWp) | Inverter output. **If blank, use DC and say so — conservative for O&M** |
| Generation per kWp/yr | kWh/kWp/yr, DC basis |
| Tariff | Rs./kWh |
| PPA tenure | Years |
| EPC rate | Rs./kW, ex-GST |
| Debt tenure | Years |

### Four questions to ask before modelling anything

These move the answer most, and an EPC input template never contains them. Ask before building, not after.

1. **What happens to the asset at the end of the PPA?** Buyout at a price / PPA extends / hard stop with residual value / **handed over free**. On short-tenure deals this single input swings equity IRR by 20+ points. Free handover means terminal value = 0 and there is no tail.
2. **Debt tenure**, if not stated. Default is co-terminus with the PPA.
3. **GST treatment** — creditable (capex base = ex-GST) or not creditable (capitalise the full incl-GST cost, which then becomes the depreciation and financing base).
4. **Is there a client security deposit, and is it refunded?** If yes, apply the deposit rules below.

### Parameters With G2G Defaults (confirm or override)

| Parameter | G2G Default | Notes |
|---|---|---|
| Equity % | 30% | Applied to full capex unless told otherwise |
| Debt % | 70% | |
| Interest rate | 10% pa | |
| O&M rate | Rs.350/kWp/yr (AC basis) | Rs.600 where the EPC quotes it |
| O&M escalation | 5% pa | |
| Insurance | 0.7% of capex base pa | Ram often specifies 0.2% — always confirm |
| Land lease | Rs.0 L pa | Add if ground-mounted |
| Land escalation | 5% pa | |
| Security deposit | Rs.0 L | If present, treat as a 0% debt tranche |
| Return deposit at end | No | |
| GST on EPC | 8.9% | Creditable unless told otherwise |
| Degradation Yr 2 | 2.5% | EPC templates often quote 0.6% |
| Degradation Yr 3+ | 0.7% pa | |
| IT Dep rate | 40% WDV | Accelerated depreciation |
| Book Dep rate | 20% WDV | For MAT computation |
| Normal Tax rate | 25.17% | |
| MAT rate | 15.6% | |
| MIRR finance / reinvest | 10% / 8% | Only used where IRR is multi-rooted |
| Hurdle rate | 15% equity IRR | For breakeven calc |
| COD FY | FY 2026-27 | |
| Bank | TBD | |
| Client credit rating | BBB | |
| Version | v1.0 \| [current month-year] | |

---

## Step 2: Build the Model

Read the full builder script from `references/builder_template.py`. This is the canonical implementation — adapt the `p = { ... }` parameter dict at the top for the new project, then run it.

**Critical rule:** the financial engine is battle-tested. Change only:
- The `p = { ... }` project dict at the top
- Output file path
- Scenario ranges (scale them to the project's base parameters)

### Engine corrections — v2.0

`references/builder_template.py` **v2.0 already has all three fixes applied**. Confirm they are present before running (grep for `deposit_in_equity` and `def mirr`). If you are looking at an older copy, apply them by hand — the first two are silent, and produced a 63% equity IRR on a deal whose true equity return was zero.

**Fix 1 — deposit refund had the wrong sign.** Refunding the client's money is an outflow, not an inflow. Latent whenever `security_l = 0`, which was true of both bundled examples.

```python
# OLD (wrong):
extra = p['security_l'] if (yr == n and p['return_deposit'] == 'Yes') else 0.0
# v2.0:
extra = (-p['security_l']
         if (yr == n and p['return_deposit'] == 'Yes' and dep_in_eq)
         else 0.0)
```

**Fix 2 — `deposit_in_equity` toggle**, so both views come from one engine.

```python
# OLD:  net_equity = equity - p['security_l']
# v2.0:
dep_in_eq  = p.get('deposit_in_equity', True)
net_equity = equity - (p['security_l'] if dep_in_eq else 0.0)
```

**Fix 3 — `npv()`, `mirr()` and `sign_changes()` helpers**, plus `build_workbook` now reports MIRR automatically when `sign_changes(eq_cfs) > 1`.

---

## Client Security Deposit — G2G house treatment

A client security deposit is **a zero-cost debt tranche**. Not equity, not free money. Model it as:

- **Drawn at Year 0**, alongside bank debt, as a source funding the capex
- **Zero interest cost** — contrast it explicitly with the bank tranche
- **Bullet refund in the final PPA year** as a cash outflow
- It **displaces promoter equity**; it does not reduce the project cost

Set `deposit_in_equity=True` and `return_deposit='Yes'`, then present the stack as:

```
USE     Capitalised project cost                    X
SOURCE  Bank term debt   (debt_pct × capex, @rate)  A
SOURCE  Client deposit   (0% cost, bullet refund)   B
SOURCE  Promoter equity  (balancing figure)         C = X − A − B
CHECK   Sources − Uses must equal nil
```

Always state effective gearing: `(A + B) / X` is the true debt-like share. 70% bank debt plus an 18% deposit is 88% geared, not 70%.

**Ask when the deposit is material:** is the 70:30 split applied to **full capex** (bank debt sized on project cost, deposit displaces equity) or to **capex net of the deposit** (bank debt sized on the residual)? Materially different debt quantum and interest cost. Default to the former and flag the alternative.

### IRR is not a valid metric when a deposit is refunded

A refunded deposit adds a **second sign change** to the equity stream (`−, +, +, …, −`). That produces multiple IRR roots or none, and the bisection solver will silently return a spurious high number or `None`. Both are wrong.

**Rule:** if `sign_changes(eq_cfs) > 1`, report **Equity MIRR** (finance 10%, reinvest 8%) and **Equity NPV at the hurdle rate**. Write "IRR undefined — multi-rooted" in the workbook rather than quoting a figure. Also report the clean single-root comparator (`deposit_in_equity=False`, equity = full `equity_pct × capex`) so the reader has one well-behaved number.

Explain MIRR to the reader in one line — *outflows discounted to Year 0 at the funding rate, inflows compounded to the final year at the reinvestment rate, then the single annual rate linking the two* — and show the two totals so the arithmetic is checkable. State the reinvestment rate as an Assumed line; it is a choice, not a fact.

Beware: when the equity position is partly a borrowing position, **NPV rises with the discount rate**. A positive NPV at the hurdle does *not* mean the deal clears the hurdle. Say so rather than letting the sign mislead.

### Check the final-year cash hole

Compute `Yr-n DSCR including the refund = EBITDA / (debt service + deposit)`. If the deal also hands the asset over free, there is no residual to sell against the refund and the promoter funds the gap out of pocket. Show the bridge line by line and quantify the shortfall. Suggested fixes: stagger the refund over the last three years, offset it against final-year energy invoices, or make handover conditional on forfeiture.

---

## Short-tenure / free-handover structures — read before reporting a result

When the PPA is short (≤ 7 years) and the asset is handed over free:

- **Terminal value is zero.** The tail is where RESCO money is made; the structure gives it away.
- **Lead with Project IRR**, not equity IRR. Unlevered, single-rooted, immune to financing tricks.
- Report the **money multiple** on capex over the PPA. 1.2x over 5 years is ~7%, and saying it that way makes the problem obvious without a model.
- **Cheap or zero-cost funding does not fix a bad asset.** Project IRR is unchanged by the capital stack. State this explicitly — it is the most common misread.
- Watch for the split verdict: **bank DSCR can pass while equity earns nothing.** "A lender can approve this deal" is not evidence the deal works for G2G. Report both.
- **Tenure is almost always the cheapest lever.** Capex is sunk at Year 0 and bank debt retires at the end of the debt tenure, so every year beyond that flows to equity unlevered. Quantify the trade explicitly: *one extra PPA year is worth Rs.X/kWh of tariff.* That is the number to take into the negotiation.

---

## Scenario Range Guidelines

Six heat map tables, ranges centred on the project's base values. Tables 4–6 are built into `build_scenarios()` in v2.0 and use `p['scen_tenures']` (default `[5,6,7,8,9,10,12,15,20,25]`).

**Table 1 — EPC Rate × Units per kWp (Equity IRR)**
- EPC range: ±25% from base, 11 steps
- Units range: base ±20%, 12 steps, include base value

**Table 2 — EPC Rate × Interest Rate (Equity IRR)**
- EPC range: same 11 steps as Table 1
- Interest range: 8% to 13%, 11 steps of 0.5%

**Table 3 — Units per kWp × Tariff (Project IRR)**
- Units range: same 12 steps as Table 1
- Tariff range: base ±45%, 11 steps

**Table 4 — PPA Tenure × Tariff (Project IRR)**
- Terminal value stays nil in every cell — note this on the sheet

**Table 5 — PPA Tenure × Tariff (Equity MIRR)**
- Same axes as Table 4. MIRR, not IRR, and say why on the sheet.

**Table 6 — PPA Tenure × EPC/Capex Rate (Project IRR)**

Tables 4–6 are what Ram reads first on any short-tenure deal. Read down a column to see what an extra year buys at zero incremental capex.

## Output Path

Save to the user's mounted folder, named `{ProjectName}_SolarModel_v{X.Y}.xlsx`. If no folder is connected, deliver in chat and ask where it should land. Never overwrite — increment the version.

---

## Step 3: Run and Verify

Run these reconciliation checks and state the result:

1. **Sources − Uses = 0** (bank debt + deposit + equity = capitalised cost)
2. **Total principal repaid = loan drawn**, closing balance nil
3. **Verify the headline IRR by a second route** — money multiple, or NPV at the reported IRR ≈ 0
4. **Breakeven tariff from BE_Solver matches an independent bisection**
5. **`sign_changes(eq_cfs)`** — more than one means MIRR, not IRR

Then print the summary to chat:
```
── {Project Name} ──
Project IRR : X.XX%   [vs 15% hurdle → PASS/FAIL]
Equity IRR  : X.XX%   [or "MIRR X.XX% — IRR undefined, multi-rooted"]
Min DSCR    : X.XXx   [vs 1.2x min → PASS/FAIL]
Yr-n DSCR incl. deposit refund : X.XXx
Payback     : X years
Breakeven   : Rs.X.XX/kWh   |   Breakeven tenure : X years
```

Provide the computer:// link so Ram can open the file directly. End with the standing reminder: model output, requires independent professional review before commitment.

---

## Sheet Structure Reference

| Sheet | Contents |
|---|---|
| **Verdict** | Front sheet, built by the calling script. Capital stack (sources & uses with a nil check), headline metrics vs hurdle, final-year cash bridge, what it takes to hit 15% one variable at a time, tenure ladder, closing Assumed/Flag block |
| **Assumptions** | All inputs (blue = user input, green = calculated). 5 sections: Technical, OpEx, Capital & Financing, Tax, Outputs |
| **Debt** | Year-by-year amortisation: opening balance, interest, principal, closing balance. Show the deposit tranche separately |
| **Depreciation** | IT dep (40% WDV) and Book dep (20% WDV) side by side, with tax shield |
| **FinCal** | 30-column wide table (years as rows). Income → Tax Loss C/F → MAT Workings → Cash Flows. Project and Equity IRR at bottom |
| **Project Summary** | Single-page summary: project details, technical, financing, financial metrics. Bank-ready |
| **BE_Solver** | Breakeven tariff table — tariff scenarios showing equity IRR, highlighting the ≥15% threshold |
| **Scenarios** | 6 colour-coded heat maps (Tables 1–6 above) |

### Scenarios Sheet Heat Map Colours

| IRR / MIRR | Background | Meaning |
|---|---|---|
| ≥ 30% | Dark green `#00B050` | Exceptional |
| 25–30% | Light green `#92D050` | Strong |
| 20–25% | Pale green `#C6EFCE` | Good |
| 15–20% | Very pale green `#E2EFDA` | Meets hurdle |
| 12–15% | Yellow `#FFEB9C` | Below hurdle |
| < 12% | Red `#FFC7CE` | Reject |
| ≤ 0% / undefined | Grey | Non-viable |

---

## Financial Engine Summary (for reference — do not rewrite)

The `compute(p, ...)` function runs the full annual model:

```
For each year 1..n:
  Generation:  Yr1 = gen_per_kwp × dc_kw
               Yr2 = Yr1 × (1 - deg_y2)
               Yr3+ = prev × (1 - deg_y3)

  Revenue:     gen_kwh × tariff / 1,00,000

  OpEx:        O&M (AC kWp × rate × esc^yr) + Insurance (% capex base) + Land

  Debt:        EMI = loan × r × (1+r)^n / ((1+r)^n − 1)
               Interest = opening_balance × rate
               Principal = EMI − interest

  IT Dep:      40% WDV each year
  Book Dep:    20% WDV each year

  IT PBT:      Revenue − OpEx − Interest − IT Dep
  Loss C/F:    If IT PBT < 0, add to loss pool. If > 0, absorb from pool.
  Normal Tax:  (IT PBT − loss used) × 25.17%

  Book PBT:    Revenue − OpEx − Interest − Book Dep
  MAT Liab:    max(0, Book PBT × 15.6%)
  Actual Tax:  max(Normal Tax, MAT Liab); MAT credit accumulates when MAT > Normal

  Project CF:  EBITDA − Actual Tax
  Equity CF:   EBITDA − Actual Tax − Debt Service − (deposit refund in final year)
  DSCR:        EBITDA / Total Debt Service   (report Yr-n separately incl. refund)

IRR:           Bisection on year-0 outflow + year 1..n CFs
               VALID ONLY WITH A SINGLE SIGN CHANGE
MIRR:          Use whenever sign_changes(cfs) > 1 (fin 10%, reinv 8%)
Breakeven:     Bisection on tariff, and separately on tenure, to reach the hurdle
```

---

## Multiple Projects in One Request

If Ram provides inputs for more than one project (e.g., uploaded spreadsheet with 2 clients), build **separate workbooks** for each — one file per project. Do not combine into a single multi-sheet file.

---

## Reference Files

- `references/builder_template.py` — complete working builder script, v2.0, with all three engine corrections applied and Tables 4–6 built in. Read this before writing any code. Adapt the project dict and output path; do not rewrite the engine.

It handles MAT credit carry-forward, loss pool, breakeven bisection, and scenario heat maps.
