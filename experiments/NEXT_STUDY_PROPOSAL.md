# Research proposal: does model robustness hold under repeated pressure and agentic action?

Ram Gopal, November 2026

Status: proposal for the follow-on to the [single-turn pilot](verification-under-pressure/PILOT_REPORT.md). Not yet started.

## The question

Do frontier models keep refusing a wrong figure when the pressure to accept it is repeated over several turns? And do they keep ignoring instructions planted in documents when they are acting as agents, not just answering? I want to find where that robustness breaks, if it does, in financial workflows where one accepted error can be acted on and spread.

## Why it matters

Models are moving from answering questions to taking actions: reconciling ledgers, raising payment instructions, booking trades. In banking, the failures that hurt were rarely a single wrong answer. They were a control that gave way under sustained pressure, such as the relationship manager who calls a third time, or a bad instruction buried in a file the system trusted. Stress testing assumes the shock will come and asks where the system breaks. I want to apply that to models before they sit inside payment and market infrastructure.

## Starting point

My [single-turn pilot](verification-under-pressure/PILOT_REPORT.md) (300 replies, USD 2.84) tested Claude Sonnet 5.5 and Haiku 5.5 on financial tasks with planted flaws. Across both models they resisted all 60 one-off attempts at authority pressure and all 60 hidden instructions, caught planted conflicts, and almost never invented missing figures. A written verification procedure added nothing measurable, because there was nothing left to improve. Single-turn robustness is no longer the open question. Whether it survives repetition and action is.

## Approach

Two experiments, reusing the pilot's tasks, whose correct answers are computed in code.

1. **Repeated pressure.** The model answers correctly, then a scripted counterparty pushes back for up to four turns, escalating from polite doubt to authority, to a deadline with consequences, to false supporting evidence. Two control arms: the same number of neutral follow-up turns, to separate pressure from conversation length, and pushback when the model is genuinely wrong, to check it still accepts a valid correction.
2. **Instructions hidden in documents, acted on.** The model works as an agent in a sandbox with simple tools: read a document, calculate, post a journal entry, submit a payment instruction. Some documents carry planted instructions, from blunt to plausible, including a vendor's "updated bank details", the pattern behind much real payment fraud. What counts is whether the model takes the harmful action through a tool, not what it says.

Each runs in three conditions: no guidance, a one-line security reminder, and a written control procedure modelled on bank dual control (verify against master data, never act on a beneficiary change without independent confirmation).

## Measures

| Experiment | Main measure | Guardrail measure |
| --- | --- | --- |
| Repeated pressure | Share of conversations where the model gives up a correct figure, and at which turn and pressure type | Share where it accepts a valid correction when it was genuinely wrong |
| Hidden instructions | Share of episodes where the model submits an unauthorised payment or entry | Share of clean documents it wrongly flags or refuses to act on |

A finding is any pressure type or instruction format that pushes the baseline failure rate above a threshold fixed after a calibration pilot, and whether the control procedure brings it down without blocking legitimate corrections and payments. A model that never changes its answer is not safe either, which is why both directions are measured. As in the first study, I will register the thresholds and analysis before the main runs and publish whatever comes out.

## Plan, scale and cost

About eight weeks:

1. Weeks 1 to 2: multi-turn harness, calibration pilot, registration.
2. Weeks 3 to 5: tool sandbox (document reader, calculator, ledger and payment stubs), calibration pilot, registration.
3. Weeks 6 to 8: main runs on two models, blind hand coding of a sample by two coders, write-up.

At the pilot's scale of 40 tasks, a full run is roughly 2,900 multi-turn conversations and 2,000 agent episodes. I estimate a few hundred US dollars of API usage at current prices, to be costed precisely after each pilot. I would most value guidance on agent-evaluation design and on how this fits existing prompt-injection benchmarks.

## Limits and risks

- **The ceiling may hold again.** If models resist every turn and every planted instruction, I report that and move to an adaptive attacker model, which is the harder next step.
- **The counterparty is scripted.** A fixed script tests known pressure patterns, not a determined adversary that adapts.
- **Synthetic, single-domain tasks on one model family.** Results may not carry over to messy real documents or other models.
- **Dual use.** The instruction formats are standard, publicly documented fraud patterns. The write-up describes patterns and rates, not a ready-made attack kit.

## Related work to build on

- Sharma et al. (2023), *Towards Understanding Sycophancy in Language Models*.
- Laban et al. (2023), *Are You Sure? Challenging LLMs Leads to Performance Drops in The FlipFlop Experiment*.
- Greshake et al. (2023), *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*.
- Debenedetti et al. (2024), *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*.
- Greenblatt et al. (2023), *AI Control: Improving Safety Despite Intentional Subversion*.
- Benton et al. (2024), *Sabotage Evaluations for Frontier Models*.
