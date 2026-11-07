---
name: numbers-integrity
description: "Verification discipline for any numbers-bearing or externally-facing deliverable — financial models, proposals, DPRs, board notes, decks. Run before shipping any version, and after any edit that touches a figure or corrects an error."
---

# Numbers integrity

Matching numbers across documents is not verification. A figure can be perfectly
consistent in the model, the Word file and the deck, and still be wrong. Every
error worth catching survives a consistency check.

Run these passes before shipping any version. Write the checks as a script, not
as a read-through — a script is repeatable across versions and does not get
tired on page 19.

## Pass 1 — Independent recomputation

Rebuild every headline output from the raw assumptions, in a second tool, without
looking at the first. Python against Excel, or Excel against a hand calculation.
Compare to a tolerance and print a pass/fail line per item.

Recompute at minimum: capacity and volume, capex build and its components' sum,
debt schedule (and check the closing balance is zero and principal repaid equals
debt drawn), EBITDA, tax with loss carry-forward, IRR, NPV, DSCR, and every
unit-economics figure quoted in prose.

A green recalc in the spreadsheet proves the formulas *evaluate*. It proves
nothing about whether they are *right*.

## Pass 2 — Structural sanity

Before trusting any output, ask what the arithmetic *must* produce, then check
the model produces it. These catch errors no cell-by-cell review will.

- **Monotonicity.** If return exceeds the discount rate, NPV must rise with
  capital deployed. If it falls, something is wrong — no exceptions.
- **Dominance.** An option that is the same deal at larger scale cannot have a
  lower return per rupee. If it does, find the bug.
- **Sign.** A negative result where positive is structurally required is a bug
  until proven otherwise. Never rationalise it into a narrative.
- **Bounds.** Percentages inside 0–100 unless a loss is intended. CUF, margins,
  DSCR, IRR all have plausible ranges — state them and test against them.
- **Sum.** Components sum to totals. Shares sum to 100%. Splits sum to the whole.

When a sanity check fails, stop. Do not ship the number with a caveat, and do
not build an argument on top of it.

## Pass 3 — Like-for-like across compared options

Wherever the output compares options, scenarios or counterparties, list every
dimension and confirm each is treated identically or that the difference is
deliberate and stated.

- Same discounting. A cost subtracted undiscounted next to discounted flows is
  an error, always.
- Same time horizon, same discount rate, same currency, same nominal-vs-real.
- Same cost base. If a fee sits inside the P&L, it is charged in every option —
  adding it again in one option double-counts it.
- Same treatment of contributed assets. If rent is expensed in the cash flows,
  it must be credited to whoever receives it, in every option.
- Same share of capital. Check the capital row and the return row use the same
  percentage.

Write the comparison dimensions out as a table and tick each one. The errors
hide in the dimension nobody listed.

## Pass 4 — One source of truth

Every number in prose, in a table, on a slide, traces to one computed cell.

- **Never round a rounded number.** Take 3.3146 to 3.31, never 3.315 to 3.32.
  Pull from the source at full precision every time.
- Derive quoted figures with a script that reads the model and greps the
  documents, so a mismatch is reported rather than eyeballed.
- Where components are displayed rounded and will not sum, say so in a footnote
  rather than adjusting a component.

## Pass 5 — Label agrees with formula

Read every label against the formula beneath it. A row headed "the Partner's
74% share" whose formula subtracts 100% is invisible to a recalc and to a
consistency check, and it will survive every version until someone questions
the answer.

Also check: a heading that counts items ("three reasons", "four things") against
the number of items actually below it, and cross-references to section numbers
after any reordering.

## Pass 6 — Citation provenance

For every external figure — a tariff, a charge, a statutory threshold, a rate:

- Name the primary instrument, not the trade-press summary of it.
- Where the only available source is secondary, say so in the document and mark
  the item for confirmation.
- **Where a secondary source is ambiguous or garbled, go to the primary rule
  before building anything on it.** A concession and a cap on escalation read
  similarly in a badly written summary and mean opposite things.
- Corroborate load-bearing regulatory figures across two independent sources at
  two levels (national rule and state regulation) before they carry an argument.

## Pass 7 — Render and read the output

Convert to PDF, rasterise, and look at the pages that changed.

- Table column widths sum to the usable text width, or the last column clips.
- Page numbers in a manual contents table match the rendered PDF, re-derived
  after every build that changes length.
- No duplicated paragraph from a restore or merge.
- Nothing addressed to the wrong reader: internal coaching, presenter notes and
  second-person asides do not belong on counterparty-facing pages.

## Pass 8 — No scar tissue

When a figure or a reading is corrected, correct the document — do not narrate
the correction inside it. The external reader never saw the earlier draft. Text
that rebuts it reads as defensiveness or confusion, and it plants a doubt the
reader did not arrive with.

**The test for every sentence: does it answer a question this reader would
actually ask, or does it rebut a claim only a previous draft made?**

Cut the second kind, and state the rule positively instead:

| Scar tissue | Write instead |
|---|---|
| "There is no concessional rate; the 50% caps escalation, it does not halve the charge." | "A third-party consumer pays it in full, with any increase capped at 50% of the year-of-grant level for twelve years." |
| "That is a cap on escalation, not a discount." | (delete — the preceding sentence already said what it is) |
| "On fees, the comparison is like for like." | "O&M and administration sit in operating cost, so they are deducted before every return shown here." |
| "Option C is not a better deal than B; it is the same deal at twice the size." | "Option C is that same deal at twice the size." |
| "Excludes O&M, which sits in operating cost in every option." | "Covers development and EPC management; operations are carried in operating cost." |

Sweep for the giveaway constructions before shipping: *there is no…*, *not an X
but a Y*, *it does not…*, *rather than what…*, *like for like*, *to be clear*,
*it should be noted that*, *contrary to*, *excludes*. Each is a candidate for
the cut, not an automatic one.

**What stays.** A caveat the reader needs in order to judge the claim is not
scar tissue: "Assumed, pending site data"; "Confirm from the tariff order"; "We
have not taken credit for these, so they are upside"; and a correction of the
*reader's own* likely expectation ("this is not a solar park in the regulatory
sense") where they brought that expectation themselves.

The same rule governs version history. A deliverable carries a version number
and nothing else — no change log, no "corrected from v1.3", no marked-up
rationale. The audit trail belongs in the chat and the working files, and stays
there.

## Pass 9 — Regression across versions

When revising, diff the new output against the previous one and account for
every change. An unexplained delta is a defect you introduced. Keep the
verification script and re-run it in full on every version — errors introduced
in v1.1 otherwise survive to v1.4.

## The report

State what was checked, what failed, and what remains unverifiable. "All checks
pass" is only worth saying when the checks were capable of failing. If a pass
was skipped, say which and why.

Report corrections to the person. Never inside the deliverable.