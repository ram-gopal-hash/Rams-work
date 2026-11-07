# Diagnostics

Read when a pass is contested, when three reasons will not separate, or when
Ram pushes back on a cut.

Contents:
1. Detail vs reason — the full test set
2. Grouping axes that tend to come out MECE
3. Where buried answers hide
4. Worked example
5. Handling pushback

---

## 1. Detail vs reason — the full test set

A reason survives all six. A detail fails at least one.

**The because test.** Put "because" in front of it and the answer behind it.
"We should sign with the EPC vendor *because* the scope now includes the DISCOM
liaison" reads. "We should sign with the EPC vendor *because* their office is in
Thane" does not — that is a fact with no argumentative weight.

**The judgement test.** Does the sentence contain an evaluation, or only an
observation? "Payment terms are 30/40/30" is an observation. "The payment
terms load too much cash before mechanical completion" is a reason.

**The peer test.** Is it the same *size* of idea as the other two? If reason 3
is an instance of reason 1 — "it is cheaper" and "the freight line is cheaper"
— it is evidence wearing a reason's clothes.

**The deletion test.** Delete it. Does the conclusion weaken, or just get less
vivid? Weakening means it was load-bearing. Less vivid means it was colour.

**The standalone test.** If the reader read only that one line and nothing
else, would they be part-persuaded? A reason persuades on its own. Evidence
only persuades once you know what it is evidence *for*.

**The count test.** Does it have a natural plural? Reasons are usually
singular claims. If the item is one of a list of similar items — three
warranty gaps, four sites, two missed milestones — the list is the evidence
and the reason is what the list demonstrates.

### Demotion, not deletion

A failed reason usually has somewhere to go. In order of preference: demote it
to evidence under the reason it actually serves; merge it with the reason it
duplicates; move it to the cut block. Deleting outright is the last option and
still goes to the cut block, never to nothing.

---

## 2. Grouping axes that tend to come out MECE

Pick one axis and stay on it. Mixing axes is the most common cause of a set
that feels incomplete without the reader being able to say why.

**Structural** — parts of a whole. Commercial / technical / legal. Upstream /
midstream / downstream. Holdco / SPV / project. Clean because the parts are
defined by the whole.

**Sequential** — steps in time. Before signing / during construction / after
COD. Clean because time does not overlap.

**Comparative** — ranked degree. Largest exposure first. Clean only if the
ranking metric is stated.

**Decision-shaped** — cost / risk / time. Or: does it make money, can we
deliver it, can we get out of it. Clean because they are the three questions
any approver asks.

**Stakeholder** — what it does for us / for the counterparty / for the lender.
Clean when the argument is about whether a deal closes.

Axes that look clean and are not: "financial and strategic and operational"
(strategic overlaps both), "short-term and long-term and risk" (risk is
orthogonal to time), "pros and cons and considerations".

---

## 3. Where buried answers hide

In rough order of frequency:

1. **Last paragraph.** The writer thought their way to the conclusion and left
   it where they found it.
2. **After a "however" or "that said".** The real position is in the
   qualification, not the thing being qualified.
3. **In a subordinate clause.** "Given that the tariff only works above 4.2,
   which it does not at current capex, we could consider..." — the answer is
   the clause, the sentence is scaffolding.
4. **In a table caption or a figure note.**
5. **Split across two paragraphs**, half in each, never stated whole.
6. **Nowhere.** Implied but never written. Common when the writer expects
   pushback and is hedging. Say so — the fix is a decision, not an edit.

---

## 4. Worked example

### Before (fragment of a financing note, 118 words)

> We have been in discussions with three lenders since March. IDFC came back
> first with an indicative term sheet in April, followed by the others in May
> and early June. The market for rooftop RESCO debt has tightened somewhat
> this year, and several NBFCs have pulled back from the sector. IDFC's
> pricing is 10.75% against 11.4% and 11.9% from the other two. IDFC also
> accepts the SPV structure without a promoter guarantee, which the other two
> do not. Their disbursement is tranche-linked to commissioning milestones,
> which suits our cash profile. There are of course other considerations. On
> balance IDFC looks like the option we should probably pursue further.

### Pass 2 output

**The one sentence:** Take the IDFC term sheet.

**Where it is hidden:** Final sentence, and hedged twice — "looks like" and
"probably" and "pursue further" put three layers between the reader and the
decision.

**Standing in front of it:** The first three sentences are chronology and
market context. The reader is being told how the writer spent five months
before being told what to do.

### Pass 3 output

| Reason | Same category? | Overlap with | Verdict |
|---|---|---|---|
| Cheapest at 10.75% | Commercial | — | Keep |
| No promoter guarantee | Risk/structure | — | Keep |
| Tranche-linked disbursement suits cash profile | Commercial/timing | Partial with cost | Keep, reframe as cash |

Axis: cost / risk / cash. Clean.
Gap: nothing on execution — IDFC's time to close is not addressed, and it is a
fair question when three lenders are live. Flagged, not filled.
"Market has tightened" is context, not a reason — it supports why we are
taking a term sheet at all, not why this one.

### After (Pass 1 + 4 + 5, 96 words)

> **Take the IDFC term sheet and drop the other two.**
>
> Cheapest: 10.75% against 11.4% and 11.9%.
>
> No promoter guarantee. Both others require one on the SPV.
>
> Disbursement is tranche-linked to commissioning, which matches when we
> actually need the cash.
>
> One open item: I have not pinned IDFC's time to close. Chasing that
> Tuesday.
>
> Need your go-ahead by Thursday to hold the indicative pricing.

**## Cut**
- Off-pyramid: five-month negotiation chronology; NBFC sector pullback
- Fails so-what: "there are of course other considerations"
- Hedges removed from the answer: "looks like", "probably", "pursue further"

Note what survived: every number, both competing rates, the named lender, the
ask, the date. Note what the compression exposed: the execution gap was
invisible in the original because the chronology made it feel covered.

---

## 5. Handling pushback

Ram will sometimes want a cut line back. Default to restoring it — it is his
document and the cut block exists precisely so the decision stays with him.
Restore it, then say where it now sits in the pyramid and what it displaced,
because a restored line has to earn a parent like any other.

If he restores something that genuinely breaks the structure — a fourth reason,
or evidence with no parent — restore it anyway and name the consequence in one
line: "this is now a four-reason pyramid" or "this sits under nothing". Do not
re-argue the cut twice.

If he says the answer sentence is wrong, that is the most important correction
available. Rebuild from it — every reason below has to be re-tested against
the new answer, because reasons that were MECE for one conclusion are rarely
MECE for a different one.
