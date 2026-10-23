"""demo.py, but Chain of Thought writes down each birthday first (see cot_lookups.py).

Usage: uv run demo2.py                    (asks for a date)
       uv run demo2.py "15 March 2027"    (or 2027-03-15)

It shows the correct answer first. Then, for each method, it shows the
prompt, waits for Enter, then shows the model's output and whether it is
right. A summary comes at the end.
"""

from functools import partial

from checks import check_coc, check_cot, summary
from coc import PURPLE
from cot_lookups import check_births, cot_lookup_prompt, run_cot_lookups
from demo import BOLD, RESET, ask_for_date, blue_questions, marked, pause, print_truth
from ground_truth import answer
from methods import is_correct, run_coc, run_direct
from prompts import coc_prompt, direct_prompt, fmt, question


def show_lm_call(prompt: str, ask) -> str:
    """The LM's first line of the trace: its whole prompt, then (after Enter) what it writes."""
    pause("see the prompt for the LM's first line")
    print(f"\n{BOLD}===== Chain of Code: prompt for the LM's first line ====={RESET}")
    print(blue_questions(prompt))
    pause("see what the LM writes")
    print(f"\n{BOLD}===== Chain of Code: what the LM writes ====={RESET}\n{PURPLE}", end="")
    written = ask()  # prints it as the LM writes it
    print(RESET)
    pause("continue the trace")
    print()
    return written


METHODS = [("Direct", run_direct), ("Chain of Thought", run_cot_lookups),
           ("Chain of Code", partial(run_coc, show_first_lm_call=show_lm_call))]
PROMPTS = {"Direct": direct_prompt, "Chain of Thought": cot_lookup_prompt, "Chain of Code": coc_prompt}


def spaced(text: str) -> str:
    """For display only: a blank line before and after each "In order through the year" line.

    The model gets the prompt without them, since a blank line is its stop sequence.
    """
    return "\n".join(f"\n{line}\n" if line.startswith("In order through the year:") else line
                     for line in text.split("\n"))


def main():
    d = ask_for_date()
    print(f"\n{blue_questions(question(d))}")
    truth = answer(d)
    print()
    print_truth(truth, d)

    results = []
    for title, run in METHODS:
        pause(f"see the {title} prompt")
        print(f"\n{BOLD}===== {title}: prompt ====={RESET}\n{blue_questions(spaced(PROMPTS[title](d)))}")
        pause(f"run {title}")
        print(f"\n{BOLD}===== {title}: model output ====={RESET}")
        result = run(d, stream=True)  # prints the output (and CoC trace) as it is generated
        if result.get("error"):
            print(f"Execution stopped: {result['error']}")
        answer_ok = is_correct(result["answer"], truth)
        print("\n" + BOLD + marked(answer_ok, f"{title} answer: {result['answer']}"))
        if title == "Chain of Thought":
            checks = check_births(result["raw"]) + check_cot(result["raw"], d)
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
