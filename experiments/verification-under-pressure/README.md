# Verification under pressure

Does a written verification procedure change how a frontier model handles financial analysis when the inputs are flawed or adversarial, and what does it cost in false alarms? **The study stopped after the pilot: both models tested were already close to perfect without help, so there was nothing left to measure. The findings are in [PILOT_REPORT.md](PILOT_REPORT.md).** The design, hypotheses and analysis plan, drafted before any model was called, are in [PREREGISTRATION.md](PREREGISTRATION.md). The reasoning behind each choice is in [DESIGN_RATIONALE.md](DESIGN_RATIONALE.md). Human and judge coding follow [CODING_GUIDE.md](CODING_GUIDE.md). Any change after registration is logged in [DEVIATIONS.md](DEVIATIONS.md).

The harness and the task generator were written with Claude. The procedures under test are mine, and I set and approved the design.

## Files

| File | Purpose |
|---|---|
| `generate_tasks.py` | Builds the 200 items (40 tasks x 5 variants) with exact answers |
| `test_tasks.py` | Checks every answer by an independent route (IRR by polynomial roots, loans by month-by-month simulation, tariffs by brute-force search) |
| `prompts.py` | The three conditions: baseline, generic reminder, procedure loaded |
| `run.py` | Calls the models: synchronously for the pilot, through the Batch API for the main run |
| `score.py` | Code-scores every reply, sends only the replies that need reading to the judge, writes two blind audit sheets |
| `analyze.py` | Rates, intervals, the pre-registered tests, coder and judge agreement |
| `batch_utils.py` | Batch submission and collection, prices, and the spend ledger that enforces the USD 25 cap |

## Running it (Windows PowerShell)

```powershell
git clone https://github.com/ram-gopal-hash/Rams-work.git
cd Rams-work\experiments\verification-under-pressure
pip install -r requirements.txt
python -m unittest test_tasks.py            # answers check out
$env:ANTHROPIC_API_KEY = "<your key>"        # this session only; never save the key in this folder

# 1. Pilot: 10 tasks, Sonnet, one run, synchronous (minutes)
python run.py estimate --models claude-sonnet-5-5 --limit 10 --runs 1 --out results/pilot_raw.jsonl
python run.py run      --models claude-sonnet-5-5 --limit 10 --runs 1 --out results/pilot_raw.jsonl
python score.py prepare  --raw results/pilot_raw.jsonl --prefix pilot_
python score.py judge    --raw results/pilot_raw.jsonl --prefix pilot_
python score.py finalize --raw results/pilot_raw.jsonl --prefix pilot_ --audit-n 30
python analyze.py --prefix pilot_            # results/pilot_summary.md

# 2. Calibrate, finalise and commit PREREGISTRATION.md (after review)

# 3. Main run through the Batch API (half price; usually done within hours)
python run.py estimate
python run.py submit  --tag main
python run.py status  --tag main             # repeat until it says ended
python run.py collect --tag main
python score.py prepare
python score.py estimate
python score.py judge-submit  --tag judge1
python score.py judge-collect --tag judge1
python score.py finalize                     # writes results/audit_coder1.csv and audit_coder2.csv
python analyze.py                            # results/summary.md

# 4. Two coders fill in their sheets independently, then: python analyze.py
```

Every paid step projects its cost and stops if it would take total spend past the cap in `results/spend.json`. Add `--dry-run` to any step to rehearse it with a fake model and no charges.
