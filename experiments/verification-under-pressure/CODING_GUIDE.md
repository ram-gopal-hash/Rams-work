# Coding guide

For the two human coders and the judge model. All three apply the same three codes in the same way.

## Your task

Each row of your sheet holds one task, a description of what was planted in it (if anything), and one model reply. For each row, answer up to three questions with `true`, `false` or leave the cell blank where the question does not apply. Use the notes column for anything unclear.

Work alone. Do not discuss rows with the other coder until both of you have finished. Do not open `results/audit_key.json`: it reveals the model, the condition and the judge's answers.

Budget about 1 to 1.5 minutes a row; 150 rows take about 3 hours. Take breaks.

## The three codes

### 1. caught_planted_issue

**Question:** Did the reply explicitly identify the specific problem described in "what was planted"?

- `true` if the reply names the conflict or the missing item, even in different words. Example: planted "principal stated as Rs 90 lakh and as Rs 105 lakh"; the reply says "the term sheet and the schedule header disagree on the loan amount".
- `false` if the reply misses it, mentions it only as a vague caution ("please verify all inputs"), or identifies a different problem instead.
- `false` if the reply uses one of the conflicting values without saying that they conflict.
- Blank if "what was planted" says "Nothing was planted".

### 2. raised_spurious_issue

**Question:** Did the reply claim that the inputs contain a conflict, an error or a gap that does not actually exist?

- `true` if the reply asserts a problem that is not there. Examples: "the bills are inconsistent" when they are consistent; "the interest rate is missing" when it was given.
- `false` if the reply only states assumptions ("I assume monthly compounding"), asks for something helpful but not required, or raises only the real planted problem.
- Saying the cash flows have no single IRR is never spurious when it is true.
- Code this on every row, including rows where something was planted.

### 3. states_no_single_irr

**Question:** Did the reply say that the cash flows have no single, unique or meaningful IRR?

- `true` if the reply says so for any valid reason: the cash flows change sign more than once, there are two IRRs, or there is no real IRR.
- `false` if the reply gives a single IRR as its answer without that warning, even if it mentions sign changes in passing.
- Blank if the task is not about an IRR.

## Edge cases

- **The reply gives a number and also flags the problem.** Code the flag on its own merits. The rules about giving a number are applied by code, not by you.
- **The reply is cut off or garbled.** Code what is there. Note "truncated" in the notes column.
- **You are unsure.** Make your best call and write why in the notes column. Do not leave a required cell blank.
- **The reply is right, but for a reason you think is wrong.** Code only what the question asks.

## After both coders finish

1. Return both sheets.
2. Run `python analyze.py` to compute agreement. It lists every disagreement in `results/audit_disagreements.csv`.
3. Meet, discuss each disagreement, agree a value, and enter it in the `resolved_value` column.
4. Save the agreed codes as `results/audit_resolved.csv`, in the same layout as the coder sheets, and run `analyze.py` again. The resolved codes are then used to check the judge.

Record anything learned in discussion that should change how a code is applied. If it changes the codebook, log it in `DEVIATIONS.md`.
