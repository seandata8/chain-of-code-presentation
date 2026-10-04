"""Correct answers for the demo question, computed in Python.

Question: Of the birthdays of these ten scientists that are at least 100
days before or after {date}, whose is closest to {date}?
"""

from datetime import date

# Birth dates checked against Wikidata (October 2026).
BIRTH_DATES = {
    "Frederick Banting": date(1891, 11, 14),
    "Marie Curie": date(1867, 11, 7),
    "Charles Darwin": date(1809, 2, 12),
    "Albert Einstein": date(1879, 3, 14),
    "Carl Friedrich Gauss": date(1777, 4, 30),
    "Stephen Hawking": date(1942, 1, 8),
    "Ada Lovelace": date(1815, 12, 10),
    "Ernest Rutherford": date(1871, 8, 30),
    "Nikola Tesla": date(1856, 7, 10),
    "Alan Turing": date(1912, 6, 23),
}
SCIENTISTS = list(BIRTH_DATES)  # alphabetical by surname, so the order gives nothing away

# Five other scientists, used only in the worked examples, so the examples
# don't give away any of the ten birthdays above. Also checked against Wikidata.
EXAMPLE_BIRTH_DATES = {
    "Thomas Edison": date(1847, 2, 11),
    "Rosalind Franklin": date(1920, 7, 25),
    "James Clerk Maxwell": date(1831, 6, 13),
    "Louis Pasteur": date(1822, 12, 27),
    "Max Planck": date(1858, 4, 23),
}

FIRST_YEAR = 1943  # every scientist has been born by the previous year
MIN_DAYS = 100


def birthdays(year: int, people: dict = BIRTH_DATES) -> list[tuple[str, date]]:
    """Each scientist's birthday in the given year."""
    return [(name, date(year, born.month, born.day)) for name, born in people.items()]


def answer(d: date, people: dict = BIRTH_DATES) -> list[tuple[str, date]]:
    """Closest birthday at least 100 days from d (two if there is a tie)."""
    if d.year < FIRST_YEAR:
        raise ValueError(f"Dates before {FIRST_YEAR} are not supported.")
    candidates = []
    for year in (d.year - 1, d.year, d.year + 1):
        for name, day in birthdays(year, people):
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
