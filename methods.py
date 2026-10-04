"""Ask the model one question three ways, and grade the answers."""

import re
from datetime import date

import coc
from llm import generate
from prompts import coc_prompt, cot_prompt, direct_prompt, question

def normalize(name: str) -> str:
    """Lower case, no punctuation, parentheses, or possessive 's."""
    name = re.sub(r"\(.*?\)", "", name.lower())
    name = re.sub(r"['’]s\b", "", name)
    name = re.sub(r"[^a-z ]", "", name)
    return " ".join(name.split())


def is_correct(model_answer, truth: list[tuple[str, date]]) -> bool:
    """Correct if it names any correct scientist (two in a tie); a surname alone is enough."""
    if not model_answer:
        return False
    given = normalize(str(model_answer))
    return any(given in (normalize(name), normalize(name).split()[-1]) for name, _ in truth)


def run_direct(d: date, stream: bool = False) -> dict:
    raw = generate(direct_prompt(d), stop=["\nQ:", "\n"], max_tokens=30, stream=stream)
    return {"raw": raw, "answer": raw.strip()}


def run_cot(d: date, stream: bool = False) -> dict:
    raw = generate(cot_prompt(d), stop=["\nQ:", "\n\n"], max_tokens=500, stream=stream)
    # First match: the model sometimes keeps writing after its answer.
    found = re.findall(r"So the answer is (.+?)\.?\s*$", raw, flags=re.MULTILINE)
    return {"raw": raw, "answer": found[0].strip() if found else None}


def run_coc(d: date, stream: bool = False) -> dict:
    raw = generate(coc_prompt(d), stop=["\nQ:", "\n\n"], max_tokens=500, stream=stream)
    if stream:
        print("\n\nTrace (red = Python, purple = LM):")
    answer, trace, error = coc.execute(question(d), raw.strip(), stream=stream)
    return {"raw": raw, "answer": answer, "trace": trace, "error": error}


METHODS = [("Direct", run_direct), ("Chain of Thought", run_cot), ("Chain of Code", run_coc)]
