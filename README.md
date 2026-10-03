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
