---
name: "solar-quote-review"
description: "Review a vendor quotation for residential or small C&I rooftop solar, hybrid solar-plus-battery or BESS in India and decide: sign, negotiate (with a number) or walk away. Core evidence, researched fresh each time: live online market price ranges built component by component (installed solar per kWp, hybrid inverter, LFP per kWh, DCR modules), and the client's electricity bills, with the slab tariff back-solved to the rupee for real savings and sizing. Outputs a chat memo (decision in line 1, counter, walk-away, vendor brief) plus an Excel workbook (bill analysis, benchmark, sizing, payback). Use whenever Ram shares a solar, inverter or battery quote, vendor proposal or price list, or a DISCOM bill with a quote, and asks if the price is fair, whether to sign, are the brands or payment terms ok, even casually ('got this quote, thoughts?'). Not for pricing G2G's own RESCO deals (solar-model, bess-model) or EPC contract redlines."
---

# Solar quote review

Turn a vendor quotation and the client's electricity bills into a decision Ram can act on: sign, negotiate (with a number), or walk away.

The verdict rests on two things, and both are researched and verified fresh each time:
1. **Market price ranges**, searched online and built component by component, cross-checked against the vendor's own catalogue.
2. **The client's bills**, with the slab tariff back-solved until it reproduces each bill's energy charge to the rupee.

Everything else (tech fit, subsidy, payment terms, brands, payback) hangs off those two.

## Ram's standing discipline applies throughout

Line 1 of the memo is the decision with a number. Every figure is traced to a source or recomputed by a second route. Tag certainty in-line: plain (cited), "Likely: [basis]", "Assumed: [X, change if Y]", and collect all Assumed items in a block at the end. Say "I don't know" for unverifiable external facts (a brand's local service network, a scheme's fund status) and turn them into written asks to the vendor. Treat the benchmark range and the slab rates as load points: check each by two routes. Run the `numbers-integrity` skill before shipping and the `writing` skill on the memo prose.

## Step 0: read everything, then ask before analysing

Read the quote, any catalogue or price list, and every bill uploaded. Recompute the quote arithmetic immediately. Then ask, in one `ask_user_input_v0` call, only what changes the answer. In the first review, each of these flipped part of the verdict:

- **Whose decision?** Client buying for themselves, or G2G evaluating the vendor as a partner. These are different deliverables.
- **Why storage, and for which loads?** Whole-home backup including ACs, essentials only, or bill savings. This decides whether the hybrid inverter and battery are justified at all.
- **Is there an existing system being replaced?** Its type (off-grid or net-metered), size, and output; and **whether it was installed with any subsidy** (if yes, the new subsidy is likely lost).
- **Typical outage length and frequency.** This sizes the battery.

If bills are missing, ask for six (one year). One bill is one season.

Give a short first read with the question (arithmetic checks and obvious red flags) so the turn isn't empty. When a later message brings new facts (another bill, the existing system, the subsidy history), say in line 1 whether the decision changes, then show only what moved.

## Step 1: Extract and check the quote

Fill the `quote` block of the spec (schema: `assets/example_spec.json`):
- Line items as quoted, including every "Brand A / Brand B" either-or, verbatim.
- Payment stages with %, stated ₹, and whether each falls before delivery.
- Subsidies the vendor claims, and the "effective cost" they show.

Then run the hygiene list in `references/red_flags_and_terms.md` §1. Contradictions inside the vendor's own documents are evidence; quote them precisely (scope line number vs note).

## Step 2: Bills (core)

Follow `references/bill_analysis.md`:
1. Extract each bill. Reconcile readings (final − initial = units) and amounts (energy − subsidy ± round-off = payable).
2. Search the current tariff order and verify the slab rates against every bill:
   ```bash
   python scripts/tariff_solver.py verify spec.json
   python scripts/tariff_solver.py fit spec.json      # if verify fails: finds the escalation factor
   ```
   Only call the rates verified when every bill matches within ₹1.
3. Derive kWh/day, average load, peak max demand vs sanctioned load, and phase.
4. Compute savings by slab displacement, net of any existing system's lost output:
   ```bash
   python scripts/tariff_solver.py savings spec.json
   ```

## Step 3: Market benchmark (core)

