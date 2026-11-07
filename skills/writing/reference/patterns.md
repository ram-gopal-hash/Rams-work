---
name: patterns
description: Full catalogue of banned words, phrase shapes, and structural tells, plus the 2026 second-generation tells (abstraction density, nominalisation, Latinate diction, under-punctuation, model fingerprints). Merged from the retired humanizer and anti-ai-writing skills. Read when drafting or auditing prose; SKILL.md carries the workflow, this file carries the lists.
---

# Pattern catalogue

Contents:
1. Banned vocabulary
2. Banned phrase shapes
3. Dead openings, transitions, engagement bait
4. Negative parallelism (hard ban)
5. Analogy and metaphor
6. Structural tells
7. Punctuation and formatting
8. Chatbot artifacts
9. Second-generation vocabulary (density, not presence)
10. Nominalisation and Latinate diction
11. Coordination and under-punctuation
12. Model fingerprints

Ram's ruling, July 2026: these bans are absolute and apply to his own
drafts as well as to generated text. Words on this list appear in his
authentic writing; strip them anyway. See `voice_profile.md`.

**Generations.** Sections 1 to 8 catalogue the 2023-24 tells: marketing
hype, ornamental vocabulary, engagement bait. Sections 9 to 12 catalogue
what replaced them, per the Economist's July 2026 study of 1.2m words
across ChatGPT, Claude, Gemini and Grok, benchmarked against its own
copy, CNN, the NYT, the Washington Post and novels from 1950 to 2022.
The older tells have not become acceptable writing, but they are no
longer diagnostic: the study found that delve and tapestry have largely
gone. Assume the same decay applies to sections 9 to 12. See the
maintenance rule in `SKILL.md` section 8.

Overriding principle from `SKILL.md` section 0: accuracy beats these
rules. If the banned word is the exact technical term and no substitute
carries the same meaning, keep it and note why. `Robust` in a statistics
sense, `integrated` in a systems-architecture sense, `align` describing
physical alignment, and `leverage` as a finance noun (leverage ratio,
3x leverage) are technical uses, not the banned figurative ones.

---

## 1. Banned vocabulary

delve, realm, harness, unlock, tapestry, paradigm, cutting-edge,
revolutionize, intricate, intricacies, showcasing, crucial, pivotal,
surpass, meticulously, vibrant, unparalleled, underscore, leverage
(figurative), synergy, innovative, game-changer, testament, commendable,
meticulous, highlight (verb), emphasize, boast, groundbreaking, align
(figurative), foster, showcase, enhance, holistic, garner, accentuate,
pioneering, trailblazing, unleash, versatile, transformative, redefine,
seamless, optimize, scalable, robust (figurative), breakthrough, empower,
streamline, frictionless, elevate, adaptive, effortless, data-driven,
insightful, proactive, mission-critical, visionary, disruptive, reimagine,
unprecedented, intuitive, leading-edge, synergize, democratize, accelerate,
state-of-the-art, dynamic, immersive, predictive, transparent, proprietary,
integrated (figurative), plug-and-play, turnkey, future-proof,
paradigm-shifting, supercharge, enduring, interplay, valuable, captivate,
landscape (abstract)

Replace with the plain word. `is`, `has`, `uses`, `gives`, `shows`,
`causes`, `changes`, `removes`, `adds`, `cut`, `reduced`, `fixed`,
`refused`, `delayed`.

## 2. Banned phrase shapes

Bloated verbs used to dodge `is` or `has`:

serves as, stands as, marks a, represents a, boasts a, features a,
offers a, plays a role in, functions as, helps to, aims to, seeks to

Write: is, has, uses.

## 3. Dead openings, transitions, engagement bait

**Openings:** In today's..., It is important to note that..., It is worth
noting..., In order to, Let's dive in, Let's explore, Let's unpack, At the
end of the day, Moving forward, To put this in perspective, What makes this
particularly interesting is, The implications here are, In other words, It
goes without saying, Nobody is talking about, Most people don't realize, In
this article I will, Despite its strengths X faces challenges, Challenges
and future prospects

**Transitions:** Furthermore, Additionally, Moreover, That said, That being
said, With that in mind, It is also worth mentioning, On top of that

Use a real transition or none. Ram's own corpus contains zero instances of
Furthermore or Moreover; this ban matches his voice rather than fighting it.

**Engagement bait:** Let that sink in, Read that again, Full stop, This
changes everything, Are you paying attention, You are not ready for this

**Hype:** 10x your anything, game-changer, cutting-edge, future-proof,
unlock, supercharge

## 4. Negative parallelism - hard ban

