---
name: registers
description: Document-class routing table. Read at the start of every writing task to decide which rules apply and which are suspended, including the 2026 second-generation checks. This is the first gate in the workflow, before any drafting.
---

# Register table

Pick the register before writing a word. The wrong register does more
damage than any banned word: blog voice in a DPR is unusable, and formal
register in a WhatsApp note to an EPC reads like a lawyer's letter.

If genuinely ambiguous, ask. One question costs less than a rewrite.

## The classes

| Register | First person | Contractions | Structured formatting | Analogies | lint flag |
|---|---|---|---|---|---|
| `contract` | no | no | required | never | `--register contract` |
| `legal` | no | no | required | never | `--register legal` |
| `dpr` | no | no | required | never | `--register dpr` |
| `bank` | no | no | required | never | `--register bank` |
| `investor` | yes | sparing | allowed | max 1 | `--register investor` |
| `article` | yes | yes | prose only | max 1 / 1,500w | `--register article` |
| `post` | yes | yes | prose only | max 1 | `--register post` |
| `email` | yes | yes | minimal | never | `--register email` |

"Structured formatting" means numbered sections, inline-header lists,
tables, title-case headings where a scheme template demands them. In the
four structured registers the formatting bans in `patterns.md` section 7
are suspended. Everywhere else they apply.

## The 2026 checks

Sections 9 to 12 of `patterns.md` are density judgements, and density
cuts differently by register. A credit note is legitimately more abstract
than a blog post.

| Register | Abstraction (s.9) | Nominalisation (s.10) | Latinate (s.10) | Punctuation density (s.11) |
|---|---|---|---|---|
| `contract` | relaxed | relaxed | suspended | applies |
| `legal` | relaxed | relaxed | suspended | applies |
| `dpr` | relaxed | relaxed | applies | applies |
| `bank` | relaxed | relaxed | applies | applies |
| `investor` | applies | applies | applies | applies |
| `article` | applies | applies | applies | applies |
| `post` | applies | applies | applies | applies |
| `email` | applies | applies | applies | applies |

**Relaxed** means lint still lists the hits so you can read them, but does
not raise a density warning. The words are often the right words in these
registers, and a warning that fires on every DPR is a warning nobody
reads.

**Suspended** means the check does not run. In `contract` and `legal`,
commence, terminate, provide and execute are terms of art tied to defined
dates and clause headings; substituting the plain word changes meaning.
In `dpr` and `bank` there is no such defence, so the Latinate list still
applies: a credit officer reading "utilise" instead of "use" gains
nothing.

**Punctuation density applies everywhere**, including the structured
registers. Formality is not a reason to write unbroken clauses, and the
comma and parenthesis floors are low enough that any competently
punctuated document clears them.

Relaxation is never an instruction to write badly. It suppresses a
mechanical flag, not the judgement in Pass B.

## No-touch zones

Do not restyle these, ever, even when they read formulaic:

- Operative clauses in an executed or near-final contract. Boilerplate is
  boilerplate for reasons that survived litigation. Comment on it, redline
  it on substance, never smooth its prose.
- Scheme-format DPR sections where JDVVNL, a DISCOM, or a lender specifies
  the wording or section order.
- Defined terms, once defined. Elegant variation is a style rule; in a
  contract it creates ambiguity.
- Regulatory filing language quoted from the source.
- Figures, formulas, spreadsheet cell contents, code.

If asked to "clean up" any of the above, say what you can safely change
(surrounding narrative, headings, the cover note) and leave the rest.

## Register notes

**contract, legal.** Precision beats everything. Long sentences are fine
when they carry conditions. Repetition of the defined term is correct.
Flag risk, incomplete fields, and departures from the prior draft; do not
improve the register. Always close with the reminder that this is for
discussion, not legal advice.

**dpr, bank.** Formal third person. No contractions, no first person, no
rhetorical devices. Numbered sections, TOC, page numbers. The reader is a
credit officer checking whether the numbers reconcile, so reconciliation
notes and stated assumptions matter more than prose quality. These
documents will score AI-ish on any detector regardless of who writes them,
because the register is genuinely low-variance. Do not optimise for that.
This is why abstraction and nominalisation density are relaxed here: the
DPR that reads generated may simply be a DPR. Cut the nominalisation
where the verb was available and shorter, and leave the rest.

**investor.** Ram's pitch corpus sits here. First person is correct - he
writes as a participant. Named actors with figures attached. Structured
formatting allowed where it aids scanning. Still no hype, still no
analogies beyond one.

**article.** Research and long-form. Full prose, sentence-length variance,
first person where it carries a judgement. This is the register where the
`voice_profile.md` rhythm targets matter most, and the one with the least
sample data - flag that when drafting until more samples arrive.

**post.** Short public writing. Same bans, tighter. No engagement bait -
that ban bites hardest here, since the format invites it.

**email.** Purpose, context, required action, deadline. Contractions fine.
Ask what the reader must do and by when; if the draft doesn't answer that,
it isn't finished.

## Ambiguity

Two signals decide most cases: who reads it, and what they do next. A
"note on the EPC scope gap" is `email` if it goes to the EPC contractor, `investor`
if it goes into a board pack, `bank` if it becomes an annexure to a loan
submission. Same facts, three registers. Ask which.
