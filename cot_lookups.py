"""Chain of Thought that writes down each birthday first.

The Chain of Thought examples in prompts.py jump straight to "the last
birthday on or before ... is X's", so the model has to recall and sort ten
birthdays in its head. The Chain of Code examples look up every birth date
first. This version of Chain of Thought does the same: one line per
scientist's birth date, then the birthdays in order through the year, then
the same steps as before.

Used by demo2.py (one date, live) and rehearse_lookups.py (30 dates).
"""

import re
from datetime import date

from ground_truth import BIRTH_DATES, EXAMPLE_BIRTH_DATES
from llm import generate
from prompts import build_prompt, cot_example, fmt

BORN = re.compile(r"^(.+?) was born on (\d{1,2} [A-Z][a-z]+ \d{4})\.$", re.MULTILINE)


def lookup_lines(people: dict) -> list[str]:
    """One line per birth date, then the birthdays in order through the year."""
    lines = [f"{name} was born on {fmt(born)}." for name, born in people.items()]
    in_order = sorted(people.items(), key=lambda p: (p[1].month, p[1].day))
    lines.append("In order through the year: "
                 + ", ".join(f"{born.day} {born:%B} ({name})" for name, born in in_order) + ".")
    return lines


def cot_lookup_example(d: date) -> str:
    """The usual Chain of Thought example, with the lookups after "Let's think step by step." """
    lines = cot_example(d).split("\n")
    return "\n".join(lines[:2] + lookup_lines(EXAMPLE_BIRTH_DATES) + lines[2:])


def cot_lookup_prompt(d: date) -> str:
    return build_prompt(cot_lookup_example, d) + "A: Let's think step by step.\n"


def run_cot_lookups(d: date, stream: bool = False) -> dict:
    raw = generate(cot_lookup_prompt(d), stop=["\nQ:", "\n\n"], max_tokens=900, stream=stream)
    # First match: the model sometimes keeps writing after its answer.
    found = re.findall(r"So the answer is (.+?)\.?\s*$", raw, flags=re.MULTILINE)
    return {"raw": raw, "answer": found[0].strip() if found else None}


def check_births(raw: str) -> list[tuple[str, str, bool]]:
    """Check each birth date the model wrote down (month and day, as for Chain of Code)."""
    given = {name: born for name, born in BORN.findall(raw)}
    checks = []
    for name, right in BIRTH_DATES.items():
        if name not in given:
            checks.append(("fact", f"{name}: not written down", False))
            continue
        ok = given[name].startswith(f"{right.day} {right:%B} ")
        checks.append(("fact", f"{name} was born on {given[name]}" + ("" if ok else f" (correct: {fmt(right)})"), ok))
    return checks
