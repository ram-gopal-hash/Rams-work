# Method reference — calibration, ranking, banned language

Contents:
1. Probability banding
2. Damage classes
3. Detection lag
4. Ranking arithmetic
5. Most likely vs most dangerous — the argument
6. Finding the invisible assumption
7. Where causes of death actually come from
8. Banned language catalogue

---

## 1. Probability banding

Assign one band per cause. Bands, not percentages — a false decimal is worse
than an honest band.

| Band | Meaning | Test |
|---|---|---|
| High | More likely than not inside the horizon | You would bet on it at even money |
| Medium | Real, not the base case | You would insure against it |
| Low | Tail, but live | It has happened to a comparable plan you can name |

A cause with no Low-or-above justification is not a cause. Delete it.

Anchor on base rates where one exists and is nameable — DISCOM approval
timelines, MSME collection ageing, EPC schedule slippage, first-time-founder
raise timelines. If you cannot name the base rate, say the band is judgement
and mark it `Likely:` per Ram's tagging convention.

Do not band by how dramatic the cause sounds. The most cinematic failure is
usually Low.

---

## 2. Damage classes

| Class | Meaning |
|---|---|
| Recoverable | Costs money or months; the plan continues |
| Costly | Forces a renegotiation, a down round, a scope cut, or a write-off, but the entity survives |
| Terminal | Ends the plan, the entity, or the relationship that the plan depends on |

Classify by the state of the world *after* the event, not by the size of the
number. A ₹5L loss that breaches a lender covenant is Terminal. A ₹40L delay
that everyone absorbs is Costly.

---

## 3. Detection lag

Weeks between the first observable signal and the point at which the outcome
is locked in.

This is the single most useful number in the autopsy and the one most often
skipped. Short lag means the user can steer. Long lag means the plan is already
decided by the time anyone notices.

Estimate it by asking: when does the evidence first exist somewhere the user
could look, and when does the last reversible decision close? The gap is the
lag.

A Low-probability, Terminal, long-lag cause outranks a High-probability,
Recoverable one. That inversion is the point of the exercise.

---

## 4. Ranking arithmetic

Rank by expected unrecoverable damage:

```
rank score = probability band × damage class
tiebreak   = longer detection lag ranks higher
```

Use a simple weighting and show it if the user asks: High 3 / Medium 2 / Low 1,
multiplied by Terminal 3 / Costly 2 / Recoverable 1. Ties broken by lag.

Do not hide the ranking basis. If two causes land within one point of each
other, say they are effectively tied rather than pretending to precision.

---

## 5. Most likely vs most dangerous — the argument

The distinction is not rhetorical. It changes what the user should do this week.

- The **most likely** cause is a budgeting problem. You price it in, you build
  the buffer, you accept the drag. It is usually visible early and usually
  survivable.
- The **most dangerous** cause is a structure problem. Buffers do not help,
  because by the time the signal is loud enough to act on, the reversible
  decisions are behind you. It is closed off at design time or not at all.

Make that concrete for the plan in front of you: name which one is a line item
and which one is a clause.

**If they are the same cause**, say so explicitly and treat it as a finding in
its own right. It means the plan has one dominant exposure with nothing else
close, which sounds simpler than it is — the whole plan is a single bet, and
the user has probably been thinking of it as a portfolio of risks. Say that.

---

## 6. Finding the invisible assumption

Method that works: read the plan for every sentence stated in the present
indicative about the future. "The DISCOM approval takes six weeks." "They will
sign in October." "We can raise the balance." Each of those is a forecast
wearing a fact's clothes.

Then filter for the one that most other causes depend on. Count how many of the
seven causes fire if it is false. The winner is usually the one with the
highest count, not the one that sounds boldest.

Two common shapes, both worth checking explicitly:

- **Assumed reciprocity.** The plan requires a counterparty to behave
  cooperatively at a moment when their incentive is to behave otherwise.
- **Assumed simultaneity.** Two independent things must land in the same
  window — funding and approval, hire and contract, capex and collection —
  and the plan treats their joint probability as if it were the higher of the
  two.

---

## 7. Where causes of death actually come from

Prompts for finding traceable causes. Use them to interrogate the plan, not as
a list to output — a cause named from this list without a trace to the user's
detail violates the firewall.

- **Cash timing.** When does money leave, when does it return, what fills the
  gap, and what happens if the return slips one cycle.
- **Sequence coupling.** Which step cannot start until another finishes, and
  which of those has no float.
- **Counterparty concentration.** Who can end this unilaterally, and what it
  costs them to do so.
- **Unpriced work.** What the plan assumes someone will do that is nobody's
  named job.
- **Attention.** What the plan needs from the user personally, in a month when
  they are also doing three other things they have described.
- **Reversibility.** Which decision is the first one that cannot be undone, and
  what is still unknown on the day it gets made.
- **Definition drift.** Whether the success metric can be hit while the actual
  objective is missed.
- **The optimistic middle.** Months 3 and 4 of most plans are described in less
  detail than months 1 and 6. Failures concentrate there.

---

## 8. Banned language catalogue

### Reassurance — never, in any form
that said · the good news is · on the positive side · with careful execution ·
this is very doable · you've clearly thought this through · none of this is
fatal · these are all manageable · with the right team · fundamentally sound ·
to be fair · it's worth noting that you've already · I don't want to be
discouraging · every plan has risks

### Generic mitigations — never
communicate early and often · build in buffer · hire experienced people · have
a contingency plan · monitor closely · align stakeholders · do more research ·
diversify · maintain open dialogue · set clear expectations · get everything in
writing · build strong relationships · stay flexible · over-communicate

Each of these is true of every plan, which is why none of them is a finding.

### Dissolving hedges — never
may potentially · could possibly · might perhaps · there is a chance that ·
it is conceivable that · in some cases

Say High, Medium or Low instead. A hedge inside a band is a band you did not
commit to.

### Category words used as mechanisms — never as a cause name
execution risk · market risk · vendor risk · regulatory risk · key person risk ·
poor communication · lack of alignment · scope creep

These are folder names. Name the mechanism that lives inside them, with the
user's own number attached.

### Test to apply to every sentence before sending

Could this sentence appear, unchanged, in the premortem of a completely
different plan? If yes, it is filler. Cut it or attach the user's detail to it.