Follow `references/market_research.md`. Search each component the quote contains, at the quoted size and phase, for the current year. Price it as qty × low and qty × high, sum, and compare the quote with the top and midpoint of the range. Run the vendor-catalogue cross-check when a catalogue exists. Name the double-count bias (installed-solar figures include an inverter) and which way it cuts.

Also search, never recall, the subsidy position: the central cap, any state top-up and its fund size against its target, the prior-subsidy rule, vendor registration and DCR.

## Step 4: Technical fit and brands

- Inverter vs bill peak demand, per-phase limits for single-phase loads such as ACs, and surge from fixed-speed compressors.
- Battery runtime at the loads the client wants backed up (from Step 0) and at the bill's average load.
- PV vs sanctioned load (net-metering cap), and daily generation vs battery and vs consumption.
- Brands: search each make for scale, product-line age, proprietary-battery coupling, and local service presence. Recommend locking a matched inverter-battery-BCU set from one maker. Rate each component plainly: good / acceptable with conditions / avoid.

## Step 5: Payment terms, economics, counter

- Money at risk before delivery, in ₹ and %. Counter with the milestone schedule in `references/red_flags_and_terms.md` §2.
- Annual savings as a range across scenarios. Show payback on the full quote, at the counter, and without any uncertain subsidy.
- Show the **solar-only payback separately**. Under net metering the battery earns little; the backup premium is outage insurance the client is choosing to buy.
- Set a counter and a walk-away (rules in §3 of the same file), both tagged Assumed. Where sizing is in question, add a right-sized option with its own price.

## Step 6: Build the workbook

1. Read `/mnt/skills/public/xlsx/SKILL.md` first.
2. Write the spec JSON (copy `assets/example_spec.json` and replace every value; delete `catalogue_check` if there is no catalogue).
3. Build, recalculate, and confirm zero formula errors:
   ```bash
   python scripts/build_workbook.py spec.json /mnt/user-data/outputs/<Client>_QuoteReview_v1.0.xlsx
   python /mnt/skills/public/xlsx/scripts/recalc.py /mnt/user-data/outputs/<Client>_QuoteReview_v1.0.xlsx 60
   ```
4. Open the recalculated file with `data_only=True` and confirm:
   - the Summary integrity checks all read "OK";
   - the benchmark range, % over top, money at risk and savings equal the memo's figures.

   If any differ, fix the memo or the spec before sending.

The sheets are: Summary, Quote, Tariff, Bills, Benchmark, Sizing, Payback, Assumptions. Inputs are blue and formulas live, so Ram can change a rate or a scenario and see the verdict move.

Name files `<Client>_QuoteReview_vX.Y.xlsx`. Increment the version on each revision; never overwrite.

## Step 7: The chat memo

Use this structure. Keep it tight: tables where they compress, prose elsewhere.

```
**[Decision in one sentence: sign / negotiate to ₹X / walk away, and the single biggest reason.]**

## 1. Price: [fair / above market by X%]
Component build-up table (component | range | source), total, quote vs top and midpoint.
Vendor-catalogue cross-check, if there is a catalogue.

## 2. Bill and savings
Bill facts (traced), verified slab rates, savings range, payback (full, counter, solar-only).

## 3. Technology and brands
Sizing vs bill; runtime; brand verdicts; conditions.

## 4. Subsidy
What's certain, what's Likely, what the client must verify.

## 5. Payment terms
Money at risk; counter schedule.

## 6. Course of action
Numbered steps, ending with the vendor brief (red_flags_and_terms.md §4).

**Assumed (change if wrong)**
- ...

For discussion; not professional or legal advice. Have the final PO reviewed before signing.
```

Close with at most one question: the single unknown that would most change the answer (usually outage length or the missing bills).

## Worked example

`assets/example_spec.json` is the first review (anonymised): a residential duplex, 4.96 kWp DCR + 10 kW 3-phase HV hybrid + 10 kWh LFP quoted at ₹10.35L incl. GST.
- The tariff was verified to the rupee on two TNPDCL bills.
- The quote came in about 11% above the top of the market range, with 95% (₹9.84L) payable before delivery.
- The inverter was 2.2× bill peak demand.
- An either-or inverter brand clause created a BMS-mismatch risk.
- Verdict: negotiate, with a counter of ₹8.5L and a walk-away of ₹9.2L.

Build it to see what a finished workbook looks like.
