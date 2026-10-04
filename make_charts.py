"""Draw the results bar charts for the slides.

The first two use data from Li et al., ICML 2024; the demo charts read our
own results from results/random-30-seed-2026.csv (made by rehearse.py).

Usage: uv run --with matplotlib make_charts.py
"""

import csv

import matplotlib.pyplot as plt

BLUE = "#2a78d6"  # Chain of Code / uses both Python and the LM
GRAY = "#b8b6ae"  # everything else
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({"font.family": "Arial", "font.size": 15, "text.color": INK,
                     "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})


def clean_axes(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def task_type_chart():
    """Figure 4 / Table A1: average BIG-Bench Hard accuracy by task type."""
    groups = {"Algorithmic tasks": [41, 71, 95], "Language tasks": [67, 74, 74]}
    methods = ["Direct", "CoT", "CoC"]
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
    positions, labels = [], []
    for g, (group, scores) in enumerate(groups.items()):
        for m, (method, score) in enumerate(zip(methods, scores)):
            x = g * 4 + m
            ax.bar(x, score, width=0.8, color=BLUE if method == "CoC" else GRAY)
            ax.text(x, score + 1.5, f"{score}%", ha="center", va="bottom",
                    fontsize=17, fontweight="bold" if method == "CoC" else "normal")
            positions.append(x)
            labels.append(method)
        ax.text(g * 4 + 1, -17, group, ha="center", fontsize=18, color=INK)
    ax.set_xticks(positions, labels)
    ax.tick_params(axis="x", length=0, labelsize=16)
    ax.set_ylim(0, 105)
    ax.set_yticks([])
    clean_axes(ax)
    fig.tight_layout()
    fig.savefig("images/results-task-type.png", transparent=True)


def ablation_chart():
    """Table 2: average BIG-Bench Hard accuracy with Python, the LM, or both running the code."""
    rows = [
        ("Python + LM (interweave)", 84, True),
        ("LM only", 57, False),
        ("Python only", 48, False),
    ]
    fig, ax = plt.subplots(figsize=(9, 3.2), dpi=200)
    for i, (label, score, both) in enumerate(rows):
        ax.barh(i, score, height=0.6, color=BLUE if both else GRAY)
        ax.text(score + 1, i, f"{score}%", va="center", fontsize=18,
                fontweight="bold" if i == 0 else "normal")
    ax.set_yticks(range(len(rows)), [label for label, _, _ in rows])
    ax.tick_params(axis="y", length=0, labelsize=18, labelcolor=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    clean_axes(ax)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(GRID)
    fig.tight_layout()
    fig.savefig("images/results-ablation.png", transparent=True)


def demo_charts(path="results/random-30-seed-2026.csv"):
    """Our demo on 30 random dates: answers right, and steps right."""
    with open(path) as f:
        rows = list(csv.DictReader(f))

    def total(column):
        return sum(int(r[column]) for r in rows)

    def bars(items, filename):
        fig, ax = plt.subplots(figsize=(6, 4.6), dpi=200)
        for x, (label, right, out_of, is_coc) in enumerate(items):
            percent = round(100 * right / out_of)
            ax.bar(x, percent, width=0.7, color=BLUE if is_coc else GRAY)
            ax.text(x, percent + 2, f"{percent}%\n({right}/{out_of})", ha="center", va="bottom",
                    fontsize=17, fontweight="bold" if is_coc else "normal")
        ax.set_xticks(range(len(items)), [label for label, *_ in items])
        ax.tick_params(axis="x", length=0, labelsize=18, labelcolor=INK)
        ax.set_ylim(0, 125)
        ax.set_yticks([])
        clean_axes(ax)
        fig.tight_layout()
        fig.savefig(f"images/{filename}", transparent=True)

    n = len(rows)
    bars([("Direct", total("Direct correct"), n, False),
          ("CoT", total("Chain of Thought correct"), n, False),
          ("CoC", total("Chain of Code correct"), n, True)], "demo-answers.png")
    bars([("CoT\nfacts", total("CoT fact right"), total("CoT fact checked"), False),
          ("CoT\nmath", total("CoT math right"), total("CoT math checked"), False),
          ("CoT\nchoices", total("CoT choice right"), total("CoT choice checked"), False),
          ("CoC\nfacts", total("CoC birthdays right"), total("CoC birthdays checked"), True)], "demo-steps.png")


if __name__ == "__main__":
    task_type_chart()
    ablation_chart()
    demo_charts()
