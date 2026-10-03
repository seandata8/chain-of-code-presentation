"""Run all three methods on a set of dates, to choose good dates for class.

Usage: uv run rehearse.py
"""

from datetime import date

from ground_truth import answer
from methods import METHODS, is_correct

DATES = [
    (date(1955, 7, 20), "Curie, after"),
    (date(1962, 10, 5), "Turing, before"),
    (date(1971, 6, 1), "Darwin, before"),
    (date(1984, 3, 1), "Banting, previous year"),
    (date(1990, 9, 1), "Lovelace, exactly 100 days"),
    (date(2003, 2, 26), "Banting, previous year"),
    (date(2007, 12, 20), "Rutherford, before"),
    (date(2011, 1, 20), "Gauss, exactly 100 days"),
    (date(2016, 4, 1), "Tesla, exactly 100 days"),
    (date(2024, 1, 26), "tie, previous year"),
    (date(2026, 11, 25), "Einstein, next year"),
    (date(2027, 3, 15), "Turing, exactly 100 days"),
    (date(2029, 8, 20), "tie"),
    (date(2030, 4, 10), "Lovelace, previous year"),
    (date(2033, 12, 31), "Gauss, next year"),
]


def main():
    rows = []
    for d, note in DATES:
        truth = answer(d)
        truth_names = " / ".join(name for name, _ in truth)
        print(f"\n##### {d}  ({note or 'no special case'})  correct: {truth_names}")
        row = [str(d), truth_names]
        for title, run in METHODS:
            result = run(d)
            mark = "✓" if is_correct(result["answer"], truth) else "✗"
            print(f"--- {title}: {result['answer']} {mark}")
            print("    " + result["raw"].strip().replace("\n", "\n    "))
            if result.get("error"):
                print(f"    Execution stopped: {result['error']}")
            row.append(f"{mark} {result['answer']}")
        rows.append(row)

    headers = ["Date", "Correct", "Direct", "Chain of Thought", "Chain of Code"]
    widths = [max(len(str(r[i])) for r in rows + [headers]) for i in range(len(headers))]
    print("\n\nSUMMARY")
    for r in [headers] + rows:
        print("  ".join(str(cell).ljust(w) for cell, w in zip(r, widths)))
    for i, (title, _) in enumerate(METHODS):
        score = sum(r[2 + i].startswith("✓") for r in rows)
        print(f"{title}: {score}/{len(rows)} correct")


if __name__ == "__main__":
    main()
