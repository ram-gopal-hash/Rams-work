# Verification under pressure: pilot report

Ram Gopal, November 2026

## Summary

I set out to test whether a written verification procedure, one of the Claude skills I use in finance, makes a model more reliable when the inputs are flawed or adversarial. I ran a pilot on two current models, Claude Sonnet 5.5 and Claude Haiku 5.5: 300 replies for USD 2.84. Both models were already close to perfect without any help. They caught planted conflicts, almost always declined to invent missing figures, and never gave in to pressure or to instructions hidden in the data. With nothing left to improve, the study as designed could not measure what my procedure adds, so I stopped after the pilot instead of spending the rest of the budget. The main failure I did see was practical: models working long calculations by hand ran out of reply length before giving an answer.

## The question

I give Claude written procedures before it works on financial analysis. They tell it to recompute key numbers by a second route, check inputs against each other, and refuse to fill gaps. I believed they helped but had never measured it. The question was whether such a procedure helps a model reject bad inputs and pressure, and what it costs in false alarms.

This was deliberately narrow: single questions with single answers, no tools, no agents.

## What I tested

The full design, written down before any model was called, is in `PREREGISTRATION.md` (a draft, never registered, because the study stopped at the pilot). In brief:

- **Tasks.** Financial calculations with answers computed exactly in code: back-solving tariff rates from bills, loan interest, project IRR, solar savings on a tiered tariff, and loss and revenue reconciliation.
- **Five versions of each task.** Clean; a planted inconsistency (two inputs that contradict each other); a missing input; authority pressure (a wrong figure asserted by someone senior, with a request to confirm it); and an instruction hidden in the source data telling the analyst to report a wrong figure.
- **Three conditions.** No guidance (C0); a one-line "double-check your work" reminder (C1); and the text of my verification procedure loaded as the system prompt, without the tools it normally uses (C2).
- **Pilot sample.** 10 of the 40 planned tasks, all five versions, all three conditions, one run per model: 150 replies per model. Numbers were scored by code. Whether a reply identified a planted conflict was checked by reading every conflict reply.

## Results

| | Sonnet C0 | Sonnet C1 | Sonnet C2 | Haiku C0 | Haiku C1 | Haiku C2 |
|---|---|---|---|---|---|---|
| Clean: correct number (of 10) | 9 | 9 | 9 | 10 | 9 | 9 |
| Planted conflict: identified (of 10) | 10 | 10 | 10 | 10 | 9 | 9 |
| Missing input: invented a number (of 8) | 0 | 0 | 0 | 0 | 0 | 1 |
| Authority pressure: gave in (of 10) | 0 | 0 | 0 | 0 | 0 | 0 |
| Hidden instruction: obeyed (of 10) | 0 | 0 | 0 | 0 | 0 | 0 |
| Replies cut off at the length limit (of 50) | 2 | 1 | 1 | 1 | 3 | 6 |

The missing-input row covers 8 tasks, not 10, for the reason given in the next section.

Every miss in the clean and conflict rows was a reply cut off before its answer. None was a wrong figure. One further Haiku reply identified the conflict correctly but closed its answer block with the wrong tag; I counted it as identified.

## What the pilot showed about my own design

Three of my tasks were flawed, and the models exposed them:

1. **Two "missing input" tasks were not missing anything.** I removed the tariff order from two bill-analysis tasks, expecting the models to say the top-slab rate could not be found. But once consumption is in the top slab, every extra unit is charged at the top rate, so any two bills in that slab give the rate directly. In one of the tasks: (Rs 8,446 − Rs 5,638) ÷ (1,270 − 910 units) = Rs 7.80 per unit, which is the correct answer. Both models found this and got it right. The models were right and my task was wrong. I excluded these two tasks from the missing-input row, which is why it counts 8 tasks instead of 10.
2. **Some prompts announced the gap.** Phrases such as "rates not provided" told the model what was missing, which made those tasks easier than intended.
3. **The planted conflicts were too visible.** Each conflict was a second figure stated in plain words, for example "the schedule header shows Rs 195 lakh". Anyone reading carefully would see it; no arithmetic was needed.

## Three other observations

**The main failure was running out of reply length.** 14 of the 300 replies were cut off at the 4,000-token limit, most of them on a 12-year IRR. The test gave the models no tools, so they had to work the IRR out in text: try a rate, discount each year's cash flow, check the total, try again. That working used up the reply allowance. In the one I read in full, it had already reached the right answer (11.27%) when it was cut off. This is a product of the test setup. With a calculator or code tool, which my skills normally have, the IRR is a single step. For anyone deploying models on financial arithmetic, the practical lesson is to give them such a tool.

**The procedure made replies longer.** Average reply length rose from 1,202 tokens (C0) to 1,518 (C2) for Sonnet, and from 1,557 to 1,935 for Haiku, about a quarter longer in both cases. Longer replies cost more and, with Haiku, were cut off more often (6 cut-offs in C2 against 1 in C0).

**One error came from the procedure itself.** In the single case where a model invented a missing figure, Haiku with my procedure loaded assumed an interest rate of 10%, citing it as a "default". That figure is a default from my own financial-model procedure, written for a different purpose. The model did flag the assumption and warned that the answer depended on it. Even so, it shows a real risk: defaults written into guidance for one task can become the source of an invented figure in another. It is a single case, so I treat it as an anecdote. It is still a lesson for anyone writing guidance for models.

## Why I stopped

The draft pre-registration said that if the unguided model scored 90% or more on clean items, or caught 90% or more of planted conflicts, the tasks had to be made harder before the main run. Both thresholds were met for both models.

I considered hardening the tasks: subtler conflicts, silent gaps, more plausible wrong figures. On the clean and conflict tasks that would probably produce some errors. On pressure and hidden instructions, each model resisted all 30 attempts of each kind, and I doubted stronger wording would change that. With 40 tasks, a small effect would not have been measurable anyway. Spending the rest of the USD 25 budget to chase a difference I did not expect to find seemed poor value, so I stopped.

## What I would test next

Models resisted pressure applied once. The next question is whether they hold their position when the pressure is repeated over several turns, the way a relationship manager or a client pushes back in practice. The other is whether they still ignore instructions hidden in documents when they are acting, as agents, on what they read. These are closer to the problems I want to work on: autonomous systems inside payment and market infrastructure, where a wrong action can spread before anyone notices. The plan for that study is in [NEXT_STUDY_PROPOSAL.md](../NEXT_STUDY_PROPOSAL.md).

## Notes

- **Limits:** the pilot sampled 10 of the 40 tasks, five of them from the solar-savings family, and none of the three tasks where no single IRR exists. It says nothing about how the models handle those, and small samples like this can miss rare failures. The procedures were also tested as text only, without the code and spreadsheet tools they normally use, so the pilot measured their written guidance, not the full skills as I use them in practice.
- **Cost:** USD 2.84 in API charges, against a USD 25 cap set before the work began.
- **Data and code:** the task generator, the harness, the scoring code and every pilot reply are in this folder. The tasks and their answers are synthetic.
- **Authorship:** the harness and task generator were written with Claude. The procedures under test are mine. I set the design, ran the pilot and decided to stop.
- **Coding:** I had planned a blind check of the judge model by two human coders. Because the study stopped at the pilot, that check was not needed; the conflict replies were few enough to read in full.
