"""Chain of Code execution: the Interweave method (Section 2.3 of the paper).

Python runs each line of the model's code. When a line fails (for example,
it calls an undefined helper like get_birth_date), the LM
acts as a code emulator ("LMulator"): it is shown the question, the code
so far, and the program state, and it returns the new values of the
variables that line changes (the "delta state"). Execution then continues.

Adapted from the authors' demo notebook (paper/coc_demo.ipynb), which also
wraps lines in try/except and follows execution with sys.settrace.
"""

import ast
import copy
import sys
from datetime import date

from llm import generate

FILENAME = "<chain-of-code>"
SIMPLE_TYPES = (bool, int, float, str, list, tuple, dict, set, date, type(None))

RED, PURPLE, RESET = "\033[31m", "\033[35m", "\033[0m"

# Shows the LM the trace format. Deliberately about people other than the
# demo's ten scientists, so it doesn't give away any of the answer.
LMULATOR_EXAMPLES = """Q: Which Beatle was born first?
from datetime import date
birthdays = get_beatles_birthdays()
state: {}
line: birthdays = get_beatles_birthdays()
delta state: {'birthdays': [('John Lennon', date(1940, 10, 9)), ('Paul McCartney', date(1942, 6, 18)), ('George Harrison', date(1943, 2, 25)), ('Ringo Starr', date(1940, 7, 7))]}

Q: What are the capitals of France and Japan?
capitals = {}
for country in ['France', 'Japan']:
    capital = get_capital(country)
state: {'capitals': {'France': 'Paris'}, 'country': 'Japan'}
line:     capital = get_capital(country)
delta state: {'capital': 'Tokyo'}"""


def show(value) -> str:
    """repr, but with dates written as date(2027, 3, 15)."""
    return repr(value).replace("datetime.date(", "date(")


def get_state(env: dict) -> dict:
    """The program's variables that have simple types (as in the notebook)."""
    return {
        name: copy.deepcopy(value)
        for name, value in env.items()
        if not name.startswith("__") and isinstance(value, SIMPLE_TYPES)
    }


def get_delta_state(before: dict, after: dict) -> dict:
    return {name: value for name, value in after.items() if name not in before or before[name] != value}


