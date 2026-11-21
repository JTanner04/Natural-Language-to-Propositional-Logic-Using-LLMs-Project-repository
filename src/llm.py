"""Ollama client that requires a JSON-only translation response."""
from __future__ import annotations
import json, time
import ollama
from .parser import FormulaError, parse_formula

SYSTEM = """You translate a simple English requirement into propositional logic. Return ONLY JSON with keys formula and explanation. Use exactly and only the supplied proposition symbols. Formula syntax: NOT/AND/OR/IMPLIES/IFF or ¬ ∧ ∨ → ↔ and parentheses. Do not introduce symbols or prose in formula."""

def translate(requirement: str, propositions: dict[str, str], model: str = "qwen2.5:3b") -> dict:
    prompt = f"Requirement: {requirement}\nPropositions: {json.dumps(propositions)}"
    started = time.perf_counter()
    try:
        response = ollama.chat(model=model, messages=[{"role":"system","content":SYSTEM}, {"role":"user","content":prompt}], format="json", options={"temperature": 0})
        raw = response["message"]["content"]
        payload = json.loads(raw)
        if not isinstance(payload, dict) or not isinstance(payload.get("formula"), str): raise ValueError("JSON must contain string key 'formula'")
        formula = payload["formula"]
        parse_formula(formula, set(propositions))
        return {"ok": True, "formula": formula, "explanation": str(payload.get("explanation", "")), "raw": raw,
                "duration_seconds": time.perf_counter() - started}
    except (Exception, FormulaError) as exc:
        return {"ok": False, "error": str(exc), "duration_seconds": time.perf_counter() - started}
