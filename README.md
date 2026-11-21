# Natural Language to Propositional Logic Using LLMs

CS 491/591 final project for Jeremiah Tanner. The app asks a local Ollama model to translate a constrained English requirement into a propositional-logic formula, validates it with a safe parser, shows a truth table, and checks it against a human-reviewed reference with Z3.

## Stack

Python 3.11+, Streamlit, Ollama (default `qwen2.5:3b`), Z3, pytest, JSON/CSV. Formula text is parsed into an AST; the project never executes model output or calls `eval`.

## Install and run (macOS)

```bash
cd nl_logic_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install ollama
ollama serve
# In another terminal:
ollama pull qwen2.5:3b
streamlit run app.py
```

Open the local URL printed by Streamlit. Select benchmark B03 for the robot/door demonstration. The app validates that the model returned JSON and used only defined symbols before accepting its formula.

## Tests and benchmark evaluation

```bash
pytest -q
python -m src.evaluation --model qwen2.5:3b
```

The benchmark command makes live local model calls and writes timestamped raw records to `results/` in JSON and CSV. It does **not** ship invented scores or LLM outputs. After a run, the dashboard shows metrics computed from the newest saved record: syntax validity, unambiguous equivalence accuracy, and individual rows. The dataset has 30 cases, including four deliberately ambiguous cases that require clarification and are excluded from accuracy.

## Pipeline

1. User supplies a requirement and symbol-to-meaning mapping.
2. Ollama receives both plus a JSON-only instruction.
3. The AST parser validates syntax, precedence, parentheses, and symbol allow-list.
4. The truth-table generator enumerates assignments (limited to 10 propositions).
5. Z3 solves `Xor(generated, reference)`: `UNSAT` means equivalent; `SAT` returns a counterexample; `UNKNOWN` is inconclusive.

For `M → D`, the false row is `M=True, D=False`: the robot moves while the door is not open. Checking `D → M` against it is SAT, because exactly that assignment distinguishes them.

## Limitations

Translation quality depends on the local model and prompt; a logically equivalent formula can still encode a mistaken human reference. Propositional logic does not express time, quantifiers, probability, or rich modal meanings. “Unless,” “when,” and natural-language `or` can require human clarification. Full truth tables grow exponentially and are capped at 10 variables.
