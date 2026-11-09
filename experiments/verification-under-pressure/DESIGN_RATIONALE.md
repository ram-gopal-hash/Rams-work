# Design rationale

Why each choice in this study was made, in plain language. Read it before the pilot, change anything you disagree with, and be ready to explain any line of it in an interview.

**Why test my own procedure at all?** Because I claim it makes model output safer to rely on, and a claim like that should be measured. The procedure is a written guardrail given to the model. Whether guardrails of this kind work, and what they cost, is a live question in AI safety.

**Why financial analysis?** It is the domain I know, the right answers can be computed exactly, and the failure modes are concrete: a wrong number, an invented figure, or a confident answer built on a bad input.

**Why five task families?** So one quirk of one task type cannot drive the result. Each family has a known trap: stale tariff rates, a loan schedule that does not close, an IRR that does not exist, an average-tariff shortcut, and unit or scale slips.

**Why the four adversarial variants?** Each maps to a recognised safety problem:
- planted inconsistency: does the model notice conflicting inputs?
- missing input: does it make a number up? (fabrication)
- authority pressure: does it agree with a wrong figure because someone senior asserted it? (sycophancy)
- hidden instruction in the data: does it obey text in a document as if it were an instruction? (prompt injection)

**Why a "double-check your work" condition (C1)?** Without it, any gain from my procedure could just be the effect of telling the model to be careful. If my procedure beats C1, the content of the procedure matters, not merely the reminder.

**Why measure false alarms?** An analyst who raises problems that are not there soon gets ignored, and a model that does the same would be switched off. H4 checks that the procedure's gains do not come with materially more false alarms: at most 5 percentage points more than the baseline.

**Why two models?** To see whether any effect holds across model sizes. Haiku costs almost nothing, so it adds evidence for very little money.

**Why three runs of each item?** The same model can answer the same question differently each time. Three runs let us use the majority answer, which is more reliable than a single draw.

**Why pre-register?** Writing the hypotheses and the analysis down, and committing them publicly before the main run, shows the goalposts did not move after the results came in.

**Why pilot first, then register?** If the tasks are too easy, every condition scores near 100% and the study cannot show anything. The pilot calibrates difficulty. Registration comes after the pilot and before the main run, which is normal practice.

**Why a judge model, and why only for some items?** Most outcomes are numbers, which code can check exactly. A few outcomes need reading: did the reply actually identify the planted conflict, or raise a problem that does not exist? Only those go to the judge, which halves the judging cost.

**Why not ask the model to tick an issue code?** Showing the model a list of issue types ("conflicting inputs", "missing input") would hint at what to look for. That hint would help every condition and hide the effect of the procedure.

**Why two human coders?** Two people independently coding the same responses is standard practice in content analysis. Coder-to-coder agreement shows the codebook is clear. Human-to-judge agreement shows the judge can be trusted. I wrote the procedure, so I am not neutral; the second coder is independent, and both of us code blind.

**What is Cohen's kappa?** Agreement between two coders after removing the agreement you would expect by chance. 1.0 is perfect; above 0.8 is strong; below 0.6 means the codes are not reliable enough to lean on.

**What is the McNemar test?** It compares two conditions on the same items. It looks only at items where the two conditions disagree, one right and one wrong, and asks whether that split is more lopsided than chance would produce. It suits paired yes/no outcomes like ours.

**Why the Holm correction?** Running three tests raises the chance of a false positive. Holm adjusts the p-values so the overall error rate stays at 5%.

**Why the Batch API?** It costs half as much. Results take hours instead of minutes, which the timeline allows.

**What would change my conclusion?** If C2 does not beat C0 on H1 to H3, the procedure does not help on these tasks. If it beats C0 but not C1, a plain reminder does as well. If it raises false alarms by more than 5 points, the gains have a real cost. Each of those is a publishable result.

**What does this study not show?** It does not test autonomous agents, real client documents, other model families or long tasks. It is a first, narrow step.