Do not reject one frame and replace it with another. Do not invent a weaker
idea to correct it. The ban applies across sentence boundaries and applies
even when the word `not` is absent.

**Fails if the text:** (a) dismisses, minimises, rejects or questions X,
then (b) asserts, reveals, upgrades or replaces it with Y.

**Explicit forms:** This isn't X. This is Y. / Not X. Y. / No X. Just Y. /
Forget X. Focus on Y. / Less X, more Y. / Not only X but also Y. / It's not
just about X, it's about Y. / X? No. Y. / Stop thinking X. Start thinking Y. /
X is dead. Y is the future. / The question is not X. The question is Y. /
You do not need X. You need Y. / X is overrated. Y matters. / It was never
about X. It was always about Y.

**Softened forms, equally banned:** While X may seem... / Although X
appears... / Sure, X... / At first glance... / On the surface... / Most
people think X... / The common assumption is X... / X gets all the
attention... / Conventional wisdom says X... / Many assume X...

**Trailing forms - assertion first, foil tacked on.** These are the ones that
survive review, because they read as precision rather than as rhetoric:

X is Y, not Z. / The constraint is A, not B. / It is P, not Q. / settled by X,
not by us. / permitted for A only, not for B. / a planning number, not a
quotation.

The test is whether the negated term is something **this reader actually
believes**. If they could plausibly have assumed Z, the negation informs -
keep it. If Z is a foil invented to give the sentence a shape, cut it and let
the positive claim stand on its own.

| Verdict | Sentence | Why |
|---|---|---|
| Keep | "levied on contracted capacity, not on units" | A reader could reasonably assume per-unit billing. |
| Keep | "a 25+5 year lease, not a sale" | The counterparty's live fear; he brought it himself. |
| Cut | "The binding constraint is evacuation and offtake, not construction." | Nobody thought construction was the constraint. |
| Cut | "The network path is settled by the substation, not by us." | Becomes: "The substation settles the network path." |

One or two informative negations in a long document are normal. Ten is a tic.
Count them before shipping.

This is the same disease as `numbers-integrity` Pass 8 (scar tissue), with a
different phantom: scar tissue negates a claim a **previous draft** made, this
negates a belief the **reader** never held. Both invent something to push
against. If you are running one sweep, run both.

**Verbless appositive fragments.** Noun phrase, comma, noun phrase, no
finite verb: "Two independent routes, same answer." / "Same project, same
tariff, same land." / "Rule 3 rewritten." The clipped form reads as
compression but is cadence, and it is strongest exactly where space is
tight - slide titles, subtitles, table captions, pull-outs. Restore the
verb: "Two independent routes give the same answer."

**Repeated foil - count across the whole set.** The keep/cut test above is
per sentence. Apply it a second time across every artefact together. The
same negated term used more than once is a tic even where each instance
would individually pass: "not a solar park" three times across a proposal
and a deck, "not a sale" twice, "not by us", "not on units". Keep the
strongest instance, delete the rest.

**Pivot words that fail after a rejected frame** (fine in ordinary use):
but, yet, actually, really, instead, rather, ultimately, in reality, the
truth is, what matters is, the real, the deeper, the actual, the hidden,
the overlooked

**Across sentences:**

- Bad: "Most teams think they have a hiring problem. They have a standards
  problem." Better: "The team's standards are unclear."
- Bad: "People blame the algorithm. The input data is broken."
  Better: "The input data is broken."

**Rhetorical-question form** is also banned: "Is this a productivity
problem? No. It's an attention problem."

## 5. Analogy and metaphor

Default: zero analogies under 800 words. One per 1,500 words above that,
and only if it earns its place. Never stack, never extend across
paragraphs, never more than one per section.

**Banned setups:** Think of it as, Imagine, Picture, It is like, It is kind
of like, As if, As though, The X of Y, Works like, Acts like, Functions as,
Serves as, A bridge between, A lens for, A mirror of, A roadmap for, The
engine of, The fuel for, The backbone of, The foundation of, The fabric of,
The heartbeat of, The DNA of, The glue that holds

**Banned families** unless the subject is literal: journey, battlefield,
machine-for-people, architecture-for-ideas, ecosystem-for-business,
engine or fuel for motivation, map or compass for strategy, signal and
noise, toolbox, iceberg, bridge, north star, flywheel, scaffolding,
plumbing, gardening, chess, sports, puzzle

**Banned metaphor verbs for abstract work:** sanded down, bolted on,
stripped back, stitched together, woven, layered, carved out, baked in,
injected, fueled, sparked, anchored, framed, mapped, distilled, unpacked,
crystallized, sharpened, surfaced, amplified, channeled, threaded,
sculpted, molded, cemented, bridged

