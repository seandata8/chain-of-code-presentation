"""Correct answers for the demo question, computed from the holiday rules.

Question: Of the Canadian federal statutory holidays that are at least
100 days before or after {date}, which one is closest to {date}?
"""

from datetime import date, timedelta

from dateutil.easter import easter

FIRST_YEAR = 1983  # first year the July 1 holiday was called Canada Day
MIN_DAYS = 100


def nth_monday(year: int, month: int, n: int) -> date:
    """The n-th Monday of a month (n = 1 for the first)."""
    first = date(year, month, 1)
    first_monday = first + timedelta(days=(0 - first.weekday()) % 7)
    return first_monday + timedelta(weeks=n - 1)


def monday_before(d: date) -> date:
    """The last Monday strictly before d."""
    return d - timedelta(days=d.weekday() or 7)


def federal_holidays(year: int) -> list[tuple[str, date]]:
    """Federal general holidays in the Canada Labour Code (actual dates, not observed)."""
    days = [
        ("New Year's Day", date(year, 1, 1)),
        ("Good Friday", easter(year) - timedelta(days=2)),
        ("Victoria Day", monday_before(date(year, 5, 25))),
        ("Canada Day", date(year, 7, 1)),
        ("Labour Day", nth_monday(year, 9, 1)),
        ("Thanksgiving", nth_monday(year, 10, 2)),
        ("Remembrance Day", date(year, 11, 11)),
        ("Christmas Day", date(year, 12, 25)),
        ("Boxing Day", date(year, 12, 26)),
    ]
    if year >= 2021:
        days.append(("National Day for Truth and Reconciliation", date(year, 9, 30)))
    return sorted(days, key=lambda h: h[1])


def answer(d: date) -> list[tuple[str, date]]:
    """Closest holiday at least 100 days from d (two if there is a tie)."""
    if d.year < FIRST_YEAR:
        raise ValueError(f"Dates before {FIRST_YEAR} are not supported.")
    candidates = []
    for year in (d.year - 1, d.year, d.year + 1):
        for name, day in federal_holidays(year):
            distance = abs((day - d).days)
            if distance >= MIN_DAYS:
                candidates.append((distance, name, day))
    best = min(distance for distance, _, _ in candidates)
    return [(name, day) for distance, name, day in candidates if distance == best]


if __name__ == "__main__":
    import sys

    d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    for name, day in answer(d):
        print(f"{d}: {name} ({day}, {abs((day - d).days)} days away)")
