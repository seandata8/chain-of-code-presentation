"""Answer the scientists' birthday question three ways, one method at a time.

Usage: uv run demo.py                    (asks for a date)
       uv run demo.py "15 March 2027"    (or 2027-03-15)

It shows the correct answer first. Then, for each method, it shows the
prompt, waits for Enter, then shows the model's output and whether it is
right. A summary comes at the end.
"""

import sys
from datetime import date, datetime

from checks import check_coc, check_cot, summary
from ground_truth import FIRST_YEAR, answer
from methods import METHODS, is_correct
from prompts import coc_prompt, cot_prompt, direct_prompt, fmt, question

PROMPTS = {"Direct": direct_prompt, "Chain of Thought": cot_prompt, "Chain of Code": coc_prompt}
# Orange, not red, for wrong answers: red already means "Python ran this line" in the trace.
BOLD, GREEN, ORANGE, RESET = "\033[1m", "\033[32m", "\033[38;5;208m", "\033[0m"


def marked(ok: bool, text: str) -> str:
    """Text with a green ✓ if ok, else an orange ✗."""
    return f"{GREEN}✓ {text}{RESET}" if ok else f"{ORANGE}✗ {text}{RESET}"


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


def print_truth(truth: list[tuple[str, date]], d: date) -> None:
    for name, day in truth:
        print(f"Correct answer (computed in Python): {name}, {fmt(day)}, {abs((day - d).days)} days away")


def main():
    d = ask_for_date()
    print(f"\n{question(d)}")
    truth = answer(d)
    print()
    print_truth(truth, d)

    results = []
    for title, run in METHODS:
        pause(f"see the {title} prompt")
        print(f"\n{BOLD}===== {title}: prompt ====={RESET}\n{PROMPTS[title](d)}")
        pause(f"run {title}")
        print(f"\n{BOLD}===== {title}: model output ====={RESET}")
        result = run(d, stream=True)  # prints the output (and CoC trace) as it is generated
        if result.get("error"):
            print(f"Execution stopped: {result['error']}")
        answer_ok = is_correct(result["answer"], truth)
        print("\n" + BOLD + marked(answer_ok, f"{title} answer: {result['answer']}"))
        if title == "Chain of Thought":
            checks = check_cot(result["raw"], d)
            print(f"\nChecking each step ({summary(checks)}):")
        elif title == "Chain of Code":
            checks = check_coc(result["trace"])
            print(f"\nChecking the LM's birthdays ({summary(checks)}):")
        else:
            checks = []
        for kind, claim, ok in checks:
            print(f"  {marked(ok, f'{kind:<6} {claim}')}")
        results.append((title, result["answer"], answer_ok))

    pause("see the results")
    print(f"\n{BOLD}===== Results for {fmt(d)} ====={RESET}")
    print_truth(truth, d)
    for title, model_answer, ok in results:
        print(f"  {marked(ok, f'{title:<17} {model_answer}')}")


if __name__ == "__main__":
    main()
