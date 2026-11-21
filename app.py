import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.llm import translate
from src.parser import FormulaError, parse_formula, to_display
from src.truth_table import make_truth_table
from src.verifier import check_equivalence

st.set_page_config(page_title="NL → Logic", layout="wide")
st.title("Natural Language → Propositional Logic")
st.caption("CS 491/591 Final Project · LLM translation, truth tables, and Z3 equivalence verification")
st.markdown("Translate a requirement with a local LLM, inspect its behavior, then verify it against a human-reviewed formula.")
st.divider()
st.header("1. Translate the requirement")
cases = json.loads(Path("data/benchmark.json").read_text())
examples = [c for c in cases if not c.get("ambiguous")]
choice = st.selectbox("Load an example", ["Custom"] + [f'{c["id"]}: {c["requirement"]}' for c in examples])
selected = next((c for c in examples if choice.startswith(c["id"] + ":")), None)
default_req = selected["requirement"] if selected else "The robot can move only if the door is open."
default_props = selected["propositions"] if selected else {"M": "The robot can move", "D": "The door is open"}
requirement = st.text_area("English requirement", default_req)
props_text = st.text_area("Propositions (JSON symbol → meaning)", json.dumps(default_props, indent=2))
model = st.text_input("Ollama model", "qwen2.5:3b")
try: propositions = json.loads(props_text); assert isinstance(propositions, dict) and all(isinstance(k, str) and isinstance(v, str) for k,v in propositions.items())
except Exception: st.error("Propositions must be a JSON object of string symbols and meanings."); st.stop()
st.write("Defined propositions:"); st.json(propositions)
if st.button("Translate with Ollama", type="primary"):
    with st.spinner("Requesting structured JSON from Ollama…"):
        st.session_state.translation = translate(requirement, propositions, model)
if "translation" in st.session_state:
    result = st.session_state.translation
    if result["ok"]:
        generated_display = to_display(parse_formula(result["formula"], set(propositions)))
        st.info(f"LLM-generated formula (not yet verified): {generated_display}")
        st.caption(f'Raw formula: `{result["formula"]}` · inference: {result["duration_seconds"]:.2f}s')
        if result["explanation"]: st.write(result["explanation"])
    else: st.error(f"Translation/validation failed: {result['error']}")
st.divider(); st.header("2. Inspect and verify the formula")
st.caption("Compare the formula with a human-reviewed reference. Z3 checks whether any truth assignment makes them disagree.")
formula_text = st.text_input("Formula to inspect", st.session_state.get("translation", {}).get("formula", selected.get("reference_formula", "M -> D") if selected else "M -> D"))
reference = st.text_input("Human-reviewed reference formula", selected.get("reference_formula", "M -> D") if selected else "M -> D")
if st.button("Generate table and verify"):
    try:
        formula, ref = parse_formula(formula_text, set(propositions)), parse_formula(reference, set(propositions))
        st.subheader("Truth table")
        table = make_truth_table(formula); st.dataframe(pd.DataFrame(table).rename(columns={"result": to_display(formula)}), use_container_width=True)
        false_rows = [r for r in table if not r["result"]]
        if false_rows: st.info(f"The formula is false for: {false_rows[0]}. For an implication, it is false precisely when its antecedent is true and consequent false.")
        else: st.info("This formula is true under every displayed assignment.")
        verdict = check_equivalence(formula, ref)
        st.subheader("Z3 verification result")
        if verdict["equivalent"]:
            st.success("UNSAT — Verified equivalent: no truth assignment makes the generated formula and human-reviewed reference disagree.")
        elif verdict["equivalent"] is False:
            assignment = verdict["counterexample"]
            generated_value, reference_value = verdict["generated_value"], verdict["reference_value"]
            st.error("SAT — Not equivalent: Z3 found a counterexample, so the generated formula does not match the human-reviewed reference.")
            st.write("**Counterexample assignment:**", assignment)
            st.write(f"Under this assignment, generated formula = **{generated_value}** and reference formula = **{reference_value}**.")
            if generated_value and not reference_value:
                st.warning("The generated formula is too permissive here: it accepts this assignment even though the human-reviewed condition rejects it.")
            else:
                st.warning("The generated formula is too restrictive here: it rejects this assignment even though the human-reviewed condition accepts it.")
        else:
            st.warning("UNKNOWN — Z3 could not determine equivalence. This result is inconclusive; do not treat the formula as verified.")
        st.caption("Equivalence only checks agreement with the human reference; it does not prove that the reference captures the English requirement.")
    except (FormulaError, ValueError) as exc: st.error(str(exc))
st.divider(); st.header("3. Experiment results")
result_files = sorted(Path("results").glob("benchmark_*.json"), reverse=True)
if result_files:
    records = json.loads(result_files[0].read_text()); unambiguous = [r for r in records if not r["ambiguous"]]
    st.write(f"Showing actual run: `{result_files[0].name}`")
    if records:
        st.metric("Syntax validity", f"{sum(bool(r.get('syntax_valid')) for r in records)/len(records):.1%}")
    if unambiguous: st.metric("Equivalence accuracy", f"{sum(r.get('equivalent') is True for r in unambiguous)/len(unambiguous):.1%}")
    if unambiguous:
        category_rows = []
        for category in sorted({r["category"] for r in unambiguous}):
            group = [r for r in unambiguous if r["category"] == category]
            category_rows.append({"category": category, "cases": len(group), "equivalence accuracy": f"{sum(r.get('equivalent') is True for r in group)/len(group):.1%}",
                                  "avg inference seconds": round(sum(r.get("duration_seconds", 0) for r in group)/len(group), 3)})
        st.write("Accuracy by requirement category")
        st.dataframe(pd.DataFrame(category_rows), use_container_width=True)
    st.dataframe(pd.DataFrame(records), use_container_width=True)
else: st.info("No recorded experiments yet. Run `python -m src.evaluation` after Ollama is running. Metrics will appear here only from real executions.")
