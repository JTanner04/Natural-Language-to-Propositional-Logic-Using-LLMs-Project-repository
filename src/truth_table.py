from itertools import product
from .logic import evaluate
from .parser import Node

def _ordered_variables(node: Node) -> list[str]:
    """First appearance order makes tables follow the input formula (M, then D)."""
    if node.op == "VAR": return [node.value]  # type: ignore[list-item]
    items = _ordered_variables(node.left) if node.left else []
    if node.right: items.extend(_ordered_variables(node.right))
    return list(dict.fromkeys(items))

def make_truth_table(formula: Node, max_variables: int = 10) -> list[dict[str, bool]]:
    symbols = _ordered_variables(formula)
    if len(symbols) > max_variables:
        raise ValueError(f"Truth tables are limited to {max_variables} propositions (got {len(symbols)}).")
    rows = []
    for values in product([False, True], repeat=len(symbols)):
        row = dict(zip(symbols, values)); row["result"] = evaluate(formula, row); rows.append(row)
    return rows
