---
name: minto-framework
description: |
  Ram's Minto Pyramid discipline for any argument that has to land in one
  read. Five passes: build the pyramid (answer, exactly three reasons,
  evidence), find the buried answer in an existing draft, MECE-test the three
  reasons, run a line-by-line so-what audit, and compress to a sub-150-word
  email. Use whenever Ram asks to structure, tighten, sharpen, restructure,
  de-waffle or cut a piece of argument — a board note, investor update, credit
  committee summary, negotiation position, cover note, proposal, escalation, or
  any email that has to make one point. Triggers on: minto, pyramid, pyramid
  principle, MECE, "so what", "what's my actual point", "this is too long",
  "bury the lede", "get to the point", "top line this", "one sentence for my
  boss", "three reasons", "tighten this", "what can I cut", "answer first".
  Also use unprompted when Ram hands over a draft over a page that argues for a
  decision and the conclusion is not in the first sentence.
---

# Minto framework

Answer first, then exactly three reasons, then evidence. Everything else goes
in the cut block.

Deliver the worked output. Do not narrate the method.

## Run order

The prompts are numbered 1-5 but that is not always the running order.

| Starting from | Order | Why |
|---|---|---|
| An existing draft | 2 → 3 → 1 → 4 → 5 | Find the buried answer before restructuring around it |
| Raw notes or a blank page | 1 → 4 → 5 | Nothing to diagnose yet |
| A draft that already leads with its answer | 3 → 4 → 5 | Skip the excavation |
| A single named pass ("just run the so-what pass") | That pass only | Honour the request |

State the order at the top of the output in one line, then run it. If running
more than one pass, put each under its own heading so the intermediate work is
inspectable.

## Two rules that override everything else

**Never delete without approval.** Passes 1 and 4 both cut. Cut material never
disappears — it moves to a `## Cut` block at the end of the output, grouped by
reason for cutting (off-pyramid / fails so-what / duplicate / evidence with no
parent). Ram decides what actually dies.

**Never invent evidence.** If a reason is real but thin, say the reason is
under-evidenced and name what would carry it. Do not manufacture a number, a
date, a source, a precedent or a counterparty quote to fill the gap. A pyramid
with a visible hole is useful. A pyramid with a fabricated brick is not.

## Pass 1 — Build

Restructure into the pyramid.

Output format:

```
**Answer:** [one sentence, one clause where possible, an assertion not a topic]

**Reason 1 — [label]**
- [evidence]
- [evidence]

**Reason 2 — [label]**
- [evidence]

**Reason 3 — [label]**
- [evidence]

## Cut
[material with no home, grouped by why]
```

The answer sentence is an assertion someone could disagree with. "Our
financing options" is a topic. "We should take the IDFC term sheet and drop
the other two" is an answer. If the sentence contains no verb of judgement,
it is not the answer yet.

Each reason is a *claim*, not a heading. "Cost" is a heading. "It is the
cheapest of the three over the full tenor" is a reason. The reader should be
able to put "because" in front of every reason and have it read.

Three, not two, not five. If the material genuinely only supports two, say so
and show what a third would have to prove. Never pad the third slot with a
restatement of the first.

Evidence sits under exactly one reason. Anything that supports the answer
directly, without passing through a reason, is either a fourth reason in
disguise or it is not load-bearing. Say which.

## Pass 2 — Find the buried answer

Read the draft and report:

1. **The one sentence.** What the draft is actually building toward, in Ram's
   words where possible, one sentence. If the draft is building toward two
   incompatible conclusions, say so and give both — that is the finding.
2. **Where it is hidden.** Quote the location: paragraph number, section, or
   "nowhere — it is implied but never stated". Buried answers hide in
   predictable places: the last paragraph, a subordinate clause mid-page, the
   caveat after a "however", or a table caption.
3. **What is standing in front of it.** Name the opening material that is
   delaying the answer — context, background, chronology, credentials. This
   is usually the largest single cut available.

If the draft has no conclusion at all — it describes rather than argues — say
that plainly. That is a different problem and restructuring will not fix it.

## Pass 3 — MECE test the three reasons

Test the reasons on three axes and produce a table:

| Reason | Same category? | Overlap with | Verdict |
|---|---|---|---|

**Mutually exclusive.** Would any single piece of evidence file naturally
under two reasons? If yes, the two reasons are one reason with a seam in it.
Name the evidence that double-files.

**Collectively exhaustive.** After the three, can the reader still ask "but
what about ___?" and have it be a fair question? Name the missing question.
Common gaps: the downside case, the counterparty's incentive, what happens if
the load-bearing assumption is wrong, who else has to agree.

**Same kind of idea.** The three should be peers on one axis. Mixing
"it is cheaper", "it closes faster" and "the CFO already likes it" mixes
economics, timing and politics — that is three axes, so the reader cannot
tell whether the set is complete. Common clean axes: commercial / technical /
legal; cost / risk / time; demand / supply / regulation; parts of a whole;
sequence in time; ranked degree.

**Detail pretending to be a reason.** Flag any reason that fails these:
- Can it stand alone as an answer to "why is the conclusion true?"
- Does it contain a judgement, or only a fact?
- Is it a peer of the other two, or an instance of one of them?
- If you deleted it, would the conclusion weaken, or only get less colourful?

A reason that fails is demoted to evidence under whichever real reason it
serves, or cut. Say which and where it goes.

## Pass 4 — So-what audit

Go line by line. After each line, ask "so what?" Every line has to answer it
in a way that moves the argument.

Output a table, then the surviving draft:

| # | Line (first ~8 words) | So-what answer | Verdict |
|---|---|---|---|

Verdicts: `keep` / `merge into #n` / `demote to evidence` / `cut`.

The so-what ladder has three rungs — fact, implication, decision. A line that
only states a fact and cannot be pushed to an implication is cut. A line that
restates the implication of the line above it is merged.

Lines that reliably fail: throat-clearing openers, restatements of the
previous paragraph in different words, background the reader already has,
hedges that remove the claim they qualify, and transitions carrying no
content.

Lines that look cuttable but are not: the number the whole case rests on, the
concession that pre-empts the reader's objection, the named source behind a
figure, and the specific ask. Do not cut the ask.

Then show what survives, in pyramid order, with a word count before and after.

## Pass 5 — Compress to an email

Under 150 words. Same structure: answer, three reasons, evidence only where it
earns its place.

Count the words. Do not estimate — count, and state the count. Over 150 is a
failed pass.

Structure in the email:
- Line 1 is the answer. No greeting-then-context. Bad news still goes line 1.
- The three reasons as three short paragraphs or three bullets. One line each
  unless a number needs stating.
- Evidence only where the reason does not survive without it. At this length
  most evidence is cut — that is correct, it lives in the attachment.
- Close with the ask and the date it is needed by.

**Voice.** Read the `writing` skill and apply it — register `email`, Ram's
voice profile, the banned-pattern catalogue, the lint pass. Compression is
where AI cadence creeps back in, because short sentences invite the
parallel-triplet tic. Keep Ram's contractions, his short declaratives and his
habit of naming the counterparty directly.

Preserve every number, name and date exactly as they appear in the source.
Compression cuts words, never precision. If a figure has to go, cut the whole
line rather than round the number.

## Reference

`reference/diagnostics.md` — worked before/after example, the full
detail-vs-reason test set, and the grouping axes that tend to come out MECE.
Read it when a pass is contested, when the three reasons will not separate
cleanly, or when Ram pushes back on a cut.
