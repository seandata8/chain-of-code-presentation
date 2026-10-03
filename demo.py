"""Answer the holiday question three ways for one date.

Usage: uv run demo.py "15 March 2027"   (or 2027-03-15)
"""

import sys
from datetime import date, datetime

import coc
from ground_truth import FIRST_YEAR, answer
from methods import METHODS, is_correct
from prompts import fmt, question


def parse_date(text: str) -> date:
    for pattern in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(text.strip(), pattern).date()
        except ValueError:
            pass
    sys.exit(f'Sorry, I couldn\'t read "{text}". Try a date like "15 March 2027" or 2027-03-15.')


def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: uv run demo.py "15 March 2027"')
    d = parse_date(sys.argv[1])
    if d.year < FIRST_YEAR:
        sys.exit(f"Sorry, please pick a date in {FIRST_YEAR} or later "
                 f"(the first year the July 1 holiday was called Canada Day).")

    print(question(d))
    truth = answer(d)
    print("\nCorrect answer (computed in Python):")
    for name, day in truth:
        print(f"  {name}: {fmt(day)}, {abs((day - d).days)} days away")

    for title, run in METHODS:
        print(f"\n===== {title} =====")
        result = run(d)
        print(f"Raw model output:\n{result['raw'].strip()}")
        if title == "Chain of Code":
            print("\nTrace (red = Python, purple = LM):")
            coc.print_trace(result["trace"])
            if result["error"]:
                print(f"Execution stopped: {result['error']}")
        mark = "✓" if is_correct(result["answer"], truth) else "✗"
        print(f"\nAnswer: {result['answer']}  {mark}")


if __name__ == "__main__":
    main()
