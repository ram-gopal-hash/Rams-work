---
name: writing
description: |
  Ram's writing standard. Apply to every writing task done for or with Ram:
  drafting, editing, rewriting, replying, summarising, or any output containing
  more than two sentences of running prose. Fires on any build or rebuild of a
  document carrying prose, however the request is phrased: "build v1.4", "fix
  the numbers and rebuild", "apply these edits" are writing tasks the moment
  the artefact contains prose. Triggers on: write, draft, edit, rewrite,
  polish, clean up, reply, post, article, memo, note, email, summary, rephrase,
  "in my voice", "for me", "this sounds like AI", "make it sound human". Also
  use when producing the narrative sections of a DPR, board note, investor
  memo, or contract cover letter. Covers register routing, a pre-draft brief, a
  fabrication firewall, the banned-pattern catalogue including the 2026
  additions, Ram's voice profile, and a mechanical lint pass. Skip only for
  code, formulas, and tables of pure data.
allowed-tools: Read Grep Glob Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/lint.py *)
---

# Writing standard

Deliver the clean version. Do not narrate the passes.

## 0. Rule priority

When rules collide, resolve in this order:

1. **Integrity.** Never invent a fact, figure, source, quotation, date,
   or credential. See section 3.
2. **Accuracy.** The exact technical term beats a style rule.
3. **Register fit.** Blog voice in a bank submission is worse than any
   banned word.
4. **Specificity.** Concrete beats polished.
5. **Style bans.** Section 5 and `reference/patterns.md`.

Never follow a style rule so hard the result gets awkward.

## 1. Register gate - do this first

Read `reference/registers.md` and pick one of:
`contract`, `legal`, `dpr`, `bank`, `investor`, `article`, `post`, `email`.

The register decides which rules fire. If it is genuinely ambiguous - the
same project note is `email` to the counterparty, `investor` in a board pack,
`bank` as a loan annexure - ask. One question beats a rewrite.

Check the no-touch list in `registers.md` before editing anything. Operative
contract clauses and scheme-format DPR sections are not restyled.

## 2. The brief

Before drafting, settle these. Most come from the prompt; infer the rest and
state the inference.

- **Reader.** Who, and what do they do after reading?
- **Decision.** What should they understand, approve, or refuse?
- **Stance.** What does Ram actually think? If the material doesn't say and
  the answer changes the draft, ask.
- **Evidence.** What is verified, what is inferred, what is disputed, what
  is unknown?
- **Constraints.** Length, jurisdiction, dates, confidentiality, source
  material.

Ask only where a missing detail materially changes the output. Otherwise
make a bounded assumption and flag it in the delivery note, not in the prose.

## 3. Fabrication firewall

Specificity is required. Invented specificity is worse than vagueness,
because it is submission-ready and wrong.

Every number, date, name, percentage, clause reference, and citation must
come from one of: material Ram supplied, a file on disk, a verified search
result, or Ram's own prior statement in this conversation.

Anything else gets marked in the draft:

- `[VERIFY]` - a figure that looks right but is unsourced
- `[ASSUMPTION: ...]` - a bounded inference, stated

Never invent a study, a statistic, a case study, a quotation, a meeting, or
a person. Never present inference as fact. Never write "42% of users" to
satisfy a specificity rule when the real number is unknown - write what is
known and mark the gap.

If the source material is too thin for the deliverable, say so and ask.
Never fill a gap with generic content.

## 4. Draft

Write from the situation, not from the topic. Before drafting, know: who
the actors are, what each knows and controls, what happened in what order,
which documents and numbers matter, and what would change the conclusion.

**Let the conclusion be earned.** Present the facts, sequence, and tension
so the conclusion follows. Do not announce a verdict then defend it.

Weak: "The project failed because of regulatory, operational and financial
challenges."

Better: "Over six months the licence approval slipped, the correspondent
bank shortened settlement windows, and hedging costs rose. The project
remained viable in principle, but its working-capital requirement no longer
matched the sponsor's funding capacity."

**Chronology when causation matters.** For negotiations, project execution,
regulatory change, and institutional failure, show the order in which people
encountered information. Sequence reveals cause better than a taxonomy.
Use categories when the reader needs reference or comparison instead.

**Let evidence create friction.** Do not smooth away the inconvenient fact,
the clause that contradicts the annexure, the assumption a calculation rests
on. Name what would change the conclusion. Analysis that never meets
resistance reads invented, because usually it was.

**Describe before evaluating.** Give the facts, not the verdict on them.
"Two adverse media alerts, three unexplained cash deposits, and a request to
redirect payment to an unrelated company in Dubai" beats "several concerning
red flags."

**Keep real uncertainty.** "The filings suggest but do not prove", "my read
is", "two explanations remain plausible". Do not manufacture hedging to
sound careful - Ram's measured hedge rate is 0.06 per 100 words, effectively
zero. Take the position the evidence supports.

**Selective emphasis.** Spend words where the evidence changes the decision.
Brief context for secondary issues. Do not weight sections equally for
symmetry.

**Trust the reader.** If two well-chosen facts make the connection obvious,
do not add "this demonstrates" or "this highlights."

## 5. Audit passes

Run all three silently, in order.

**Pass A - substance.** Is the central claim clear? Cut anything that does
not advance it. Does the conclusion follow from the evidence, or was it
assumed? Are the assumptions named? Do the numbers reconcile against each
other and against the source? For legal, regulatory, and financial work,
identify what needs professional verification.

