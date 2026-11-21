# Presentation Guide (30 minutes)

## Architecture (5 min)

Explain the path: English + explicit proposition map → Ollama JSON response → safe AST parser → truth table → Z3 XOR equivalence check. Emphasize that the LLM is not trusted: invalid syntax and unknown symbols are rejected, and no generated text is executed.

## Live demo (12 min)

1. Start with B03: “The robot can move only if the door is open.” Point out `M` and `D`.
2. Click **Translate with Ollama**. State the model result as observed—do not promise it will produce `M → D`.
3. Put `M -> D` in Formula to inspect and click **Generate table and verify**. Explain the false row (`M=True, D=False`).
4. Use `M -> D` as reference; show `UNSAT` means there is no disagreement.
5. Replace inspected formula with `D -> M`; show `SAT` and its counterexample. This exposes the common “only if” reversal error.
6. Scroll to results. If you ran the benchmark, distinguish measured metrics from model-independent tests. If not, explain why empty results are honest.

## Experiments (6 min)

The 30 curated cases cover implications, only-if, iff, conjunction, disjunction, negation, unless, nesting, multiple symbols, and explicit ambiguity. Run the evaluation command ahead of time with the exact model used in the demo. The saved JSON/CSV preserves formula text, duration, syntax outcome, equivalence verdict, and counterexample. Accuracy excludes the four ambiguous cases.

## Questions to prepare for (7 min)

- **Why Z3?** It proves logical equivalence by asking whether XOR can ever be true, and produces a witness when it can.
- **Why truth tables too?** They are transparent and pedagogically useful, though exponential.
- **Does equivalence prove the English translation correct?** No; it proves agreement with the human-reviewed reference only.
- **Why local Ollama?** Reproducible, private inference without a paid API key.
- **What is next?** Improve prompt/evaluation, add uncertainty/clarification handling, and move beyond propositional logic for temporal or quantified requirements.
