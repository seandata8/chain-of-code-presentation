"""Check the claims behind an answer, to see where each method goes wrong.

Chain of Thought: the model follows the template of the examples, so each
claim sits in a known sentence. Each step is checked using the model's own
earlier numbers, so one early mistake isn't counted again in later steps.

Chain of Code: the facts are the birthdays (month and day) the LM supplied,
read from the `born` dictionary the program actually used.
"""

import re
from datetime import date, datetime, timedelta

from ground_truth import BIRTH_DATES, MIN_DAYS, birthdays
from prompts import fmt

DATE = r"(\d{1,2} [A-Z][a-z]+ \d{4})"
WINDOW = re.compile(rf"{MIN_DAYS} days before .+? is {DATE}, and {MIN_DAYS} days after is {DATE}")
BEFORE = re.compile(rf"last birthday on or before {DATE} is (.+?)'s \({DATE}\), which is (\d+) days before")
AFTER = re.compile(rf"first birthday on or after {DATE} is (.+?)'s \({DATE}\), which is (\d+) days after")
COMPARE = re.compile(r"(\d+) is less than (\d+)")


def to_date(text: str) -> date | None:
    try:
        return datetime.strptime(text, "%d %B %Y").date()
    except ValueError:
        return None


def check_cot(raw: str, d: date) -> list[tuple[str, str, bool]]:
    """Return (kind, claim, correct) for each claim found; kind is math, fact, or choice."""
    checks = []
    days = sorted(day for year in (d.year - 1, d.year, d.year + 1) for _, day in birthdays(year))

    if m := WINDOW.search(raw):
        too_late, too_early = to_date(m[1]), to_date(m[2])
        right_late, right_early = d - timedelta(days=MIN_DAYS), d + timedelta(days=MIN_DAYS)
        checks.append(("math", f"{MIN_DAYS} days before is {m[1]} (correct: {fmt(right_late)})", too_late == right_late))
        checks.append(("math", f"{MIN_DAYS} days after is {m[2]} (correct: {fmt(right_early)})", too_early == right_early))

    for pattern, side in ((BEFORE, "before"), (AFTER, "after")):
        if not (m := pattern.search(raw)):
            continue
        limit, name, day, count = to_date(m[1]), m[2], to_date(m[3]), int(m[4])
        born = BIRTH_DATES.get(name)
        checks.append(("fact", f"{name}'s birthday is {m[3][:-5]}",
                       bool(born and day and (day.month, day.day) == (born.month, born.day))))
        if limit and day:
            if side == "before":
                right = max((x for x in days if x <= limit), default=None)
                claim = f"last birthday on or before {m[1]} is {m[3]}"
            else:
                right = min((x for x in days if x >= limit), default=None)
                claim = f"first birthday on or after {m[1]} is {m[3]}"
            checks.append(("choice", f"{claim} (correct: {fmt(right) if right else 'none'})", day == right))
        if day:
            right_count = abs((day - d).days)
            checks.append(("math", f"{m[3]} is {count} days {side} (correct: {right_count})", count == right_count))

    if m := COMPARE.search(raw):
        checks.append(("math", f"{m[1]} is less than {m[2]}", int(m[1]) < int(m[2])))
    return checks


def check_coc(trace: list[dict]) -> list[tuple[str, str, bool]]:
    """Check each birthday (month and day) in the program's final `born` dictionary.

    Only the month and day matter to the answer, so a wrong birth year isn't counted.
    """
    born = {}
    for entry in trace:
        if entry["delta"] and isinstance(entry["delta"].get("born"), dict):
            born = entry["delta"]["born"]
    checks = []
    for name, right in BIRTH_DATES.items():
        given = born.get(name)
        if not isinstance(given, date):
            checks.append(("fact", f"{name}: not looked up", False))
        elif (given.month, given.day) == (right.month, right.day):
            checks.append(("fact", f"{name}'s birthday is {given.day} {given:%B}", True))
        else:
            checks.append(("fact", f"{name}'s birthday is {given.day} {given:%B} "
                                   f"(correct: {right.day} {right:%B})", False))
    return checks


def count(checks: list[tuple[str, str, bool]], kind: str) -> tuple[int, int]:
    """(number right, number checked) for one kind of claim."""
    found = [ok for k, _, ok in checks if k == kind]
    return sum(found), len(found)


def summary(checks: list[tuple[str, str, bool]]) -> str:
    """E.g. 'math 1/5, facts 2/2, choices 0/2'."""
    parts = []
    for kind, label in (("math", "math"), ("fact", "facts"), ("choice", "choices")):
        found = [ok for k, _, ok in checks if k == kind]
        if found:
            parts.append(f"{label} {sum(found)}/{len(found)}")
    return ", ".join(parts) or "no checkable claims"