def to_python(node: ast.expr):
    """Convert the LM's text to Python values: literals and date(y, m, d), nothing else."""
    if isinstance(node, ast.Call) and ast.unparse(node.func) in ("date", "datetime.date"):
        return date(*(to_python(arg) for arg in node.args))
    if isinstance(node, ast.List):
        return [to_python(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(to_python(item) for item in node.elts)
    if isinstance(node, ast.Set):
        return {to_python(item) for item in node.elts}
    if isinstance(node, ast.Dict):
        return {to_python(k): to_python(v) for k, v in zip(node.keys, node.values)}
    return ast.literal_eval(node)


def parse_delta_state(text: str) -> dict:
    value = to_python(ast.parse(text.strip(), mode="eval").body)
    if not isinstance(value, dict):
        raise ValueError("delta state is not a dict")
    return value


def assigned_names(line: str) -> set[str]:
    """Variables a plain assignment line overwrites, e.g. {'born'} for `born = f(x)`."""
    try:
        stmt = ast.parse(line.strip()).body[0]
    except (SyntaxError, IndexError):
        return set()
    if not isinstance(stmt, ast.Assign):
        return set()
    targets = [t for target in stmt.targets for t in (target.elts if isinstance(target, ast.Tuple) else [target])]
    return {t.id for t in targets if isinstance(t, ast.Name)}


def ask_lmulator(question: str, lines: list[str], lineno: int, state: dict) -> str:
    # Leave out the old values of the variables this line overwrites: a small
    # LM tends to copy them (e.g. the previous scientist's birth date).
    overwritten = assigned_names(lines[lineno - 1])
    state = {name: value for name, value in state.items() if name not in overwritten}
    code_so_far = "\n".join(lines[:lineno])
    prompt = (
        f"{LMULATOR_EXAMPLES}\n\n{question}\n{code_so_far}\n"
        f"state: {show(state)}\nline: {lines[lineno - 1]}\ndelta state:"
    )
    return generate(prompt, stop=["\n"], max_tokens=1000).strip()


def wrap_in_try(statements: list[ast.stmt], wrapped_lines: set[int]) -> list[ast.stmt]:
    """Put each simple statement in `try: ... except Exception: pass`.

    The try keeps the statement's line number, so the trace still lines up
    with the model's code. Loops and ifs aren't wrapped, but their bodies are.
    """
    result = []
    for stmt in statements:
        if hasattr(stmt, "body"):
            stmt.body = wrap_in_try(stmt.body, wrapped_lines)
            stmt.orelse = wrap_in_try(getattr(stmt, "orelse", []), wrapped_lines)
            result.append(stmt)
        else:
            handler = ast.ExceptHandler(type=ast.Name("Exception"), name=None, body=[ast.Pass()])
            result.append(ast.copy_location(ast.Try(body=[stmt], handlers=[handler], orelse=[], finalbody=[]), stmt))
            wrapped_lines.add(stmt.lineno)
    return result


def execute(question: str, code: str):
    """Run the code with Python, falling back to the LM line by line.

    Returns (answer, trace, error). Each trace entry is one line run:
    {"line", "by": "Python" or "LM", "delta": delta state, "lm_output"}.
    """
    lines = code.splitlines()
    wrapped_lines = set()
    tree = ast.parse(code)
    tree.body = wrap_in_try(tree.body, wrapped_lines)
    program = compile(ast.fix_missing_locations(tree), FILENAME, "exec")

    env = {}
    trace = []
    before = {}  # state when the current line started

    def finish_line():
        if trace and trace[-1]["delta"] is None:
            trace[-1]["delta"] = get_delta_state(before, get_state(env))

    def tracer(frame, event, arg):
        nonlocal before
        if frame.f_code.co_filename != FILENAME or frame.f_code.co_name != "<module>":
            return None  # ignore lambdas and other functions the code calls
        if event == "line":
            if trace and trace[-1]["lineno"] == frame.f_lineno:
                return tracer  # same line again (the try/except bookkeeping)
            finish_line()
            before = get_state(env)
            trace.append({"lineno": frame.f_lineno, "line": lines[frame.f_lineno - 1],
                          "by": "Python", "delta": None, "lm_output": None})
        elif event == "exception" and trace[-1]["by"] == "Python" and frame.f_lineno in wrapped_lines:
            # Errors here must be caught: an exception in a trace function
            # silently switches tracing off.
            entry = trace[-1]
            entry["by"] = "LM"
            try:
                entry["lm_output"] = ask_lmulator(question, lines, frame.f_lineno, before)
                entry["delta"] = parse_delta_state(entry["lm_output"])  # show what the LM said
                env.update(entry["delta"])
                entry["usable"] = True
            except Exception as e:
                entry["usable"] = False  # state is unchanged; the trace shows why
                entry["lm_error"] = f"{type(e).__name__}: {e}"
        elif event == "return":
            finish_line()
        return tracer

    error = None
    sys.settrace(tracer)
    try:
        exec(program, env)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    finally:
        sys.settrace(None)
    return env.get("answer"), trace, error


def print_trace(trace: list[dict], width: int = 160) -> None:
    """Python lines in red, LM lines in purple, as in the paper's figures.

    The LM's output is shown in full; long Python deltas are cut to `width`.
    """
    for entry in trace:
        color = RED if entry["by"] == "Python" else PURPLE
        print(f"{color}{entry['by']:>6} | {entry['line']}{RESET}")
        if entry["by"] == "LM" and not entry["usable"]:
            print(f"       | LM output not usable ({entry['lm_error']}): {entry['lm_output']}")
            continue
        delta = f"delta state: {show(entry['delta'])}"
        if entry["by"] == "Python" and len(delta) > width:
            delta = delta[:width] + " ..."
        print(f"       | {color}{delta}{RESET}")
