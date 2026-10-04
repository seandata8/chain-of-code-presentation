"""Run all three methods on a set of dates, to choose good dates for class
and to measure how well each method does.

Usage: uv run rehearse.py                          (the 15 hand-picked dates below)
       uv run rehearse.py --random 30 [--seed 2026] (random dates, 1950-2035)

Prints a summary table and saves one row per date to results/<name>.csv,
including the Chain of Thought step checks and Chain of Code birthday checks.
"""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

from checks import check_coc, check_cot, count, summary
from ground_truth import answer
from methods import METHODS, is_correct
from prompts import EXAMPLE_DATES

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


def random_dates(n: int, seed: int) -> list[tuple[date, str]]:
    """n different random dates from 1950 to 2035, skipping example and hand-picked dates."""
    start, end = date(1950, 1, 1), date(2035, 12, 31)
    skip = set(EXAMPLE_DATES) | {d for d, _ in DATES}
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    days = [d for d in days if d not in skip]
    return [(d, "random") for d in sorted(random.Random(seed).sample(days, n))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", type=int, metavar="N", help="use N random dates instead")
    parser.add_argument("--seed", type=int, default=2026, help="random seed (default 2026)")
    args = parser.parse_args()
    if args.random:
        dates, name = random_dates(args.random, args.seed), f"random-{args.random}-seed-{args.seed}"
    else:
        dates, name = DATES, "hand-picked"

    rows, csv_rows = [], []
    all_checks = []  # every Chain of Thought step, for a total at the end
    all_facts = []  # every Chain of Code birthday
    for d, note in dates:
        truth = answer(d)
        truth_names = " / ".join(name for name, _ in truth)
        print(f"\n##### {d}  ({note})  correct: {truth_names}")
        row = [str(d), truth_names]
        csv_row = {"date": d, "note": note, "correct": truth_names}
        for title, run in METHODS:
            result = run(d)
            ok = is_correct(result["answer"], truth)
            print(f"--- {title}: {result['answer']} {'✓' if ok else '✗'}")
            print("    " + result["raw"].strip().replace("\n", "\n    "))
            if result.get("error"):
                print(f"    Execution stopped: {result['error']}")
            row.append(f"{'✓' if ok else '✗'} {result['answer']}")
            csv_row[f"{title} answer"] = result["answer"]
            csv_row[f"{title} correct"] = int(ok)
            if title == "Chain of Thought":
                checks = check_cot(result["raw"], d)
                all_checks += checks
                print(f"    Steps: {summary(checks)}")
                for kind in ("math", "fact", "choice"):
                    csv_row[f"CoT {kind} right"], csv_row[f"CoT {kind} checked"] = count(checks, kind)
            if title == "Chain of Code":
                facts = check_coc(result["trace"])
                all_facts += facts
                print(f"    Birthdays: {summary(facts)}")
                csv_row["CoC birthdays right"], csv_row["CoC birthdays checked"] = count(facts, "fact")
        rows.append(row + [summary(checks), summary(facts)])
        csv_rows.append(csv_row)

    headers = ["Date", "Correct", "Direct", "Chain of Thought", "Chain of Code", "CoT steps right", "CoC birthdays right"]
    widths = [max(len(str(r[i])) for r in rows + [headers]) for i in range(len(headers))]
    print("\n\nSUMMARY")
    for r in [headers] + rows:
        print("  ".join(str(cell).ljust(w) for cell, w in zip(r, widths)))
    for title, _ in METHODS:
        score = sum(r[f"{title} correct"] for r in csv_rows)
        print(f"{title}: {score}/{len(csv_rows)} correct")
    print(f"Chain of Thought steps, all dates: {summary(all_checks)}")
    print(f"Chain of Code birthdays, all dates: {summary(all_facts)}")

    path = Path("results") / f"{name}.csv"
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
