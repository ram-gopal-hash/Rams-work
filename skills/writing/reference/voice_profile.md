---
name: voice_profile
description: Ram's measured writing parameters, derived from his own unassisted pitch corpus. Read before drafting anything in his voice; consumed numerically by scripts/lint.py via voice_profile.json.
sources: [Kaamyabi_Narrative.docx, The_Pitch_v2.docx, Pitch_Script.docx]
---

# Voice profile - Ram Gopal

## Scope limit - read this first

Derived from 3,417 words of investor-pitch narration written by Ram
without model assistance. `Kaamyabi_Narrative.docx` and `The_Pitch_v2.docx`
are successive drafts of the same document, so they count as one sample,
not two. `Pitch_Script.docx` is a bulleted research dump. The .pptx and
.pdf are slide decks with negligible running prose.

**This profile covers one register: spoken-pitch narration.** It is not
yet calibrated for email, memo, legal commentary, or long-form article.
Do not assume the numbers below transfer to those without more samples.

The corpus is bullet-form. "Unit" below means one bullet, which is Ram's
actual thought unit in this register, not a grammatical sentence.

## Measured parameters

| Parameter | Measured | Note |
|---|---|---|
| Unit length, mean | 22.8 words | |
| Unit length, sd | 12.4 | |
| Unit length, CV | 0.54 | healthy variance; above the 0.45 metronome threshold |
| Unit range | 4 to 83 words | he genuinely mixes very short and very long |
| Short units (=10w) | 11% | |
| Long units (>=40w) | 9% | |
| Numbers / 100w | 2.55 | |
| Currency and capacity units / 100w | 1.64 | Rs, crore, lakh, GW, MW, kW, kWp, bn |
| First person / 100w | 4.27 | very high; he writes as a participant, not an observer |
| Contractions / 100w | 1.11 | present, moderate |
| Commas / 100w | 7.08 | comma-heavy; long chained clauses |
| Parentheses / 100w | 0.50 | |
| Em dashes / 100w | 0.38 | he uses them; ban overrides - see below |
| Hedges / 100w | 0.06 | effectively zero |

Combined concrete-quantity density is about 4.2 markers per 100 words.
That is the single strongest signature in the corpus.

## Habits that show up repeatedly

- **Named actors, not categories.** A named customer in a named town with turnover
  attached; a named EPC lead; a named promoter with cash in hand. (Names
  removed for publication.)
  He never writes "a typical EPC" when he can write a person's name and
  their turnover.
- **`c.` for circa**, before approximate figures: c. 10 cr, c. $12 billion.
- **Numbers carry their own arithmetic**: "9 GW out of 13.5", "85 + 55 = 140 GW",
  "70% to be financed for a 2 MW facility worth Rs 10 crore".
- **Conversational asides inside formal content**: "Just to be clear...",
  "You got the father and son electrician...", "These folks...",
  "tying with our IB background!"
- **Enumeration that doesn't stay parallel**: "One, they want to close the
  deal quickly... Second, they want to scale their business." He starts with
  "One" and switches to "Second". Leave inconsistencies like this alone.
- **Concession before the point**: "While he's handling residential projects
  to keep the lights on, he's selectively rejecting smaller deals."
- **Opens units with we / our / this / at.** Rarely opens with a connective
  adverb. No "Furthermore", no "Moreover" anywhere in the corpus.
- **States a failure plainly.** On Barclays consumer: "our consumer business
  didn't take off - it was a humbling lesson in timing or rather
  product-market fit, concept we didn't even have the vocabulary for back
  then." No cushioning, and the self-correction is left in.

## Resolved conflict: the ban list flags his own writing

`anti-ai-writing` section 4A bans 22 words that appear in Ram's own
unassisted pitch:

| Word | Count | Word | Count |
|---|---|---|---|
| seamless | 4 | pivotal | 1 |
| leverage | 3 | unparalleled | 1 |
| highlight | 2 | innovative | 1 |
| align | 2 | foster | 1 |
| crucial | 1 | holistic | 1 |
| robust | 1 | empower | 1 |
| data-driven | 1 | predictive | 1 |
| integrated | 1 | valuable | 1 |

`seamless` and `leverage` are load-bearing for him: "as seamless as paying
cash", "leverage their established influence". These are banker register,
not AI tells. Ram has ruled they go anyway. Record the loss, apply the ban.

Same for em dashes: corpus shows 0.38 per 100 words, used for the
self-interrupting aside he favours. The absolute ban stands. Rewrite the
aside with a comma, colon, or full stop rather than dropping the thought.

**Resolved: the ban list wins.** Ram's ruling, July 2026. Strip these
words and all em dashes from every draft including his own. The profile
records the conflict so future-you understands why edited output will
read slightly cleaner than Ram's raw drafts. That gap is intended.

The other measured parameters are still targets to hit, not habits to
suppress: unit-length variance, quantity density, first person, and the
near-total absence of hedging all stay.

## What would improve this profile

Samples in registers not yet covered, each 300+ words, unassisted:

- an email or WhatsApp note to a counterparty (EPC and O&M counterparties)
- a board or internal memo
- a LinkedIn post or public comment
- an investment research piece, if any predate mid-2023

Pre-2023 material is preferable where it exists, since anything later may
carry model influence and would contaminate the baseline.
