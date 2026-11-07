# Market research protocol

The benchmark is the load point of every quote review. A wrong range flips the verdict, so research it fresh every time and tag every figure by source quality.

## 1. Build the benchmark by component, never as one number

A single "₹/kW" figure hides the battery and inverter, which are usually where the margin sits. Price each component the quote actually contains:

| Component | Unit to search | Search queries that worked (append current year) |
|---|---|---|
| Solar, installed, residential | ₹/kWp all-in | `rooftop solar price per kW <city> <year> DCR TOPCon residential` |
| DCR module (ex-works) | ₹/Wp | `DCR TOPCon module price per watt India <year>` (JMK Research, Mercom, OPIS are the good sources) |
| Hybrid inverter | ₹ per unit at the quoted kW and phase | `<kW> three phase HV hybrid inverter price India <year>` |
| LFP battery | ₹/kWh | `<kWh> high voltage LFP battery price India <year> residential` |
| Hybrid inverter, per kW | ₹/kW | use to price a smaller- or larger-inverter alternative |
| On-grid string inverter | ₹ per unit | needed to strip double counting from the "installed solar" figure |

**Double-count guard.** "Installed solar ₹/kWp" figures include an on-grid inverter. When the quote has a hybrid inverter priced separately, the top of the range is overstated by roughly one string inverter. Say so, and say which way it biases the verdict (it flatters the vendor).

## 2. Source quality ranking

Tag each range in the memo and in the workbook's Source column.

1. **Plain (cite):** government or regulator documents (MNRE, PIB, TNERC/SERC orders), research houses (JMK, Mercom, BNEF, OPIS), manufacturer press releases, listed-company filings.
2. **Likely:** installer and aggregator blogs (quickestimate, solarsquare, qbitsenergy, heavengreen and similar), dated retail price trackers (price-history.in), e-commerce listings.
3. **Do not use:** foreign-market prices (a Pakistani or Kenyan listing for the same inverter), undated pages, forum posts, anything older than about 9 months for battery and module prices (they move fast).

Most residential price ranges only exist at tier 2. That's fine. Say so in one line, and make the competing-quotes step the real test.

## 3. Cross-checks to run every time

- **Vendor's own catalogue.** Method: catalogue price of the vendor's nearest standard system + justified uplift for each hardware difference (priced at market per-kW / per-kWh rates, low and high) = fair price on the vendor's own pricing. Unexplained premium: min = quote − high fair price, max = quote − low fair price. Where the catalogue's own spec is ambiguous (e.g. battery kWh stated two ways), take the reading that favours the vendor and say so.
  Example: If the vendor sent a product list, find their nearest standard system, add a justified uplift for the spec difference (priced from step 1), and compute the unexplained premium. This was the sharpest single argument in the first review: the custom quote ran ₹1.2–2.3L above the vendor's own catalogue logic.
- **Branded retail ceiling.** One branded retail listing for the main inverter shows whether the top of the blog range is realistic.
- **Recompute ranges by hand** in the memo: `qty × low`, `qty × high`, sum, midpoint, quote ÷ high − 1, quote ÷ mid − 1. The workbook does the same; the two must agree.

## 4. Subsidy and scheme facts: always search, never recall

Search each time: `PM Surya Ghar subsidy` plus the state name and the year, and `<state> rooftop solar subsidy <year>`. Check:
- Central cap and the kW at which it maxes out (₹78,000 at 3 kW+ as of Oct 2026).
- Any state top-up, its **funding pool**, and its target. Divide pool by per-home amount and compare with the target; if the pool covers fewer homes than the target, tag the top-up "Assumed: subject to funds".
- Eligibility. "Must not have availed any other subsidy for solar panels" is the rule that bites on **replacement** systems: ask about the old system's history.
- Vendor registration on the PM Surya Ghar portal for that DISCOM, the DCR certificate requirement, and that the subsidy applies to the solar portion only, not the battery.
- Mandatory vendor obligations: 5-year free repair and maintenance and a 5-year system warranty from commissioning (REC framework).

## 5. Brand due diligence

Search each named make separately: `<brand> hybrid inverter India company`, `<brand> service network India warranty`. Record for each:
- Founding year, scale, listed or not, manufacturing in India.
- When the specific product line launched. A range launched in the last 12 months has no field record.
- Whether its batteries are proprietary. A hybrid that is "compatible with its own HV batteries" paired with another brand's battery is a BMS risk.
- India service presence in the client's city. If you cannot find it, say "I don't know" and make it a written ask to the vendor.

## 6. Dated reference points (Oct 2026), for orientation only

These are what the first review found. They exist so you can tell whether a fresh search result is wildly off. **Never quote them without re-searching.**

| Item | Range found | Tier |
|---|---|---|
| Residential installed solar | ₹55,000–85,000/kW | 2 |
| DCR TOPCon module, ex-works | ~₹22.3/Wp (Apr 2026, JMK) | 1 |
| Non-DCR TOPCon, ex-works | ~₹14.2/Wp | 1 |
| 10 kW 3-phase hybrid inverter | ₹95,000–1,60,000 | 2 |
| Hybrid inverter per kW | ₹18,000–28,000 | 2 |
| LFP battery | ₹20,000–35,000/kWh | 2 |
| Branded 10 kW 3-phase hybrid, retail | ~₹1.9–2.3L | 2 |
| Generation, Chennai | 4–6 kWh/kWp/day (CAG) | 1 |
