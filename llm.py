"""The language model: a base (completion) model served by Ollama."""

import ollama

MODEL = "qwen2.5-coder:7b-base"


def generate(prompt: str, stop: list[str], max_tokens: int) -> str:
    """Continue the prompt as raw text (no chat template), greedily."""
    response = ollama.generate(
        model=MODEL,
        prompt=prompt,
        raw=True,
        options={"temperature": 0, "stop": stop, "num_predict": max_tokens},
    )
    return response.response
