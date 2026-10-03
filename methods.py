"""Ask the model one question three ways, and grade the answers."""

import re
from datetime import date

import coc
from llm import generate
from prompts import coc_prompt, cot_prompt, direct_prompt, question

# Accepted variants of holiday names (after normalize()).
ALIASES = {
    "thanksgiving day": "thanksgiving",
    "christmas": "christmas day",
    "new years": "new years day",
    "labor day": "labour day",
    "truth and reconciliation day": "national day for truth and reconciliation",
    "day for truth and reconciliation": "national day for truth and reconciliation",
}


def normalize(name: str) -> str:
    """Lower case, no punctuation or parentheses, aliases resolved."""
    name = re.sub(r"\(.*?\)", "", name.lower()).replace("&", "and")
    name = re.sub(r"[^a-z ]", "", name)
    name = " ".join(name.split()).removeprefix("the ")
    return ALIASES.get(name, name)


def is_correct(model_answer, truth: list[tuple[str, date]]) -> bool:
    """Correct if it names any correct holiday (two in a tie)."""
    if not model_answer:
        return False
    return normalize(str(model_answer)) in {normalize(name) for name, _ in truth}


def run_direct(d: date) -> dict:
    raw = generate(direct_prompt(d), stop=["\nQ:", "\n"], max_tokens=30)
    return {"raw": raw, "answer": raw.strip()}


def run_cot(d: date) -> dict:
    raw = generate(cot_prompt(d), stop=["\nQ:", "\n\n"], max_tokens=500)
    # First match: the model sometimes keeps writing after its answer.
    found = re.findall(r"So the answer is (.+?)\.?\s*$", raw, flags=re.MULTILINE)
    return {"raw": raw, "answer": found[0].strip() if found else None}


def run_coc(d: date) -> dict:
    raw = generate(coc_prompt(d), stop=["\nQ:", "\n\n"], max_tokens=500)
    answer, trace, error = coc.execute(question(d), raw.strip())
    return {"raw": raw, "answer": answer, "trace": trace, "error": error}


METHODS = [("Direct", run_direct), ("Chain of Thought", run_cot), ("Chain of Code", run_coc)]
