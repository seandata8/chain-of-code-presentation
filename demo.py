"""Answer the scientists' birthday question three ways, one method at a time.

Usage: uv run demo.py                    (asks for a date)
       uv run demo.py "15 March 2027"    (or 2027-03-15)

For each method it shows the prompt, waits for Enter, then shows the
model's output and whether it is right. A summary comes at the end.
"""

import sys
from datetime import date, datetime

import coc
from ground_truth import FIRST_YEAR, answer
from methods import METHODS, is_correct
from prompts import coc_prompt, cot_prompt, direct_prompt, fmt, question

PROMPTS = {"Direct": direct_prompt, "Chain of Thought": cot_prompt, "Chain of Code": coc_prompt}
BOLD, RESET = "\033[1m", "\033[0m"


def parse_date(text: str) -> date | None:
    for pattern in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(text.strip(), pattern).date()
        except ValueError:
            pass
    return None


def ask_for_date() -> date:
    text = sys.argv[1] if len(sys.argv) > 1 else input("Enter a date (e.g. 15 March 2027): ")
    while True:
        d = parse_date(text)
        if d is None:
            print(f'Sorry, I couldn\'t read "{text}". Try a date like "15 March 2027" or 2027-03-15.')
        elif d.year < FIRST_YEAR:
            print(f"Sorry, please pick a date in {FIRST_YEAR} or later (so every scientist has been born).")
        else:
            return d
        text = input("Enter a date: ")


def pause(message: str) -> None:
    input(f"\n{BOLD}[Press Enter to {message}]{RESET}")


def main():
    d = ask_for_date()
    print(f"\n{question(d)}")
    truth = answer(d)

    results = []
    for title, run in METHODS:
        pause(f"see the {title} prompt")
        print(f"\n{BOLD}===== {title}: prompt ====={RESET}\n{PROMPTS[title](d)}")
        pause(f"run {title}")
        print(f"\n{BOLD}===== {title}: model output ====={RESET}")
        result = run(d)
        print(result["raw"].strip())
        if title == "Chain of Code":
            print("\nTrace (red = Python, purple = LM):")
            coc.print_trace(result["trace"])
            if result["error"]:
                print(f"Execution stopped: {result['error']}")
        mark = "✓" if is_correct(result["answer"], truth) else "✗"
        print(f"\n{BOLD}{title} answer: {result['answer']}  {mark}{RESET}")
        results.append((title, result["answer"], mark))

    pause("see the results")
    print(f"\n{BOLD}===== Results for {fmt(d)} ====={RESET}")
    for name, day in truth:
        print(f"Correct answer (computed in Python): {name}, {fmt(day)}, {abs((day - d).days)} days away")
    for title, model_answer, mark in results:
        print(f"  {mark} {title:<17} {model_answer}")


if __name__ == "__main__":
    main()