Use: cut, added, removed, changed, joined, caused, showed, explained,
reduced, clarified, fixed, named, listed, compared, chose, rejected.

Rewrites:

- "Your onboarding is a leaky bucket." -> "42% of users leave on step 2
  because the form asks for billing details before showing the product."
- "The strategy is a compass." -> "The strategy says which customers to
  ignore."

## 6. Structural tells

**Significance inflation.** a key turning point, a pivotal moment, setting
the stage for, marking a significant evolution, broader implications, is a
testament to, indelible mark, deeply rooted, evolving landscape. State the
fact; let the reader weigh it.

**Rule of three.** Do not force claims into triads. "speed, efficiency, and
innovation" is a tell. Use one item if one matters, two or four if that is
what is true. Ram's pitch corpus shows 20 triads in 3,400 words - this is
his most frequent structural tell and the check stays on for his drafts.

**False ranges.** "from ancient traditions to modern innovation". If the
range has no meaningful middle, delete it.

**Elegant variation.** Do not swap names to avoid repetition. "Sarah joined
in 2021. The seasoned operator then led the team." Use the name again, or
a pronoun.

**Participle padding.** highlighting its importance, underscoring its
significance, reflecting broader trends, contributing to a rich history,
paving the way for, opening the door to. If the analysis matters, give it
a sentence with a specific claim.

**Meta commentary.** In this section, This article will cover, Let me walk
you through, Here is a comprehensive overview. Say the thing.

**Vague attribution.** Industry reports, Observers have cited, Experts
argue, Some critics argue, Many believe. Name the source or cut the claim.

**Knowledge-cutoff disclaimers.** As of my last update, Based on available
information, While specific details are limited, I don't have real-time
access. If current facts matter, verify them before writing.

**Metronome rhythm.** Same-length sentences, same-size paragraphs. Target
sentence-length CV above 0.45. See `voice_profile.md` for Ram's measured
0.54.

**Fractal summaries.** Previewing each section then recapping it. Cut both.

**Empty conclusions.** In conclusion, Overall, As we move forward, the
future looks bright, exciting times lie ahead. If the ending only repeats
the point, delete the ending.

**Symmetric weighting.** Sections of equal length regardless of what
matters. Spend words where the evidence changes the decision.

## 7. Punctuation and formatting

- **No em dashes.** Absolute, per Ram's ruling, despite his own usage.
  Rewrite with comma, colon, parentheses, or full stop. Do not drop the
  thought - re-cut the sentence.
- No curly quotes in authored text. Word smart quotes in an imported
  source file are a source artifact, not a style error; do not report them.
- No emojis.
- Bold sparingly, one or two moments per section.
- Sentence case in headings.
- Digits for numbers: 3 years, 10 tools, 500 users.
- Inline-header vertical lists (`- **Thing:** description`) are banned in
  prose registers, required in structured ones. See `registers.md`.

Everything above is prohibitive. Section 11 carries the positive rule:
too little punctuation is now a stronger tell than too much.

## 8. Chatbot artifacts

Certainly, Of course, Great question, Happy to help, I hope this helps,
Let me know if you'd like, Would you like me to, You're absolutely right.

Strip entirely from any text intended to leave the chat.

---

## 9. Second-generation vocabulary - density, not presence

Section 1 bans words on sight. This list does not work that way. These
are ordinary words that carry real meaning in a credit note or a risk
section, and a flat ban would fight the `bank`, `dpr` and `legal`
registers. What marks the text as generated is how many of them appear
per hundred words, and whether each one is doing work.

**Abstract quantifiers and consequence nouns:** significant,
significantly, increasingly, substantial, considerable, notable, marked,
consequences, implications, ramifications, factors, aspects, elements,
dimensions, considerations, developments, dynamics

**Borrowed-authority nouns:** framework, methodology, parameter,
parameters, mechanism, criteria, approach, context, scope, capacity,
capability

**Rare-register words:** interdependence, reindustrialisation,
proliferation, differentiation, convergence, optimisation, prioritisation

The test for each one: delete it and see what breaks. If nothing breaks,
it was filler. If the sentence loses precision, keep it.

- "a significant increase in tariff" -> the number. "tariff rose from
  Rs 6.20 to Rs 7.05"
- "increasingly difficult to fund" -> when, and how much harder.
  "three of the four lenders declined in the March quarter"
- "the consequences for the project" -> name one. "the COD slips past
  the scheme deadline and the subsidy lapses"
- "our methodology for tariff discovery" -> "how we set the tariff"

`Significant` has a statistics meaning and `parameter` has an
engineering meaning. Both are accuracy exceptions under `SKILL.md`
section 0. The ban is on the vague use, not the technical one.

