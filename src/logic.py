"""Formula evaluation; formulas are data structures, never executable code."""
from .parser import Node

def evaluate(node: Node, assignment: dict[str, bool]) -> bool:
    if node.op == "VAR":
        if node.value not in assignment: raise KeyError(f"Missing truth value for {node.value}")
        return assignment[node.value]  # type: ignore[index]
    if node.op == "NOT": return not evaluate(node.left, assignment)  # type: ignore[arg-type]
    left, right = evaluate(node.left, assignment), evaluate(node.right, assignment)  # type: ignore[arg-type]
    if node.op == "AND": return left and right
    if node.op == "OR": return left or right
    if node.op == "IMPLIES": return (not left) or right
    if node.op == "IFF": return left == right
    raise ValueError(f"Unknown operation {node.op}")