**Pass B - patterns.** Load `reference/patterns.md` (in `${CLAUDE_SKILL_DIR}`) and apply it. The bans
are absolute per Ram's July 2026 ruling and apply to his own drafts:
banned vocabulary, bloated verbs, dead openings and transitions, negative
parallelism, analogies, significance inflation, rule of three, participle
padding, meta commentary, em dashes.

Sections 9 to 12 of `patterns.md` are the 2026 additions and work
differently. Second-generation vocabulary, nominalisation and Latinate
diction are density judgements, not sight-bans: the words are legitimate
in `bank`, `dpr` and `legal` and get cut only where they are doing no
work. Section 12 records what this model in particular over-produces.

Formatting bans suspend in `contract`, `legal`, `dpr`, `bank`. Everything
else in `patterns.md` applies in every register.

**Pass C - voice.** Load `reference/voice_profile.md`. Targets:

- sentence-length CV above 0.45; Ram's measured baseline is 0.54
- quantity density around 4 per 100 words, from real sources only
- first person where the register allows it - he writes as a participant
- named actors with figures attached, not categories
- near-zero hedging
- `c.` before approximations
- commas above 4.5 per 100 words; Ram's measured baseline is 7.08
- parentheses present, not near-zero; his baseline is 0.50 per 100 words
- no sentence carrying three or more `and`s
- nominalisation and abstraction density on the low side, per
  `patterns.md` sections 9 and 10

The profile is calibrated on pitch narration only. For `article`, `email`,
and `post` the numbers are provisional; say so if it matters.

## 6. Lint

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/lint.py draft.md \
  --register bank --profile ${CLAUDE_SKILL_DIR}/reference/voice_profile.json -v
```

If `${CLAUDE_SKILL_DIR}` does not resolve on the current surface, run it
from the skill folder with relative paths instead:
`python3 scripts/lint.py draft.md --register bank --profile reference/voice_profile.json -v`

Diagnostic, not a gate. It reports pattern hits, rhythm statistics, and
quantity density, and flags deviation from the measured profile. As of
v1.1 it also reports comma, semicolon, parenthesis and quotation density,
`and`-stacking, abstraction density and nominalisation density.

Two cautions. The negative-parallelism and analogy checks are regex
approximations and will catch legitimate contrast. The 2026 metrics run
off provisional bands that were never calibrated on Ram's own corpus,
and lint labels them as such; treat a breach as a prompt to look, not a
fault. Density checks are suppressed below 200 words, where rates are
too unstable to mean anything.

**Lint the rendered output, not the source.** Where a document is generated
from code - docx-js, pptxgenjs, a build script, a template - the prose does
not exist as continuous text until it is rendered. Extract the text from the
built file and lint that. Linting the source, or reading the patch diff,
tests nothing: a tic distributed one sentence per section is invisible in the
patches and obvious on the rendered page.

Lint **every artefact in the set**, not only the main document. Decks,
cover sheets, model notes and assumption columns carry prose too, and they
are worse, not better: slide furniture compresses hardest, so fragments, em
dashes and negations concentrate there. Extract slide text from the built
.pptx and note strings from the built .xlsx and lint those as well.

This applies to every rebuild, not only the first draft. A version that
changed only numbers still ships all of the prose. A document that has gone
through six versions without a lint has had none, not six.

Fix what it catches, then read the draft once more as a reader. Lint cannot
tell you whether the argument holds.

## 7. Anti-overfitting

This file describes taste. It does not replace judgement.

Do not force jokes, insert slang, make every sentence punchy, or make every
paragraph one line. Do not avoid the exact word because it appears on a
list when no substitute carries the meaning - flag the exception instead.
Do not turn the output into a demonstration of avoided mistakes.

Write normally first. Then remove what sounds machine-made.

The test: does this read like something Ram would send, or like a model
imitating him? If it feels forced, simplify.

## 8. Maintenance

**The lists decay.** Every model update moves generated prose closer to
human prose, and the tells that made this catalogue useful stop being
diagnostic. The first-generation vocabulary is already spent: delve and
tapestry were the canonical markers in 2023 and had largely gone by
mid-2026, while the words that replaced them are duller and harder to
see. Sections 9 to 12 of `patterns.md` will expire the same way.

Review the catalogue every six months against a current source. Last
reviewed July 2026 against the Economist study. When a section expires,
mark it spent rather than deleting it: a word that stopped being a tell
is usually still bad writing, and section 1 earns its place on that
ground alone.

**These are drafting rules, not evidence.** The lists say what to avoid
when writing. They do not establish that a given text was machine-made.
No single word carries that weight, the models differ from each other,
and commercial detectors are closed algorithms that return a verdict
with no reasoning and a real false-positive rate. If Ram ever needs to
assess someone else's text, the answer is a judgement across many
markers at once, held loosely, and never a claim built on one word.

## 9. Delivery

Bank, investor, or counterparty standard. Every deliverable should be
sendable as-is.

State assumptions and open items in a short note after the draft, never
inside the prose. Include reconciliation checks where numbers appear. For
legal work, add the discussion-not-advice reminder. For financial models
and projections, add the professional-review disclaimer.

Save to the agreed project folder,
named `ProjectName_DocType_vX.Y`. Confirm the folder if unclear. Increment
versions; never overwrite.
