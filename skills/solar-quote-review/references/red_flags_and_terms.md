# Red flags, payment terms and the vendor brief

## 1. Quote hygiene: check every item

**Arithmetic and structure**
- Recompute every payment split, subtotal and GST figure. Rounding drift under ₹1 is fine; anything more is a flag.
- Missing serial numbers in the scope table, missing price validity date ("valid till proposal validity"), no GST breakup by HSN.

**Internal contradictions** (quote vs its own notes vs catalogue)
- Scope line says "Included" while notes say "customer scope" (civil work for structure legs, net-meter fees, DISCOM charges).
- Catalogue specs that don't multiply out (V × Ah ≠ the kWh claimed), or two versions of the same catalogue disagreeing.

**Equipment**
- **"Brand A / Brand B" either-or clauses.** The vendor picks at delivery. Demand one make and model number per component.
- **Inverter–battery mismatch.** If one of the either-or inverter brands is designed for its own proprietary HV battery, pairing it with the other brand's battery is a BMS and warranty risk.
- **Young product lines.** A range launched in the last 12 months has no field history; prefer established ranges for a 10-year asset.
- **DCR.** Modules must carry the DCR certificate for the subsidy. Confirm the module wattage × count equals the quoted kWp.

**Sizing**
- Inverter far above bill peak demand (see bill_analysis.md).
- Battery runtime that doesn't cover the client's actual outage length at the loads they want backed up.
- Heavy loads such as geysers on the backup circuit. Exclude them.

**Warranty and service**
- Warranty years not stated for modules, inverter, and battery; no battery cycle or throughput warranty.
- Protective devices (SPD, MCB, MC4) excluded from warranty.
- No named service partner in the client's city.
- Under PM Surya Ghar the vendor owes 5-year free maintenance and a 5-year system warranty; if the quote is silent, put it in the PO.

**Replacement jobs**
- Dismantling the old system, removal of the old structure, and take-back of old batteries are usually missing.
- Rewiring old UPS-backed circuits to the new backup port, and the backup DB design.
- Prior-subsidy history of the old system (subsidy eligibility).

**Payment hygiene**
- Bank details printed on a marketing graphic. Verify by phone against letterhead and GST registration; pay only to the company current account. Never process or repeat account numbers in the memo.

## 2. Payment terms

Compute **money at risk before delivery** (₹ and %). Residential vendors often ask 90–95% before material reaches site, with nothing held for commissioning, net meter, or subsidy release, which are exactly the steps where jobs stall.

Default counter:

| Stage | % |
|---|---|
| Order, after DISCOM technical feasibility | 10% |
| Material delivered to site, makes and serials verified against PO | 50% |
| Installation and commissioning complete, system running | 30% |
| Net meter installed and DISCOM inspection passed (subsidy-eligible) | 10% |

## 3. Setting the counter and walk-away

Tag both "Assumed" and show the basis:
- **Counter:** near the top of the market range, or the vendor-catalogue-implied fair price, whichever is lower.
- **Walk-away:** the top of the market range (adjusted for any double count) or the high end of the catalogue-implied price.
- If the quote also carries a sizing excess (e.g. inverter oversized vs bill peak), add a second counter for the right-sized option, priced with the per-kW benchmark.
- Revise both once competing quotes arrive. Two competing quotes on an identical spec are always the recommended next step.

## 4. Vendor brief template (end of every memo)

1. Equipment locked by make and model; no either-or.
2. Price both the quoted and the right-sized option where sizing is in question; price any expansion path (extra battery module).
3. Backup DB design: which circuits, phase allocation for heavy single-phase loads, heavy loads excluded.
4. Dismantling and take-back of any existing system.
5. Warranty years per component (battery in years and cycles), service partner in the client's city, 5-year free maintenance.
6. Milestone payment schedule (section 2).
7. Resolve every contradiction found; dated price validity; HSN-wise GST breakup.
8. Vendor registered with the DISCOM on the PM Surya Ghar portal, verified before the first payment.
