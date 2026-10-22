"""Does Chain of Thought do better if it writes down each birthday first?

Runs the Chain of Thought prompt from cot_lookups.py on the same 30 random
dates as the slide charts, and compares it with the usual Chain of Thought
results in results/random-30-seed-2026.csv (made by rehearse.py).

Usage: uv run rehearse_lookups.py    (takes about 11 minutes)

Prints one line per date, then a before/after table, and saves one row per
date to results/cot-lookups-random-30-seed-2026.csv.
"""

import csv
from pathlib import Path

from checks import check_cot, summary
from cot_lookups import check_births, run_cot_lookups
from ground_truth import answer
from methods import is_correct
from rehearse import random_dates

OLD_RESULTS = Path("results/random-30-seed-2026.csv")


def total(rows: list[dict], column: str) -> int:
    return sum(int(r[column]) for r in rows)


def main():
    old = {r["date"]: r for r in csv.DictReader(OLD_RESULTS.open())}
    rows = []
    for d, _ in random_dates(30, 2026):
        truth = answer(d)
        result = run_cot_lookups(d)
        ok = is_correct(result["answer"], truth)
        births, steps = check_births(result["raw"]), check_cot(result["raw"], d)
        row = {"date": d, "correct": " / ".join(n for n, _ in truth), "answer": result["answer"], "right": int(ok)}
        for kind in ("math", "fact", "choice"):
            found = [good for k, _, good in steps if k == kind]
            row[f"{kind} right"], row[f"{kind} checked"] = sum(found), len(found)
        row["births right"], row["births checked"] = sum(good for *_, good in births), len(births)
        rows.append(row)
        before = "✓" if old[str(d)]["Chain of Thought correct"] == "1" else "✗"
        print(f"{d}  correct: {row['correct']:<18}  before: {before}  with lookups: "
              f"{'✓' if ok else '✗'} {result['answer']}  ({summary(births + steps)})", flush=True)

    old_rows = [old[str(r["date"])] for r in rows]
    n = len(rows)
    print(f"\n{'':<34}{'before':>10}{'with lookups':>16}")
    lines = [
        ("Correct answers", total(old_rows, "Chain of Thought correct"), n, total(rows, "right"), n),
        ("Birth dates written down, right", 0, 0, total(rows, "births right"), total(rows, "births checked")),
        ("Birthdays in sentences, right", total(old_rows, "CoT fact right"), total(old_rows, "CoT fact checked"),
         total(rows, "fact right"), total(rows, "fact checked")),
        ("Right candidates chosen", total(old_rows, "CoT choice right"), total(old_rows, "CoT choice checked"),
         total(rows, "choice right"), total(rows, "choice checked")),
        ("Math steps right", total(old_rows, "CoT math right"), total(old_rows, "CoT math checked"),
         total(rows, "math right"), total(rows, "math checked")),
    ]
    for label, a, b, c, e in lines:
        print(f"{label:<34}{(f'{a}/{b}' if b else '-'):>10}{f'{c}/{e}':>16}")

    path = Path("results/cot-lookups-random-30-seed-2026.csv")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
