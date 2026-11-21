"""Z3-backed equivalence verification with concrete counterexamples."""
from z3 import Bool, Not, And, Or, Implies, Xor, Solver, sat, unsat
from .logic import evaluate
from .parser import Node, variables

def to_z3(node: Node, symbols: dict[str, object]):
    if node.op == "VAR": return symbols[node.value]
    if node.op == "NOT": return Not(to_z3(node.left, symbols))
    a, b = to_z3(node.left, symbols), to_z3(node.right, symbols)
    return {"AND": And, "OR": Or, "IMPLIES": Implies, "IFF": lambda x, y: x == y}[node.op](a, b)

def check_equivalence(generated: Node, reference: Node) -> dict:
    names = sorted(variables(generated) | variables(reference)); z = {name: Bool(name) for name in names}
    solver = Solver(); solver.add(Xor(to_z3(generated, z), to_z3(reference, z)))
    result = solver.check()
    if result == unsat: return {"status": "UNSAT", "equivalent": True, "counterexample": None}
    if result == sat:
        model = solver.model(); assignment = {n: bool(model.eval(z[n], model_completion=True)) for n in names}
        return {"status": "SAT", "equivalent": False, "counterexample": assignment,
                "generated_value": evaluate(generated, assignment), "reference_value": evaluate(reference, assignment)}
    return {"status": "UNKNOWN", "equivalent": None, "counterexample": None}
