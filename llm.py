"""The language model: a base (completion) model served by Ollama."""

import ollama

MODEL = "qwen2.5-coder:7b-base"


def generate(prompt: str, stop: list[str], max_tokens: int, stream: bool = False) -> str:
    """Continue the prompt as raw text (no chat template), greedily.

    With stream=True, also print the text piece by piece as the model writes it.
    """
    options = {"temperature": 0, "stop": stop, "num_predict": max_tokens}
    if not stream:
        return ollama.generate(model=MODEL, prompt=prompt, raw=True, options=options).response
    text = ""
    for chunk in ollama.generate(model=MODEL, prompt=prompt, raw=True, options=options, stream=True):
        print(chunk.response, end="", flush=True)
        text += chunk.response
    return text
