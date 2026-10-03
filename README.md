# Chain of Code: Paper Presentation

A presentation of the paper *Chain of Code: Reasoning with a Language Model-Augmented Code Emulator* (Li et al., ICML 2024), prepared for **CSC2108: Automated Reasoning** at the University of Toronto.

**[View the slides](https://seandata8.github.io/chain-of-code-presentation/)**

## The paper

Li, C., Liang, J., Zeng, A., Chen, X., Hausman, K., Sadigh, D., Levine, S., Fei-Fei, L., Xia, F., & Ichter, B. (2024). *Chain of Code: Reasoning with a Language Model-Augmented Code Emulator.* Proceedings of the 41st International Conference on Machine Learning (ICML), PMLR 235.

- Paper: <https://arxiv.org/abs/2312.04474>
- Project page: <https://chain-of-code.github.io/>

Figures taken from the paper are credited on the slides where they appear. The paper itself is not included in this repository.

## Building the slides

The slides are written in [Quarto](https://quarto.org/) as a reveal.js presentation.

```bash
quarto render
```

This renders `slides.qmd` into `docs/`. GitHub Pages serves the site from that folder, so commit `docs/` after rendering. To preview locally while editing:

```bash
quarto preview slides.qmd
```

## Layout

| Path | Contents |
| --- | --- |
| `slides.qmd` | Slide source |
| `_quarto.yml` | Quarto project config (sets the output folder to `docs/`) |
| `docs/` | Rendered site published by GitHub Pages |
| `docs/index.html` | Redirects the site root to the slides |

## Running the demo

The demo asks a local language model one question three ways (Direct, Chain of Thought, Chain of Code) and checks each answer against one computed in Python:

> Of the Canadian federal statutory holidays that are at least 100 days before or after {date}, which one is closest to {date}?

It needs [uv](https://docs.astral.sh/uv/) and [Ollama](https://ollama.com/) with the base model pulled:

```bash
ollama pull qwen2.5-coder:7b-base
```

Then:

```bash
uv run demo.py "15 March 2027"   # one date (also accepts 2027-03-15); dates from 1983 on
uv run rehearse.py               # all three methods on 15 test dates, with a summary table
```

The Chain of Code trace shows each line in red if Python ran it and purple if the language model emulated it.

| File | Contents |
| --- | --- |
| `ground_truth.py` | Holiday dates from rules, and the correct answer |
| `prompts.py` | Few-shot prompts for the three methods |
| `llm.py` | The model call (Ollama, raw completion, temperature 0) |
| `coc.py` | Chain of Code executor (Interweave: Python, falling back to the LM line by line) |
| `methods.py` | Runs each method and grades its answer |
| `demo.py`, `rehearse.py` | The scripts above |