## 10. Nominalisation and Latinate diction

**Nominalisation.** Turning a verb into a noun and then propping it up
with a weak verb. This is now among the clearest generated-text markers,
and it is the main way a DPR paragraph goes flat.

Shape: `[weak verb] + [noun ending in -tion, -ment, -ance, -ence, -ity,
-ism, -ing]`.

- "the implementation of the revised schedule was undertaken by the EPC
  contractor" -> "the EPC contractor implemented the revised schedule"
- "there was a reduction in generation" -> "generation fell 8%"
- "the provision of a corporate guarantee is a requirement" ->
  "the lender requires a corporate guarantee"
- "completion of the evaluation" -> "we evaluated it"

Weak verbs that signal a nominalisation is coming: undertake, conduct,
perform, carry out, provide, achieve, effect, facilitate, enable, make,
give, there is, there was, there are.

Not every abstract noun is a fault. `Depreciation`, `commissioning`,
`arbitration` and `allotment` are the names of things. The fault is
using a noun where the verb was available and shorter.

**Latinate over Saxon.** Orwell's pretentious diction: reaching for the
grander-sounding root when the plain one is exact. The study found more
Latin-derived suffixes in generated text than in human text across every
comparison corpus.

utilise -> use. commence -> start. terminate -> end. purchase -> buy.
demonstrate -> show. facilitate -> help. sufficient -> enough.
subsequent -> later, next. prior to -> before. additional -> more.
attempt -> try. require -> need. obtain -> get. assist -> help.
indicate -> show. sustain -> keep. component -> part. numerous -> many.
initiate -> start. finalise -> finish. ascertain -> find out.

Contract and legal registers keep the formal term where it is the term
of art. `Commence` in a clause about the commencement date stays.
`Terminate` in a termination clause stays. Everywhere else, use the
short word.

## 11. Coordination and under-punctuation

**Comma splicing by "and".** The most overused word in generated prose.
Clauses get chained with `and` instead of subordinated, split, or
punctuated, which produces long flat sentences that never signal which
part matters.

- Bad: "The lender reviewed the model and raised three queries on the
  DSCR and asked for the revised PPA and we responded on 14 March."
- Better: "The lender reviewed the model, raised three queries on the
  DSCR, and asked for the revised PPA. We responded on 14 March."
- Better still, if the DSCR query is the point: "The lender raised three
  queries on the DSCR. Two were arithmetic. The third asked why the
  P90 case still cleared 1.35x, and that one took a week to answer."

Check: any sentence with three or more `and`s is a rebuild candidate.

**Under-punctuation.** The 2026 finding that inverts the old advice.
Generated text uses fewer commas and semicolons than human writing and
almost no parentheses. It reads unbroken. Three causes, all fixable:
sentences run long, clauses get coordinated instead of nested, and
nobody is quoted.

Do not sprinkle commas to hit a number. Fix the cause:

- Nest a qualifier instead of starting a new sentence for it.
- Use a semicolon where two clauses are genuinely paired.
- Use parentheses for the aside, the unit, the cross-reference, the
  arithmetic. Ram's own writing runs c. 0.50 parens per 100 words and
  puts arithmetic inline; the profile lists this as a signature marker.
- Quote a named person. Generated text does not quote, because it has
  nobody to quote. A sentence with a lender's actual words in it cannot
  have been invented, which is also why section 6 bans vague attribution.

Targets are in `voice_profile.json`. Lint reports comma, semicolon and
parenthesis density and flags the low side.

**Paragraph monotony.** Related tell: paragraphs of similar length with
no short one to break them. `para_cv` below 0.25 is the flag.

## 12. Model fingerprints

There is no single AI style. The models differ, and the differences
matter here because Ram's drafts come out of Claude.

**Claude, per the July 2026 study:**

- highest use of nominalisations and rare words, alongside Gemini
- the only model still using more em dashes than human writers
- joint highest, with ChatGPT, on the three rhetorical constructions:
  not-X-but-Y, not-only-but-also, and the rule of three

Consequences for this skill:

1. The em-dash ban is well aimed for this pipeline even though the
   general tell has expired. ChatGPT now uses fewer em dashes than human
   writers; Claude does not. Ram's ruling stands on taste grounds, and
   the data supports keeping it for text that originated here.
2. Sections 4 and 6 are correctly prioritised. The two constructions we
   ban hardest are the two this model reaches for most.
3. Sections 9 and 10 are the highest-yield additions, because
   nominalisation and rare vocabulary are this model's strongest markers.

Do not read the fingerprint as a detection claim about any specific
text. See `SKILL.md` section 8.
