# Worked example — register and depth calibration

**This example is fictional.** The company, numbers, counterparty and dates are
invented to demonstrate format only. Never carry any figure from this file into
a real autopsy. It is here to calibrate tone and specificity, nothing else.

The method is domain-agnostic. This example is a solar rooftop plan because
that is the common case; the same structure applies to a raise, a hire, a
product launch or a bid.

---

## The plan as the user gave it (abridged)

> Sign the 600 kWp rooftop RESCO deal with a textile cluster in Bhiwandi.
> ₹2.6 Cr project cost. ₹65L equity from promoter loans, ₹1.95 Cr term debt
> from a PSU bank, sanction expected September. EPC contractor is a firm we
> used once before, 30% mobilisation advance. Commissioning target January,
> first invoice February. Success = commissioned and invoicing by 28 February
> at ₹6.10/kWh with the anchor tenant on a 15-year PPA.

Today is 4 August 2026. Horizon: 4 February 2027 — but the stated success date
is 28 February 2027, so the horizon moves to 28 February 2027.

---

## Line 1 (the verdict)

> This plan has a fatal flaw: on your own numbers the mobilisation advance
> leaves before the sanction lands, so a September sanction slip you cannot
> control converts ₹78L of promoter money into an unsecured advance to a
> contractor with one delivery to their name.

---

## One cause of death, at full depth

**Cause 1 — Advance paid ahead of sanction**
`Probability: High` · `Damage: Terminal` · `Detection lag: 7 weeks`

**What killed it.** The 30% mobilisation advance is ₹78L against a ₹2.6 Cr
contract, and it falls due at contract signature in September. Equity available
is ₹65L. The plan closes that ₹13L gap with the term loan, but the first
disbursement is conditional on a sanction the bank had not issued. You paid the
advance anyway to hold the January commissioning date, funded by stretching
promoter loans, and after that the schedule was hostage to a contractor holding
your cash with no lien and no bank guarantee named anywhere in what you
described.

**How it unfolded.**

| Month | What happened | What was visible |
|---|---|---|
| Aug 2026 | Contract negotiated, advance terms accepted | Nothing |
| Sep 2026 | Sanction went to a second committee; advance paid to hold the slot | Bank asked for a revised DPR — the only signal |
| Oct 2026 | Contractor mobilised two of five crews; sanction still pending | Crew count on site |
| Nov 2026 | Last recoverable month. Sanction issued with a condition precedent you could not meet in time | — |
| Dec 2026 | Contractor demobilised to a paying site; ₹78L unrecovered | Site empty |
| Jan–Feb 2027 | No commissioning, no invoice, promoter loans exhausted | Terminal |

**The assumption that allowed it.** *"The sanction is basically done, it's just
paperwork now."*

**First warning sign.** The bank coming back in September for a revised
document instead of a sanction letter. Not a rejection — a request. That is what
a slipping sanction looks like from the outside.

**Traces to.** Your "₹65L equity, 30% mobilisation advance, sanction expected
September" — the advance is ₹78L and the equity is ₹65L.

---

## Most likely vs most dangerous — the register to aim for

> Most likely is Cause 3, commissioning slipping past February. It is High
> probability and Costly: it costs you a quarter of revenue and an awkward
> conversation with the anchor tenant, and you trade your way out of it.
>
> Most dangerous is Cause 1. It is the same probability but Terminal, and it
> has a seven-week detection lag — by the time the contractor demobilises in
> December, the last decision you could have reversed was the advance you paid
> in September. The difference matters because Cause 3 is a line item you can
> budget for, and Cause 1 is a clause you either put in the contract now or
> live without for the rest of the project.

---

## The invisible assumption — the register to aim for

> You are assuming the sanction is a timing question, not an outcome question.
> You wrote "sanction expected September" as a fact. It is a forecast, and it
> is resting on a bank that has not yet seen a commissioned project from you.
> Four of the seven causes above fire if that forecast is wrong by eight weeks.

---

## Changelog row — the register to aim for

| # | What changed | Failure mode closed | What it costs | Residual risk |
|---|---|---|---|---|
| 1 | Advance capped at 10% (₹26L) with the balance 20% released against a bank guarantee, payable only after sanction letter | Cause 1 | Contractor will price this in — expect 2–3% on contract value, ~₹6L, and two weeks in renegotiation | Contractor may decline and you lose the January slot; that is a better loss than ₹78L |

---

## Checklist row — the register to aim for

| # | Verify | How | Pass | Walk away entirely if |
|---|---|---|---|---|
| 1 | The sanction is at final committee, not in appraisal | Ask the branch credit manager for the current stage and the next committee date, in writing on email | Named committee date on or before 15 Sep | They will not put the stage in writing. It means the file has not moved, and you will be told that in November instead of August. |

---

## Tripwire rows — the register to aim for

| Failure mode | Signal | Trips at | Check on | Action if tripped |
|---|---|---|---|---|
| Advance ahead of sanction | Days since sanction file lodged, per bank email | 45 days | Week 6 — 15 Sep 2026 | Do not pay the advance. Renegotiate to the 10% structure. |
| Commissioning slip | Crews on site, counted on a site photo | Fewer than 4 | Week 12 — 27 Oct 2026 | Invoke the schedule clause and re-baseline the PPA start date with the tenant now, not in January. |

Note the shape: a number, one threshold, a real date, and a decision. Not
"watch the sanction closely".
