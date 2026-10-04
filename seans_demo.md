# Class Demo: Direct vs. Chain of Thought vs. Chain of Code

## Goal

Build a demo for my class presentation of the paper *Chain of Code: Reasoning with a Language Model-Augmented Code Emulator* (Li et al., ICML 2024). During class I will take a date from the audience, and the demo will answer one question three ways (Direct, Chain of Thought, Chain of Code), comparing each answer with a correct answer computed in Python.

Work in this folder (`~/VSCodeProjects/ChainOfCode`). Do not modify `slides.qmd`. Use Python. Keep the code simple and readable, because I may show it in class. Don't add features I didn't ask for.

## The question

> Of the Canadian federal statutory holidays that are at least 100 days before or after {date}, which one is closest to {date}?

Definitions (use these exactly):

- **Holiday set:** the federal general holidays in the Canada Labour Code: New Year's Day, Good Friday, Victoria Day, Canada Day, Labour Day, Thanksgiving, Remembrance Day, Christmas Day, Boxing Day, and, **from 2021 on only**, the National Day for Truth and Reconciliation (September 30). Use the actual calendar date, not the "observed" weekday when a holiday falls on a weekend.
- **Allowed years:** 1983 or later (the first year the July 1 holiday was called Canada Day). `demo.py` should politely reject earlier dates.
- **"At least 100 days before or after":** the absolute number of days between the holiday and the given date is ≥ 100.
- **"Closest":** the holiday with the smallest absolute distance among those meeting that condition. Search the previous, given, and next years.
- **Ties** (one holiday N days before, another N days after): report both, and count a model's answer as correct if it names either one.
- Do **not** list the holidays in the question sent to the model. Knowing them is part of the test.

## Model

- Ollama, model `qwen2.5-coder:3b-base` (already downloaded). This is a base (completion) model, used in place of text-davinci-003, which no longer exists.
- Always call `ollama.generate(..., raw=True)` so no chat template is applied.
- Use `temperature: 0` and stop sequences (at least `"\nQ:"`) so the model stops after one answer.

## Ground truth

Write `ground_truth.py` with a function `answer(d: date) -> list[(name, date)]` (a list, so ties can return two). Compute holiday dates from rules (Easter via `dateutil.easter`, Victoria Day = Monday before May 25, Thanksgiving = second Monday of October, and so on). Cross-check the dates against the `holidays` package for 1983–2035 and report any disagreement to me rather than silently picking one.

## The three methods

Use few-shot prompting as in the paper: three worked examples from the same task, then the new question. Use different dates in the examples than in the demo. **Compute every example answer with `ground_truth.py`** so the examples are correct.

1. **Direct:** examples show `Q: ...` then `A: <holiday name>`.
2. **Chain of Thought:** examples show `Q: ...`, then `A: Let's think step by step.`, then reasoning in English ending with `So the answer is <holiday name>.`
3. **Chain of Code:** examples show `Q: ...` then Python code in the paper's style (see Fig. A2): use `datetime`/`timedelta` for arithmetic and undefined helper functions for knowledge (e.g., `get_canadian_federal_holidays(year)`), ending with `answer = ...`.

### Chain of Code execution (the LMulator)

The authors' demo notebook is at `papers/coc_demo.ipynb`. Read it first and reuse or adapt its executor. If it is missing or doesn't work with Ollama, implement the **Interweave** method from Section 2.3 of the paper:

- Run the generated code with Python.
- When a line can't be executed (undefined function, exception), send the LM the question, the code so far, and the current program state, and have it return the new values of the affected variables (the "delta state"). Parse those into Python values and continue.
- Retrieve the final answer from the variable `answer`.
- Simple Python types only (str, int, list, dict, tuple, date) are fine, as in the paper.

Print a **trace** for the class: each line, whether **Python** or the **LM** ran it (red for Python, purple for LM, as in the paper's figures), and the delta state.

## Scripts

- `demo.py "15 March 2027"`: accepts a date like `15 March 2027` or `2027-03-15`. Prints the ground truth, then for each method the raw model output, the extracted answer, and ✓/✗. Show the CoC trace.
- `rehearse.py`: runs all three methods on about 15 dates (spread across 1983 to 2035, including some where the answer is Good Friday, some where it is Truth and Reconciliation Day, some just before 2021 where a model might wrongly pick Truth and Reconciliation Day, some where the answer falls in the previous or next year, and at least one tie) and prints a summary table, so I can choose good backup dates for class.

Grading: compare holiday names leniently (ignore case and punctuation, and accept obvious variants like "Truth and Reconciliation Day"). Always show the raw output so I can judge borderline cases myself.

## Setup

I have already run `uv init` in this folder. Use uv for everything: add only what's needed with `uv add ollama holidays python-dateutil`, and run scripts with `uv run` (e.g., `uv run demo.py "15 March 2027"`). Don't use pip. Add a short section to the `README.md` that uv created explaining how to run the demo.

## When done

Run `rehearse.py` and give me a short summary: which dates show the clearest difference between the three methods, and any problems you hit.
