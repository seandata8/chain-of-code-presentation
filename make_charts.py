"""Draw the two results bar charts for the slides (data from Li et al., ICML 2024).

Usage: uv run --with matplotlib make_charts.py
"""

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
    """Table 2: average BIG-Bench Hard accuracy for each way of running the code."""
    rows = [
        ("Interweave (line by line)", 84, True),
        ("Try Python, else LM traces state", 82, True),
        ("Try Python, else LM answers", 80, True),
        ("LM only, traces state", 63, False),
        ("LM only", 57, False),
        ("Python only", 48, False),
    ]
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
    for i, (label, score, both) in enumerate(rows):
        ax.barh(i, score, height=0.62, color=BLUE if both else GRAY)
        ax.text(score + 1, i, f"{score}%", va="center", fontsize=16,
                fontweight="bold" if i == 0 else "normal")
    ax.set_yticks(range(len(rows)), [label for label, _, _ in rows])
    ax.tick_params(axis="y", length=0, labelsize=15, labelcolor=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    clean_axes(ax)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(GRID)
    fig.tight_layout()
    fig.savefig("images/results-ablation.png", transparent=True)


if __name__ == "__main__":
    task_type_chart()
    ablation_chart()
