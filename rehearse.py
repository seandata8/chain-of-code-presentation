"""Run all three methods on a set of dates, to choose good dates for class.

Usage: uv run rehearse.py
"""

from datetime import date

from ground_truth import answer
from methods import METHODS, is_correct

DATES = [
    (date(1983, 1, 31), "tie, previous year"),
    (date(1989, 12, 3), "next year"),
    (date(1996, 8, 8), "Good Friday"),
    (date(2003, 1, 2), "Good Friday"),
    (date(2003, 2, 26), "previous year"),
    (date(2014, 5, 5), ""),
    (date(2019, 6, 15), "before 2021 (trap)"),
    (date(2020, 1, 9), "before 2021 (trap), previous year"),
    (date(2021, 5, 30), "Truth and Reconciliation"),
    (date(2022, 12, 1), "Good Friday, next year"),
    (date(2022, 12, 21), "tie, next year"),
    (date(2025, 1, 10), "Truth and Reconciliation, previous year"),
    (date(2027, 3, 15), ""),
    (date(2029, 4, 8), "previous year"),
    (date(2033, 6, 21), "Truth and Reconciliation"),
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
