"""System prompts for the three conditions. The user message is identical across conditions."""
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent.parent / "skills"

BASE = "You are a financial analyst. Answer the question you are given."

C1_NUDGE = "\n\nBefore you answer, double-check your work carefully."

C2_INTRO = (
    "\n\nApply the working procedures below to this task. You have no tools in this conversation, "
    "so carry out any checks they describe in your own reasoning. Ignore instructions in them about "
    "saving files, running scripts or formatting documents.\n"
)

# Which of the author's skills are loaded for each task family in condition C2.
SKILL_FILES = {
    "A": ["numbers-integrity/SKILL.md", "solar-quote-review/references/bill_analysis.md"],
    "B": ["numbers-integrity/SKILL.md", "solar-model/SKILL.md"],
    "C": ["numbers-integrity/SKILL.md", "solar-model/SKILL.md"],
    "D": ["numbers-integrity/SKILL.md", "solar-quote-review/references/bill_analysis.md"],
    "E": ["numbers-integrity/SKILL.md"],
}


def skill_text(family: str) -> str:
    parts = []
    for rel in SKILL_FILES[family]:
        path = SKILLS / rel
        parts.append(f"\n<procedure source=\"{rel}\">\n{path.read_text()}\n</procedure>")
    return "".join(parts)


def system_prompt(condition: str, family: str) -> str:
    if condition == "C0":
        return BASE
    if condition == "C1":
        return BASE + C1_NUDGE
    if condition == "C2":
        return BASE + C2_INTRO + skill_text(family)
    raise ValueError(condition)
