"""Reproducible benchmark runner. It records only live Ollama responses."""
from __future__ import annotations
import argparse, csv, json
from datetime import datetime, timezone
from pathlib import Path
from .llm import translate
from .parser import parse_formula
from .verifier import check_equivalence

def run(benchmark_path: str, model: str, output_dir: str) -> list[dict]:
    cases = json.loads(Path(benchmark_path).read_text())
    records = []
    for case in cases:
        result = translate(case["requirement"], case["propositions"], model)
        record = {"id": case["id"], "category": case["category"], "ambiguous": case.get("ambiguous", False), "requirement": case["requirement"], "reference_formula": case.get("reference_formula"), "model": model, **result}
        if result["ok"]:
            record["syntax_valid"] = True
            if not record["ambiguous"]:
                verdict = check_equivalence(parse_formula(result["formula"], set(case["propositions"])), parse_formula(case["reference_formula"], set(case["propositions"])))
                record.update({"equivalent": verdict["equivalent"], "sat_status": verdict["status"], "counterexample": verdict["counterexample"]})
        else: record["syntax_valid"] = False
        records.append(record)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out / f"benchmark_{stamp}.json"; csv_path = out / f"benchmark_{stamp}.csv"
    json_path.write_text(json.dumps(records, indent=2))
    fields = sorted({key for row in records for key in row});
    with csv_path.open("w", newline="") as f: writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(records)
    print(f"Saved actual execution records: {json_path}\n{csv_path}")
    return records

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--benchmark", default="data/benchmark.json"); p.add_argument("--model", default="qwen2.5:3b"); p.add_argument("--output-dir", default="results")
    args = p.parse_args(); run(args.benchmark, args.model, args.output_dir)
