# Ram Gopal: working repository

I spent 30 years running banking operations and technology (Citibank, Standard Chartered, Barclays, where I was CEO of the Indian banking entity from 2017 to 2023). In 2024 I co-founded Kaamyabi, a distributed solar company that owns and operates plants and sells the power per unit. This repository holds the tools I use day to day. Nothing in it is a demo built for this page: each piece came out of a real decision, and the data has been replaced with synthetic data so it can be shared.

There are two parts.

## 1. `skills/`: instructions that make a language model safe to rely on in finance

Most of my analytical work now runs through Claude. Early on I found that the output was fluent and often wrong in ways that are expensive in my line of work: a debt schedule that does not close to zero, an IRR quoted where the cash flows have two sign changes and the IRR is undefined, a savings figure built on an average tariff when the tariff is telescopic, a confident sentence with an invented source behind it.

The skills in this folder are my response. Each one is a written procedure that the model loads before it works on a task of that type. The common thread is verification: recompute every headline number by a second route, test what the arithmetic must produce before trusting what it did produce, tag every claim as sourced, inferred or assumed, and refuse to fill a gap with generic content.

| Skill | What it does | Why it exists |
|---|---|---|
| `numbers-integrity` | Nine passes run before any numbers-bearing document ships, including independent recomputation in a second tool, structural sanity tests (monotonicity, dominance, sign), citation provenance, regression across versions, and a check that corrections are made in the document instead of narrated inside it | A figure can match across the model, the memo and the deck and still be wrong |
| `writing` | A fabrication firewall, register rules, a pattern catalogue of machine-written prose, a measured voice profile and a lint script (`scripts/lint.py`) | Readers stop trusting text they think a model wrote, and invented specifics are worse than vagueness |
| `premortem` | Assumes a plan has already failed at a fixed date and writes the autopsy: ranked causes traced to the plan's own details, the load-bearing assumption, dated numeric tripwires | Before an irreversible commitment, the useful question is how it dies |
| `minto-framework` | Answer first, three reasons that are mutually exclusive and collectively exhaustive, then a line-by-line test of what each sentence adds | Board and credit papers get read once |
| `solar-quote-review` | Decides sign, negotiate (with a number) or walk away on a vendor quote, using component-level market ranges and the client's own bills with the slab tariff back-solved to the rupee | Vendors quote a headline price; the risk sits in the components and the payment terms |
| `solar-model` | Builds an 8-sheet project finance model with MAT and loss carry-forward, DSCR, MIRR where IRR is multi-rooted, breakeven solvers and sensitivity tables | Bank and investor submissions |
| `bess-model` | Prices a battery as a lease or a storage PPA, solving for the tariff that hits a target equity IRR, and tests it against the customer's value ceiling | A tolling structure where the charging source does not affect the owner's return, which most first drafts get wrong |

Client names, counterparties, file paths and personal details have been removed. Model defaults (hurdle rates, debt terms) are illustrative inputs, not offers.

## 2. `analytics/`: small, tested tools in Python, R and SQL

| Folder | Language | Question it answers |
|---|---|---|
| `bill-review-python` | Python | What will solar actually save on this customer's bills? Back-solves the slab tariff from the bills (searching for the escalation factor when the published order is stale), verifies it to within Rs 1 on every bill, then computes savings bill by bill for three yield cases and the payback with and without subsidy |
| `quote-benchmark-r` | R (base R only) | Is this quotation fair? Places each line item inside a researched market range, scores the payment terms, sets a counter-offer and a walk-away price, and prints a payback sensitivity grid |
| `generation-sql` | SQL (SQLite) | Is the plant performing, and is the invoice right? Reconciles inverter energy to the billing meter, computes weather-corrected performance ratio, finds runs of underperforming sunny days with a gaps-and-islands query, tracks soiling and cleaning with a rolling window, and puts a rupee figure on the faults |

Each folder runs on its own and has tests:

```bash
cd analytics/bill-review-python && python bill_review.py sample_bills.json && python -m unittest
cd analytics/quote-benchmark-r  && Rscript quote_benchmark.R && Rscript test_quote_benchmark.R
cd analytics/generation-sql     && python seed.py && sqlite3 solar.db < queries.sql && python -m unittest
```

The SQL data set has three faults planted in it (an inverter trip, soiling, a meter under-recording) and the tests check that the queries find each one and nothing else.

## What I do not claim

I am not a software engineer. I write Python, R and SQL for analysis, and I have spent three decades accountable for large technology estates (core banking, card processing, payments, AML monitoring, the first cloud platform for payments in the Barclays group), but I have not built production systems myself.

## Rights

Shared for review. © 2026 Green2Green Enterprises Pvt Ltd. All rights reserved. No licence is granted to copy, modify or reuse this material; contact agr7116@gmail.com for any reuse.

## Contact

Ram Gopal · [LinkedIn](https://www.linkedin.com/in/ram-gopal) · agr7116@gmail.com
