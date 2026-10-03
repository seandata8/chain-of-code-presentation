"""Few-shot prompts for Direct, Chain of Thought, and Chain of Code.

Every example answer (and every date and day count in the reasoning) is
computed with ground_truth.py, so the examples are guaranteed correct.
"""

from datetime import date, timedelta

from ground_truth import MIN_DAYS, answer, federal_holidays

EXAMPLE_DATES = [date(2009, 6, 12), date(2016, 12, 10), date(2031, 10, 30)]


def fmt(d: date) -> str:
    """15 March 2027 style."""
    return f"{d.day} {d:%B %Y}"


def question(d: date) -> str:
    return (
        f"Q: Of the Canadian federal statutory holidays that are at least "
        f"{MIN_DAYS} days before or after {fmt(d)}, which one is closest to {fmt(d)}?"
    )


def direct_example(d: date) -> str:
    name = answer(d)[0][0]
    return f"{question(d)}\nA: {name}"


def cot_example(d: date) -> str:
    holidays = [h for year in (d.year - 1, d.year, d.year + 1) for h in federal_holidays(year)]
    too_late = d - timedelta(days=MIN_DAYS)
    too_early = d + timedelta(days=MIN_DAYS)
    before_name, before_day = max((h for h in holidays if h[1] <= too_late), key=lambda h: h[1])
    after_name, after_day = min((h for h in holidays if h[1] >= too_early), key=lambda h: h[1])
    before_days = (d - before_day).days
    after_days = (after_day - d).days
    name = before_name if before_days < after_days else after_name
    assert before_days != after_days and [name] == [n for n, _ in answer(d)]
    smaller, larger = sorted([before_days, after_days])
    return "\n".join([
        question(d),
        "A: Let's think step by step.",
        f"{MIN_DAYS} days before {fmt(d)} is {fmt(too_late)}, "
        f"and {MIN_DAYS} days after is {fmt(too_early)}.",
        f"The last holiday on or before {fmt(too_late)} is {before_name} "
        f"({fmt(before_day)}), which is {before_days} days before {fmt(d)}.",
        f"The first holiday on or after {fmt(too_early)} is {after_name} "
        f"({fmt(after_day)}), which is {after_days} days after {fmt(d)}.",
        f"{smaller} is less than {larger}, so the closest is {name}.",
        f"So the answer is {name}.",
    ])


def coc_code(d: date) -> str:
    return f"""from datetime import date
target = date({d.year}, {d.month}, {d.day})
all_holidays = []
for year in [target.year - 1, target.year, target.year + 1]:
    year_holidays = get_canadian_federal_holidays(year)
    all_holidays += year_holidays
far_enough = [(name, day) for name, day in all_holidays if abs((day - target).days) >= {MIN_DAYS}]
answer = min(far_enough, key=lambda h: abs((h[1] - target).days))[0]"""


def coc_example(d: date) -> str:
    return f"{question(d)}\n{coc_code(d)}"


def build_prompt(example, d: date) -> str:
    """Three worked examples, then the new question for the model to complete."""
    shots = "\n\n".join(example(e) for e in EXAMPLE_DATES)
    return f"{shots}\n\n{question(d)}\n"


def direct_prompt(d: date) -> str:
    return build_prompt(direct_example, d) + "A:"


def cot_prompt(d: date) -> str:
    return build_prompt(cot_example, d) + "A: Let's think step by step.\n"


def coc_prompt(d: date) -> str:
    return build_prompt(coc_example, d)


if __name__ == "__main__":
    import sys

    d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date(2027, 3, 15)
    for title, prompt in [("DIRECT", direct_prompt), ("CHAIN OF THOUGHT", cot_prompt), ("CHAIN OF CODE", coc_prompt)]:
        print(f"===== {title} =====\n{prompt(d)}\n")
